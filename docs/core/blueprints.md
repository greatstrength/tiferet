# Blueprints in Tiferet

Blueprints are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving sessions, wiring the five-handler context contract, and executing features.

While contexts define the runtime shape and behavior of an individual session, blueprints orchestrate the overall application lifecycle and wiring.

## What is a Blueprint?

A blueprint in Tiferet is a module-level function that encapsulates the initialization and orchestration logic required to prepare and run an application session. Blueprints are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, handler composition, and delegation to the appropriate `AppSessionContext` or `CliSessionContext`.

The canonical implementation is `build_app` in `tiferet/blueprints/core.py` (exported as `App`), which chains the composition functions `build_cache` → `get_app_session` → `build_app_session_context`. The CLI entrypoint (`build_cli` / `CLI`) and the admin entry points (`build_admin_app` / `AdminApp`, `build_admin_cli` / `AdminCLI`) reuse the same core composition helpers with session-specific cache seeding and resolver wiring.

### Role in the Architecture

Blueprints sit at the highest level of the application graph:

- They build the shared `CacheContext`, pre-seeded with the framework's default errors, app services, constants, and (where applicable) logging settings, features, and CLI commands (`build_cache`)
- They compose the application service and resolve the app session via a domain event (`get_app_session` → `GetAppSession`)
- They build the app service container from the cache defaults merged with the session's own overrides, and compose a feature-level `ServiceResolver` (`build_app_session_context`)
- They wire the five required template-method handlers (`build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, `response_handler`) into the session context
- They delegate feature execution to the resolved `AppSessionContext` / `CliSessionContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Blueprints

Tiferet currently defines four public blueprints:

- **App blueprint**: `build_app` — used for general script and custom interfaces. Exposed globally as `App`.
- **CLI blueprint**: `build_cli` — a thin entrypoint that resolves and realizes a CLI session (which must point at `CliSessionContext`) and delegates `sys.argv` translation and feature dispatch to `CliSessionContext.run`. Exposed globally as `CLI`.
- **Admin App blueprint**: `build_admin_app` — builds the built-in management session (`admin`) with admin-scoped service resolution. Exposed globally as `AdminApp`.
- **Admin CLI blueprint**: `build_admin_cli` — builds the built-in management CLI (`admin_cli`) and powers the `tiferet` console script. Exposed globally as `AdminCLI`.

Future specialized blueprints may include:

- Web blueprint — for web framework integration (Flask, FastAPI, etc.)
- Test blueprint — for integration and unit testing with mocked services

### CLI Blueprint Build Procedure

The CLI blueprint (`build_cli`) is a thin entrypoint; argparse parsing and request derivation live in `CliSessionContext` (`tiferet/contexts/cli.py`) behind an injected `parse_cli_args` closure. Its flow follows these steps:

1. **Build the context** via the CLI session composer (which wires all five handlers, including `build_logger_handler`, plus `parse_cli_args`). The interface must point at `tiferet.contexts.cli` / `CliSessionContext`.
2. **Delegate to the context** by calling `cli_context.run(argv)`, which parses `argv` (argparse exits `2` on failure), derives `feature_id`/`headers`/`data`, dispatches through the inherited hub `run`, prints the response when appropriate, and converts a `TiferetAPIError` into `sys.exit(1)`.

Consumer CLI interfaces opt in by declaring `module_path: tiferet.contexts.cli` / `class_name: CliSessionContext` in their session config.

## Structured Code Design of Blueprints

Blueprints follow Tiferet's standard artifact comment structure.

### Artifact Comments

Blueprints are organized under the `# *** blueprints` top-level comment, with individual blueprints under `# ** blueprint: <snake_case_name>`. Each blueprint function uses standard RST docstrings and code snippet conventions.

Side-effect-free helpers (pure input→output transforms with no I/O, instantiation, or error raising) belong in a `# *** functions` section above `# *** blueprints`, with individual helpers under `# ** function: <snake_case_name>`. In `tiferet/blueprints/core.py`, `resolve_collaborators` and `merge_logging_settings` are grouped this way — small pure helpers consumed by the orchestration functions below them. Reserve `# *** blueprints` for the orchestration entry points reused by other blueprints or clients (e.g. `core.build_app`, `core.build_app_session_context`, `core.build_logger_handler`).

**Spacing rules:**

- One empty line between `# *** blueprints` and first `# ** blueprint`
- One empty line between each blueprint function
- One empty line after docstrings and between code snippets

### Core Blueprint Artifacts (`tiferet/blueprints/core.py`)

Key `# *** functions` and `# *** blueprints` in the core module:

| Artifact | Kind | Role |
| --- | --- | --- |
| `RESERVED_CONTEXT_PARAMETERS` | constant | Constructor params supplied by session builders (includes all five handlers + `parse_cli_args`) |
| `resolve_collaborators` | function | DI-resolves remaining injectable context collaborators, skipping reserved names |
| `merge_logging_settings` | function | Merges repository logging sections over cache-seeded defaults by `.id` |
| `parse_parameter` | blueprint | Injectable wrapper over `ParseParameter.execute` |
| `build_app_service_container` | blueprint | Singleton app container from cache defaults + session overrides |
| `build_service_resolver` | blueprint | Feature-level resolver; caches the app container under the `app` flag |
| `build_cache` | blueprint | Shared cache pre-seeded with framework catalogs |
| `get_error` / `get_feature` | blueprint | Lazy-caching domain-object handlers |
| `build_logger_handler` | blueprint | Cache-backed logger construction under `LOGGER_CACHE_PREFIX` |
| `create_request_context` / `create_session_request` | blueprint | Request factory used as `create_request_handler` |
| `create_feature_context` | blueprint | Returns a domain-bound `FeatureContext` (not a tuple) |
| `execute_feature_handler` | blueprint | Closure: `create_feature_context(...).execute_feature(request, ...)` |
| `raise_error_handler` | blueprint | Formats domain errors into `TiferetAPIError` |
| `response_handler` | blueprint | Delegates to `request.handle_response()` |
| `build_app_session_context` | blueprint | Wires all five handlers into `AppSessionContext.from_domain` |
| `build_app` | blueprint | Single-call public entry point (`App`) |

#### `merge_logging_settings`

```python
# ** function: merge_logging_settings
def merge_logging_settings(cache, formatters, handlers, loggers) -> LoggingSettings:
    # Retrieve cache-seeded defaults (tolerate none).
    # Merge repository entries over defaults keyed by .id (repository wins).
    # Return LoggingSettings(formatters=..., handlers=..., loggers=...).
```

#### `build_logger_handler`

```python
# ** blueprint: build_logger_handler
def build_logger_handler(cache, get_dependency) -> Callable:
    def handler(logger_id: str):
        cached = cache.get(logger_id, *LOGGER_CACHE_PREFIX)
        if cached is not None:
            return cached
        formatters, handlers, loggers = get_dependency('logging_list_all_evt', 'app').execute()
        settings = merge_logging_settings(cache, formatters, handlers, loggers)
        logger = LoggingContext.from_domain(settings, logger_id=logger_id).build_logger()
        cache.set(logger_id, logger, *LOGGER_CACHE_PREFIX)
        return logger
    return handler
```

#### `create_feature_context` / `execute_feature_handler`

```python
# ** blueprint: create_feature_context
def create_feature_context(get_dependency, cache, feature_id) -> FeatureContext:
    feature = get_feature(cache, get_dependency)(feature_id)
    return FeatureContext.from_domain(feature, get_dependency=get_dependency, cache=cache)

# ** blueprint: execute_feature_handler
def execute_feature_handler(get_dependency, cache) -> Callable:
    def handler(feature_id, request, *flags, **kwargs) -> None:
        feature_context = create_feature_context(get_dependency, cache, feature_id)
        feature_context.execute_feature(request, *flags, **kwargs)
    return handler
```

`create_feature_context` returns only the bound `FeatureContext`. The inner call is `feature_context.execute_feature(request, ...)` — there is no `feature` parameter on the context method.

#### Five-handler wiring in `build_app_session_context`

```python
handlers = dict(
    build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
    execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
    raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
    response_handler=response_handler,
    create_request_handler=create_session_request,
)
return AppSessionContext.from_domain(
    app_session,
    get_dependency=resolver.get_dependency,
    cache=cache,
    **handlers,
    **collaborators,
)
```

## Admin Blueprints

### `tiferet/blueprints/admin.py`

| Artifact | Role |
| --- | --- |
| `build_cache` | Core cache plus admin catalogs: `ADMIN_DEFAULT_SERVICES`, `ADMIN_DEFAULT_CONSTANTS`, `ADMIN_DEFAULT_FEATURES`, `ADMIN_DEFAULT_ERRORS` |
| `build_admin_service_resolver` | Dual-container resolver: app container under `'app'`; admin container under `'admin'` **and** as the empty-flag default |
| `build_admin_app_session_context` | Mirrors `build_app_session_context` with the admin resolver and the same five handlers |
| `build_admin_app` / `AdminApp` | Single-call entry point defaulting to `TIFERET_ADMIN_ID` |

Admin-scoped resolution pattern:

```python
resolver.add_container(app_container, 'app')
resolver.add_container(admin_container, 'admin')
resolver.add_container(admin_container)  # empty-flag default
```

Feature steps therefore resolve from the admin container unless they explicitly request the `'app'` flag.

### `tiferet/blueprints/admin_cli.py`

| Artifact | Role |
| --- | --- |
| `build_cache` | Admin cache plus `ADMIN_DEFAULT_COMMANDS` |
| `build_admin_cli_session_context` | Wires `CliSessionContext` with the admin resolver, five handlers, and CLI parse/request/response helpers |
| `build_admin_cli` / `AdminCLI` | Resolves `TIFERET_ADMIN_CLI_ID`, re-seeds all `*_config` constants to the consumer path, runs `cli_context.run(argv)` |
| `main` | Console entry for the `tiferet` script; pre-parses `--config` without consuming help/remaining argv |

Exports:

```python
from tiferet import App, CLI
from tiferet.blueprints import AdminApp, AdminCLI
# also: build_app, build_cli, build_admin_app, build_admin_cli
# AdminApp / AdminCLI are blueprints-package exports only (not package-root).
```

Full catalog reference: [docs/guides/admin.md](../guides/admin.md).

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
   - `merge_logging_settings` / `build_logger_handler` — logger construction for the fifth handler slot
   - `create_feature_context` / `execute_feature_handler` — domain-bound feature execution
   - `build_app_session_context` — import/construct the context class with all five handlers
   - `build_app` — high-level single-call entry point chaining the above

### Key Patterns

**Single-call entry point**  
`build_app` resolves and realizes in one call:

```python
app = App('basic_calc', app_config='config.yml')
```

**Default configuration injection**  
The core path sources the framework's `CORE_DEFAULT_SERVICES` / `CORE_DEFAULT_CONSTANTS` catalogs (defined in `assets/app.py`, accessed as `a.app`) from the shared cache seeded by `build_cache`. `build_app_service_container` merges those cache defaults with the session's own constants and services (session wins) *before* building the container:

```python
container = build_app_service_container(cache, app_session)  # cache defaults + session overrides
```

**Cache pre-seeding**  
The core `build_cache` blueprint (`tiferet/blueprints/core.py`) pre-seeds a `CacheContext` with framework catalogs via stacked decorators, namespacing each catalog under its own cache-key prefix.

**Service resolver injection**  
`build_service_resolver` composes a `ServiceResolver` from the app service container (caching it under the `app` flag), and `build_app_session_context` injects its `get_dependency` handler into the context:

```python
resolver = build_service_resolver(app_container)
return context_cls.from_domain(app_session, get_dependency=resolver.get_dependency, ...)
```

**Five-handler context wiring**  
Always pass `build_logger_handler` (never a long-lived `logging_context` constructor keyword). See [docs/core/contexts.md](contexts.md).

## Testing Blueprints

Blueprint tests use `pytest` with `unittest.mock`. Focus on:

- Correct composition of the app service and app session (`create_app_service` / `get_app_session`)
- Cache defaults merged with session overrides in `build_app_service_container`
- Five-handler wiring in `build_app_session_context` / admin variants
- Validation of the resolved `AppSessionContext` (raising `INVALID_APP_SESSION_TYPE`)
- High-level `core.build_app()` / `build_admin_app()` behavior

## Best Practices

- Keep blueprints **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in the single-call entry points.
- Use `TiferetError.raise_error()` for all domain-outcome error paths with proper constants.
- Inject the `ServiceResolver`'s `get_dependency` handler into the context so contexts remain decoupled from the DI engine.
- Wire all five handlers; never leave a hub slot unset in production paths.

## Conclusion

Blueprints provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, five-handler wiring, and session resolution while delegating execution to `AppSessionContext`. Their functional design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/blueprints/` and blueprint tests in the top-level `tests/` tree for implementation details.

## Related Documentation

- [docs/guides/blueprints.md](../guides/blueprints.md) — blueprint strategies and patterns
- [docs/guides/admin.md](../guides/admin.md) — admin application and CLI catalog
- [docs/core/contexts.md](contexts.md) — five-handler context contract
- [docs/core/di.md](di.md) — dependency injection and service provider design
- [docs/core/events.md](events.md) — domain event design and usage
- [docs/guides/domain/app.md](../guides/domain/app.md) — application session and service registration guide
- [docs/core/code_style.md](code_style.md) — artifact comments and formatting
