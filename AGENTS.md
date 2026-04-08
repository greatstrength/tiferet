# AGENTS.md — Tiferet Framework (v2.0.0a9)

## Project Overview

**Tiferet** is a Python framework for Domain-Driven Design (DDD). It provides a layered architecture for building applications with domain events, service interfaces, configuration-driven feature workflows, and dependency injection. The framework uses YAML-based configuration files and `schematics` for model validation.

- **Repository:** https://github.com/greatstrength/tiferet
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `2.0.0a9`

## Architecture

### Layer Overview

The v2.0 codebase is a clean, single-layer architecture. All legacy packages have been removed.

```
tiferet/
├── assets/               # Constants, exceptions (TiferetError), shared config
├── builders/             # AppBuilder and top-level runtime orchestration
├── contexts/             # Runtime orchestration (AppInterface, DIContext, Feature, Error, CLI, Logging)
├── di/                   # App-level DI: ServiceProvider, DependenciesServiceProvider
├── domain/               # DomainObject base class and domain modules
├── events/               # DomainEvent base class and domain event modules
├── interfaces/           # Service ABC and domain service interfaces
├── mappers/              # Aggregate + TransferObject base classes and domain mappers
├── repos/                # YAML-backed Service implementations
├── utils/                # Infrastructure utilities (file I/O, database, computational processes)
└── tests_int/            # Integration tests
```

### Key Concepts

**Key Concepts**:

- **DomainObject** (`domain/settings.py`): Base domain model class extending `schematics.Model`. Instantiate via `DomainObject.new(Type, **kwargs)`. Domain objects are read-only; mutation goes through Aggregates.
- **DomainEvent** (`events/settings.py`): Base class for domain operations. Receives dependencies via constructor injection. Entry point is `execute(**kwargs)`. Use `@DomainEvent.parameters_required([...])` for declarative input validation. Use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` for invocation in tests.
- **Service** (`interfaces/settings.py`): Abstract base class (`ABC`) for all service contracts. All vertical concerns (data access, config, utilities) are unified under Service.
- **Aggregate** (`mappers/settings.py`): Mutable extension of domain objects. Factory: `Aggregate.new(Type, **kwargs)`. Provides `set_attribute()` for validated mutation.
- **TransferObject** (`mappers/settings.py`): Serialization layer with role-based field control (`allow()`, `deny()`). Methods: `map()`, `from_model()`, `from_data()`.

### Runtime Flow

1. `App()` (alias for `AppBuilder`) is initialized.
2. `app.load_app_service(...)` loads the app repository service (typically `AppYamlRepository`).
3. `app.run(interface_id, feature_id, data={})` resolves the interface via `GetAppInterface` and builds an `AppInterfaceContext`.
4. `FeatureContext.execute_feature()` loads the feature config, resolves services from `DIContext`, and executes them sequentially.
5. Each step is a `DomainEvent` subclass that receives injected services and performs domain logic.
6. Results flow back through `RequestContext` and `handle_response()`.

### Builders

- `AppBuilder` is defined in `tiferet/builders/main.py`.
- It is the primary public orchestration entry point and is exported as `App` from `tiferet/__init__.py`.
- Core responsibilities:
  - Loading the app service (`load_app_service`)
  - Injecting default services and constants (`load_default_services`, `DEFAULT_CONSTANTS`)
  - Resolving interface contexts (`load_interface`)
  - Delegating feature execution (`run`)

### Dependency Injection

Tiferet uses a two-layer DI architecture:

- **App-level DI** (`tiferet/di/`) — `ServiceProvider` ABC and `DependenciesServiceProvider` concrete implementation. Backs `AppBuilder.load_app_instance()`: assembles the full interface dependency graph (contexts, repos, events) via `AppInterface.get_service_type_mapping()` and resolves `AppInterfaceContext` via `service_provider.get_service('app_context')`.
- **Feature-level DI** (`tiferet/contexts/di.py` — `DIContext`) — Builds and caches a `DependenciesServiceProvider` per flag set from `ServiceConfiguration` objects loaded by `DIYamlRepository`. `FeatureContext` calls `DIContext.get_dependency(service_id, *flags)` to resolve each feature step.

## Structured Code Style

All code follows a strict artifact comment hierarchy. **This is mandatory.**

### Comment Levels

- `# *** <section>` — Top-level: `imports`, `exports`, `models`, `events`, `contexts`, `interfaces`, `mappers`, `repos`, `constants`, `classes`
- `# ** <category>: <name>` — Mid-level: `core`, `infra`, `app` (for imports); `model: <name>`, `event: <name>`, `context: <name>`, etc.
- `# * <component>` — Low-level: `attribute: <name>`, `init`, `method: <name>`, `method: <name> (static)`

### Spacing Rules

- One empty line between `# ***` and first `# **`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets within methods.

### Import Organization

```python
# *** imports

# ** core
from typing import List, Any

# ** infra
from schematics import Model

# ** app
from ..domain import Feature
from ..interfaces import FeatureService
```

### Docstrings

Use RST format with `:param`, `:type`, `:return`, `:rtype` for all public methods.

### Code Snippets

Each logical step within a method is a separate snippet preceded by a 1–2 line comment:

```python
# Retrieve the feature from the service.
feature = self.feature_service.get(id)

# Verify the feature exists.
self.verify(
    expression=feature is not None,
    error_code=a.const.FEATURE_NOT_FOUND_ID,
    feature_id=id,
)

# Return the feature.
return feature
```

## Domain Events

Domain events are the primary operational units. Key patterns:

- Extend `DomainEvent` from `tiferet/events/settings.py`.
- Dependencies via constructor injection (usually a Service).
- `execute(**kwargs)` is the entry point.
- `@DomainEvent.parameters_required(['param1', 'param2'])` for declarative input validation (decorator on `execute`).
- `self.verify(expression, error_code, message, **kwargs)` for domain rule enforcement.
- `self.raise_error(error_code, message, **kwargs)` for direct error raising.
- Return domain models or identifiers.

### Static Events

`ParseParameter`, `ImportDependency`, `RaiseError` in `events/static.py` are utility events called with static `.execute()` methods.

### Testing Events

Always use `DomainEvent.handle()` in tests:

```python
result = DomainEvent.handle(
    GetFeature,
    dependencies={'feature_service': mock_service},
    id='group.feature_key',
)
```

## Domain Objects

- Extend `DomainObject` from `tiferet/domain/settings.py`.
- Use Schematics types: `StringType`, `IntegerType`, `FloatType`, `BooleanType`, `ListType`, `DictType`, `ModelType`.
- Instantiate via `DomainObject.new(Type, **kwargs)`.
- Domain objects are **read-only**; place mutation logic in Aggregates (`mappers/`).

### Domain Modules

- `domain/app.py` — `AppInterface`, `AppServiceDependency`
- `domain/cli.py` — `CliCommand`, `CliArgument`
- `domain/di.py` — `ServiceConfiguration`, `FlaggedDependency`
- `domain/error.py` — `Error`, `ErrorMessage`
- `domain/feature.py` — `Feature`, `FeatureStep`, `FeatureEvent`
- `domain/logging.py` — `Formatter`, `Handler`, `Logger`

## Interfaces (Services)

- Extend `Service` (ABC) from `tiferet/interfaces/settings.py`.
- All methods marked `@abstractmethod`.
- Artifact comments use `# *** interfaces` / `# ** interface: <name>`.
- Services: `AppService`, `CliService`, `ConfigurationService`, `ContainerService`, `ErrorService`, `FeatureService`, `FileService`, `LoggingService`, `SqliteService`, `CacheService`.

## Mappers

Split into two classes:

- **Aggregate** — Extends domain object + `Aggregate`. Adds mutation methods (`rename()`, `add_command()`, `set_attribute()`).
- **TransferObject** — Extends domain object + `TransferObject`. Adds serialization roles via inner `Options` class with `allow()`/`deny()`.

### Naming Convention

- `<Domain>Aggregate` (e.g., `FeatureAggregate`, `ErrorAggregate`, `ServiceConfigurationAggregate`)
- `<Domain>YamlObject` (e.g., `FeatureYamlObject`, `ErrorYamlObject`, `ServiceConfigurationYamlObject`)

## Repositories

Concrete `Service` implementations in `tiferet/repos/`. Currently all YAML-backed. Repositories are **never exported** from `__init__.py` — they are resolved at runtime through DI configuration.

- `AppYamlRepository`, `CliYamlRepository`, `ContainerYamlRepository`
- `DIYamlRepository`, `ErrorYamlRepository`, `FeatureYamlRepository`, `LoggingYamlRepository`

Key patterns:
- Artifact comments use `# *** repos` / `# ** repo: <name>`.
- Three-attribute foundation: `yaml_file`, `encoding`, `default_role`.
- Constructor param convention: `<domain>_yaml_file` (e.g., `error_yaml_file`).
- Reads use `Yaml` utility with `start_node` lambdas; writes use `TransferObject.from_model` → `to_primitive(default_role)` → `Yaml.save`.
- Delete operations are always idempotent.
- Tests are integration tests using `tmp_path` fixtures with real temporary YAML files.

See [docs/core/repos.md](docs/core/repos.md) for structured code design and [docs/guides/repos.md](docs/guides/repos.md) for cross-cutting strategies.

## Error Handling

- `TiferetError` (`assets/exceptions.py`): Base exception with `error_code` and `kwargs`.
- `TiferetAPIError`: Extends `TiferetError` with `name` and `message` for API responses.
- Error constants defined in `assets/constants.py` (e.g., `FEATURE_NOT_FOUND_ID`, `COMMAND_PARAMETER_REQUIRED_ID`).
- Default error definitions in `assets/constants.py::DEFAULT_ERRORS` dict.
- Access constants via `from .. import assets as a` then `a.const.ERROR_CODE_ID`.

## Configuration

Applications are configured in a consolidated root `config.yml` file:

- `interfaces` — Interface definitions (name, module_path, class_name, service dependencies)
- `services` — Feature-level DI service configurations (module_path, class_name, parameters, flagged dependencies)
- `features` — Feature workflows (commands with service_id, parameters, and data mapping)
- `errors` — Error definitions with multilingual messages
- `cli` — CLI command definitions with arguments
- `logging` — Logging formatters, handlers, loggers

## Testing

- **Framework:** `pytest` (with `pytest_env` for environment variables).
- **Test location:** Co-located in `<package>/tests/` directories (e.g., `domain/tests/`, `events/tests/`, `mappers/tests/`).
- **Integration tests:** `tiferet/tests_int/`.
- **Run tests:** `pytest tiferet/` from project root (with venv activated).
- **Test structure:** Uses artifact comments (`# *** fixtures`, `# ** fixture: <name>`, `# *** tests`, `# ** test: <name>`).
- **Mocking:** Use `unittest.mock`. Mock injected services. Verify calls and return values.
- **Event testing:** Always invoke via `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)`.

## Utilities

`tiferet/utils/` provides concrete infrastructure implementations satisfying Service interfaces (`FileService`, `SqliteService`, etc.). Utilities encapsulate repeatable processes — physical (file I/O, database) and computational (algorithms, inference, transformations) — behind injectable, testable contracts.

See [docs/core/utils.md](docs/core/utils.md) for the full design document.

Current utilities:
- `File` / `FileLoader` — Base file I/O implementing `FileService`.
- `Yaml` / `YamlLoader` — YAML read/write via PyYAML.
- `Json` / `JsonLoader` — JSON read/write with path support.
- `Csv` / `CsvLoader` — List-based CSV with helpers.
- `CsvDict` / `CsvDictLoader` — Dict-based CSV.
- `Sqlite` / `SqliteClient` — SQLite client implementing `SqliteService` and `FileService`.

## Package Exports

The top-level `tiferet/__init__.py` exports:

**Core:**
- `App` (alias for `AppBuilder`)
- `TiferetError`, `TiferetAPIError`

**Domain:**
- `DomainObject` and Schematics type wrappers (`StringType`, `IntegerType`, `BooleanType`, `FloatType`, `ListType`, `DictType`, `ModelType`)

**Events:**
- `DomainEvent`, `ParseParameter` (from `tiferet.events`)

**Interfaces:**
- `Service` (from `tiferet.interfaces`)

**Mappers:**
- `Aggregate`, `TransferObject` (from `tiferet.mappers`)

**Utils:**
- `File`/`FileLoader`, `Yaml`/`YamlLoader`, `Json`/`JsonLoader`, `Csv`/`CsvLoader`, `CsvDict`/`CsvDictLoader`, `Sqlite`/`SqliteClient`

## Key Files for Orientation

- `tiferet/__init__.py` — Version and public exports
- `tiferet/di/settings.py` — `ServiceProvider` (ABC) base class
- `tiferet/di/dependencies.py` — `DependenciesServiceProvider` (app-level DI)
- `tiferet/domain/settings.py` — `DomainObject` base class
- `tiferet/events/settings.py` — `DomainEvent` base class (execute, verify, parameters_required, handle)
- `tiferet/mappers/settings.py` — `Aggregate` and `TransferObject` base classes
- `tiferet/interfaces/settings.py` — `Service` (ABC) base class
- `tiferet/di/settings.py` — `ServiceProvider` ABC
- `tiferet/di/dependencies.py` — `DependenciesServiceProvider` (app-level DI)
- `tiferet/builders/main.py` — `AppBuilder` (public app orchestration entry point)
- `tiferet/contexts/app.py` — `AppInterfaceContext`
- `tiferet/contexts/di.py` — `DIContext` (feature-level DI)
- `tiferet/contexts/feature.py` — `FeatureContext` (feature execution engine)
- `tiferet/assets/constants.py` — Error codes and `DEFAULT_SERVICES` configuration
- `tiferet/assets/exceptions.py` — `TiferetError` and `TiferetAPIError`

## Contributing

See `CONTRIBUTING.md` for the full workflow:

1. Tie work to a GitHub issue.
2. Write a TRD (Technical Requirements Document) for non-trivial changes.
3. Implement following structured code style and component-specific guides in `docs/core/`.
4. Separate functional changes from docs/config in distinct commits.
5. Include `Co-Authored-By:` lines when collaborating with AI agents.
6. Publish a Collaboration Report on the issue upon completion.
