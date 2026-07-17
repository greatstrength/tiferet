# Migration Guide: v1 to v2

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

This document is the single authoritative reference for every breaking change, rename, and removed API that occurred between Tiferet v1.x and the stable v2.0 release. All other documentation in this repository describes v2 conventions exclusively. Consult this guide only when porting existing v1 code or when encountering unfamiliar terminology in pre-v2 configuration files or source.

---

## Domain Layer

### Model library: Schematics → Pydantic v2

v1 domain objects extended `schematics.Model` and used type descriptors as field declarations.
v2 domain objects extend `pydantic.BaseModel` (via the shared `DomainObject` base) and use standard Python type annotations with `pydantic.Field(...)`.

**v1 field declaration style:**
```python
from schematics.types import StringType, IntegerType, ListType
from tiferet import ModelObject

class Feature(ModelObject):
    id = StringType(required=True)
    name = StringType(required=True)
    commands = ListType(StringType())
```

**v2 field declaration style:**
```python
from pydantic import Field
from tiferet import DomainObject

class Feature(DomainObject):
    id: str = Field(..., description='The feature identifier.')
    name: str = Field(..., description='The feature name.')
    steps: list = Field(default_factory=list)
```

Schematics type wrappers that were previously re-exported from `tiferet` (`StringType`, `IntegerType`, `FloatType`, `BooleanType`, `ListType`, `DictType`, `ModelType`) are no longer exported or used.

### `DomainObject.new()` static factory removed

v1 domain objects were instantiated with the static factory `DomainObject.new(Type, **kwargs)`.
v2 uses the direct Pydantic constructor.

```python
# v1
feature = DomainObject.new(Feature, id='calc.add', name='Add')

# v2
feature = Feature(id='calc.add', name='Add')
```

For external/untrusted data, use `model_validate(data_dict)`. For derivation logic that was previously in custom `new()` methods, use `@model_validator(mode='before')`.

### Package rename: `tiferet/entities/` → `tiferet/domain/`

The domain model package was renamed from `entities` to `domain`. The base class `ModelObject` was renamed to `DomainObject` and the base module from `settings.py` to `core.py`.

```python
# v1
from tiferet.entities.settings import ModelObject

# v2
from tiferet.domain.core import DomainObject
# or, via the public export:
from tiferet import DomainObject
```

### `domain/settings.py` → `domain/core.py`

The main domain base module was renamed from `settings.py` to `core.py`. It also gained the shared `ServiceDependency` core model. All other module names (`app.py`, `cli.py`, `di.py`, etc.) are unchanged.

---

## Interfaces / Contracts Layer

### Package rename: `tiferet/contracts/` → `tiferet/interfaces/`

The service interface package was renamed from `contracts` to `interfaces`, and the artifact comments updated to match.

```python
# v1
from tiferet.contracts.error import ErrorService

# v2
from tiferet.interfaces.error import ErrorService
# or, via the public export:
from tiferet.interfaces import ErrorService
```

Artifact comment updates in source files:
- `# *** contracts` → `# *** interfaces`
- `# ** contract: <name>` → `# ** interface: <name>`

The `tiferet/contracts/` package was retained during the transition period for backward compatibility but should no longer be used.

---

## Mapper Layer

### `*YamlObject` → `*ConfigObject`

All `TransferObject` subclasses were renamed from the `*YamlObject` suffix to `*ConfigObject` to reflect that repositories can now load from both YAML and JSON.

| v1 Name | v2 Name |
|---|---|
| `AppInterfaceYamlObject` | `AppInterfaceConfigObject` |
| `CliCommandYamlObject` | `CliCommandConfigObject` |
| `ServiceConfigurationYamlObject` | `ServiceRegistrationConfigObject` |
| `ErrorYamlObject` | `ErrorConfigObject` |
| `FeatureYamlObject` | `FeatureConfigObject` |
| `FeatureEventYamlObject` | `EventFeatureStepConfigObject` |
| `LoggingSettingsYamlObject` | `LoggingSettingsConfigObject` |

Artifact comments updated from `# ** mapper: *_yaml_object` to `# ** mapper: *_config_object`. The role key `'to_data.yaml'` was consolidated to `'to_data'` and the `'to_data.json'` role was removed; all repositories use `default_role = 'to_data'`.

### `Aggregate.new()` factory removed

v1 aggregates were created with `Aggregate.new(Type, **kwargs)`. v2 uses the direct Pydantic constructor identically to domain objects.

```python
# v1
feature = Aggregate.new(FeatureAggregate, id='calc.add', name='Add')

# v2
feature = FeatureAggregate(id='calc.add', name='Add')
```

### `TransferObject` API changes

| v1 API | v2 equivalent |
|---|---|
| `TransferObject.from_data(Type, **kwargs)` | `Type.model_validate(data_dict)` |
| `class Options: allow/deny` | `_ROLES: ClassVar[Dict]` with `model_dump` kwargs |
| `to_primitive(role)` | `to_primitive(role)` (same name, now delegates to `model_dump`) |
| `allow()` / `deny()` | `_ROLES` include/exclude dicts |
| `serialize_when_none` | `exclude_none=True` in `_ROLES` or `to_primitive` |
| `serialized_name` | `serialization_alias` |
| `deserialize_from` | `validation_alias=AliasChoices(...)` |

---

## Dependency Injection Layer

### DI library: `dependencies` → `dependency-injector`

v1 used the `dependencies` library (`dependencies.Injector`) as the DI backend.
v2 uses the `dependency-injector` library (`dependency_injector.containers.DynamicContainer`).

```toml
# v1 pyproject.toml
dependencies = ">=7.7.0"

# v2 pyproject.toml
dependency-injector = ">=4.49.0"
```

### `ServiceProvider` / `DynamicServiceProvider` / `DependenciesServiceProvider` removed

The v1 `ServiceProvider` ABC, `DynamicServiceProvider` concrete class, and the `DependenciesServiceProvider` backward-compatibility alias have all been removed. The low-level engine is now `ServiceContainer` and the application's public provider is `ServiceResolver` (both in `tiferet/di/settings.py`), with abstract contracts in `tiferet/di/core.py` and `dependency-injector`-backed implementations in `tiferet/di/dependency_injector.py`.

```python
# v1
from tiferet.di import ServiceProvider, DynamicServiceProvider

# v2 — contexts consume an injected get_dependency callable; never hold a provider directly
# Tests inject: get_dependency=mock.Mock()
```

### `DIContext` removed

The feature-level `DIContext` (`tiferet/contexts/di.py`) that previously built a `DependenciesServiceProvider` per flag set has been removed. Service resolution is now handled by the `ServiceResolver` whose bound `get_dependency(registration_id, *flags)` method is injected into `AppInterfaceContext` and forwarded to each `FeatureContext`.

### `create_service_provider` blueprint factory removed

The `create_service_provider` function that was registered in the blueprint's dependency registry has been removed. Interface wiring on the standard path now uses the core composition functions (`build_app_service_container`, `build_service_resolver`) in `tiferet/blueprints/core.py`.

---

## Repositories Layer

### `*YamlRepository` → `*ConfigRepository`

All repository classes were renamed from the `*YamlRepository` suffix to `*ConfigRepository`. A new `ConfigurationRepository` base class in `tiferet/repos/settings.py` dispatches reads and writes to `YamlLoader` or `JsonLoader` based on the configuration file extension, making format selection automatic.

| v1 Name | v2 Name |
|---|---|
| `AppYamlRepository` | `AppConfigRepository` |
| `CliYamlRepository` | `CliConfigRepository` |
| `DIYamlRepository` | `DIConfigRepository` |
| `ErrorYamlRepository` | `ErrorConfigRepository` |
| `FeatureYamlRepository` | `FeatureConfigRepository` |
| `LoggingYamlRepository` | `LoggingConfigRepository` |

### Constructor parameter rename: `*_yaml_file` → `*_config`

Each repository's constructor parameter was renamed to match the new `*ConfigRepository` naming. The `DEFAULT_CONSTANTS` keys in `assets/blueprints.py` were updated to match.

```python
# v1 DI registration
error_yaml_file: app/configs/error.yml

# v2 DI registration
error_config: app/configs/error.yml
```

---

## Blueprints Layer

### Builders removed: `AppBuilder` / `CliBuilder` → `build_app` / `build_cli`

The class-based builder pattern was replaced with module-level functions.

```python
# v1 (AppBuilder)
from tiferet import App
app = App()
app.load_app_service(app_yaml_file='config.yml')
result = app.run('basic_calc', 'calc.add', data={'a': 1, 'b': 2})

# v2 (build_app function, exported as App)
from tiferet import App
app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 1, 'b': 2})
```

### `tiferet/blueprints/main.py` retired

The `main.py` blueprint module was retired in the Chapter M cleanup. Its public entry point (`build_app`) and composition helpers (`build_cache`, `get_app_session`, `build_app_session_context`, `build_app_service_container`, `build_service_resolver`) moved to `tiferet/blueprints/core.py`. The legacy declarative feature-DI bootstrap (`wire_services`, `load_app_instance`, `_resolve_bootstrap_session`, and related helpers), which only the built-in `tiferet_cli` session still uses, was relocated module-private to `tiferet/blueprints/tiferet_cli.py`.

```python
# v1 import
from tiferet.blueprints.main import build_app

# v2 import
from tiferet.blueprints.core import build_app
# or via the top-level alias:
from tiferet import App
```

---

## Domain Objects: Specific Renames

### `AppAttribute` → `AppServiceDependency`

The class representing a single injectable service dependency binding for an application interface was renamed from `AppAttribute` to `AppServiceDependency`. The field `attribute_id` is retained for backward-compatibility lookup but is superseded by `service_id`.

### `ContainerAttribute` / `ContainerService` → `ServiceRegistration` / `DIService`

The dependency injection domain object and its service interface were renamed to better reflect their role.

| v1 Name | v2 Name |
|---|---|
| `ContainerAttribute` | `ServiceRegistration` |
| `ContainerService` | `DIService` |
| `attribute_exists()` | `registration_exists()` |
| `get_attribute()` | `get_registration()` |
| `save_attribute()` | `save_registration()` |
| `delete_attribute()` | `delete_registration()` |
| `ATTRIBUTE_ALREADY_EXISTS` | `SERVICE_REGISTRATION_ALREADY_EXISTS` |
| `tiferet/domain/container.py` | `tiferet/domain/di.py` |

The v1 container events in `tiferet/events/container.py` were superseded by the DI events in `tiferet/events/di.py`.

### `FeatureCommand` → `FeatureEvent` → `EventFeatureStep`

The concrete step domain object for a feature workflow underwent two renames:
- v1: `FeatureCommand` (aligned with the v1 `Command` abstraction)
- v2.0 early: `FeatureEvent` (aligned with the v2 `DomainEvent` abstraction)
- v2.0 stable: `EventFeatureStep` (frees `FeatureEvent` for the per-module base domain event)

The field set and semantics are unchanged across all three names. v2 stable code uses `EventFeatureStep` exclusively.

---

## Configuration Structure

### Unified `config.yml`

v1 used separate per-domain configuration files: `app.yml`, `di.yml`, `feature.yml`, `error.yml`, `cli.yml`, `logging.yml`.
v2 consolidates all configuration into a single root `config.yml` with top-level sections: `interfaces`, `services`, `features`, `errors`, `cli`, `logging`. Per-file configs are still supported (the section key and format are unchanged); only the default recommended layout changed.

### Default service merging moved out of `GetAppInterface`

In early v2 releases `GetAppInterface` accepted `default_services` / `default_constants` parameters and merged framework defaults into the loaded interface. In v2.0 stable this merge responsibility was moved:
- `AppInterface.apply_defaults(default_services, default_constants)` — non-mutating domain method for merging defaults into an `AppInterface` (used only by the built-in bootstrapper path).
- `build_app_service_container(cache, app_session)` — blueprint function that merges cache-seeded framework defaults with the session's own services and constants before constructing the app-level service container.
- `GetAppInterface` is now a repo-only read with no default-merging parameters.

---

## See Also

- [docs/core/domain.md](../core/domain.md) — current `DomainObject` conventions
- [docs/core/di.md](../core/di.md) — current DI layer architecture
- [docs/core/interfaces.md](../core/interfaces.md) — current service interface conventions
- [docs/core/mappers.md](../core/mappers.md) — current Aggregate and TransferObject conventions
- [docs/core/blueprints.md](../core/blueprints.md) — current blueprint design
- [docs/core/repos.md](../core/repos.md) — current repository conventions
