# Blueprints in Tiferet

Blueprints are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While contexts define the runtime shape and behavior of an individual interface, blueprints orchestrate the overall application lifecycle and wiring. They replace previous direct usage of lower-level contexts for application initialization.

## What is a Blueprint?

A blueprint in Tiferet is a module-level function that encapsulates the initialization and orchestration logic required to prepare and run an application interface. Blueprints are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppInterfaceContext`.

The canonical implementation is `build_app` in `tiferet/blueprints/main.py`.

### Role in the Architecture

Blueprints sit at the highest level of the application graph:

- They load the application service (typically a repository)
- They prepare default services and constants from `assets.app` (`a.app.CORE_DEFAULT_SERVICES` / `a.app.CORE_DEFAULT_CONSTANTS`)
- They resolve interfaces via domain events (`GetAppInterface`)
- They declaratively wire service dependencies into a name-to-value registry (no app-level DI container) and compose a `ServiceResolver` via the `CreateServiceResolver` bootstrap event
- They delegate feature execution to the resolved `AppInterfaceContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Blueprints

Tiferet currently defines two blueprints:

- **App blueprint**: `build_app` — used for general script and custom interfaces. Exposed globally as `App`.
- **CLI blueprint**: `build_cli` — a thin entrypoint that resolves and realizes a CLI interface (which must point at `CliContext`) and delegates `sys.argv` translation and feature dispatch to `CliContext.run_cli`. Exposed globally as `CLI`.

Future specialized blueprints may include:

- Web blueprint — for web framework integration (Flask, FastAPI, etc.)
- Test blueprint — for integration and unit testing with mocked services

### CLI Blueprint Build Procedure

The CLI blueprint (`build_cli`) is a thin entrypoint; argparse parsing and request derivation live in the reincorporated `CliContext` (`tiferet/contexts/cli.py`). Its flow follows these steps:

1. **Resolve the interface** via `resolve_interface(interface_id)`.
2. **Realize the context** via `realize_interface(...)`. The interface must point at `tiferet.contexts.cli` / `CliContext`, so the realized context is a `CliContext`.
3. **Delegate to the context** by calling `cli_context.run_cli(argv)`, which builds the parser from the interface's CLI commands and parent arguments, parses `argv` (argparse exits `2` on failure), derives `feature_id`/`headers`, dispatches through the inherited `run`, prints the response, and converts a `TiferetAPIError` into `sys.exit(1)`.

Consumer CLI interfaces opt in by declaring `module_path: tiferet.contexts.cli` / `class_name: CliContext` in their interface config.

## Structured Code Design of Blueprints

Blueprints follow Tiferet's standard artifact comment structure.

### Artifact Comments

Blueprints are organized under the `# *** blueprints` top-level comment, with individual blueprints under `# ** blueprint: <snake_case_name>`. Each blueprint function uses standard RST docstrings and code snippet conventions.

Side-effect-free helpers (pure input→output transforms with no I/O, instantiation, or error raising) belong in a `# *** functions` section above `# *** blueprints`, with individual helpers under `# ** function: <snake_case_name>`. In `tiferet/blueprints/main.py` these are `resolve_ctor_kwargs`, `build_wiring_constants`, and `resolve_collaborators` — small pure helpers consumed by the orchestration functions below them. Reserve `# *** blueprints` for the orchestration entry points reused by other blueprints or clients (e.g. `wire_services`, `resolve_interface`, `load_app_instance`, `build_app`).

**Spacing rules:**

- One empty line between `# *** blueprints` and first `# ** blueprint`
- One empty line between each blueprint function
- One empty line after docstrings and between code snippets

## Writing Blueprints

### Creating a New Blueprint

1. Place the function under `# *** blueprints` in an appropriate module (for example, `tiferet/blueprints/main.py`).
2. Use `# ** blueprint: <snake_case_name>`.
3. Implement the standard lifecycle functions:
   - `load_app_service` — import and construct the app service
   - `load_default_services` — load default service dependencies
   - `resolve_interface` — resolve the interface definition
   - `wire_services` — declaratively instantiate service dependencies into a name-to-value registry
   - `load_app_instance` — compose the `ServiceResolver` via the `CreateServiceResolver` bootstrap event and construct the context, injecting `get_dependency`
   - `realize_interface` — build and validate the interface context
   - `build_app` — high-level entry point

### Key Patterns

**Single-call entry point**  
`build_app` resolves and realizes in one call:

```python
app = App('basic_calc', app_config='config.yml')
```

**Default configuration injection**  
Blueprints inject the framework's `CORE_DEFAULT_SERVICES` and `CORE_DEFAULT_CONSTANTS` catalogs (defined in `assets/app.py`, accessed as `a.app`) via the `AppInterface.apply_defaults` domain method after the repo-only `GetAppInterface` read (with the context helper `resolve_default_interface` providing the bootstrap interface fallback):

```python
app_interface = app_interface.apply_defaults(
    default_services=default_services,
    default_constants=a.app.CORE_DEFAULT_CONSTANTS,
)
```

**Cache pre-seeding**  
The core `build_cache` blueprint (`tiferet/blueprints/core.py`) pre-seeds a `CacheContext` with three framework catalogs via stacked decorators — `add_default_errors`, `add_default_app_services`, and `add_default_app_constants` (the latter two defined in `contexts/app.py`) — namespacing each catalog under its own cache-key prefix (`error_`, `app_service_`, `app_constant_`). Errors and services are reconstituted into domain objects (`Error`, `AppServiceDependency`); constants are seeded as scalars:

```python
@add_default_app_constants(a.app.CORE_DEFAULT_CONSTANTS)
@add_default_app_services(a.app.CORE_DEFAULT_SERVICES)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(cache=None) -> CacheContext:
    return CacheContext(cache=cache)
```

**Declarative service wiring**  
`wire_services` instantiates the interface's dependencies into a name-to-value registry, and `load_app_instance` composes a `ServiceResolver` via the `CreateServiceResolver` bootstrap event, injecting its `get_dependency` handler into the context:

```python
resolver = DomainEvent.handle(CreateServiceResolver, dependencies={}, app_interface=app_interface, ...)
return context_cls.from_domain(app_interface, get_dependency=resolver.get_dependency, ...)
```

## Testing Blueprints

Blueprint tests use `pytest` with `unittest.mock`. Focus on:

- Correct loading of the app service
- Delegation to `GetAppInterface` (repo-only) with defaults merged via `AppInterface.apply_defaults`
- Validation of the resolved `AppInterfaceContext`
- High-level `build_app()` behavior

## Best Practices

- Keep blueprints **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type in `realize_interface`.
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
