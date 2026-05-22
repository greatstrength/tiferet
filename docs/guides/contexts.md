# Contexts – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/contexts/`  
**Version:** 2.0.0

## Overview

Contexts form the runtime "body" of a Tiferet application. They encapsulate interaction surfaces, orchestration, and supporting services behind clean, injectable classes. While blueprints (`tiferet/blueprints/`) own the application lifecycle and wiring, contexts own the per-interface runtime shape — how requests are parsed, features are executed, errors are handled, and responses are returned.

Tiferet distinguishes between two categories of contexts:

- **High-level contexts** — extend `AppInterfaceContext` and expose the interface's runtime entry point (e.g., a CLI interface or a web API). They delegate to lower-level contexts for execution concerns.
- **Low-level contexts** — single-purpose orchestrators that back the high-level context (e.g., `FeatureContext`, `DIContext`, `RequestContext`, `ErrorContext`, `LoggingContext`, `CacheContext`).

This guide covers cross-cutting strategies for using, extending, and composing contexts. For artifact-level structure and code style, see [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md).

## Context Responsibilities

Every context in `tiferet/contexts/` has a single, well-defined responsibility:

| Context | Responsibility |
| --- | --- |
| `AppInterfaceContext` | Parse the incoming request, execute the feature, format the response, and handle errors at the interface boundary. |
| `FeatureContext` | Load a feature, resolve each configured step from the DI container, parse parameters, and execute the steps sequentially against a `RequestContext`. |
| `DIContext` | Build and cache feature-level service providers from `ServiceConfiguration` objects, resolving per-flag dependency types. |
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

    # Format and return the response.
    return self.handle_response(request)
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

### CLI Interfaces Without Custom Contexts

In v2.0+, CLI interfaces are handled by `CliBuilder` rather than a `CliContext`. All argparse wiring lives in the builder; the CLI interface runs against the default `AppInterfaceContext`. As a result, CLI interface definitions in `app.yml` no longer require `module_path`/`class_name` overrides.

If a CLI interface needs custom request parsing beyond argparse, the preferred pattern is still to extend `CliBuilder` — not to reintroduce a dedicated CLI context.

## Low-Level Context Lifecycles

### FeatureContext

`FeatureContext.execute_feature` drives the core feature pipeline:

1. Load the feature (cached when possible) via `get_feature_handler`.
2. For each configured step:
   - Evaluate the step's `condition` expression (if present) via `evaluate_condition`. If the condition resolves to `False`, the step is silently skipped.
   - Resolve the domain event from `DIContext.get_dependency(service_id, *flags)`.
   - Parse each step parameter with `parse_request_parameter` (supports `$r.<key>` request-backed parameters).
   - Invoke `handle_command`, which executes the event and stores the result on the `RequestContext` under `data_key`.

Feature-level flags (defined on the `Feature`) are combined with step-level flags and passed to the DI context. Higher priority is given to feature-level flags.

### Conditional Step Execution

`FeatureEvent` supports an optional `condition` field — a boolean expression string evaluated against request data before the step executes. The `$r.` prefix references values from `request.data` (e.g., `$r.b != 0`, `$r.mode == 'advanced'`).

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

### DIContext

`DIContext.build_service_provider(flags)` is the sole entry point for feature-level dependency resolution:

1. Normalize flags and derive a cache key.
2. Return cached `ServiceProvider` if present.
3. Load all `ServiceConfiguration` objects and top-level constants from `list_all_configs_handler`.
4. Merge per-configuration parameters into the constants dict, honoring flag-scoped overrides.
5. Resolve each configuration to a concrete type via `get_configuration_type`.
6. Call `create_service_provider(type_map=..., **constants)` to instantiate a provider.
7. Cache and return the provider.

The `create_service_provider` factory is supplied by the builder via `AppBuilder.create_service_provider` so that app-level and feature-level providers share a consistent construction strategy.

### RequestContext

`RequestContext` is a plain data carrier populated by `parse_request` and mutated by step handlers via `set_result(result, data_key)`. Its `handle_response` method builds the final response object returned by `AppInterfaceContext.run`.

### ErrorContext and LoggingContext

Both are configuration-driven:

- `ErrorContext` receives a `TiferetError`, formats it via `ErrorService`, and returns a localized payload. `AppInterfaceContext.handle_error` wraps the payload in `TiferetAPIError`.
- `LoggingContext.build_logger` composes formatters, handlers, and loggers defined in configuration into a ready-to-use logger instance.

Both contexts are injected into `AppInterfaceContext` and are typically not subclassed — extend the underlying services instead.

### CacheContext

A simple keyed in-memory cache used by `FeatureContext` (for loaded features) and `DIContext` (for service providers). Treat it as a per-interface cache — it is not shared across interfaces.

## Composition in the Application Graph

At runtime, a fully wired interface graph looks roughly like this:

```
AppBuilder
  └── AppInterfaceContext
        ├── FeatureContext
        │     ├── DIContext  ── CacheContext
        │     └── CacheContext
        ├── ErrorContext
        └── LoggingContext
```

Each `AppInterfaceContext` instance is per-interface; its dependencies are resolved by the app-level service provider. Because all contexts are constructor-injected, tests can replace any node in this graph with a mock.

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
def app_interface_context():
    return AppInterfaceContext(
        interface_id='basic_calc',
        features=mock.Mock(spec=FeatureContext),
        errors=mock.Mock(spec=ErrorContext),
        logging=mock.Mock(spec=LoggingContext),
    )

# *** tests

# ** test: run_success
def test_run_success(app_interface_context):
    '''
    Verify run executes the feature and returns the response payload.
    '''

    # Arrange the logger and response.
    app_interface_context.logging.build_logger.return_value = mock.Mock()

    # Act.
    result = app_interface_context.run('calc.add', data={'a': 1, 'b': 2})

    # Assert execution and response handling were invoked.
    app_interface_context.features.execute_feature.assert_called_once()
    assert result is not None
```

## Best Practices

### 1. Keep Contexts Focused

A context owns one runtime concern. If a context grows multiple responsibilities, split it into a high-level context plus one or more low-level contexts.

### 2. Delegate to Services, Not Other Contexts (Where Possible)

Low-level contexts should depend on services — not on each other — except where composition is intrinsic (e.g., `FeatureContext` composing `DIContext` and `CacheContext`). This keeps the dependency graph shallow.

### 3. Prefer `super()` Over Reimplementation

When extending `AppInterfaceContext`, override only the steps that differ and call `super()` for the rest. This preserves logging, timing, and error handling behavior for free.

### 4. Never Inject Contexts into Domain Events

Domain events depend on **services**, not contexts. Passing a context into an event couples domain logic to the runtime graph and makes the event harder to test.

### 5. Use `RaiseError.execute()` for Context-Level Errors

Contexts must raise structured `TiferetError` instances with framework error codes — never raw exceptions. `AppInterfaceContext.handle_error` wraps unhandled exceptions, but preferring structured errors at the source yields better diagnostics.

### 6. Treat CacheContext as Per-Interface

Do not share a single `CacheContext` instance across interfaces. Each `AppInterfaceContext` (and its nested contexts) gets its own cache instance to avoid cross-interface leakage.

## Related Documentation

- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context base classes, artifact comments, and code style reference
- [docs/core/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md) — Blueprint design (build_app, build_cli)
- [docs/guides/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/blueprints.md) — Blueprint strategies and patterns
- [docs/core/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md) — Dependency injection and service provider architecture
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and usage
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting rules
