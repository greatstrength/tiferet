# AGENTS.md — Tiferet Framework (v2.0-proto)

## Project Overview

**Tiferet** is a Python framework for Domain-Driven Design (DDD). It provides a layered architecture for building applications with domain events, service interfaces, configuration-driven feature workflows, and dependency injection. The framework uses YAML-based configuration files and `schematics` for model validation.

- **Repository:** https://github.com/greatstrength/tiferet
- **Branch:** `v2.0-proto` (active development — migration from v1.x)
- **Python:** ≥ 3.10
- **Version:** `2.0.0a0` (alpha, defined in `tiferet/__init__.py`)

## Architecture

### Layer Overview

```
tiferet/
├── assets/          # Constants, exceptions (TiferetError), shared config
├── builders/        # (Reserved, currently empty)
├── contexts/        # Runtime orchestration (AppManager, Feature, Error, CLI, etc.)
├── domain/          # Domain objects (read-only models, schematics-based)
├── events/          # Domain events (business logic units with DI and validation)
├── interfaces/      # Abstract service contracts (ABC-based)
├── mappers/         # Aggregates (mutation) and TransferObjects (serialization)
├── repos/           # Concrete service implementations (YAML-backed repositories)
├── utils/           # File I/O utilities (YAML, JSON, CSV, SQLite)
└── tests_int/       # Integration tests
```

### Key Concepts

- **DomainObject** (`domain/settings.py`): Base class extending `schematics.Model`. Instantiate via `DomainObject.new(Type, **kwargs)`. Domain objects are read-only; mutation goes through Aggregates.
- **DomainEvent** (`events/settings.py`): Base class for business operations. Receives dependencies via constructor injection. Entry point is `execute(**kwargs)`. Use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` for invocation in tests.
- **Service** (`interfaces/settings.py`): Abstract base class (`ABC`) for service contracts. All vertical concerns (data access, config, middleware) are unified under Service.
- **Aggregate** (`mappers/settings.py`): Mutable extension of domain objects. Factory: `Aggregate.new(Type, **kwargs)`. Provides `set_attribute()` for validated mutation.
- **TransferObject** (`mappers/settings.py`): Serialization layer with role-based field control (`allow()`, `deny()`). Methods: `map()`, `from_model()`, `from_data()`.
- **Context** (`contexts/`): Runtime orchestrators. `AppManagerContext` is the entry point (`App` alias). `AppInterfaceContext` handles request→feature→response lifecycle. Low-level contexts: `FeatureContext`, `ErrorContext`, `ContainerContext`, `CacheContext`, `LoggingContext`, `RequestContext`.

### Runtime Flow

1. `App()` (alias for `AppManagerContext`) loads settings.
2. `app.run(interface_id, feature_id, data={})` loads the interface via `AppInterfaceContext`.
3. `FeatureContext.execute_feature()` loads the feature config, resolves commands from the container, and executes them sequentially.
4. Each command is a `DomainEvent` subclass that receives injected services and performs domain logic.
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

- `domain/app.py` — `AppInterface`, `AppAttribute`
- `domain/cli.py` — `CliCommand`, `CliArgument`
- `domain/container.py` — `ContainerAttribute`, `FlaggedDependency`
- `domain/error.py` — `Error`, `ErrorMessage`
- `domain/feature.py` — `Feature`, `FeatureCommand`
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

- `<Domain>Aggregate` (e.g., `FeatureAggregate`, `ErrorAggregate`)
- `<Domain>YamlObject` (e.g., `FeatureYamlObject`, `ErrorYamlObject`)

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

### v2.0-proto Note

Some tests may fail during collection due to the ongoing v1.x → v2.0 migration (e.g., `Command` alias removed from exports). This is expected on this branch.

## Utilities

`tiferet/utils/` provides file I/O wrappers:

- `FileLoader` / `File` — Base file operations (open, close, read, write) with context manager support.
- `YamlLoader` / `Yaml` — YAML read/write via PyYAML.
- `JsonLoader` / `Json` — JSON read/write.
- `CsvLoader` / `Csv` — CSV read/write.
- `CsvDictLoader` / `CsvDict` — CSV with dict reader/writer.
- `SqliteClient` / `Sqlite` — SQLite connection management with context manager.

## Package Exports

The top-level `tiferet/__init__.py` exports:

- `App` (alias for `AppManagerContext`)
- `TiferetError`, `TiferetAPIError`
- `DomainObject` and Schematics type wrappers
- `DomainEvent`, `Command` (alias), `ParseParameter`
- `Service`
- `DataObject` (backward compat alias for mappers)
- File utilities: `File`, `Yaml`, `Json`, `Csv`, `CsvDict`

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

## v2.0 Migration Notes

v2.0 renames and restructures several packages from v1.x:

- `entities/` → `domain/` (`ModelObject` → `DomainObject`)
- `commands/` → `events/` (`Command` → `DomainEvent`)
- `contracts/` → `interfaces/` (artifact comments `# *** contracts` → `# *** interfaces`)
- `data/` → `mappers/` (`DataObject` split into `Aggregate` + `TransferObject`)
- Backward compatibility aliases exist but new code should use the v2.0 names.

## Contributing

See `CONTRIBUTING.md` for the full workflow:

1. Tie work to a GitHub issue.
2. Write a TRD (Technical Requirements Document) for non-trivial changes.
3. Implement following structured code style and component-specific guides in `docs/core/`.
4. Separate functional changes from docs/config in distinct commits.
5. Include `Co-Authored-By:` lines when collaborating with AI agents.
6. Publish a Collaboration Report on the issue upon completion.
