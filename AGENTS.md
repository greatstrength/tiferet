# AGENTS.md — Tiferet Framework (v1.9.x)

## Project Overview

**Tiferet** is a Python framework for Domain-Driven Design (DDD). It provides a layered architecture for building applications with domain events, service interfaces, configuration-driven feature workflows, and dependency injection. The framework uses YAML-based configuration files and `schematics` for model validation.

- **Repository:** https://github.com/greatstrength/tiferet
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `1.9.x`

## Architecture

### Layer Overview

The codebase maintains a **dual-package structure**: legacy packages from v1.x coexist alongside forward-compatible packages that introduce the v2.0 naming and design. Both are fully supported; new code should prefer the forward-compatible packages.

```
tiferet/
├── assets/               # Constants, exceptions (TiferetError), shared config
├── commands/             # Legacy: Command base class
├── contexts/             # Runtime orchestration (AppManager, Feature, Error, CLI, etc.)
├── contracts/            # Legacy: Service/Repository contracts
├── data/                 # Legacy: DataObject
├── domain/               # Forward: DomainObject
├── events/               # Forward: DomainEvent
├── handlers/             # Handler implementations
├── interfaces/           # Forward: Service ABC
├── mappers/              # Forward: Aggregate + TransferObject
├── middleware/           # File I/O middleware (deprecated — use utils/)
├── models/               # Legacy: ModelObject
├── proxies/              # YAML/JSON/CSV proxies
├── repos/                # Repository implementations
├── utils/                # Infrastructure utilities (file I/O, database, computational processes)
└── tests_int/            # Integration tests
```

### Key Concepts

**Legacy packages** (fully supported, carried from v1.x):

- **ModelObject** (`models/settings.py`): Base domain model class extending `schematics.Model`. Instantiate via `ModelObject.new(Type, **kwargs)`.
- **Command** (`commands/settings.py`): Base class for business operations with dependency injection and `execute(**kwargs)` entry point.
- **DataObject** (`data/settings.py`): Combined data mapping/serialization class with `new()`, `map()`, `from_model()`, `from_data()`, `allow()`, `deny()`.
- **Repository** / **Service** / **ModelContract** (`contracts/`): Abstract base classes for service and repository contracts.

**Forward-compatible packages** (new in v1.9.x, aligned with v2.0 design):

- **DomainObject** (`domain/settings.py`): Drop-in successor to `ModelObject`. Base class extending `schematics.Model`. Instantiate via `DomainObject.new(Type, **kwargs)`. Domain objects are read-only; mutation goes through Aggregates.
- **DomainEvent** (`events/settings.py`): Successor to `Command`. Receives dependencies via constructor injection. Entry point is `execute(**kwargs)`. Use `@DomainEvent.parameters_required([...])` for declarative input validation. Use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` for invocation in tests.
- **Service** (`interfaces/settings.py`): Abstract base class (`ABC`) for service contracts. Successor to `contracts/` service interfaces. All vertical concerns (data access, config, middleware) are unified under Service.
- **Aggregate** (`mappers/settings.py`): Mutable extension of domain objects. Successor to the mutation side of `DataObject`. Factory: `Aggregate.new(Type, **kwargs)`. Provides `set_attribute()` for validated mutation.
- **TransferObject** (`mappers/settings.py`): Serialization layer with role-based field control (`allow()`, `deny()`). Successor to the serialization side of `DataObject`. Methods: `map()`, `from_model()`, `from_data()`.

### Runtime Flow

1. `App()` (alias for `AppManagerContext`) loads settings.
2. `app.run(interface_id, feature_id, data={})` loads the interface via `AppInterfaceContext`.
3. `FeatureContext.execute_feature()` loads the feature config, resolves commands from the container, and executes them sequentially.
4. Each command is a `DomainEvent` (or legacy `Command`) subclass that receives injected services and performs domain logic.
5. Results flow back through `RequestContext` and `handle_response()`.

### Dependency Injection

Tiferet uses the `dependencies` library for runtime DI. Injectors are created per app interface in `AppManagerContext.load_app_instance()`. Container attributes are defined in `app/configs/container.yml` and resolved via `ContainerContext`.

## Structured Code Style

All code follows a strict artifact comment hierarchy. **This is mandatory.**

### Comment Levels

- `# *** <section>` — Top-level: `imports`, `exports`, `models`, `events`, `contexts`, `interfaces`, `mappers`, `constants`, `classes`
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

Concrete `Service` implementations in `tiferet/repos/`. Currently all YAML-backed:

- `AppYamlRepository`, `CliYamlRepository`, `ContainerYamlRepository`
- `ErrorYamlRepository`, `FeatureYamlRepository`, `LoggingYamlRepository`

## Error Handling

- `TiferetError` (`assets/exceptions.py`): Base exception with `error_code` and `kwargs`.
- `TiferetAPIError`: Extends `TiferetError` with `name` and `message` for API responses.
- Error constants defined in `assets/constants.py` (e.g., `FEATURE_NOT_FOUND_ID`, `COMMAND_PARAMETER_REQUIRED_ID`).
- Default error definitions in `assets/constants.py::DEFAULT_ERRORS` dict.
- Access constants via `from .. import assets as a` then `a.const.ERROR_CODE_ID`.

## Configuration

Applications are configured via YAML files in `app/configs/`:

- `app.yml` — Interface definitions (name, module_path, class_name, attributes)
- `container.yml` — Dependency injection container attributes (module_path, class_name, parameters)
- `feature.yml` — Feature workflows (commands with attribute_id, parameters, data_key)
- `error.yml` — Error definitions with multilingual messages
- `cli.yml` — CLI command definitions with arguments
- `logging.yml` — Logging formatters, handlers, loggers

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
- `App` (alias for `AppManagerContext`)
- `TiferetError`, `TiferetAPIError`

**Legacy:**
- `ModelObject` and Schematics type wrappers (`StringType`, `IntegerType`, `BooleanType`, `FloatType`, `ListType`, `DictType`, `ModelType`)
- `Command`, `ParseParameter` (from `commands/`)
- `ModelContract`, `Repository`, `Service` (from `contracts/`)
- `DataObject` (from `data/`)

**Proxies and Middleware:**
- `YamlFileProxy`, `JsonFileProxy`, `CsvFileProxy` (from `proxies/`)
- `File`, `FileLoaderMiddleware`, `Yaml`, `YamlLoaderMiddleware`, `Json`, `JsonLoaderMiddleware`, `Csv`, `CsvLoaderMiddleware`, `CsvDict`, `CsvDictLoaderMiddleware` (from `middleware/`)

**Forward-compatible** (available via their respective packages):
- `DomainObject` (from `tiferet.domain`)
- `DomainEvent`, `ParseParameter`, `ImportDependency`, `RaiseError` (from `tiferet.events`)
- `Service` (from `tiferet.interfaces`)
- `Aggregate`, `TransferObject` (from `tiferet.mappers`)

## Forward-Compatible Packages

The following forward-compatible packages are successors to legacy packages. New code should prefer these packages. Legacy packages remain fully supported.

- **`tiferet/domain/`** → `DomainObject` — drop-in successor to `ModelObject` (`models/`). Same API, new name.
- **`tiferet/events/`** → `DomainEvent` — successor to `Command` (`commands/`). Adds `@parameters_required` decorator and `DomainEvent.handle()` for testing.
- **`tiferet/interfaces/`** → `Service` (ABC) — successor to `contracts/` service interfaces. Cleaner abstract base with `@abstractmethod`.
- **`tiferet/mappers/`** → `Aggregate` + `TransferObject` — successor to `DataObject` (`data/`). Splits mutation (Aggregate) from serialization (TransferObject) for cleaner separation of concerns.

## Key Files for Orientation

- `tiferet/__init__.py` — Version and public exports
- `tiferet/domain/settings.py` — `DomainObject` base class
- `tiferet/events/settings.py` — `DomainEvent` base class (execute, verify, parameters_required, handle)
- `tiferet/mappers/settings.py` — `Aggregate` and `TransferObject` base classes
- `tiferet/interfaces/settings.py` — `Service` (ABC) base class
- `tiferet/contexts/app.py` — `AppManagerContext` and `AppInterfaceContext`
- `tiferet/contexts/feature.py` — `FeatureContext` (feature execution engine)
- `tiferet/assets/constants.py` — Error codes and default configuration
- `tiferet/assets/exceptions.py` — `TiferetError` and `TiferetAPIError`

## Contributing

See `CONTRIBUTING.md` for the full workflow:

1. Tie work to a GitHub issue.
2. Write a TRD (Technical Requirements Document) for non-trivial changes.
3. Implement following structured code style and component-specific guides in `docs/core/`.
4. Separate functional changes from docs/config in distinct commits.
5. Include `Co-Authored-By:` lines when collaborating with AI agents.
6. Publish a Collaboration Report on the issue upon completion.
