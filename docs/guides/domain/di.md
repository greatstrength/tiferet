# Domain – DI (Dependency Injection Wiring)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The DI domain defines **how services are connected at runtime**. Every domain event that a feature step executes is resolved from the DI container — and the DI domain controls what class is instantiated, what parameters it receives, and which implementation is selected based on active flags.

A `ServiceConfiguration` is a registry entry that maps an identifier to a concrete class. It can optionally carry `FlaggedDependency` overrides that swap the implementation based on the runtime environment (e.g., a YAML-backed repository for production, a mock for testing). The `ContainerContext` reads all service configurations, resolves their types, and builds a live DI injector.

> **Rename note (v2.0a2):** The module was renamed from `container.py` to `di.py` to capture its true role as part of the Dependency Injection infrastructure. `ContainerAttribute` was renamed to `ServiceConfiguration` to align with the event naming (`AddServiceConfiguration`, etc.).

## Domain Objects

### FlaggedDependency

Represents one flag-qualified implementation override for a service.

| Attribute      | Type                   | Required | Default | Description                                   |
|----------------|------------------------|----------|---------|-----------------------------------------------|
| `module_path`  | `str`                  | Yes      | —       | The module path.                               |
| `class_name`   | `str`                  | Yes      | —       | The class name.                                |
| `flag`         | `str`                  | Yes      | —       | The flag for the container dependency.          |
| `parameters`   | `Dict[str, str]`       | No       | `{}`    | The container dependency parameters.            |

No methods. Pure data structure.

### ServiceConfiguration

A single entry in the DI registry. Defines how to resolve a dependency — either from a default type or from a flag-matched override.

| Attribute       | Type                                  | Required | Default | Description                                       |
|-----------------|---------------------------------------|----------|---------|---------------------------------------------------|
| `id`            | `str`                                 | Yes      | —       | The unique identifier for the service configuration. |
| `name`          | `str \| None`                         | No       | `None`  | The name of the service configuration.             |
| `module_path`   | `str \| None`                         | No       | `None`  | The default module path for the dependency class.  |
| `class_name`    | `str \| None`                         | No       | `None`  | The default class name for the dependency class.   |
| `parameters`    | `Dict[str, str]`                      | No       | `{}`    | The default configuration parameters.              |
| `dependencies`  | `List[FlaggedDependency]`             | No       | `[]`    | The flag-specific implementation overrides.        |

A `ServiceConfiguration` must have **at least one** type source: either a default `module_path`/`class_name` pair, or one or more `FlaggedDependency` entries. The domain events enforce this invariant.

**Behavior method:**

- `get_dependency(*flags)` — searches flagged dependencies in flag-priority order. Returns the first `FlaggedDependency` whose `flag` matches any of the provided flags, or `None` if no match is found. This enables ordinal flag precedence — the caller lists flags from highest to lowest priority.

### FlaggedDependency

An alternative implementation binding activated by a specific flag. When the runtime's active flags match, this dependency's `module_path`/`class_name` is used instead of the default.

| Attribute | Type | Description |
|-----------|------|-------------|
| `module_path` | `str` (required) | Module path for the flag-specific implementation |
| `class_name` | `str` (required) | Class name for the flag-specific implementation |
| `flag` | `str` (required) | The flag that activates this dependency |
| `parameters` | `Dict[str, str]` (default: `{}`) | Flag-specific configuration parameters |

### Flag Resolution

Flags flow from two sources:

At resolution time, `DIContext` merges these flag sources and calls `ServiceConfiguration.get_dependency(*merged_flags)` to select the correct concrete implementation for each service.

## Runtime Role

`ContainerContext` is the sole consumer of the DI domain at runtime. The flow is:

1. **`DIContext`** loads all `ServiceConfiguration` entries from the `services` section of the configuration file via `DIService`.
2. **`build_service_provider()`** iterates each `ServiceConfiguration`, resolving concrete types:
   - If a matching `FlaggedDependency` is found via `get_dependency(*flags)`, its `module_path` and `class_name` are used.
   - Otherwise, the default `module_path` and `class_name` on `ServiceConfiguration` are used.
3. **`get_configuration_type()`** calls `ImportDependency.execute()` to dynamically import the resolved class.
4. The resolved types and their parameters are wired into the DI service provider.
5. Domain events and contexts receive fully constructed service instances via constructor injection.

The injector is cached per flag combination, so repeated calls with the same flags reuse the same container.

Service configurations are defined in the `services` section of the configuration file (typically `config.yml`). Each top-level key maps to a `ServiceConfiguration`:

```yaml
services:
  error_service:
    module_path: tiferet.repos.error
    class_name: ErrorYamlRepository
    params:
      error_yaml_file: config.yml
    deps:
      - flag: sqlite
        module_path: tiferet.repos.error_sqlite
        class_name: ErrorSqliteRepository
        params:
          db_path: app/data/errors.db

  feature_service:
    module_path: tiferet.repos.feature
    class_name: FeatureYamlRepository
    params:
      feature_yaml_file: config.yml
```

Each key under `attrs` becomes the `ServiceConfiguration.id`. The `dependencies` list maps to `FlaggedDependency` entries, enabling environment-specific overrides without changing the feature configuration.

## Domain Events

The following domain events interact with `ServiceConfiguration` and `FlaggedDependency`:

| Event                       | Description                                              |
|-----------------------------|----------------------------------------------------------|
| `ListAllSettings`           | Lists all `ServiceConfiguration` entries.                |
| `AddServiceConfiguration`   | Creates and persists a new `ServiceConfiguration`.        |
| `UpdateServiceConfiguration`| Modifies an existing `ServiceConfiguration` via aggregate.|
| `DeleteServiceConfiguration`| Removes a `ServiceConfiguration` by ID.                   |

These events depend on the `DIService` interface for persistence operations.

## Service Interface

**`DIService`** (`tiferet/interfaces/di.py`) defines the abstract contract for DI configuration persistence:

- `configuration_exists(id: str) -> bool`
- `get_configuration(id: str) -> ServiceConfiguration`
- `list_all() -> Tuple[List[ServiceConfiguration], Dict[str, str]]`
- `save_configuration(service_configuration) -> None`
- `delete_configuration(id: str) -> None`
- `save_constants(constants: Dict[str, Any]) -> None`

Concrete implementations (e.g., `DIYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `AppInterface.flags` provides the primary set of runtime flags used during dependency resolution.
- **Feature:** `Feature.flags` and `FeatureEvent.flags` can override or extend the active flag set for specific workflows.
- **Error:** Error service implementations are resolved through the DI container, making `ServiceConfiguration` entries for `error_service` a common pattern.

## Instantiation

Both domain objects are instantiated directly via the Pydantic constructor:

```python
from tiferet.domain import FlaggedDependency, ServiceConfiguration

dep = FlaggedDependency(
    flag='sqlite',
    module_path='tiferet.repos.error_sqlite',
    class_name='ErrorSqliteRepository',
    parameters={'db_path': 'app/data/errors.db'},
)

config = ServiceConfiguration(
    id='error_service',
    module_path='tiferet.repos.error',
    class_name='ErrorYamlRepository',
    parameters={'error_config_file': 'app/configs/error.yml'},
    dependencies=[dep],
)
```

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns
- [docs/guides/domain/feature.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/feature.md) — Feature domain guide
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
