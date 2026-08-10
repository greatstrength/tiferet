# Domain – DI: ServiceRegistration and FlaggedDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

The DI (Dependency Injection) domain defines the structural configuration for the Tiferet service container. Every injectable service entry is described by a `ServiceRegistration` domain object, which holds a default implementation binding and zero or more `FlaggedDependency` overrides that are selected based on active runtime flags.

These domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing dependencies, setting default types, updating parameters) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/di.py`
**Vision:** See the `ServiceRegistration` class docstring in `tiferet/domain/di.py` for the value statement this guide distills.

## Ubiquitous Language

- **Service registration** — one DI-registry entry: a default implementation binding plus zero or more flag-qualified overrides.
- **Flagged dependency** — one flag-qualified implementation override on a `ServiceRegistration`, selected in place of the default when its `flag` is active.
- **Flag priority order** — the ordinal precedence of the flags passed to `get_dependency`/`get_service_type`/`resolve_service`: the first flag with a matching override wins.
- **Effective service dependency** — the `ServiceDependency` `resolve_service` returns after applying flagged-override-then-default precedence; the single source `get_service_type` imports from.

## Domain Objects

### FlaggedDependency

Extends `ServiceDependency` (`tiferet/domain/core.py`) with the one identity field a bare `ServiceDependency` lacks: the `flag` that selects it.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="flaggeddependency-flag"></a>`flag` | `str` | Yes | — | The flag for the container dependency. |
| <a id="flaggeddependency-module-path"></a>`module_path` | `str` | Yes | — | Inherited from `ServiceDependency`. The module path. |
| <a id="flaggeddependency-class-name"></a>`class_name` | `str` | Yes | — | Inherited from `ServiceDependency`. The class name. |
| <a id="flaggeddependency-parameters"></a>`parameters` | `Dict[str, str]` | No | `{}` | Inherited from `ServiceDependency`. The container dependency parameters. |

No methods beyond the inherited `get_service_type()` (see [docs/guides/domain/core.md](core.md#servicedependency-get-service-type)).

### ServiceRegistration

Represents a single injectable service entry in the DI registry.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="serviceregistration-id"></a>`id` | `str` | Yes | — | The unique identifier for the service registration. |
| <a id="serviceregistration-name"></a>`name` | `str \| None` | No | `None` | The name of the service registration. |
| <a id="serviceregistration-module-path"></a>`module_path` | `str \| None` | No | `None` | The default module path for the dependency class. |
| <a id="serviceregistration-class-name"></a>`class_name` | `str \| None` | No | `None` | The default class name for the dependency class. |
| <a id="serviceregistration-parameters"></a>`parameters` | `Dict[str, str]` | No | `{}` | The default configuration parameters. |
| <a id="serviceregistration-dependencies"></a>`dependencies` | `List[FlaggedDependency]` | No | `[]` | The flag-specific implementation overrides. |

#### Methods

<a id="serviceregistration-get-dependency"></a>
**`get_dependency(*flags) -> FlaggedDependency | None`**

Returns the first `FlaggedDependency` whose `flag` matches any of the provided flags. Flags are evaluated in argument order (ordinal priority), so the first match wins. Returns `None` if no dependency matches.

```python
# Single flag lookup
dep = config.get_dependency('yaml')

# Priority-ordered lookup: prefer 'sqlite' over 'yaml'
dep = config.get_dependency('sqlite', 'yaml')
```

<a id="serviceregistration-resolve-service"></a>
**`resolve_service(*flags) -> ServiceDependency | None`**

Resolves the effective core `ServiceDependency` for the given flags, centralizing the flagged-override → default precedence in one place: prefers a matching `FlaggedDependency` (via `get_dependency`), falls back to the registration's own default `module_path`/`class_name`/`parameters` when both are set, and returns `None` when neither source is defined.

```python
effective = config.resolve_service('sqlite', 'yaml')
```

<a id="serviceregistration-get-service-type"></a>
**`get_service_type(*flags) -> type | None`**

Delegates to `resolve_service` for the effective dependency, then imports and returns its type via `ServiceDependency.get_service_type()`. Returns `None` when no service is defined for the given flags.

```python
service_type = config.get_service_type('sqlite', 'yaml')
```

## Flag Resolution Flow

Flags flow into the DI container from multiple sources:

1. **`AppSession.flags`** — session-level flags set in the configuration's `interfaces` section (e.g., `['yaml']`, `['sqlite', 'yaml']`).
2. **`Feature.flags`** — feature-level flag overrides defined in `feature.yml`.
3. **`EventFeatureStep.flags`** — step-level flag overrides within a feature workflow.

At resolution time, the feature context combines these flag sources and `ServiceResolver` calls `ServiceRegistration.get_service_type(*merged_flags)` (which itself calls `resolve_service(*merged_flags)` and `get_dependency(*merged_flags)` in turn) to select the correct concrete implementation for each service.

## Runtime Role

The DI domain objects participate in the service resolution flow:

1. **`ServiceResolver`** loads all `ServiceRegistration` entries (and constants) from the `services` section of the configuration file via `DIService.list_all()`, merging any bootstrap defaults.
2. **`ServiceResolver.build_type_map()`** iterates each `ServiceRegistration`, resolving concrete types via `get_service_type(*flags)`:
   - If a matching `FlaggedDependency` is found, its `module_path` and `class_name` are used.
   - Otherwise, the default `module_path` and `class_name` on `ServiceRegistration` are used.
3. The resolved type is dynamically imported (via `ImportDependency`) and registered in a per-flag `ServiceContainer`.
4. The resolved types and their parameters are wired into the `ServiceContainer` as `Factory`/`Object` providers.
5. Domain events and contexts receive fully constructed service instances via the resolver's `get_dependency` handler and constructor injection.

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

The following domain events (`tiferet/events/di.py`) interact with `ServiceRegistration` and `FlaggedDependency`:

| Event | Description |
|---|---|
| `AddServiceRegistration` | Creates and persists a new `ServiceRegistration`. |
| `SetDefaultServiceRegistration` | Sets or updates the default `module_path`/`class_name`/`parameters` on an existing registration via `set_default_type`. |
| `SetServiceDependency` | Sets or updates a flagged dependency on an existing registration via `set_dependency`. |
| `RemoveServiceDependency` | Removes a flagged dependency by flag (idempotent) via `remove_dependency`. |
| `RemoveServiceRegistration` | Removes a `ServiceRegistration` by ID (idempotent). |
| `SetServiceConstants` | Sets or clears service-level constants. |
| `ListAllSettings` | Lists all `ServiceRegistration` entries and constants. |

These events depend on the `DIService` interface for persistence operations.

## Service Interface

**`DIService`** (`tiferet/interfaces/di.py`) defines the abstract contract for DI configuration persistence:

- `registration_exists(id: str) -> bool`
- `get_registration(id: str) -> ServiceRegistration`
- `list_all() -> Tuple[List[ServiceRegistration], Dict[str, str]]`
- `save_registration(service_registration) -> None`
- `delete_registration(id: str) -> None`
- `save_constants(constants: Dict[str, Any]) -> None`

Concrete implementations (e.g., `DIConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **Core:** `FlaggedDependency` extends `ServiceDependency` (`docs/guides/domain/core.md`), and `resolve_service` returns a plain `ServiceDependency` rather than a `FlaggedDependency`/`ServiceRegistration`-specific shape.
- **App:** `AppSession.flags` provides the primary set of runtime flags used during dependency resolution.
- **Feature:** `Feature.flags` and `EventFeatureStep.flags` can override or extend the active flag set for specific workflows.
- **Error:** Error service implementations are resolved through the DI container, making `ServiceRegistration` entries for `error_service` a common pattern.

## Boundaries

**Inside this domain:** the declared shape of a DI registry entry (`ServiceRegistration`) and its flag-qualified overrides (`FlaggedDependency`), plus the flagged-override → default precedence logic (`resolve_service`, `get_dependency`, `get_service_type`).
**Outside this domain:** building and caching the actual per-flag `ServiceContainer` (`ServiceResolver`, `docs/guides/di.md`), the concrete `dependency_injector`-backed engine classes (`docs/guides/di/dependency_injector.md`), and mutation of a `ServiceRegistration` (`ServiceRegistrationAggregate` in `mappers`).

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
    class_name='ErrorConfigRepository',
    parameters={'error_config_file': 'app/configs/error.yml'},
    dependencies=[dep],
)
```

## Related Documentation

- [docs/guides/domain/core.md](core.md) — `ServiceDependency`, the base class `FlaggedDependency` extends
- [docs/guides/di.md](../di.md) — the `ServiceResolver`/`ServiceContainer` strategy layer that consumes `ServiceRegistration`
- [docs/guides/di/dependency_injector.md](../di/dependency_injector.md) — the concrete `dependency_injector`-backed engine classes
- [docs/guides/domain/app.md](app.md) — App domain guide (`AppSession.flags`)
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
