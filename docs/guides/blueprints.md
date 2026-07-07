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
- Declaratively wiring service dependencies and composing a `ServiceResolver` via the `CreateServiceResolver` bootstrap event
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
- **Default configuration** — injecting `CORE_DEFAULT_SERVICES` and `CORE_DEFAULT_CONSTANTS` from `assets.app` (`a.app`)
- **Interface resolution** — calling `GetAppInterface` and validating the result
- **Execution** — delegating to `AppInterfaceContext.run()`

Blueprints are intentionally **thin** — they coordinate rather than implement business logic.

## The build_app Blueprint

`build_app` follows a clear, composable pattern built from smaller blueprint functions:

### 1. Declarative Service Wiring

`wire_services` instantiates the interface's service dependencies into a name-to-value registry without an app-level DI container, deferring any service whose constructor arguments are not yet resolvable and retrying until all are built:

```python
def wire_services(
    services: List[AppServiceDependency],
    constants: Dict[str, Any],
) -> Dict[str, Any]:
    ...
```

`load_app_instance` then composes a `ServiceResolver` via the `CreateServiceResolver` bootstrap event and injects its `get_dependency` handler into the context.

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
        AppServiceDependency.model_validate(record)
        for record in a.app.CORE_DEFAULT_SERVICES.values()
    ]
```

Default services and constants are merged into the interface by the `AppInterface.apply_defaults` domain method (see step 4).

### 4. Interface Resolution Flow

`resolve_interface` reads the interface via the repo-only `GetAppInterface` event, falls back to the bootstrap default interface definitions through the context helper `resolve_default_interface` when the consumer's config omits it, then merges framework default services and constants via the `AppInterface.apply_defaults` domain method.

```python
def resolve_interface(interface_id, ..., default_interfaces=[]) -> tuple:
    app_service = load_app_service(...)
    default_services = load_default_services()
    try:
        app_interface = DomainEvent.handle(
            GetAppInterface,
            dependencies={'app_service': app_service},
            interface_id=interface_id,
        )
    except a.TiferetError:
        app_interface = resolve_default_interface(interface_id, default_interfaces)
        if app_interface is None:
            raise
    app_interface = app_interface.apply_defaults(
        default_services=default_services,
        default_constants=a.app.CORE_DEFAULT_CONSTANTS,
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

The CLI blueprint is a thin entrypoint. Argparse parsing and request derivation are owned by the reincorporated `CliContext` (`tiferet/contexts/cli.py`); the blueprint only resolves, realizes, and delegates.

### Usage

```python
from tiferet import CLI

if __name__ == '__main__':
    CLI('basic_calc_cli', app_config='config.yml')
```

### Build Procedure

`build_cli(interface_id, argv=None, ...)` follows these steps:

1. Resolve the interface via `resolve_interface(interface_id, ...)`.
2. Realize the interface context via `realize_interface(...)`. Because the interface points at `CliContext`, the realized context exposes `run_cli`.
3. Delegate to `cli_context.run_cli(argv)`, which builds the parser, parses `argv` (exiting `2` on failure), derives the feature request, dispatches through the inherited `run`, prints the response, and converts a `TiferetAPIError` into `sys.exit(1)`.

Consumer CLI interfaces opt in by declaring `module_path: tiferet.contexts.cli` / `class_name: CliContext` in their interface config.

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

### 4. Inject `get_dependency` into the Context

Compose a `ServiceResolver` via the `CreateServiceResolver` bootstrap event and inject its `get_dependency` handler so contexts resolve feature-step services without coupling to the DI engine:

```python
resolver = DomainEvent.handle(CreateServiceResolver, dependencies={}, app_interface=app_interface, ...)
return context_cls.from_domain(app_interface, get_dependency=resolver.get_dependency, ...)
```

## Related Documentation

- [docs/core/blueprints.md](../core/blueprints.md) — detailed blueprint implementation reference
- [docs/guides/domain/app.md](../guides/domain/app.md) — application-level configuration and runtime orchestration
- [docs/guides/events/app.md](../guides/events/app.md) — app event usage in interface resolution
- [docs/core/di.md](../core/di.md) — dependency injection and service provider architecture
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
