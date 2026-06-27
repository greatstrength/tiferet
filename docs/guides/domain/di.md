# Domain – DI: ServiceRegistration and FlaggedDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The DI (Dependency Injection) domain defines the structural configuration for the Tiferet service container. Every injectable service entry is described by a `ServiceRegistration` domain object, which holds a default implementation binding and zero or more `FlaggedDependency` overrides that are selected based on active runtime flags.

These domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing dependencies, setting default types, updating parameters) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/di.py`

### Rename Note: container.py → di.py, ContainerAttribute → ServiceRegistration

In v1.x, dependency injection configuration was defined in `container.py` with the `ContainerAttribute` domain object. In v2.0, the module is renamed to `di.py` and the class to `ServiceRegistration` to better reflect its role in the DI infrastructure. `FlaggedDependency` retains its original name. The field set and semantics are unchanged.

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

### ServiceRegistration

Represents a single injectable service entry in the DI registry.

| Attribute       | Type                                  | Required | Default | Description                                       |
|-----------------|---------------------------------------|----------|---------|---------------------------------------------------|
| `id`            | `str`                                 | Yes      | —       | The unique identifier for the service registration. |
| `name`          | `str \| None`                         | No       | `None`  | The name of the service registration.             |
| `module_path`   | `str \| None`                         | No       | `None`  | The default module path for the dependency class.  |
| `class_name`    | `str \| None`                         | No       | `None`  | The default class name for the dependency class.   |
| `parameters`    | `Dict[str, str]`                      | No       | `{}`    | The default configuration parameters.              |
| `dependencies`  | `List[FlaggedDependency]`             | No       | `[]`    | The flag-specific implementation overrides.        |

#### Methods

**`get_dependency(*flags) -> FlaggedDependency`**

Returns the first `FlaggedDependency` whose `flag` matches any of the provided flags. Flags are evaluated in argument order (ordinal priority), so the first match wins. Returns `None` if no dependency matches.

```python
# Single flag lookup
dep = config.get_dependency('yaml')

# Priority-ordered lookup: prefer 'sqlite' over 'yaml'
dep = config.get_dependency('sqlite', 'yaml')
```

## Flag Resolution Flow

Flags flow into the DI container from multiple sources:

1. **`AppInterface.flags`** — interface-level flags set in `app/configs/app.yml` (e.g., `['yaml']`, `['sqlite', 'yaml']`).
2. **`Feature.flags`** — feature-level flag overrides defined in `feature.yml`.
3. **`EventFeatureStep.flags`** — step-level flag overrides within a feature workflow.

At resolution time, `DIContext` merges these flag sources and calls `ServiceRegistration.get_dependency(*merged_flags)` to select the correct concrete implementation for each service.

## Runtime Role

The DI domain objects participate in the service resolution flow:

1. **`DIContext`** loads all `ServiceRegistration` entries from the `services` section of the configuration file via `DIService`.
2. **`build_service_provider()`** iterates each `ServiceRegistration`, resolving concrete types:
   - If a matching `FlaggedDependency` is found via `get_dependency(*flags)`, its `module_path` and `class_name` are used.
   - Otherwise, the default `module_path` and `class_name` on `ServiceRegistration` are used.
3. **`get_configuration_type()`** calls `ImportDependency.execute()` to dynamically import the resolved class.
4. The resolved types and their parameters are wired into the DI service provider.
5. Domain events and contexts receive fully constructed service instances via constructor injection.

## Configuration Mapping

Service configurations are defined in the `services` section of the configuration file (typically `config.yml`). Each top-level key maps to a `ServiceRegistration`:

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

## Domain Events

The following domain events interact with `ServiceRegistration` and `FlaggedDependency`:

| Event                       | Description                                              |
|-----------------------------|----------------------------------------------------------|
| `ListAllSettings`           | Lists all `ServiceRegistration` entries.                |
| `AddServiceConfiguration`   | Creates and persists a new `ServiceRegistration`.        |
| `UpdateServiceConfiguration`| Modifies an existing `ServiceRegistration` via aggregate.|
| `DeleteServiceConfiguration`| Removes a `ServiceRegistration` by ID.                   |

These events depend on the `DIService` interface for persistence operations.

## Service Interface

**`DIService`** (`tiferet/interfaces/di.py`) defines the abstract contract for DI configuration persistence:

- `registration_exists(id: str) -> bool`
- `get_registration(registration_id: str, flag: str = None) -> ServiceRegistration`
- `list_all() -> Tuple[List[ServiceRegistration], Dict[str, str]]`
- `save_registration(registration) -> None`
- `delete_registration(registration_id: str) -> None`
- `save_constants(constants: Dict[str, Any]) -> None`

Concrete implementations (e.g., `DIYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `AppInterface.flags` provides the primary set of runtime flags used during dependency resolution.
- **Feature:** `Feature.flags` and `EventFeatureStep.flags` can override or extend the active flag set for specific workflows.
- **Error:** Error service implementations are resolved through the DI container, making `ServiceRegistration` entries for `error_service` a common pattern.

## Instantiation

Both domain objects are instantiated directly via the Pydantic constructor:

```python
from tiferet.domain import FlaggedDependency, ServiceRegistration

dep = FlaggedDependency(
    flag='sqlite',
    module_path='tiferet.repos.error_sqlite',
    class_name='ErrorSqliteRepository',
    parameters={'db_path': 'app/data/errors.db'},
)

config = ServiceRegistration(
    id='error_service',
    module_path='tiferet.repos.error',
    class_name='ErrorYamlRepository',
    parameters={'error_config_file': 'app/configs/error.yml'},
    dependencies=[dep],
)
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide (AppInterface, flags)
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
