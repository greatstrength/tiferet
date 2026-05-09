# Blueprints in Tiferet

Blueprints are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While contexts define the runtime shape and behavior of an individual interface, blueprints orchestrate the overall application lifecycle and wiring. They replace previous direct usage of lower-level contexts for application initialization.

## What is a Blueprint?

A blueprint in Tiferet is a module of public functions that encapsulate the initialization and orchestration logic required to prepare and run an application interface. Blueprints are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppInterfaceContext`.

The canonical implementation is `build_app` in `tiferet/blueprints/main.py`.

### Role in the Architecture

Builders sit at the highest level of the application graph:

- They load the application service (typically a repository)
- They prepare default services and constants from `assets.constants`
- They resolve interfaces via domain events (`GetAppInterface`)
- They wire the dependency injection container
- They delegate feature execution to the resolved `AppInterfaceContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Builders

Tiferet currently defines two blueprints:

- **High-level blueprint**: `build_app` — used for general script and custom interfaces. Exposed globally as `App`.
- **CLI blueprint**: `cli.build_app` — a specialized `build_app` subclass that adds argparse-based CLI build-time translation of `sys.argv` into a feature invocation. Exposed globally as `CLI`.

Future specialized blueprints may include:

- `WebBuilder` — for web framework integration (Flask, FastAPI, etc.)
- `TestBuilder` — for integration and unit testing with mocked services

### cli.build_app Build Procedure

`cli.build_app` keeps all build-time CLI parsing in the blueprint and delegates runtime execution to the inherited `AppInterfaceContext`. Its `run(interface_id, argv=None)` method follows a four-step flow:

1. **Load the interface context** via the inherited `load_interface(interface_id)`.
2. **Build the argparse parser** by composing `get_commands()` (resolves `list_commands_evt` and groups returned commands by `group_key`), `get_parent_arguments()` (resolves `get_parent_args_evt`), and `build_parser(cli_commands, parent_arguments)`.
3. **Parse arguments** with `vars(parser.parse_args(argv))`; on failure, print to stderr and `sys.exit(2)`.
4. **Dispatch the feature** by deriving `feature_id = f"{group.replace('-', '_')}.{command.replace('-', '_')}"` and `headers = {'command_group': ..., 'command_key': ...}`, then calling `interface_context.run(feature_id=feature_id, headers=headers, data=parsed)`. On `TiferetAPIError`, print to stderr and `sys.exit(1)`; otherwise print and return the response.

Because the default `AppInterfaceContext` is sufficient for CLI interfaces, CLI interface definitions in YAML no longer require `module_path`/`class_name` overrides.

## Structured Code Design of Builders

Builders follow Tiferet’s standard artifact comment structure.

### Artifact Comments

Blueprints are organized under the `# *** blueprints` top-level comment, with individual blueprints under `# ** blueprint: <snake_case_name>`. Within each blueprint:

- `# * attribute: <name>` — instance attributes (with type hints)
- `# * init` — constructor
- `# * method: <name>` — methods (including static factory methods)

**Spacing rules:**

- One empty line between `# *** blueprints` and first `# ** blueprint`
- One empty line between each `# *` section
- One empty line after docstrings and between code snippets

## Writing Builders

### Creating a New Builder

1. Place the class under `# *** blueprints` in an appropriate module (for example, `tiferet/blueprints/main.py`).
2. Use `# ** blueprint: <snake_case_name>`.
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
blueprint = build_app().load_app_service(...)
```

**Default configuration injection**  
Builders automatically inject `DEFAULT_SERVICES` and `DEFAULT_CONSTANTS` via `GetAppInterface`:

```python
app_interface = DomainEvent.handle(
    GetAppInterface,
    ...,
    default_services=default_services,
    default_constants=a.bps.DEFAULT_CONSTANTS,
)
```

**Service provider registration**  
The blueprint’s static factory is registered so contexts can create scoped providers:

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

- Keep blueprints **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type in `load_interface`.
- Use `RaiseError.execute()` for all error paths with proper constants.
- Support method chaining where it improves developer experience.
- Register `create_service_provider` so contexts remain decoupled from the blueprint.

## Conclusion

Builders provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, and interface resolution while delegating execution to `AppInterfaceContext`. Their structured design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/blueprints/` and tests in `tiferet/blueprints/tests/` for implementation details.

## Related Documentation

- [docs/guides/blueprints.md](../guides/blueprints.md) — blueprint strategies and patterns
- [docs/core/di.md](../core/di.md) — dependency injection and service provider design
- [docs/core/events.md](../core/events.md) — domain event design and usage
- [docs/guides/domain/app.md](../guides/domain/app.md) — application interface and service configuration guide
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
