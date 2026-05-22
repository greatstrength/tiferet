# Domain – App: AppInterface and AppServiceDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The App domain defines **how the application is assembled**. It is the entry point for every Tiferet runtime session — before any feature executes, before any dependency is resolved, an `AppInterface` is loaded and its `AppServiceDependency` list is used to wire up the entire application context.

Think of `AppInterface` as the blueprint for a running application instance. It declares which context class to instantiate, what service dependencies to inject, and which flags to use for dependency resolution. `AppServiceDependency` is a single entry in that blueprint — one service binding that tells the framework where to find a class and how to configure it.

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

The top-level configuration for a single application interface. Every runtime session begins by loading one `AppInterface` by ID.

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

The `build_app` blueprint (`tiferet/blueprints/main.py`) is the primary consumer of the App domain at runtime. The flow is:

1. **`App('basic_calc', app_yaml_file='config.yml')`** calls `build_app`, which loads the app service and resolves the interface.
2. **`resolve_interface(interface_id)`** retrieves the `AppInterface` via the `GetAppInterface` domain event, merging default services.
3. **`realize_interface(app_interface, ...)`** iterates through `app_interface.services`, imports each class via `ImportDependency.execute()`, and collects them (along with parameters and constants) into a dependencies dict.
4. The dependencies dict is passed to `create_service_provider`, which builds a DI container that instantiates the context class with all its wired services.
5. The resulting `AppInterfaceContext` is returned, ready to execute features.

```python
# Simplified runtime flow
from tiferet import App

app = App('basic_calc', app_yaml_file='config.yml')  # resolves interface, wires dependencies
result = app.run('calc.add', data={'a': 1, 'b': 2})  # executes features via the wired context
```

```python
# Simplified runtime flow
app = App()                                     # creates AppManagerContext
interface = app.load_interface('calc_cli')       # loads AppInterface, wires dependencies
result = interface.run()                         # executes features via the wired context
```

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
        class_name: CliYamlRepository
        params:
          cli_yaml_file: config.yml
```

CLI interfaces no longer require `module_path`/`class_name` overrides — they use the default `AppInterfaceContext` with argparse wiring handled by the `build_cli` blueprint.

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
    class_name='CliYamlRepository',
    parameters={'cli_yaml_file': 'config.yml'},
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
