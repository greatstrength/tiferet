# Blueprints in Tiferet

Blueprints are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While contexts define the runtime shape and behavior of an individual interface, blueprints orchestrate the overall application lifecycle and wiring. They replace previous direct usage of lower-level contexts for application initialization.

## What is a Blueprint?

A blueprint in Tiferet is a module-level function that encapsulates the initialization and orchestration logic required to prepare and run an application interface. Blueprints are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppInterfaceContext`.

The canonical implementation is `build_app` in `tiferet/blueprints/main.py`.

### Role in the Architecture

Blueprints sit at the highest level of the application graph:

- They load the application service (typically a repository)
- They prepare default services and constants from `assets.blueprints`
- They resolve interfaces via domain events (`GetAppInterface`)
- They wire the dependency injection container
- They delegate feature execution to the resolved `AppInterfaceContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Blueprints

Tiferet currently defines two blueprints:

- **App blueprint**: `build_app` — used for general script and custom interfaces. Exposed globally as `App`.
- **CLI blueprint**: `build_cli` — extends the app blueprint with argparse-based CLI build-time translation of `sys.argv` into a feature invocation. Exposed globally as `CLI`.

Future specialized blueprints may include:

- Web blueprint — for web framework integration (Flask, FastAPI, etc.)
- Test blueprint — for integration and unit testing with mocked services

### CLI Blueprint Build Procedure

The CLI blueprint (`build_cli`) keeps all build-time CLI parsing in the blueprint and delegates runtime execution to the `AppInterfaceContext`. Its flow follows these steps:

1. **Resolve the interface** via `resolve_interface(interface_id)`.
2. **Build the argparse parser** by composing `get_commands()` (resolves `list_commands_evt` and groups returned commands by `group_key`), `get_parent_arguments()` (resolves `get_parent_args_evt`), and `build_parser(cli_commands, parent_arguments)`.
3. **Parse arguments** with `parse_argv(parser, argv)`; on failure, print to stderr and `sys.exit(2)`.
4. **Dispatch the feature** by deriving `feature_id` and `headers` via `derive_feature_request(parsed)`, then calling `interface_context.run(feature_id=feature_id, headers=headers, data=parsed)`. On `TiferetAPIError`, print to stderr and `sys.exit(1)`; otherwise print and return the response.

Because the default `AppInterfaceContext` is sufficient for CLI interfaces, CLI interface definitions in YAML no longer require `module_path`/`class_name` overrides.

## Structured Code Design of Blueprints

Blueprints follow Tiferet's standard artifact comment structure.

### Artifact Comments

Blueprints are organized under the `# *** blueprints` top-level comment, with individual blueprints under `# ** blueprint: <snake_case_name>`. Each blueprint function uses standard RST docstrings and code snippet conventions.

**Spacing rules:**

- One empty line between `# *** blueprints` and first `# ** blueprint`
- One empty line between each blueprint function
- One empty line after docstrings and between code snippets

## Writing Blueprints

### Creating a New Blueprint

1. Place the function under `# *** blueprints` in an appropriate module (for example, `tiferet/blueprints/main.py`).
2. Use `# ** blueprint: <snake_case_name>`.
3. Implement the standard lifecycle functions:
   - `create_service_provider` — provider factory
   - `load_app_service` — import and construct the app service
   - `load_default_services` — load default service dependencies
   - `resolve_interface` — resolve the interface definition
   - `realize_interface` — build and validate the interface context
   - `build_app` — high-level entry point

### Key Patterns

**Single-call entry point**  
`build_app` resolves and realizes in one call:

```python
app = App('basic_calc', app_yaml_file='config.yml')
```

**Default configuration injection**  
Blueprints automatically inject `DEFAULT_SERVICES` and `DEFAULT_CONSTANTS` via `GetAppInterface`:

```python
app_interface = DomainEvent.handle(
    GetAppInterface,
    ...,
    default_services=default_services,
    default_constants=a.bps.DEFAULT_CONSTANTS,
)
```

**Service provider registration**  
The `create_service_provider` function is registered so contexts can create scoped providers:

```python
dependencies['create_service_provider'] = create_service_provider
```

## Testing Blueprints

Blueprint tests use `pytest` with `unittest.mock`. Focus on:

- Correct loading of the app service
- Delegation to `GetAppInterface` with defaults injected
- Validation of the resolved `AppInterfaceContext`
- High-level `build_app()` behavior

## Best Practices

- Keep blueprints **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type in `realize_interface`.
- Use `RaiseError.execute()` for all error paths with proper constants.
- Register `create_service_provider` so contexts remain decoupled from the blueprint.

## Conclusion

Blueprints provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, and interface resolution while delegating execution to `AppInterfaceContext`. Their functional design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/blueprints/` and tests in `tiferet/blueprints/tests/` for implementation details.

## Related Documentation

- [docs/guides/blueprints.md](../guides/blueprints.md) — blueprint strategies and patterns
- [docs/core/di.md](../core/di.md) — dependency injection and service provider design
- [docs/core/events.md](../core/events.md) — domain event design and usage
- [docs/guides/domain/app.md](../guides/domain/app.md) — application interface and service configuration guide
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
