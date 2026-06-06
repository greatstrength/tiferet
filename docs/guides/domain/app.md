# Domain – App: AppInterface and AppServiceDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The App domain defines the structural foundation for application entry points in Tiferet. Every runnable interface — whether a REST API, CLI, background worker, or custom context — is described by an `AppInterface` domain object. Each interface declares its context implementation, logging configuration, dependency-resolution flags, static constants, and a list of injectable service dependency bindings (`AppServiceDependency`).

These domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing services, updating constants, renaming) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/app.py`

## Domain Objects

### AppServiceDependency

Represents a single injectable service dependency binding for an application interface.

| Attribute      | Type                   | Required | Default | Description                                                                      |
|----------------|------------------------|----------|---------|----------------------------------------------------------------------------------|
| `module_path`  | `str`                  | Yes      | —       | The module path for the app dependency.                                           |
| `class_name`   | `str`                  | Yes      | —       | The class name for the app dependency.                                            |
| `service_id`   | `str`                  | No *(todo: required)* | — | The canonical service id for the application dependency.             |
| `attribute_id` | `str`                  | No *(obsolete)* | — | The attribute id for the application dependency. Superseded by `service_id`. |
| `parameters`   | `Dict[str, str]`       | No       | `{}`    | The parameters for the application dependency.                                    |

No methods. Pure data structure.

#### Rename Note: AppAttribute → AppServiceDependency

In v1.x, service dependency bindings were called `AppAttribute`. In v2.0, the class is renamed to `AppServiceDependency` to better reflect its role as a service dependency binding rather than a generic attribute. The field set and semantics are unchanged.

### AppInterface

Represents the complete configuration of an application entry point.

| Attribute      | Type                                | Required | Default       | Description                                           |
|----------------|-------------------------------------|----------|---------------|-------------------------------------------------------|
| `id`           | `str`                               | Yes      | —             | The unique identifier for the application interface.   |
| `name`         | `str`                               | Yes      | —             | The name of the application interface.                 |
| `description`  | `str \| None`                       | No       | `None`        | The description of the application interface.          |
| `module_path`  | `str`                               | Yes      | —             | The module path for the application instance context.  |
| `class_name`   | `str`                               | Yes      | —             | The class name for the application instance context.   |
| `logger_id`    | `str`                               | No       | `'default'`   | The logger ID for the application instance.            |
| `flags`        | `List[str]`                         | No       | `['default']` | The flags for the application interface.               |
| `services`     | `List[AppServiceDependency]`        | Yes      | `[]`          | The application instance service dependencies.         |
| `constants`    | `Dict[str, str]`                    | No       | `{}`          | The application dependency constants.                  |

#### Methods

**`get_service(service_id: str) -> AppServiceDependency`**

Returns the `AppServiceDependency` whose `service_id` matches the given value, or `None` if no match is found. For backward compatibility, also falls back to matching on `attribute_id` (this fallback will be removed once `attribute_id` is fully migrated).

```python
service = app_interface.get_service('cli_repo')
if service:
    print(service.module_path, service.class_name)
```

## Runtime Role

The `build_app` blueprint (`tiferet/blueprints/main.py`) is the primary consumer of the App domain at runtime. The flow is:

1. **`App('basic_calc', app_config='config.yml')`** calls `build_app`, which loads the app service and resolves the interface.
2. **`resolve_interface(interface_id)`** retrieves the `AppInterface` via the `GetAppInterface` domain event, merging default services.
3. **`realize_interface(app_interface, ...)`** iterates through `app_interface.services`, imports each class via `ImportDependency.execute()`, and collects them (along with parameters and constants) into a dependencies dict.
4. The dependencies dict is passed to `create_service_provider`, which builds a DI container that instantiates the context class with all its wired services.
5. The resulting `AppInterfaceContext` is returned, ready to execute features.

```python
# Simplified runtime flow
from tiferet import App

app = App('basic_calc', app_config='config.yml')  # resolves interface, wires dependencies
result = app.run('calc.add', data={'a': 1, 'b': 2})  # executes features via the wired context
```

## Configuration Mapping

Application interfaces are defined in the `interfaces` section of the configuration file (typically `config.yml`). Each top-level key under `interfaces` maps to an `AppInterface`, and nested `attrs` entries map to `AppServiceDependency` objects. Each key under `attrs` becomes the `service_id` of the corresponding `AppServiceDependency`:

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
  basic_calc_cli:
    name: Calculator CLI
    description: Perform basic calculator operations via CLI
    attrs:
      cli_repo:
        module_path: tiferet.repos.cli
        class_name: CliConfigRepository
        params:
          cli_config: config.yml
```

CLI interfaces no longer require `module_path`/`class_name` overrides — they use the default `AppInterfaceContext` with argparse wiring handled by the `build_cli` blueprint.

## Domain Events

The following domain events interact with `AppInterface` and `AppServiceDependency`:

| Event                | Description                                       |
|----------------------|---------------------------------------------------|
| `GetAppInterface`    | Retrieves an `AppInterface` by ID.                |
| `AddAppInterface`    | Creates and persists a new `AppInterface`.         |
| `UpdateAppInterface` | Modifies an existing `AppInterface` via aggregate. |
| `DeleteAppInterface` | Removes an `AppInterface` by ID.                   |

These events depend on the `AppService` interface for persistence operations.

## Service Interface

**`AppService`** (`tiferet/interfaces/app.py`) defines the abstract contract for App domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> AppInterface`
- `list() -> List[AppInterface]`
- `save(app_interface) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `AppConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **Dependency Injection:** `AppServiceDependency` entries reference service configurations that are resolved at runtime via `DIContext`.
- **Feature:** Once an interface is loaded and its context instantiated, features defined in the configuration are executed through the `FeatureContext`.
- **Logging:** `AppInterface.logger_id` references a logger configuration from the Logging domain.

## Instantiation

Both domain objects are instantiated directly via the Pydantic constructor:

```python
from tiferet.domain import AppServiceDependency, AppInterface

dep = AppServiceDependency(
    service_id='cli_repo',
    module_path='tiferet.repos.cli',
    class_name='CliConfigRepository',
    parameters={'cli_config': 'config.yml'},
)

interface = AppInterface(
    id='basic_calc_cli',
    name='Calculator CLI',
    services=[dep],
)
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
