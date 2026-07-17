# Blueprints in Tiferet

Blueprints are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While contexts define the runtime shape and behavior of an individual interface, blueprints orchestrate the overall application lifecycle and wiring.

## What is a Blueprint?

A blueprint in Tiferet is a module-level function that encapsulates the initialization and orchestration logic required to prepare and run an application interface. Blueprints are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppInterfaceContext`.

The canonical implementation is `build_app` in `tiferet/blueprints/core.py` (exported as `App`), which chains the composition functions `build_cache` → `get_app_session` → `build_app_session_context`. The built-in CLI bootstrapper (`build_tiferet_cli`) uses a separate declarative bootstrap path in `tiferet/blueprints/tiferet_cli.py`.

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
- **CLI blueprint**: `build_cli` — a thin entrypoint that resolves and realizes a CLI interface (which must point at `CliContext`) and delegates `sys.argv` translation and feature dispatch to `CliContext.run_cli`. Exposed globally as `CLI`.

Future specialized blueprints may include:

- Web blueprint — for web framework integration (Flask, FastAPI, etc.)
- Test blueprint — for integration and unit testing with mocked services

### CLI Blueprint Build Procedure

The CLI blueprint (`build_cli`) is a thin entrypoint; argparse parsing and request derivation live in `CliContext` (`tiferet/contexts/cli.py`). Its flow follows these steps:

1. **Build the context** via `core.build_app(interface_id, ...)`. The interface must point at `tiferet.contexts.cli` / `CliContext`, so the composed context is a `CliContext`.
2. **Delegate to the context** by calling `cli_context.run_cli(argv)`, which builds the parser from the interface's CLI commands and parent arguments, parses `argv` (argparse exits `2` on failure), derives `feature_id`/`headers`, dispatches through the inherited `run`, prints the response, and converts a `TiferetAPIError` into `sys.exit(1)`.

Consumer CLI interfaces opt in by declaring `module_path: tiferet.contexts.cli` / `class_name: CliContext` in their interface config.

## Structured Code Design of Blueprints

Blueprints follow Tiferet's standard artifact comment structure.

### Artifact Comments

Blueprints are organized under the `# *** blueprints` top-level comment, with individual blueprints under `# ** blueprint: <snake_case_name>`. Each blueprint function uses standard RST docstrings and code snippet conventions.

Side-effect-free helpers (pure input→output transforms with no I/O, instantiation, or error raising) belong in a `# *** functions` section above `# *** blueprints`, with individual helpers under `# ** function: <snake_case_name>`. In `tiferet/blueprints/tiferet_cli.py` the bootstrap helpers `_resolve_ctor_kwargs`, `_build_wiring_constants`, and `_resolve_collaborators` (module-private, underscore-prefixed) are grouped this way — small pure helpers consumed by the orchestration functions below them (`_wire_services`, `_load_app_instance`, `_resolve_bootstrap_session`). Reserve `# *** blueprints` for the orchestration entry points reused by other blueprints or clients (e.g. `core.build_app`, `core.build_app_session_context`).

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
   - `build_app_session_context` — import the declared context class, resolve its collaborators, wire the FE4 handlers, and construct the context
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

The `AppInterface.apply_defaults` domain method and the `resolve_default_interface` bootstrap fallback are used by the built-in bootstrappers (`_resolve_bootstrap_session` in `tiferet/blueprints/tiferet_cli.py`), whose sessions (`tiferet_app`, `tiferet_cli`) are not defined in the consumer config.

**Cache pre-seeding**  
The core `build_cache` blueprint (`tiferet/blueprints/core.py`) pre-seeds a `CacheContext` with three framework catalogs via stacked decorators — `add_default_errors`, `add_default_app_services`, and `add_default_app_constants` (the latter two defined in `contexts/app.py`) — namespacing each catalog under its own cache-key prefix (`error_`, `app_service_`, `app_constant_`). Errors and services are reconstituted into domain objects (`Error`, `AppServiceDependency`); constants are seeded as scalars:

```python
@add_default_app_constants(a.app.CORE_DEFAULT_CONSTANTS)
@add_default_app_services(a.app.CORE_DEFAULT_SERVICES)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(cache=None) -> CacheContext:
    return CacheContext(cache=cache)
```

**Service resolver injection**  
`build_service_resolver` composes a `ServiceResolver` from the app service container (caching it under the `app` flag), and `build_app_session_context` injects its `get_dependency` handler into the context:

```python
resolver = build_service_resolver(app_container)
return context_cls.from_domain(app_session, get_dependency=resolver.get_dependency, ...)
```

The declarative registry wiring (`_wire_services` + the `CreateServiceResolver` bootstrap event) is used in `tiferet/blueprints/tiferet_cli.py` for `build_tiferet_cli`'s feature-DI bootstrap.

## Testing Blueprints

Blueprint tests use `pytest` with `unittest.mock`. Focus on:

- Correct composition of the app service and app session (`create_app_service` / `get_app_session`)
- Cache defaults merged with session overrides in `build_app_service_container`
- Validation of the resolved `AppSessionContext` (raising `INVALID_APP_SESSION_TYPE`)
- High-level `core.build_app()` behavior

## Best Practices

- Keep blueprints **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in the single-call entry points (`core.build_app`, `build_tiferet_app`, `build_tiferet_cli`).
- Use `RaiseError.execute()` for all error paths with proper constants.
- Inject the `ServiceResolver`'s `get_dependency` handler into the context so contexts remain decoupled from the DI engine.

## Conclusion

Blueprints provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, and interface resolution while delegating execution to `AppInterfaceContext`. Their functional design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/blueprints/` and blueprint tests in the top-level `tests/` tree for implementation details.

## Related Documentation

- [docs/guides/blueprints.md](../guides/blueprints.md) — blueprint strategies and patterns
- [docs/core/di.md](../core/di.md) — dependency injection and service provider design
- [docs/core/events.md](../core/events.md) — domain event design and usage
- [docs/guides/domain/app.md](../guides/domain/app.md) — application interface and service registration guide
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
