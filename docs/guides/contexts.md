# Contexts – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/contexts/`  
**Version:** 2.0.0

## Overview

Contexts form the runtime "body" of a Tiferet application. They encapsulate interaction surfaces, orchestration, and supporting services behind clean, injectable classes. While blueprints (`tiferet/blueprints/`) own the application lifecycle and wiring, contexts own the per-interface runtime shape — how requests are parsed, features are executed, errors are handled, and responses are returned.

Tiferet distinguishes between two categories of contexts:

- **High-level contexts** — extend `AppInterfaceContext` and expose the interface's runtime entry point (e.g., a CLI interface or a web API). They delegate to lower-level contexts for execution concerns.
- **Low-level contexts** — single-purpose orchestrators that back the high-level context (e.g., `FeatureContext`, `AsyncFeatureContext`, `RequestContext`, `ErrorContext`, `LoggingContext`, `CacheContext`).

This guide covers cross-cutting strategies for using, extending, and composing contexts. For artifact-level structure and code style, see [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md).

## Context Responsibilities

Every context in `tiferet/contexts/` has a single, well-defined responsibility:

| Context | Responsibility |
| --- | --- |
| `AppInterfaceContext` | Parse the incoming request, execute the feature, format the response, and handle errors at the interface boundary. |
| `CliContext` | Extend `AppInterfaceContext` with CLI concerns: build an argparse parser from configured commands/arguments, parse `argv` into a request (`parse_cli_request`), and dispatch via the inherited `run` (`run_cli`). |
| `FeatureContext` | Resolve each configured step via the injected `get_dependency` handler, parse parameters, and execute the steps sequentially against a `RequestContext` (operating on a pre-loaded `Feature`). |
| `AsyncFeatureContext` | Subclass of `FeatureContext` that awaits coroutine-based steps via `execute_feature_async`; selected by `AppInterfaceContext` when a feature's `is_async` flag is set. |
| `ErrorContext` | Format exceptions into structured, localized API responses using `ErrorService`. |
| `LoggingContext` | Build loggers from configured formatters, handlers, and logger specs. |
| `CacheContext` | Provide an in-memory keyed cache for reusable objects (e.g., loaded features, service providers). |
| `RequestContext` | Carry request headers, data, and the feature result through the execution pipeline; produce the final response via `handle_response`. |

Contexts are consumed by the `AppInterfaceContext` (and its subclasses) — not by domain events. Domain events only receive injected **services**, never contexts.

## The AppInterfaceContext Pattern

`AppInterfaceContext` is the canonical high-level context. Its `run` method defines the standard request lifecycle:

```python
def run(self, feature_id, headers=None, data=None, **kwargs):
    # Build logger.
    logger = self.logging.build_logger()

    # Parse request into a RequestContext.
    request = self.parse_request(headers or {}, data or {}, feature_id)

    # Execute the feature, capturing TiferetError.
    try:
        self.execute_feature(feature_id=feature_id, request=request, logger=logger, **kwargs)
    except TiferetError as e:
        return self.handle_error(e)

    # Return the response via the request context.
    return request.handle_response()
```

The four steps — **parse**, **execute**, **handle errors**, **handle response** — are the extension points subclasses typically override.

### Extending AppInterfaceContext

Create a subclass when the interface needs to translate a transport-specific payload (e.g., CLI `argv`, Flask `Request`) into a `RequestContext`, or when the response needs transport-specific formatting.

```python
# ** context: flask_api_context
class FlaskApiContext(AppInterfaceContext):
    '''
    Flask API context that translates Flask requests into feature invocations.
    '''

    # * attribute: flask_handler
    flask_handler: FlaskApiHandler

    # * init
    def __init__(self, interface_id, features, errors, logging, flask_handler):
        super().__init__(interface_id, features, errors, logging)
        self.flask_handler = flask_handler

    # * method: parse_request
    def parse_request(self, flask_request) -> RequestContext:
        '''
        Translate a Flask request into a RequestContext.
        '''

        # Extract headers, data, and feature_id from the Flask request.
        headers, data, feature_id = self.flask_handler.extract(flask_request)

        # Delegate to the base parse_request for RequestContext construction.
        return super().parse_request(headers=headers, data=data, feature_id=feature_id)
```

Override only the methods you need. Always call `super()` for shared behavior (e.g., adding `interface_id` to headers).

### CLI Interfaces and CliContext

CLI interfaces are handled by `CliContext` (`tiferet/contexts/cli.py`), a high-level context that extends `AppInterfaceContext` with command-line concerns. It retrieves CLI commands (`list_commands_evt`) and parent arguments (`get_parent_args_evt`), builds an argparse parser, parses `argv` into a `RequestContext` (`parse_cli_request`), and dispatches through the inherited `run` pipeline (`run_cli`). Stateless parsing helpers — `group_commands_by_key`, `build_parser`, and `derive_feature_request` — live as side-effect-free module-level functions, and per-argument argparse translation lives on `CliArgument.to_argparse_kwargs()`.

A consumer CLI interface opts in by pointing its config at `module_path: tiferet.contexts.cli` / `class_name: CliContext`. The `build_cli` blueprint is a thin entrypoint that realizes the interface and calls `cli_context.run_cli(argv)`. `CliContext` is selected explicitly through the interface config; it intentionally omits `domain_type`, so the `ContextMeta` registry keeps mapping `AppInterface` to `AppInterfaceContext`.

## Low-Level Context Lifecycles

### FeatureContext

`FeatureContext.execute_feature` drives the core feature pipeline:

1. Load the feature (cached when possible) via `get_feature_handler`.
2. For each configured step:
   - Evaluate the step's `condition` expression (if present) via `evaluate_condition`. If the condition resolves to `False`, the step is silently skipped.
   - Resolve the domain event via the injected `get_dependency(service_id, *flags)` handler.
   - Parse each step parameter with `parse_request_parameter` (supports `$r.<key>` request-backed parameters).
   - Invoke `handle_feature_step`, which executes the event and stores the result on the `RequestContext` under `data_key`.

Feature-level flags (defined on the `Feature`) are combined with step-level flags and passed to the `get_dependency` handler. Higher priority is given to feature-level flags.

### Conditional Step Execution

`EventFeatureStep` supports an optional `condition` field — a boolean expression string evaluated against request data before the step executes. The `$r.` prefix references values from `request.data` (e.g., `$r.b != 0`, `$r.mode == 'advanced'`).

- When `condition` is `None` or empty, the step always executes (backward compatible).
- When `condition` evaluates to `False`, the step is silently skipped (no error raised).
- Invalid or unparseable expressions are treated as `False` (defensive).

YAML configuration example:

```yaml
features:
  calc:
    safe_divide:
      name: Safe Divide
      description: Divides only when denominator is non-zero
      commands:
        - service_id: divide_number_event
          name: Divide a by b
          condition: '$r.b != 0'
```

### AsyncFeatureContext

`AsyncFeatureContext` extends `FeatureContext` for features whose steps execute asynchronously. It adds `handle_feature_step_async` and `execute_feature_async`, which await coroutine-based domain events (and async middleware) while reusing the inherited step resolution, parameter parsing, condition evaluation, and middleware composition. The synchronous helpers are unchanged.

Selection is driven by the `Feature.is_async` flag. `AppInterfaceContext.execute_feature` instantiates `AsyncFeatureContext` instead of `FeatureContext` when `is_async` is `True` and drives `execute_feature_async` to completion via an internal `_run_coroutine` helper — `asyncio.run` when no event loop is running, otherwise a short-lived worker thread — so the public `run()` entry point stays synchronous. Because `AsyncFeatureContext` does not declare its own `domain_type`, the `ContextMeta` registry still resolves `Feature` to the synchronous `FeatureContext`.

### Service Resolution (ServiceResolver)

Feature-step services are resolved by `ServiceResolver` (`tiferet/di/settings.py`), whose bound `get_dependency(configuration_id, *flags)` method is injected into the hub and forwarded to each `FeatureContext`. There is no `DIContext`. `ServiceResolver.get_dependency` performs:

1. Normalize the flags into a flat list.
2. Build (or retrieve from cache) a per-flag `ServiceContainer` via `build_container`.
3. Resolve and return the service from the container by `configuration_id`.

`build_container` lists all `ServiceConfiguration` objects and constants (merging bootstrap defaults via `list_all_settings`), parses constants and per-configuration parameters (`load_constants`), resolves each configuration to a concrete type (`build_type_map`), and constructs a `ServiceContainer` directly (registering constants before service types). The blueprint composes the `ServiceResolver` via the `CreateServiceResolver` bootstrap event in `load_app_instance` (`tiferet/blueprints/main.py`).

### RequestContext

`RequestContext` is a plain data carrier populated by `parse_request` and mutated by step handlers via `set_result(result, data_key)`. Its `handle_response` method builds the final response object returned by `AppInterfaceContext.run`.

### ErrorContext and LoggingContext

- `ErrorContext.format_response(error, exception, lang)` formats a localized payload from a pre-loaded `Error` domain object (error retrieval is owned by the hub's `load_error_domain`). `AppInterfaceContext.handle_error` loads the error domain, formats the payload, and wraps it in `TiferetAPIError`.
- `LoggingContext.build_logger` composes formatters, handlers, and loggers defined in configuration into a ready-to-use logger instance.

The error context is built on demand inside `handle_error`; the logging context is lazily cached via `load_logging_context`. Both are typically not subclassed — extend the underlying services instead.

### CacheContext

A simple keyed in-memory cache. `AppInterfaceContext` creates one `CacheContext` per interface and shares it with the sub-contexts it builds (the feature, error, and logging contexts). Treat it as a per-interface cache — it is not shared across interfaces.

## Composition in the Application Graph

The `build_app` blueprint constructs the `AppInterfaceContext` declaratively from the loaded `AppInterface` (binding it as `self.domain`). The hub then builds its sub-contexts on demand, sharing a single `CacheContext`:

```
build_app (blueprint)
  └── ServiceResolver           (owns DI assembly; get_dependency injected into the hub)
        └── AppInterfaceContext  (hub, bound to AppInterface)
              ├── FeatureContext   ── get_dependency + shared CacheContext
              ├── ErrorContext     ── shared CacheContext
              └── LoggingContext   ── shared CacheContext
```

Each `AppInterfaceContext` instance is per-interface. Interface events and repositories are wired by name into a registry; the context graph itself is built declaratively. Tests can inject a `get_dependency` mock and the logging mock via the hub's lazy cache (`_logging`), and provide feature/error contexts by patching `BaseContext.for_domain`.

## Testing Contexts

Context tests use `pytest` with `unittest.mock`. Focus on behavior, not implementation detail.

### Patterns

- **Mock all injected dependencies** — use `mock.Mock(spec=...)` against the expected type.
- **Test each method in isolation** — `parse_request`, `execute_feature`, `handle_error`, `handle_response`, and `run`.
- **Verify service interactions** — assert that service and handler calls occur with expected arguments.
- **Exercise both success and error paths** — especially for `AppInterfaceContext.run`, which has distinct branches for successful completion and `TiferetError` recovery.

### Example

```python
# *** fixtures

# ** fixture: app_interface_context
@pytest.fixture
def app_interface_context(app_interface):
    # Build the hub declaratively, then inject mock sub-contexts via the caches.
    context = AppInterfaceContext.from_domain(
        app_interface,
        get_feature_evt=mock.Mock(),
        get_error_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
    )
    # Inject the logging mock via its cache; feature/error contexts are built on
    # demand, so patch BaseContext.for_domain to supply mocks for them.
    context._logging = mock.Mock(spec=LoggingContext)
    return context

# *** tests

# ** test: run_success
def test_run_success(app_interface_context):
    '''
    Verify run executes the feature and returns the response payload.
    '''

    # Arrange the logger and response.
    app_interface_context.load_logging_context().build_logger.return_value = mock.Mock()

    # Act.
    result = app_interface_context.run('calc.add', data={'a': 1, 'b': 2})

    # Assert the run completed and produced a response (the feature context is
    # built on demand inside execute_feature).
    assert result is not None
```

## Best Practices

### 1. Keep Contexts Focused

A context owns one runtime concern. If a context grows multiple responsibilities, split it into a high-level context plus one or more low-level contexts.

### 2. Delegate to Services, Not Other Contexts (Where Possible)

Low-level contexts should depend on services — not on each other — except where composition is intrinsic (e.g., `FeatureContext` using the injected `get_dependency` handler and a shared `CacheContext`). This keeps the dependency graph shallow.

### 3. Prefer `super()` Over Reimplementation

When extending `AppInterfaceContext`, override only the steps that differ and call `super()` for the rest. This preserves logging, timing, and error handling behavior for free.

### 4. Never Inject Contexts into Domain Events

Domain events depend on **services**, not contexts. Passing a context into an event couples domain logic to the runtime graph and makes the event harder to test.

### 5. Use `RaiseError.execute()` for Context-Level Errors

Contexts must raise structured `TiferetError` instances with framework error codes — never raw exceptions. `AppInterfaceContext.handle_error` wraps unhandled exceptions, but preferring structured errors at the source yields better diagnostics.

### 6. Treat CacheContext as Per-Interface

Each `AppInterfaceContext` creates one `CacheContext` and shares it with the sub-contexts it builds. Do not share a single `CacheContext` across interfaces — a fresh hub per interface means a fresh cache, avoiding cross-interface leakage.

## Related Documentation

- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context base classes, artifact comments, and code style reference
- [docs/core/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md) — Blueprint design (build_app, build_cli)
- [docs/guides/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/blueprints.md) — Blueprint strategies and patterns
- [docs/core/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md) — Dependency injection and service provider architecture
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and usage
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting rules
