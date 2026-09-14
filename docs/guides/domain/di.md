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
dep = registration.get_dependency('yaml')

# Priority-ordered lookup: prefer 'sqlite' over 'yaml'
dep = registration.get_dependency('sqlite', 'yaml')
```

Prefer `resolve_service(*flags)` at a call site that wants the *effective* dependency, since it applies the override-then-default precedence and returns a core `ServiceDependency`. `get_dependency` returns only a matching override, or `None`.

## Flag Resolution Flow

Flags flow into the DI container from multiple sources:

1. **`AppSession.flags`** — session-level flags declared under `sessions.<id>.flags` in the configuration file (e.g., `['yaml']`, `['sqlite', 'yaml']`).
2. **`Feature.flags`** — feature-level flag overrides declared in the `features` section.
3. **`EventFeatureStep.flags`** — step-level flag overrides within a feature workflow.

At resolution time `FeatureContext` combines these flag sources additively and passes them to `get_dependency(service_id, *flags)`; the resolver then calls `ServiceRegistration.resolve_service(*flags)` to select the correct concrete implementation for each service.

## Runtime Role

The DI domain objects are the declarative input the resolution layer reads. There is no `DIContext` — the feature-level resolver is `DIDynamicServiceResolver` (`tiferet/di/dependency_injector.py`), composed by `build_service_resolver` in `tiferet/blueprints/core.py`:

1. **`DIDynamicServiceResolver.build_container(flags)`** reads every `ServiceRegistration` and the top-level constants in one call to `DIService.list_all()`.
2. For each registration it calls **`resolve_service(*flags)`**, which owns the precedence in exactly one place: a matching `FlaggedDependency` first (in flag priority order), then the registration's own default `module_path`/`class_name`, then `None`.
3. A registration resolving to `None` is **skipped** rather than raised on, so it is simply absent from that flag set's container.
4. **`ServiceDependency.get_service_type()`** imports the effective class. (The former `ImportDependency` static event no longer exists.)
5. Resolved types are registered on a `DIDynamicServiceContainer` at `Factory` scope, with constructor kwargs wired to sibling providers by parameter name.
6. Domain events and contexts receive fully constructed service instances via constructor injection. A `service_id` with no provider raises `ServiceError`, not `TiferetError`.

One container is built and cached per distinct flag set by the inherited `ServiceResolver` template method — see [docs/guides/di.md](../di.md).

## Configuration Mapping

Service configurations are defined in the `services` section of the configuration file (typically `config.yml`). Each top-level key maps to a `ServiceRegistration`:

```yaml
services:
  error_service:
    module_path: tiferet.repos.error
    class_name: ErrorConfigRepository
    params:
      error_config: config.yml
    deps:
      - flag: sqlite
        module_path: tiferet.repos.error_sqlite
        class_name: ErrorSqliteRepository
        params:
          db_path: app/data/errors.db

  feature_service:
    module_path: tiferet.repos.feature
    class_name: FeatureConfigRepository
    params:
      feature_config: config.yml
```

## Domain Events

The following domain events interact with `ServiceRegistration` and `FlaggedDependency`:

| Event                            | Description                                                        |
|----------------------------------|--------------------------------------------------------------------|
| `ListAllSettings`                | Lists all `ServiceRegistration` entries and the top-level constants. |
| `AddServiceRegistration`         | Creates and persists a new `ServiceRegistration`.                  |
| `SetDefaultServiceRegistration`  | Sets the registration's default `module_path` / `class_name` / parameters. |
| `RemoveServiceRegistration`      | Removes a `ServiceRegistration` by ID (idempotent).                |
| `SetServiceDependency`           | Adds or updates one `FlaggedDependency` override on a registration. |
| `RemoveServiceDependency`        | Removes a `FlaggedDependency` override by flag (idempotent).       |
| `SetServiceConstants`            | Sets, merges, or clears the top-level DI constants.                |

These events depend on the `DIService` interface for persistence operations. There are no `AddServiceConfiguration` / `UpdateServiceConfiguration` / `DeleteServiceConfiguration` events — the domain concept was renamed to `ServiceRegistration`, and the mutation surface is split into default, dependency, and constant setters rather than a single update.

## Service Interface

**`DIService`** (`tiferet/interfaces/di.py`) defines the abstract contract for DI configuration persistence:

- `registration_exists(id: str) -> bool`
- `get_registration(registration_id: str, flag: str = None) -> ServiceRegistrationAggregate`
- `list_all() -> Tuple[List[ServiceRegistrationAggregate], Dict[str, str]]`
- `save_registration(registration: ServiceRegistrationAggregate) -> None`
- `delete_registration(registration_id: str) -> None`
- `save_constants(constants: Dict[str, Any] = {}) -> None`

Note the return types: the contract is typed with `ServiceRegistrationAggregate`, not the bare domain object, because a caller that retrieves a registration is generally about to mutate and re-save it. This is why `interfaces` may import `mappers` — see [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md).

Concrete implementations (e.g., `DIConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `AppSession.flags` provides the primary set of runtime flags used during dependency resolution.
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

registration = ServiceRegistration(
    id='error_service',
    module_path='tiferet.repos.error',
    class_name='ErrorConfigRepository',
    parameters={'error_config': 'config.yml'},
    dependencies=[dep],
)
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide (AppSession, flags)
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
