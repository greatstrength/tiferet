# Domain – App (Bootstrap & Assembly)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 11, 2026  
**Version:** 2.0.0a5

## Overview

The App domain defines **how the application is assembled**. It is the entry point for every Tiferet runtime session — before any feature executes, before any dependency is resolved, an `AppInterface` is loaded and its `AppServiceDependency` list is used to wire up the entire application context.

Think of `AppInterface` as the blueprint for a running application instance. It declares which context class to instantiate, what service dependencies to inject, and which flags to use for dependency resolution. `AppServiceDependency` is a single entry in that blueprint — one service binding that tells the framework where to find a class and how to configure it.

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

The top-level configuration for a single application interface. Every runtime session begins by loading one `AppInterface` by ID.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Unique identifier (e.g., `basic_calc`, `calc_cli`) |
| `name` | `str` (required) | Human-readable name |
| `description` | `str` | Optional description |
| `module_path` | `str` (required) | Python module path of the context class to instantiate |
| `class_name` | `str` (required) | Class name of the context to instantiate |
| `logger_id` | `str` (default: `'default'`) | Logger configuration to use at runtime |
| `flags` | `List[str]` (default: `['default']`) | Flags for dependency resolution |
| `services` | `List[AppServiceDependency]` (default: `[]`) | Service dependencies to inject into the context |
| `constants` | `Dict[str, str]` (default: `{}`) | Constant values passed to the DI injector |

**Behavior method:**

**`get_service(service_id: str) -> AppServiceDependency`**

Returns the `AppServiceDependency` whose `service_id` matches the given value, or `None` if no match is found. For backward compatibility, also falls back to matching on `attribute_id` (this fallback will be removed once `attribute_id` is fully migrated).

A single service dependency that tells the framework what to import and how to bind it in the dependency injector.

> **Rename note (v2.0a2):** Previously named `AppAttribute`. Renamed to `AppServiceDependency` to reflect its true role as a service dependency binding, not a generic attribute.

| Attribute | Type | Description |
||-----------|------|-------------|
|| `service_id` | `str` *(todo: required)* | The dependency name in the injector (e.g., `cli_repo`, `cli_service`). Canonical identifier going forward. |
|| `attribute_id` | `str` *(obsolete)* | Deprecated alias for `service_id`. Retained for backward compatibility; will be removed once all layers are migrated. |
|| `module_path` | `str` (required) | Python module path for the dependency class |
|| `class_name` | `str` (required) | Class name to import |
|| `parameters` | `Dict[str, str]` (default: `{}`) | Configuration parameters passed to the dependency |

## Runtime Role

`AppManagerContext` is the sole consumer of the App domain at runtime. The flow is:

1. **`App()`** creates an `AppManagerContext` with optional settings.
2. **`load_interface(interface_id)`** retrieves the `AppInterface` via the `GetAppInterface` domain event.
3. **`load_app_instance(app_interface, default_attrs)`** iterates through `app_interface.services`, imports each class via `ImportDependency.execute()`, and collects them (along with parameters and constants) into a dependencies dict.
4. The dependencies dict is passed to `create_injector`, which builds a DI container that instantiates the context class with all its wired services.
5. The resulting context (e.g., `AppInterfaceContext`, `CliContext`) is returned, ready to execute features.

```python
# Simplified runtime flow
app = App()                                     # creates AppManagerContext
interface = app.load_interface('calc_cli')       # loads AppInterface, wires dependencies
result = interface.run()                         # executes features via the wired context
```

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
        module_path: tiferet.repos.cli
        class_name: CliYamlRepository
        params:
          cli_config_file: app/configs/cli.yml
      cli_service:
        module_path: tiferet.handlers.cli
        class_name: CliHandler
```

Each key under `interfaces` becomes the `AppInterface.id`. The `attrs` section maps to the `services` list, where each key becomes the `service_id` of the corresponding `AppServiceDependency`.

## Domain Events

| Event | Purpose |
|-------|---------|
| `GetAppInterface` | Retrieve an interface by ID (used during bootstrapping) |
| `AddAppInterface` | Create a new interface configuration |
| `UpdateAppInterface` | Update a scalar attribute on an existing interface |
| `SetAppConstants` | Set or clear constants on an interface |
| `SetServiceDependency` | Add or update a dependency on an interface |
| `RemoveServiceDependency` | Remove a dependency from an interface |
| `RemoveAppInterface` | Delete an entire interface configuration |
| `ListAppInterfaces` | List all configured interfaces |

## Service Interface

`AppService` (`tiferet/interfaces/app.py`) — abstracts CRUD access to app interface configurations.

## Relationship to Other Domains

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

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
