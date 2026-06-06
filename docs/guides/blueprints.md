# Blueprints – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/blueprints/`  
**Version:** 2.0.0

## Overview

Blueprints are the top-level orchestration layer in Tiferet v2.0+. They serve as the primary public entry point for applications, providing module-level functions that replace the previous class-based `AppBuilder`/`CliBuilder` pattern.

A blueprint is responsible for:

- Loading the application service (repository)
- Preparing default services and constants
- Resolving interfaces via domain events
- Wiring dependency injection
- Executing features through the resolved interface context

The canonical example is `build_app` in `tiferet/blueprints/main.py`.

## Role of Blueprints in the Architecture

Blueprints sit at the highest level of the runtime graph. They are what application code interacts with directly:

```python
from tiferet import App

app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 5, 'b': 3})
```

Key responsibilities:

- **Service loading** — dynamic import of the app service (usually a repository)
- **Default configuration** — injecting `DEFAULT_SERVICES` and `DEFAULT_CONSTANTS` from `assets.blueprints`
- **Interface resolution** — calling `GetAppInterface` and validating the result
- **Execution** — delegating to `AppInterfaceContext.run()`

Blueprints are intentionally **thin** — they coordinate rather than implement business logic.

## The build_app Blueprint

`build_app` follows a clear, composable pattern built from smaller blueprint functions:

### 1. Service Provider Factory

A standalone function allows downstream contexts to create providers consistently:

```python
def create_service_provider(
    provider_type: type = DynamicServiceProvider,
    type_map: Dict[str, type] = None,
    **constants
) -> ServiceProvider:
    ...
```

This is registered in the DI container so contexts can create scoped providers.

### 2. Loading the App Service

```python
def load_app_service(module_path=..., class_name=..., **parameters) -> Any:
    service_cls = ImportDependency.execute(module_path, class_name)
    return service_cls(**parameters)
```

### 3. Loading Default Services and Constants

```python
def load_default_services() -> List[AppServiceDependency]:
    return [
        AppServiceDependency.model_construct(...)
        for ... in a.bps.DEFAULT_SERVICES
    ]
```

Constants are passed via `default_constants=a.bps.DEFAULT_CONSTANTS` to `GetAppInterface`.

### 4. Interface Resolution Flow

```python
def resolve_interface(interface_id, ...) -> tuple:
    app_service = load_app_service(...)
    default_services = load_default_services()
    app_interface = DomainEvent.handle(
        GetAppInterface,
        dependencies={'app_service': app_service},
        interface_id=interface_id,
        default_services=default_services,
        default_constants=a.bps.DEFAULT_CONSTANTS,
    )
    return app_interface, default_services
```

### 5. High-level Entry Point

```python
def build_app(interface_id, ...) -> AppInterfaceContext:
    app_interface, _ = resolve_interface(interface_id, ...)
    return realize_interface(app_interface, interface_id)
```

## The build_cli Blueprint

The CLI blueprint extends the app blueprint with argparse-based CLI parsing. All argparse wiring lives in the blueprint; runtime execution is delegated to `AppInterfaceContext.run`.

### Usage

```python
from tiferet import CLI

if __name__ == '__main__':
    CLI('basic_calc_cli', app_config='config.yml')
```

### Build Procedure

`build_cli(interface_id, argv=None, ...)` follows these steps:

1. Resolve the interface via `resolve_interface(interface_id, ...)`.
2. Build the argparse parser by composing `get_commands()`, `get_parent_arguments()`, and `build_parser(cli_commands, parent_arguments)`.
3. Parse arguments with `parse_argv(parser, argv)`; on failure, print to stderr and `sys.exit(2)`.
4. Derive `feature_id` and `headers` via `derive_feature_request(parsed)` and dispatch to `interface_context.run(...)`. On `TiferetAPIError`, print to stderr and `sys.exit(1)`; otherwise print and return the response.

Because the CLI blueprint uses the default `AppInterfaceContext`, CLI interface definitions in YAML no longer require `module_path`/`class_name` overrides.

## When to Create a New Blueprint

Create a new blueprint when you need a specialized entry point:

- Web blueprint — for Flask/FastAPI integration
- Test blueprint — for integration testing with mocked services

If you find yourself repeating the same loading and wiring logic in multiple scripts, extract it into a dedicated blueprint.

## Blueprint vs Context

| Concern | Blueprint | Context |
| --- | --- | --- |
| Public API | Yes (`App('basic_calc')`) | Internal (used by blueprint) |
| Service loading | Yes | No |
| Default config injection | Yes | No |
| Feature execution | Delegates to interface context | Yes (`execute_feature`, `run`) |
| Lifecycle | Application-level | Per-interface |

Blueprints are **application-level**; contexts are **interface-level**.

## Best Practices

### 1. Single-call Entry Point

`build_app` resolves and realizes in one call:

```python
app = App('basic_calc', app_config='config.yml')
```

### 2. Consistent Error Handling

Use framework constants and `RaiseError.execute()` for all failure paths.

### 3. Keep Blueprints Thin

Blueprints should **not** contain domain logic — only orchestration, wiring, and delegation.

### 4. Register `create_service_provider`

Always register the function so contexts can create scoped providers:

```python
dependencies['create_service_provider'] = create_service_provider
```

## Related Documentation

- [docs/core/blueprints.md](../core/blueprints.md) — detailed blueprint implementation reference
- [docs/guides/domain/app.md](../guides/domain/app.md) — application-level configuration and runtime orchestration
- [docs/guides/events/app.md](../guides/events/app.md) — app event usage in interface resolution
- [docs/core/di.md](../core/di.md) — dependency injection and service provider architecture
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
