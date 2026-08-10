# Blueprints in Tiferet

Blueprints are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While contexts define the runtime shape and behavior of an individual interface, blueprints orchestrate the overall application lifecycle and wiring.

## What is a Blueprint?

A blueprint in Tiferet is a module-level function that encapsulates the initialization and orchestration logic required to prepare and run an application interface. Blueprints are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppSessionContext`.

The canonical implementation is `build_app` in `tiferet/blueprints/core.py` (exported as `App`), which chains the composition functions `build_cache` → `get_app_session` → `build_app_session_context`. The framework's own built-in sessions (`admin`, `admin_cli`) are composed by a parallel pair of blueprints, `tiferet/blueprints/admin.py` / `admin_cli.py`, that mirror this chain function-for-function with an admin-aware cache and resolver — see [docs/guides/blueprints.md § Admin Blueprints](../guides/blueprints.md#admin-blueprints).

### Role in the Architecture

Blueprints sit at the highest level of the application graph:

- They build the shared `CacheContext`, pre-seeded with the framework's default errors, app services, and constants (`build_cache`)
- They compose the application service and resolve the app session via a domain event (`get_app_session` → `GetAppSession`)
- They build the app service container from the cache defaults merged with the session's own overrides, and compose a feature-level `ServiceResolver` (`build_app_session_context`)
- They delegate feature execution to the resolved `AppSessionContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Blueprints

Tiferet currently defines two blueprints:

- **App blueprint**: `build_app` — used for general script and custom interfaces. Exposed globally as `App`.
- **CLI blueprint**: `build_cli` (`tiferet/blueprints/cli.py`) — runs its own parallel composition chain (not delegating through `core.build_app`), hardcoding `CliSessionContext` in place of `AppSessionContext` and dispatching `sys.argv` via `cli_context.run(argv)`. Exposed globally as `CLI`.

Future specialized blueprints may include:

- Web blueprint — for web framework integration (Flask, FastAPI, etc.)
- Test blueprint — for integration and unit testing with mocked services

### CLI Blueprint Build Procedure

The CLI blueprint (`build_cli`, `tiferet/blueprints/cli.py`) builds its own cache, session, and context rather than delegating to `core.build_app`; argparse parsing and CLI-specific request/response handling live in blueprint-level closures, not in a context method. Its flow follows these steps:

1. **Build the CLI cache** via `build_cli_cache()`, which layers `add_default_cli_commands` on top of `core.build_cache`.
2. **Resolve the app session** via `core.get_app_session(interface_id, cache, ...)`.
3. **Compose the context** via `build_cli_session_context(app_session, cache)`, which hardcodes `CliSessionContext`, builds the `parse_cli_args` closure from the resolved `list_commands_evt`/`get_parent_args_evt` collaborators, and overrides the `create_request_handler`/`response_handler` slots with `create_cli_request_context`/`cli_response_handler`.
4. **Delegate to the context** by calling `cli_context.run(argv)`, which parses `argv` via the injected closure (argparse exits `2` on failure), dispatches through the inherited `AppSessionContext.run`, prints the response, and converts an unhandled `TiferetAPIError` into `sys.exit(1)`.

There is no interface-config opt-in — any interface resolved through `build_cli`/`CLI` always gets a `CliSessionContext`.

## Structured Code Design of Blueprints

Blueprints follow Tiferet's standard artifact comment structure.

### Artifact Comments

Blueprints are organized under the `# *** blueprints` top-level comment, with individual blueprints under `# ** blueprint: <snake_case_name>`. Each blueprint function uses standard RST docstrings and code snippet conventions.

Side-effect-free helpers (pure input→output transforms with no I/O, instantiation, or error raising) belong in a `# *** functions` section above `# *** blueprints`, with individual helpers under `# ** function: <snake_case_name>`. `tiferet/blueprints/core.py` groups `resolve_collaborators` and `merge_logging_settings` this way — small pure helpers consumed by the orchestration functions below them. Reserve `# *** blueprints` for the orchestration entry points reused by other blueprints or clients (e.g. `core.build_app`, `core.build_app_session_context`).

**Spacing rules:**

- One empty line between `# *** blueprints` and first `# ** blueprint`
- One empty line between each blueprint function
- One empty line after docstrings and between code snippets

## Writing Blueprints

### Creating a New Blueprint

1. Place the function under `# *** blueprints` in an appropriate module (for example, `tiferet/blueprints/core.py`).
2. Use `# ** blueprint: <snake_case_name>`.
3. Reuse the core composition functions (`tiferet/blueprints/core.py`):
   - `build_cache` — build the shared cache pre-seeded with default errors, services, and constants
   - `create_app_service` — compose the app service via a single-use dynamic container
   - `get_app_session` — resolve the app session via the `GetAppSession` event
   - `build_app_service_container` — build the singleton app service container from cache defaults merged with the session's overrides
   - `build_service_resolver` — compose the feature-level `ServiceResolver`, caching the app container under the `app` flag
   - `build_app_session_context` — hardcode the `AppSessionContext` class, resolve its remaining collaborators, wire the five template-method handlers, and construct the context
   - `create_feature_context` — load the feature when only an id is given and return a `FeatureContext` with that feature bound as its `domain`
   - `build_app` — high-level single-call entry point chaining the above

### Key Patterns

**Single-call entry point**  
`build_app` resolves and realizes in one call:

```python
app = App('basic_calc', app_config='config.yml')
```

**Default configuration injection**  
The core path sources the framework's `CORE_DEFAULT_SERVICES` / `CORE_DEFAULT_CONSTANTS` catalogs (defined in `assets/app.py`, accessed as `a.app`) from the shared cache seeded by `build_cache`. `build_app_service_container` merges those cache defaults with the session's own constants and services (session wins) *before* building the container, so `core.build_app` never calls `apply_defaults`:

```python
container = build_app_service_container(cache, app_session)  # cache defaults + session overrides
```

The framework's own built-in sessions (`admin`, `admin_cli`) take a different route entirely: `assets/app.py`'s `CORE_DEFAULT_APP_SESSIONS` seeds them directly into the cache via `add_default_app_sessions`, so `get_app_session` returns them from the cache before ever touching a consumer config file or an `apply_defaults`-style fallback.

**Cache pre-seeding**  
The core `build_cache` blueprint (`tiferet/blueprints/core.py`) pre-seeds a `CacheContext` with three framework catalogs via stacked decorators — `add_default_errors`, `add_default_app_services`, and `add_default_app_constants` (the latter two defined in `contexts/app.py`) — namespacing each catalog under its own cache-key prefix (`error_`, `app_service_`, `app_constant_`). Errors and services are reconstituted into domain objects (`Error`, `AppServiceDependency`); constants are seeded as scalars:

```python
@add_default_app_constants(a.app.CORE_DEFAULT_CONSTANTS)
@add_default_app_services(a.app.CORE_DEFAULT_SERVICES)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(cache=None) -> CacheContext:
    return CacheContext(cache=cache)
```

**Blueprint-owned callables as container constants**  
Callables the blueprint layer owns are registered by `build_app_service_container` as app-container constants so lower layers receive them through constructor injection instead of importing `blueprints`. The cache loader is registered as `'load_cache'`, which `build_singleton` wires into `CacheMiddleware` by constructor inspection.

**Required feature-execution wiring**  
None of the hub's five template-method handlers is optional. `AppSessionContext.build_logger`, `build_request`, `execute_feature`, `handle_error`, and `build_response` have no fallback paths: an unwired handler raises `APP_ERROR` naming the missing slot (`build_logger_handler`, `create_request_handler`, `execute_feature_handler`, `raise_error_handler`, or `response_handler`) via the `raise_unwired_handler_error` helper in `contexts/app.py`, because a hub that cannot complete the `run` pipeline is a composition bug rather than a condition to degrade around. Every context builder — `build_app_session_context`, `build_cli_session_context`, and the admin equivalents — must wire all five. `build_logger` additionally formats a `TiferetError` raised by its handler into a `TiferetAPIError` via `handle_error`, so `run`'s pre-try region raises only `TiferetAPIError`.

Because the unwired-handler error is raised as a `TiferetAPIError`, it reaches the caller verbatim: `handle_error` passes an already-formatted API error straight through instead of round-tripping it through `raise_error_handler`, so an unwired `execute_feature_handler` is reported as such even when `raise_error_handler` is also missing. `handle_error` attaches the original error's code and message as `original_error_code` / `original_error_message` kwargs so a missing `raise_error_handler` does not destroy the underlying failure.

**Feature context binding**  
`create_feature_context` composes the `FeatureContext` via `FeatureContext.from_domain(feature, ...)` and returns the context alone; the feature is reachable as `feature_context.domain`. `execute_feature_handler` therefore calls `feature_context.execute_feature(request, *flags, **kwargs)` without threading the feature through the call:

```python
feature_context = create_feature_context(get_dependency, cache, feature_id=feature_id)
feature_context.execute_feature(request, *flags, **kwargs)
```

**Service resolver injection**  
`build_service_resolver` composes a `ServiceResolver` from the app service container (caching it under the `app` flag), and `build_app_session_context` injects its `get_dependency` handler into the context:

```python
resolver = build_service_resolver(app_container)
return context_cls.from_domain(app_session, get_dependency=resolver.get_dependency, ...)
```

## Testing Blueprints

Blueprint tests use `pytest` with `unittest.mock`. Focus on:

- Correct composition of the app service and app session (`create_app_service` / `get_app_session`)
- Cache defaults merged with session overrides in `build_app_service_container`
- Validation of the resolved `AppSessionContext` (raising `INVALID_APP_SESSION_TYPE`)
- High-level `core.build_app()` behavior

## Best Practices

- Keep blueprints **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in the single-call entry points (`core.build_app`, `admin.build_admin_app`).
- Use `TiferetError.raise_error()` for all error paths with proper constants.
- Inject the `ServiceResolver`'s `get_dependency` handler into the context so contexts remain decoupled from the DI engine.

## Conclusion

Blueprints provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, and interface resolution while delegating execution to `AppSessionContext`. Their functional design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/blueprints/` and blueprint tests in the top-level `tests/` tree for implementation details.

## Related Documentation

- [docs/guides/blueprints.md](../guides/blueprints.md) — blueprint strategies and patterns
- [docs/core/di.md](../core/di.md) — dependency injection and service provider design
- [docs/core/events.md](../core/events.md) — domain event design and usage
- [docs/guides/domain/app.md](../guides/domain/app.md) — application interface and service registration guide
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
