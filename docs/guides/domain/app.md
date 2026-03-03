# Domain – App (Bootstrap & Assembly)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/domain/app.py`  
**Version:** 2.0.0a2

## Overview

The App domain defines **how the application is assembled**. It is the entry point for every Tiferet runtime session — before any feature executes, before any dependency is resolved, an `AppInterface` is loaded and its `AppServiceDependency` list is used to wire up the entire application context.

Think of `AppInterface` as the blueprint for a running application instance. It declares which context class to instantiate, what service dependencies to inject, and which flags to use for dependency resolution. `AppServiceDependency` is a single entry in that blueprint — one service binding that tells the framework where to find a class and how to configure it.

## Domain Objects

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

- `get_service(attribute_id)` — retrieves an `AppServiceDependency` by its `attribute_id`. Used during bootstrapping to look up specific service dependency bindings.

### AppServiceDependency

A single service dependency that tells the framework what to import and how to bind it in the dependency injector.

> **Rename note (v2.0a2):** Previously named `AppAttribute`. Renamed to `AppServiceDependency` to reflect its true role as a service dependency binding, not a generic attribute.

| Attribute | Type | Description |
|-----------|------|-------------|
| `module_path` | `str` (required) | Python module path for the dependency class |
| `class_name` | `str` (required) | Class name to import |
| `attribute_id` | `str` (required) | The dependency name in the injector (e.g., `cli_repo`, `cli_service`) |
| `parameters` | `Dict[str, str]` (default: `{}`) | Configuration parameters passed to the dependency |

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

## Configuration

App interfaces are defined in `app/configs/app.yml`:

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

Each key under `interfaces` becomes the `AppInterface.id`. The `attrs` section maps to the `services` list, where each key becomes the `attribute_id`.

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

- **DI domain** — `AppServiceDependency` entries reference classes that are often the same implementations registered in the DI service configurations. The `flags` on `AppInterface` are passed to `ContainerContext` to control flag-based dependency resolution.
- **Feature domain** — Features are executed *within* a loaded app interface. The interface provides the runtime context (features, errors, logging) that features operate in.
- **Logging domain** — Each `AppInterface` specifies a `logger_id` that determines which logging configuration is used at runtime.

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/events.md) — Domain event patterns
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/interfaces.md) — Service interface conventions
