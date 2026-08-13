# Contexts – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/contexts/`  
**Version:** 2.0.0

## Overview

Contexts form the runtime "body" of a Tiferet application. They encapsulate interaction surfaces, orchestration, and supporting services behind clean, injectable classes. While blueprints (`tiferet/blueprints/`) own the application lifecycle and wiring, contexts own the per-session runtime shape — how requests are built, features are executed, errors are handled, loggers are constructed, and responses are returned.

Tiferet distinguishes between two categories of contexts:

- **High-level contexts** — extend `AppSessionContext` and expose the session's runtime entry point (e.g., a CLI session or a web API). They implement the five required template-method handlers and delegate low-level work through those slots.
- **Low-level contexts** — single-purpose orchestrators that back the high-level context (e.g., `FeatureContext`, `RequestContext`, `ErrorContext`, `LoggingContext`, `CacheContext`).

This guide covers cross-cutting strategies for using, extending, and composing contexts. For artifact-level structure and code style, see [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md).

## Context Responsibilities

Every context in `tiferet/contexts/` has a single, well-defined responsibility:

| Context | Responsibility |
| --- | --- |
| `AppSessionContext` | Session hub: `build_logger` → `build_request` → `execute_feature` → `handle_error` / `build_response` via five required handlers. |
| `CliSessionContext` | High-level CLI session: injects `parse_cli_args`, overrides `run(argv)` and CLI-aware `build_response`. |
| `FeatureContext` | Domain-bound feature executor: reads `self.domain`, resolves steps from DI, parses parameters, runs sync/async steps. |
| `ErrorContext` | Format exceptions into structured, localized API responses from a pre-loaded `Error`. |
| `LoggingContext` | Build a logger from a pre-assembled `LoggingSettings` domain object (`from_domain` + `build_logger`). |
| `CacheContext` | Provide an in-memory keyed cache for reusable objects (features, errors, loggers, defaults). |
| `RequestContext` | Carry request headers, data, and the feature result through the execution pipeline; produce the final response via `handle_response`. |

Contexts are consumed by blueprints and by `AppSessionContext` (and its subclasses) — not by domain events. Domain events only receive injected **services**, never contexts.

## The AppSessionContext Five-Handler Pattern

`AppSessionContext` is the canonical high-level context. Its `run` method defines the standard request lifecycle through five **required** template methods:

```python
def run(self, feature_id, headers=None, data=None, **kwargs):
    # Build logger via the required build_logger_handler slot.
    logger = self.build_logger()

    # Build the request via create_request_handler.
    request = self.build_request(feature_id, headers or {}, data or {})

    # Execute the feature via execute_feature_handler, capturing TiferetError.
    try:
        self.execute_feature(feature_id, request, logger=logger, **kwargs)
    except TiferetError as e:
        return self.handle_error(e)

    # Build and return the response via response_handler.
    return self.build_response(request)
```

| Template method | Handler constructor kwarg | Unwired behavior |
| --- | --- | --- |
| `build_logger` | `build_logger_handler` | `raise_unwired_handler_error('build_logger_handler', ...)` |
| `build_request` | `create_request_handler` | `raise_unwired_handler_error('create_request_handler', ...)` |
| `execute_feature` | `execute_feature_handler` | `raise_unwired_handler_error('execute_feature_handler', ...)` |
| `handle_error` | `raise_error_handler` | Re-raise `TiferetAPIError` verbatim; otherwise unwired → `raise_unwired_handler_error` |
| `build_response` | `response_handler` | `raise_unwired_handler_error('response_handler', ...)` |

There are **no** truthiness-guarded inline fallbacks. Blueprints must wire every slot. Constructing a hub with a `logging_context` constructor keyword keyword is no longer supported — use `build_logger_handler=`:

```python
context = AppSessionContext.from_domain(
    app_session,
    get_dependency=resolver.get_dependency,
    cache=cache,
    build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
    execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
    create_request_handler=create_session_request,
    raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
    response_handler=response_handler,
)
```

The same five kwargs are forwarded by `CliSessionContext` (plus `parse_cli_args=` for argv parsing).

### Extending AppSessionContext

Create a subclass when the interface needs to translate a transport-specific payload (e.g., CLI `argv`, Flask `Request`) into a `RequestContext`, or when the response needs transport-specific formatting.

```python
# ** context: flask_api_context
class FlaskApiContext(AppSessionContext):
    """
    Flask API context that translates Flask requests into feature invocations.
    """

    # * attribute: flask_handler
    flask_handler: FlaskApiHandler

    # * init
    def __init__(self, flask_handler, **kwargs):
        # Forward get_dependency, cache, and the five handlers to the hub.
        super().__init__(**kwargs)
        self.flask_handler = flask_handler
```

Override only the methods you need. Always call `super()` for shared behavior so the required-handler guards remain intact.

### CLI Sessions with CliSessionContext

CLI interfaces use `CliSessionContext` (`tiferet/contexts/cli.py`), a high-level subclass of `AppSessionContext`. The CLI blueprint wires:

- the same five handlers (with CLI-specific `create_request_handler` / `response_handler` where needed)
- `build_logger_handler` (not a standalone `LoggingContext`)
- `parse_cli_args`, a closure that discovers commands, builds the argparse parser, and derives `(feature_id, headers, data)`

`CliSessionContext.run(argv=None)` parses argv, then delegates to `AppSessionContext.run`. Consumer CLI interfaces opt in by pointing their session config at `tiferet.contexts.cli` / `CliSessionContext`. The built-in admin CLI uses the same context class via `build_admin_cli`.

## Low-Level Context Lifecycles

### FeatureContext

`FeatureContext` is **domain-bound**: the `Feature` is supplied at construction via `from_domain` and read as `self.domain`. Public methods take no `feature` parameter:

```python
feature_context = FeatureContext.from_domain(
    feature,
    get_dependency=get_dependency,
    cache=cache,
)
feature_context.execute_feature(request, *flags, **kwargs)
```

`execute_feature(request, *flags, **kwargs)` drives the pipeline:

1. Read `feature = self.domain`.
2. Validate request data against the feature schema (`validate_request`).
3. If `feature.is_async`, drive the full async loop via `run_coroutine(self._execute_async(...))`.
4. Otherwise, for each step from `resolve_feature_steps(request, *flags)`:
   - Evaluate the step's `condition` (if present); skip when `False`.
   - Resolve the domain event via `get_dependency(service_id, *combined_flags)`.
   - Parse each step parameter with `parse_request_parameter` (supports `$r.<key>` request-backed parameters).
   - If `step.is_async`, drive `run_coroutine(self._execute_step_async(...))`; else call `execute_step`.

There is no separate `AsyncFeatureContext` class and no hub-level `get_feature_handler` / `handle_feature_step` API.

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

### RequestContext

`RequestContext` is a plain data carrier populated by `build_request` / `create_request_handler` and mutated by step handlers via `set_result(result, data_key)`. Its `handle_response` method builds the final response object returned by the hub's `response_handler` (default: `request.handle_response()`). CLI runs may use `CliRequestContext`, which maps list/dict results into typed CLI output models.

### ErrorContext and LoggingContext

Both are configuration-driven, but they are no longer long-lived children of the hub:

- `ErrorContext` receives a pre-loaded `Error` and formats a structured response. The blueprint's `raise_error_handler` resolves the `Error` (via a cache-backed `get_error` closure), constructs the registered `ErrorContext`, and raises `TiferetAPIError`.
- `LoggingContext` is constructed **on demand** from a `LoggingSettings` value object (`LoggingContext.from_domain(settings, logger_id=...)`) inside the blueprint's `build_logger_handler`. Built loggers are cached under `LOGGER_CACHE_PREFIX` (`('logging', 'loggers')`) so `dictConfig` runs once per logger id per process.

Neither context is stored on `AppSessionContext`. Do not pass `logging_context` constructor keyword into the hub constructor.

### CacheContext

A simple keyed in-memory cache used by blueprints and contexts for loaded features, errors, loggers, and bootstrap catalogs. Treat it as a per-session cache — it is not shared across sessions.

## Composition in the Application Graph

At runtime, a fully wired session graph looks roughly like this:

```
build_app / build_cli / build_admin_app / build_admin_cli
  └── AppSessionContext (or CliSessionContext)
        ├── handlers:
        │     build_logger_handler  → LoggingContext (ephemeral) + LOGGER_CACHE_PREFIX
        │     create_request_handler → RequestContext / CliRequestContext
        │     execute_feature_handler → FeatureContext.from_domain(feature)
        │     raise_error_handler → ErrorContext.format_response
        │     response_handler → request.handle_response (or CLI print path)
        └── CacheContext (shared bootstrap cache)
```

Each session context instance is per-session; its handlers and `get_dependency` are resolved by the blueprint. Because handlers are constructor-injected, tests can replace any slot with a mock.

## Testing Contexts

Context tests use `pytest` with `unittest.mock`. Focus on behavior, not implementation detail.

### Patterns

- **Mock all five handlers** — use `mock.Mock()` for each slot; leave a slot `None` only to assert `raise_unwired_handler_error`.
- **Test each template method in isolation** — `build_logger`, `build_request`, `execute_feature`, `handle_error`, `build_response`, and `run`.
- **Verify handler interactions** — assert that handler calls occur with expected arguments.
- **Exercise both success and error paths** — especially for `AppSessionContext.run`, which has distinct branches for successful completion and `TiferetError` recovery.
- **FeatureContext tests bind a domain** — construct via `FeatureContext.from_domain(feature, ...)` and call `execute_feature(request)` without a `feature=` argument.

### Example

```python
# *** fixtures

# ** fixture: app_session_context
@pytest.fixture
def app_session_context(app_session):
    return AppSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        build_logger_handler=mock.Mock(return_value=mock.Mock()),
        execute_feature_handler=mock.Mock(),
        create_request_handler=mock.Mock(return_value=mock.Mock(spec=RequestContext)),
        raise_error_handler=mock.Mock(),
        response_handler=mock.Mock(return_value={'ok': True}),
    )

# *** tests

# ** test: run_success
def test_run_success(app_session_context):
    """
    Verify run executes the feature and returns the response payload.
    """

    # Act.
    result = app_session_context.run('calc.add', data={'a': 1, 'b': 2})

    # Assert execution and response handling were invoked.
    app_session_context._execute_feature.assert_called_once()
    app_session_context._build_response.assert_called_once()
    assert result is not None
```

## Best Practices

### 1. Keep Contexts Focused

A context owns one runtime concern. If a context grows multiple responsibilities, split it into a high-level context plus one or more low-level contexts.

### 2. Wire All Five Handlers

Never leave a hub handler slot unset in production wiring. Prefer blueprint helpers (`build_logger_handler`, `execute_feature_handler`, `raise_error_handler`, `response_handler`, `create_session_request`) over ad-hoc closures.

### 3. Delegate to Services, Not Other Contexts (Where Possible)

Low-level contexts should depend on services — not on each other — except where composition is intrinsic (e.g., `FeatureContext` sharing a `CacheContext`). This keeps the dependency graph shallow.

### 4. Prefer `super()` Over Reimplementation

When extending `AppSessionContext`, override only the steps that differ and call `super()` for the rest. This preserves the unwired-handler guards, logging, timing, and error handling behavior for free.

### 5. Never Inject Contexts into Domain Events

Domain events depend on **services**, not contexts. Passing a context into an event couples domain logic to the runtime graph and makes the event harder to test.

### 6. Use Structured Errors at the Source

Contexts and blueprints must raise structured `TiferetError` instances with framework error codes — never raw exceptions where a domain outcome is known. Prefer `TiferetError.raise_error(...)` at the source; `handle_error` formats what escapes.

### 7. Treat CacheContext as Per-Session

Do not share a single `CacheContext` instance across sessions. Each `AppSessionContext` (and its handlers) gets its own cache instance to avoid cross-session leakage.

## Related Documentation

- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context base classes, five-handler contract, artifact comments, and code style reference
- [docs/core/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md) — Blueprint design (`build_app`, `build_cli`, `build_admin_app`, `build_admin_cli`)
- [docs/guides/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/blueprints.md) — Blueprint strategies and patterns
- [docs/guides/admin.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/admin.md) — Admin application and CLI catalog
- [docs/core/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md) — Dependency injection and service resolver architecture
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and usage
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting rules
