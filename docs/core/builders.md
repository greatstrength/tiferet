# Builders in Tiferet

Builders are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While contexts define the runtime shape and behavior of an individual interface, builders orchestrate the overall application lifecycle and wiring. They replace previous direct usage of lower-level contexts for application initialization.

## What is a Builder?

A builder in Tiferet is a class that encapsulates the initialization and orchestration logic required to prepare and run an application interface. Builders are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppInterfaceContext`.

The canonical implementation is `AppBuilder` in `tiferet/builders/main.py`.

### Role in the Architecture

Builders sit at the highest level of the application graph:

- They load the application service (typically a repository)
- They prepare default services and constants from `assets.constants`
- They resolve interfaces via domain events (`GetAppInterface`)
- They wire the dependency injection container
- They delegate feature execution to the resolved `AppInterfaceContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Builders

Tiferet currently defines two builders:

- **High-level builder**: `AppBuilder` — used for general script, web, and custom interfaces.
- **CLI builder**: `CliBuilder` — extends `AppBuilder` to absorb argparse-based CLI parsing into the build procedure. Exposed globally as `CLI`.

Future specialized builders may include:

- `WebBuilder` — for web framework integration (Flask, FastAPI, etc.)
- `TestBuilder` — for integration and unit testing with mocked services

### CliBuilder Build Procedure

`CliBuilder` inherits everything from `AppBuilder` and overrides `run(interface_id, argv=None)` to:

1. `load_interface(interface_id)` — inherited from `AppBuilder`.
2. `get_commands()` / `get_parent_arguments()` — resolve CLI metadata via `list_commands_evt` / `get_parent_args_evt` from the builder's populated `service_provider`.
3. `build_parser(cli_commands, parent_arguments)` — compose an `argparse.ArgumentParser` tree.
4. Parse argv, derive `(feature_id, headers, data)`, and delegate to `interface_context.run(feature_id, headers, data)` like the base builder. Parse errors exit with code 2; `TiferetAPIError` from the interface exits with code 1.

No argparse logic lives in runtime contexts — the default `AppInterfaceContext` is sufficient to run CLI interfaces.

## Structured Code Design of Builders

Builders follow Tiferet’s standard artifact comment structure.

### Artifact Comments

Builders are organized under the `# *** builders` top-level comment, with individual builders under `# ** builder: <snake_case_name>`. Within each builder:

- `# * attribute: <name>` — instance attributes (with type hints)
- `# * init` — constructor
- `# * method: <name>` — methods (including static factory methods)

**Spacing rules:**

- One empty line between `# *** builders` and first `# ** builder`
- One empty line between each `# *` section
- One empty line after docstrings and between code snippets

## Writing Builders

### Creating a New Builder

1. Place the class under `# *** builders` in an appropriate module (for example, `tiferet/builders/main.py`).
2. Use `# ** builder: <snake_case_name>`.
3. Implement the standard lifecycle:
   - `__init__`
   - `create_service_provider` (static factory)
   - `load_app_service`
   - `load_default_services`
   - `load_app_instance`
   - `load_interface`
   - `run` (high-level entry point)

### Key Patterns

**Method chaining**  
`load_app_service()` returns `self` to support fluent usage:

```python
builder = AppBuilder().load_app_service(...)
```

**Default configuration injection**  
Builders automatically inject `DEFAULT_SERVICES` and `DEFAULT_CONSTANTS` via `GetAppInterface`:

```python
app_interface = DomainEvent.handle(
    GetAppInterface,
    ...,
    default_services=default_services,
    default_constants=a.const.DEFAULT_CONSTANTS,
)
```

**Service provider registration**  
The builder’s static factory is registered so contexts can create scoped providers:

```python
dependencies['create_service_provider'] = self.create_service_provider
```

**Defensive service lookup**  
Always check the cache before using the app service:

```python
app_service = self.cache.get(APP_SERVICE_KEY)
if not app_service:
    RaiseError.execute(...)
```

## Testing Builders

Builder tests use `pytest` with `unittest.mock`. Focus on:

- Proper initialization of cache and service provider
- Correct loading of the app service
- Delegation to `GetAppInterface` with defaults injected
- Validation of the resolved `AppInterfaceContext`
- High-level `run()` behavior

## Best Practices

- Keep builders **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type in `load_interface`.
- Use `RaiseError.execute()` for all error paths with proper constants.
- Support method chaining where it improves developer experience.
- Register `create_service_provider` so contexts remain decoupled from the builder.

## Conclusion

Builders provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, and interface resolution while delegating execution to `AppInterfaceContext`. Their structured design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/builders/` and tests in `tiferet/builders/tests/` for implementation details.

## Related Documentation

- [docs/guides/builders.md](../guides/builders.md) — builder strategies and patterns
- [docs/core/di.md](../core/di.md) — dependency injection and service provider design
- [docs/core/events.md](../core/events.md) — domain event design and usage
- [docs/guides/domain/app.md](../guides/domain/app.md) — application interface and service configuration guide
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
