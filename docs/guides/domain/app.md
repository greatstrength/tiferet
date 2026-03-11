**This conversation is part of the Tiferet Framework project.**  
**Repository:** https://github.com/greatstrength/tiferet – Tiferet Framework  

```markdown
# Domain – App: AppInterface and AppServiceDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 11, 2026  
**Version:** 2.0.0a5

## Overview

The App domain defines the structural foundation for application entry points in Tiferet. Every runnable interface — whether a REST API, CLI, background worker, or custom context — is described by an `AppInterface` domain object. Each interface declares its context implementation, logging configuration, dependency-resolution flags, static constants, and a list of injectable service dependency bindings (`AppServiceDependency`).

These domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing services, updating constants, renaming) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/app.py`

## Domain Objects

### AppServiceDependency

Represents a single injectable service dependency binding for an application interface.

| Attribute      | Type                   | Required | Default | Description                                                                      |
|----------------|------------------------|----------|---------|----------------------------------------------------------------------------------|
| `module_path`  | `StringType`           | Yes      | —       | The module path for the app dependency.                                           |
| `class_name`   | `StringType`           | Yes      | —       | The class name for the app dependency.                                            |
| `service_id`   | `StringType`           | No *(todo: required)* | — | The canonical service id for the application dependency.             |
| `attribute_id` | `StringType`           | No *(obsolete)* | — | The attribute id for the application dependency. Superseded by `service_id`. |
| `parameters`   | `DictType(StringType)` | No       | `{}`    | The parameters for the application dependency.                                    |

No methods. Pure data structure.

#### Rename Note: AppAttribute → AppServiceDependency

In v1.x, service dependency bindings were called `AppAttribute`. In v2.0, the class is renamed to `AppServiceDependency` to better reflect its role as a service dependency binding rather than a generic attribute. The field set and semantics are unchanged.

### AppInterface

Represents the complete configuration of an application entry point.

| Attribute      | Type                                | Required | Default       | Description                                           |
|----------------|-------------------------------------|----------|---------------|-------------------------------------------------------|
| `id`           | `StringType`                        | Yes      | —             | The unique identifier for the application interface.   |
| `name`         | `StringType`                        | Yes      | —             | The name of the application interface.                 |
| `description`  | `StringType`                        | No       | —             | The description of the application interface.          |
| `module_path`  | `StringType`                        | Yes      | —             | The module path for the application instance context.  |
| `class_name`   | `StringType`                        | Yes      | —             | The class name for the application instance context.   |
| `logger_id`    | `StringType`                        | No       | `'default'`   | The logger ID for the application instance.            |
| `flags`        | `ListType(StringType)`              | No       | `['default']` | The flags for the application interface.               |
| `services`     | `ListType(ModelType(AppServiceDependency))` | Yes | `[]`        | The application instance service dependencies.         |
| `constants`    | `DictType(StringType)`              | No       | `{}`          | The application dependency constants.                  |

#### Methods

**`get_service(service_id: str) -> AppServiceDependency`**

Returns the `AppServiceDependency` whose `service_id` matches the given value, or `None` if no match is found. For backward compatibility, also falls back to matching on `attribute_id` (this fallback will be removed once `attribute_id` is fully migrated).

```python
service = app_interface.get_service('cli_repo')
if service:
    print(service.module_path, service.class_name)
```

## Runtime Role

The App domain objects participate in the application bootstrapping flow:

1. **`AppManagerContext`** (alias `App`) loads application settings and interface configurations from `app/configs/app.yml`.
2. **`app.load_interface(interface_id)`** retrieves the `AppInterface` domain object for the requested interface.
3. **`load_app_instance()`** reads `AppInterface.module_path` and `AppInterface.class_name` to import and instantiate the context class.
4. Each `AppServiceDependency` in `AppInterface.services` is resolved via the dependency injection container, wiring constructor parameters from `AppServiceDependency.parameters`.
5. The instantiated context is ready to execute features, handle requests, or run CLI commands.

## Configuration Mapping

Application interfaces are defined in `app/configs/app.yml`. Each top-level key under `interfaces` maps to an `AppInterface`, and nested `attrs` entries map to `AppServiceDependency` objects. Each key under `attrs` becomes the `service_id` of the corresponding `AppServiceDependency`:

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
  calc_cli:
    name: Calculator CLI
    description: Perform basic calculator operations via CLI
    module_path: tiferet.contexts.cli
    class_name: CliContext
    attrs:
      cli_repo:
        module_path: tiferet.proxies.yaml.cli
        class_name: CliYamlProxy
        params:
          cli_config_file: app/configs/cli.yml
      cli_service:
        module_path: tiferet.handlers.cli
        class_name: CliHandler
```

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

Concrete implementations (e.g., `AppYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **Dependency Injection (Container):** `AppServiceDependency` entries reference container attributes that are resolved at runtime via `ContainerContext`.
- **Feature:** Once an interface is loaded and its context instantiated, features defined in `feature.yml` are executed through the `FeatureContext`.
- **Logging:** `AppInterface.logger_id` references a logger configuration from the Logging domain (`logging.yml`).

## Instantiation

Both domain objects are instantiated via the standard `DomainObject.new()` factory:

```python
from tiferet.domain import DomainObject, AppServiceDependency, AppInterface

dep = DomainObject.new(
    AppServiceDependency,
    service_id='cli_repo',
    module_path='tiferet.proxies.yaml.cli',
    class_name='CliYamlProxy',
    parameters={'cli_config_file': 'app/configs/cli.yml'},
)

interface = DomainObject.new(
    AppInterface,
    id='calc_cli',
    name='Calculator CLI',
    module_path='tiferet.contexts.cli',
    class_name='CliContext',
    services=[dep],
)
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
```
