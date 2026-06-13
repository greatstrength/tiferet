# AGENTS.md — Tiferet Framework (v2.0.0)

## Project Overview

**Tiferet** is a Python framework for Domain-Driven Design (DDD). It provides a layered architecture for building applications with domain events, service interfaces, configuration-driven feature workflows, and dependency injection. The framework uses YAML or JSON configuration files and Pydantic v2 for model validation.

- **Repository:** https://github.com/greatstrength/tiferet
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `2.0.0`

## Architecture

### Layer Overview

The v2.0 codebase is a clean, single-layer architecture. All legacy packages have been removed.

```
tiferet/
├── assets/               # Constants, exceptions (TiferetError), shared config
├── blueprints/           # build_app, build_cli and top-level runtime orchestration
├── contexts/             # Runtime orchestration: BaseContext registry + AppInterfaceContext hub (DIContext, Feature, Error, Logging)
├── di/                   # App-level DI: ServiceProvider, DynamicServiceProvider
├── domain/               # DomainObject base class and domain modules
├── events/               # DomainEvent base class and domain event modules
├── interfaces/           # Service ABC and domain service interfaces
├── mappers/              # Aggregate + TransferObject base classes and domain mappers
├── repos/                # Configuration-backed Service implementations (YAML/JSON)
├── utils/                # Infrastructure utilities (file I/O, database, computational processes)
└── tests_int/            # Integration tests
```

A working calculator application is provided in `examples/basic_calculator/`.

### Key Concepts

**Key Concepts**:

- **DomainObject** (`domain/settings.py`): Base domain model class extending `pydantic.BaseModel`. Instantiate via direct Pydantic constructors (e.g., `Feature(id='calc.add', ...)`). Use `model_construct()` to skip validation. Domain objects are read-only; mutation goes through Aggregates.
- **DomainEvent** (`events/settings.py`): Base class for domain operations. Receives dependencies via constructor injection. Entry point is `execute(**kwargs)`. Use `@DomainEvent.parameters_required([...])` for declarative input validation. Use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` for invocation in tests.
- **Service** (`interfaces/settings.py`): Abstract base class (`ABC`) for all service contracts. All vertical concerns (data access, config, utilities) are unified under Service.
- **MiddlewareService** (`interfaces/middleware.py`): Abstract callable that wraps domain event execution. Implement `__call__(self, event, kwargs, next_fn)` for sync middleware or `async def __call__` for async. Resolved from the DI container by `service_id` and composed into an ordered chain by `FeatureContext`.
- **Aggregate** (`mappers/settings.py`): Mutable extension of domain objects. Instantiate via direct constructors. Provides `set_attribute()` for validated mutation with `validate_assignment=True`.
- **TransferObject** (`mappers/settings.py`): Serialization layer with role-based field control via `_ROLES` ClassVar. Methods: `to_primitive(role)`, `map(target)`, `@classmethod from_model()`. Uses lenient config (`extra='ignore'`).
- **BaseContext** (`contexts/base.py`): Base class for all contexts, with a `ContextMeta` metaclass registry keyed by `domain_type`. `BaseContext.for_domain(DomainType)` resolves the registered context class; `BaseContext.from_domain(domain_obj, **kwargs)` constructs a context and binds the domain object as `ctx.domain`. The `AppInterfaceContext` hub binds the loaded `AppInterface` and builds its sub-contexts on demand.

### Runtime Flow

1. `App(interface_id)` (alias for `build_app`) resolves the interface and returns an `AppInterfaceContext`.
2. The blueprint loads the app service (typically `AppConfigRepository`), resolves the interface via `GetAppInterface`, resolves the context's event/repo collaborators by name from the DI container, and constructs the `AppInterfaceContext` declaratively via `BaseContext.from_domain(app_interface, ...)` — the context graph itself is not DI-resolved.
3. `AppInterfaceContext.run(feature_id, data={})` builds a logger, parses the request, loads the `Feature` domain object, executes it, and returns the response.
4. The hub builds its sub-contexts (`DIContext`, `FeatureContext`, `ErrorContext`, `LoggingContext`) on demand; `FeatureContext.execute_feature(feature, request)` resolves each step's service from `DIContext` and executes it sequentially.
5. Each step is a `DomainEvent` subclass that receives injected services and performs domain logic.
6. Results flow back through `RequestContext` and `handle_response()`.

### Blueprints

Blueprints (`tiferet/blueprints/`) are module-level functions that orchestrate application bootstrapping and execution. They replace the previous class-based `AppBuilder`/`CliBuilder` pattern from v2.0.0b2.

- `build_app(interface_id, ...)` is defined in `tiferet/blueprints/main.py` and exported as `App` from `tiferet/__init__.py`. It resolves the interface definition, builds the DI container, and returns a fully wired `AppInterfaceContext`.
- `build_cli(interface_id, ...)` is defined in `tiferet/blueprints/cli.py` and exported as `CLI` from `tiferet/__init__.py`. It extends the app blueprint with argparse-based CLI parsing.

**Key blueprint functions in `main.py`:**
- `create_service_provider(provider_type, type_map, **constants)` — Creates and configures a `ServiceProvider` instance.
- `load_app_service(module_path, class_name, **parameters)` — Imports and constructs the application service.
- `load_default_services()` — Loads default app service dependencies from `assets.blueprints`.
- `resolve_interface(interface_id, ...)` — Loads the app service and resolves the interface definition via `GetAppInterface`.
- `realize_interface(app_interface, interface_id, service_provider, **context_kwargs)` — Declaratively builds and validates the concrete `AppInterfaceContext` from the loaded interface; forwards `**context_kwargs` (e.g. bootstrap defaults) to the context constructor.
- `build_app(interface_id, ...)` — Resolves and realizes the interface in a single call.

**CLI blueprint functions in `cli.py`:**
- `get_commands(service_provider)` — Resolves and groups `CliCommand` objects by `group_key`.
- `get_parent_arguments(service_provider)` — Resolves parent-level CLI arguments.
- `build_parser(cli_commands, parent_arguments)` — Composes the root `argparse.ArgumentParser`.
- `parse_argv(parser, argv)` — Parses CLI arguments; exits 2 on failure.
- `derive_feature_request(parsed)` — Derives `feature_id` and `headers` from parsed arguments.
- `build_app(interface_id, argv, ...)` — Full CLI build: resolve interface, build parser, parse argv, dispatch feature. Exits 1 on `TiferetAPIError`.

CLI interfaces resolve to the default `AppInterfaceContext`; `CliContext` has been retired.

### Dependency Injection

Tiferet uses a two-layer DI architecture:

- **App-level DI** (`tiferet/di/`) — `ServiceProvider` ABC and `DynamicServiceProvider` concrete implementation backed by `dependency-injector`'s `DynamicContainer`. The provider resolves the interface's events and repositories (via `AppInterface.get_service_type_mapping()`); `load_app_instance` then resolves those named collaborators and constructs the `AppInterfaceContext` declaratively (the hub is no longer resolved from the container).
- **Feature-level DI** (`tiferet/contexts/di.py` — `DIContext`) — Builds and caches a `DynamicServiceProvider` per flag set from `ServiceConfiguration` objects loaded by `DIConfigRepository`. `FeatureContext` calls `DIContext.get_dependency(service_id, *flags)` to resolve each feature step.

`DynamicServiceProvider.build_factory(service_type)` is a public method that builds a `Factory` provider with constructor kwargs wired to sibling providers. It inspects the constructor signature to identify injectable parameters and maps them to registered sibling providers.

## Structured Code Style

All code follows a strict artifact comment hierarchy. **This is mandatory.**

### Comment Levels

- `# *** <section>` — Top-level: `imports`, `exports`, `models`, `events`, `contexts`, `interfaces`, `mappers`, `repos`, `constants`, `classes`, `blueprints`
- `# ** <category>: <name>` — Mid-level: `core`, `infra`, `app` (for imports); `model: <name>`, `event: <name>`, `context: <name>`, `blueprint: <name>`, etc.
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
from pydantic import BaseModel, Field, model_validator

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
- `DomainObject` extends `pydantic.BaseModel` with `ConfigDict(extra='forbid', populate_by_name=True, validate_assignment=True)`.
- Declare fields with idiomatic Pydantic annotations: `name: str = Field(...)`.
- Instantiate via direct constructors: `Error(id='invalid_input', name='Invalid Input')`.
- Use `model_construct()` to skip validation where needed.
- Use `@model_validator(mode='before')` for custom factory/derivation logic (replaces the old `DomainObject.new()` / custom `new()` factories).
- Use `model_validate(data)` to construct from dicts with validation.
- Use `model_dump()` to serialize to dicts.
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
- Services: `AppService`, `CliService`, `ConfigurationService`, `ContainerService`, `ErrorService`, `FeatureService`, `FileService`, `LoggingService`, `SqliteService`, `CacheService`, `MiddlewareService`.

## Mappers

Split into two classes:

- **Aggregate** — Extends domain object + `Aggregate`. Adds mutation methods (`rename()`, `add_command()`, `set_attribute()`). Inherits `validate_assignment=True` from `DomainObject`, so direct `setattr` triggers Pydantic field validation. `set_attribute()` checks `model_fields` for existence before assignment.
- **TransferObject** — Extends domain object + `TransferObject`. Uses lenient config (`extra='ignore'`, `validate_assignment=False`). Role-based serialization via `_ROLES` ClassVar mapping role names to `model_dump` kwargs. Methods: `to_primitive(role)`, `map(target)`, `@classmethod from_model(model)`.

### Naming Convention

- `<Domain>Aggregate` (e.g., `FeatureAggregate`, `ErrorAggregate`, `ServiceConfigurationAggregate`)
- `<Domain>YamlObject` (e.g., `FeatureYamlObject`, `ErrorYamlObject`, `ServiceConfigurationYamlObject`)

## Repositories

Concrete `Service` implementations in `tiferet/repos/`. All configuration repositories extend `ConfigurationRepository` (`repos/settings.py`), which provides format-agnostic I/O via `_load()` / `_save()` with automatic dispatch to YAML or JSON based on file extension. Repositories are **never exported** from `__init__.py` — they are resolved at runtime through DI configuration.

- `AppConfigRepository`, `CliConfigRepository`
- `DIConfigRepository`, `ErrorConfigRepository`, `FeatureConfigRepository`, `LoggingConfigRepository`

Key patterns:
- Artifact comments use `# *** repos` / `# ** repo: <name>`.
- All repos extend `ConfigurationRepository` which provides: `config_file`, `encoding`, `default_role` (set to `'to_data'`).
- Constructor param convention: `<domain>_config` (e.g., `error_config`, `app_config`).
- Reads use `self._load(start_node=..., data_factory=...)` and `model_validate` to construct TransferObjects; writes use `TransferObject.from_model` → `to_primitive(self.default_role)` → `self._save(data=...)`.
- Delete operations are always idempotent.
- Tests are integration tests using `tmp_path` fixtures with real temporary YAML files.

See [docs/core/repos.md](docs/core/repos.md) for structured code design and [docs/guides/repos.md](docs/guides/repos.md) for cross-cutting strategies.

## Error Handling

- `TiferetError` (`assets/exceptions.py`): Base exception with `error_code` and `kwargs`.
- `TiferetAPIError`: Extends `TiferetError` with `name` and `message` for API responses.
- Error constants defined in `assets/constants.py` (e.g., `FEATURE_NOT_FOUND_ID`, `COMMAND_PARAMETER_REQUIRED_ID`).
- Default error definitions in `assets/constants.py::DEFAULT_ERRORS` dict.
- Access constants via `from .. import assets as a` then `a.const.ERROR_CODE_ID`.

### Error Constants (v2.0.0b3)

New error constants added in the b2→b3 cycle:

- `YAML_FILE_NOT_FOUND_ID`, `YAML_FILE_LOAD_ERROR_ID`, `YAML_FILE_SAVE_ERROR_ID` — YAML utility errors.
- `JSON_FILE_NOT_FOUND_ID`, `JSON_FILE_LOAD_ERROR_ID`, `JSON_FILE_SAVE_ERROR_ID`, `INVALID_JSON_PATH_ID` — JSON utility errors.
- `CSV_INVALID_MODE_ID`, `CSV_HANDLE_NOT_INITIALIZED_ID`, `CSV_INVALID_READ_MODE_ID`, `CSV_INVALID_WRITE_MODE_ID`, `CSV_FIELDNAMES_REQUIRED_ID`, `CSV_DICT_NO_HEADER_ID` — CSV utility errors.
- `CONFIG_FILE_NOT_FOUND`, `APP_CONFIG_LOADING_FAILED`, `CONTAINER_CONFIG_LOADING_FAILED`, `FEATURE_CONFIG_LOADING_FAILED`, `ERROR_CONFIG_LOADING_FAILED`, `CLI_CONFIG_LOADING_FAILED` — Configuration loading errors.

## Configuration

Applications are configured in a consolidated root `config.yml` file:

- `interfaces` — Interface definitions (name, module_path, class_name, service dependencies)
- `services` — Feature-level DI service configurations (module_path, class_name, parameters, flagged dependencies)
- `features` — Feature workflows (commands with service_id, parameters, data mapping, optional `condition` expressions for conditional step execution, and optional `middleware` lists at feature or step level)
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
- `LoggingMiddleware` — DEBUG/ERROR logging middleware via stdlib `logging`; takes `logger_id: str`.
- `TimingMiddleware` — Wall-clock timing middleware via `time.perf_counter`; takes `logger_id: str`.

### SQLite API (v2.0.0b3)

`SqliteClient` constructor signature:
```python
SqliteClient(path=':memory:', mode='rw', isolation_level=None, timeout=5.0, **kwargs)
```

Key methods: `execute(sql, parameters)`, `executemany(sql, seq_of_parameters)`, `executescript(sql_script)`, `fetch_one(query, parameters)`, `fetch_all(query, parameters)`, `commit()`, `rollback()`, `backup(target_path, pages, progress)`.

All query/mutation methods guard against uninitialized connections with `SQLITE_CONN_NOT_INITIALIZED` errors. Context manager protocol (`__enter__`/`__exit__`) auto-commits on success and auto-rolls-back on exception.

## Package Exports

The top-level `tiferet/__init__.py` exports:

**Core:**
- `App` (alias for `build_app`)
- `CLI` (alias for `build_cli`)
- `TiferetError`, `TiferetAPIError`

**Domain:**
- `DomainObject`

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
- `tiferet/domain/settings.py` — `DomainObject` base class (extends `pydantic.BaseModel`)
- `tiferet/events/settings.py` — `DomainEvent` base class (execute, verify, parameters_required, handle)
- `tiferet/mappers/settings.py` — `Aggregate` and `TransferObject` base classes
- `tiferet/interfaces/settings.py` — `Service` (ABC) base class
- `tiferet/di/settings.py` — `ServiceProvider` ABC
- `tiferet/di/dynamic.py` — `DynamicServiceProvider` (app-level DI, backed by `dependency-injector`)
- `tiferet/blueprints/main.py` — `build_app` (public app orchestration entry point)
- `tiferet/blueprints/cli.py` — `build_cli` (CLI orchestration entry point, exported as `CLI`)
- `tiferet/contexts/base.py` — `BaseContext` and `ContextMeta` (domain→context registry, `for_domain`, `from_domain`)
- `tiferet/contexts/app.py` — `AppInterfaceContext` (minimal declarative hub bound to the loaded `AppInterface`)
- `tiferet/contexts/di.py` — `DIContext` (feature-level DI)
- `tiferet/contexts/feature.py` — `FeatureContext` (feature execution engine)
- `tiferet/assets/constants.py` — Error codes and `DEFAULT_SERVICES` configuration
- `tiferet/assets/exceptions.py` — `TiferetError` and `TiferetAPIError`
- `tiferet/repos/settings.py` — `ConfigurationRepository` base class (format-agnostic config I/O)
- `examples/basic_calculator/` — Working calculator application example

## Migration Notes

### v2.0.0b9: Declarative Context Architecture (Minimal Hub)

The v2.0.0b9 release standardizes contexts under a `BaseContext` registry and makes the application interface context a minimal, declaratively-constructed hub. Key changes:

- **`BaseContext` + `ContextMeta`** (`tiferet/contexts/base.py`) — New base class and metaclass. Contexts declare a `domain_type` ClassVar; the metaclass registers each `{domain_type: context_class}` pair (own-namespace declarations only, so subclasses do not clobber base registrations). `BaseContext.for_domain(DomainType)` resolves the registered class (raising `CONTEXT_NOT_FOUND` when missing); `BaseContext.from_domain(domain_obj, **kwargs)` constructs the context and binds the object as `ctx.domain`.
- **`AppInterfaceContext` is now a minimal hub** — It no longer stores `interface_id`/`features`/`errors`/`logging`. Its constructor takes collaborators (`get_feature_evt`, `get_error_evt`, `di_list_all_configs_evt`, `logging_list_all_evt`, `create_service_provider`, `cache`) plus bootstrap defaults (`default_features`, `default_commands`, `default_configurations`, `default_constants`). It binds the loaded `AppInterface` via `from_domain` and reads `self.domain.id` / `self.domain.logger_id` on demand. Sub-contexts are built lazily and share one `CacheContext` (`load_feature`, `load_error_context`, `load_logging_context`, `load_feature_domain`, `load_error_domain`).
- **Declarative construction** — `load_app_instance` resolves the events/repos by name from the DI container, imports the context class from the interface's `module_path`/`class_name` (custom contexts like `FlaskApiContext` still work), and constructs it via `from_domain`. `AppInterface.get_service_type_mapping()` no longer adds an `app_context` entry, and `DEFAULT_SERVICES` no longer registers the `services`/`features`/`errors`/`logging` contexts.
- **Specialized contexts are pure operational behavior** — `FeatureContext.execute_feature(feature, request)` (and async/`resolve_feature_steps`) accept a pre-loaded `Feature`; feature retrieval moved to the hub. `ErrorContext` exposes `format_response(error, exception, lang)` (error retrieval moved to the hub's `load_error_domain`). The b9 `set_default_*` setters were removed; bootstrap defaults are seeded on the hub initializer and threaded through `realize_interface(..., default_*=...)`.

### v2.0.0b7: ConfigurationRepository & Role Consolidation

The v2.0.0b7 release introduces a format-agnostic `ConfigurationRepository` base class and consolidates TransferObject serialization roles. Key changes:

- **`ConfigurationRepository`** (`tiferet/repos/settings.py`) — New base class providing `_load()`, `_save()`, and `_get_loader()` methods that dispatch to `YamlLoader` or `JsonLoader` based on the config file extension (`.yml`/`.yaml` → YAML, `.json` → JSON). Raises `UNSUPPORTED_CONFIG_FILE_TYPE` for unknown extensions.
- **Repository renames** — All six concrete repos have been renamed from `*YamlRepository` to `*ConfigRepository`:
  - `AppYamlRepository` → `AppConfigRepository`
  - `CliYamlRepository` → `CliConfigRepository`
  - `DIYamlRepository` → `DIConfigRepository`
  - `ErrorYamlRepository` → `ErrorConfigRepository`
  - `FeatureYamlRepository` → `FeatureConfigRepository`
  - `LoggingYamlRepository` → `LoggingConfigRepository`
- **Constructor scalars** — Each repo’s constructor parameter has been renamed from `<domain>_yaml_file` to `<domain>_config` (e.g., `app_yaml_file` → `app_config`, `error_yaml_file` → `error_config`).
- **Bootstrap defaults** (`tiferet/assets/blueprints.py`) — `DEFAULT_CONSTANTS` keys updated to match (`cli_config`, `di_config`, `error_config`, `logging_config`, `feature_config`). `DEFAULT_APP_SERVICE_CLASS_NAME` changed to `'AppConfigRepository'`. All `DEFAULT_SERVICES` class names updated.
- **`_ROLES` consolidation** — All TransferObject `_ROLES` dicts have been consolidated: `'to_data.yaml'` → `'to_data'`, and redundant `'to_data.json'` entries have been removed. The `default_role` on all repos is now `'to_data'`.
- **Usage pattern change**:
  ```python
  # Before (v2.0.0b6)
  from tiferet import App
  app = App('basic_calc', app_yaml_file='config.yml')

  # After (v2.0.0b7)
  from tiferet import App
  app = App('basic_calc', app_config='config.yml')
  ```

### v2.0.0b3: Blueprints Pattern

The v2.0.0b3 release replaces the class-based `AppBuilder`/`CliBuilder` pattern with module-level blueprint functions. Key changes:

- **`tiferet/builders/`** package has been renamed to **`tiferet/blueprints/`**. The `builders` package no longer exists.
- **`AppBuilder`** class has been replaced by the **`build_app`** function in `tiferet/blueprints/main.py`. The `App` export is now an alias for `build_app` (not `AppBuilder`).
- **`CliBuilder`** class has been replaced by the **`build_cli`** function (also named `build_app` locally) in `tiferet/blueprints/cli.py`. The `CLI` export is now an alias for `build_cli`.
- **`_build_factory`** (previously a private method on `DynamicServiceProvider`) is now the **public** method **`build_factory`** on `DynamicServiceProvider`. It builds a `Factory` provider with constructor kwargs wired to sibling providers.
- **Blueprint constants** live in `tiferet/assets/blueprints.py` (accessible as `a.bps`), providing `DEFAULT_CONSTANTS`, `DEFAULT_SERVICES`, `DEFAULT_APP_SERVICE_MODULE_PATH`, and `DEFAULT_APP_SERVICE_CLASS_NAME`.
- **SQLite API** — `SqliteClient.__init__` now accepts `mode='rw'` (default), `isolation_level`, and `timeout` parameters. All query/mutation methods guard against uninitialized connections.
- **Usage pattern change**:
  ```python
  # Before (v2.0.0b2)
  from tiferet import App
  app = App()
  app.load_app_service(app_yaml_file='config.yml')
  result = app.run('basic_calc', 'calc.add', data={'a': 1, 'b': 2})

  # After (v2.0.0b3)
  from tiferet import App
  app = App('basic_calc', app_yaml_file='config.yml')
  result = app.run('calc.add', data={'a': 1, 'b': 2})
  ```
- The `ServiceProvider` ABC is unchanged.
- The backward-compatible alias `DependenciesServiceProvider = DynamicServiceProvider` remains in `tiferet/di/__init__.py`.

### v2.0.0b2: DI Backend Migration

The v2.0.0b2 release replaces the `dependencies` library DI backend with `dependency-injector`. Key changes:

- **`DependenciesServiceProvider`** (backed by `dependencies.Injector`) has been removed. The concrete implementation is now `DynamicServiceProvider` (backed by `dependency-injector`'s `DynamicContainer`).
- **`tiferet/di/dependencies.py`** has been deleted. The implementation lives in `tiferet/di/dynamic.py`.
- **`pyproject.toml`** dependency is `dependency-injector>=4.49.0` (not `dependencies>=7.7.0`).
- **Backward-compatible alias**: `DependenciesServiceProvider = DynamicServiceProvider` is provided in `tiferet/di/__init__.py` for downstream consumers.
- **Scalar constants** registered via `add_constants()` can now be resolved directly via `get_service()` (previously not possible with the `dependencies` library).
- **Class types** are registered as `Factory` providers (new instance per resolution); non-type values are registered as `Object` providers (pass-through).
- The `ServiceProvider` ABC is unchanged.

### v2.0.0b1: Schematics to Pydantic v2

The v2.0.0b1 release completed the migration from `schematics` to Pydantic v2. Key breaking changes:

- **`DomainObject`** now extends `pydantic.BaseModel` instead of `schematics.Model`.
- **`DomainObject.new(Type, **kwargs)`** has been removed. Use direct constructors: `Feature(id='calc.add', name='Add')`. Use `model_construct()` to skip validation.
- **`Aggregate.new(Type, **kwargs)`** has been removed. Use direct constructors.
- **Schematics type wrappers** (`StringType`, `IntegerType`, `FloatType`, `BooleanType`, `ListType`, `DictType`, `ModelType`) are no longer exported. Use standard Python type annotations with `pydantic.Field(...)`.
- **`TransferObject`** no longer uses `class Options`, `allow()`, `deny()`, or `from_data()`. Instead:
  - Role-based serialization uses a `_ROLES: ClassVar[Dict]` mapping role names to `model_dump` kwargs.
  - `to_primitive(role)` delegates to `model_dump()` with role-specific kwargs.
  - `map(target)` constructs an Aggregate from the serialized data.
  - `from_model(model)` is a `@classmethod` that constructs a TransferObject from a domain model via `model_validate`.
- **Custom factories** on domain objects (`Error.new`, `Feature.new`, `CliCommand.new`) have been replaced by `@model_validator(mode='before')` class methods for pre-construction derivation logic.
- **`model_validate(data)`** replaces `from_data()` at all call-sites.
- **`model_dump()`** replaces `to_primitive()` at non-role call-sites.
- **Aliases** use `serialization_alias` and `validation_alias=AliasChoices(...)` instead of Schematics `serialized_name` / `deserialize_from`.
- **`pyproject.toml`** dependency is `pydantic>=2.6` (not `schematics`).

## Contributing

See `CONTRIBUTING.md` for the full workflow:

1. Tie work to a GitHub issue.
2. Write a TRD (Technical Requirements Document) for non-trivial changes.
3. Implement following structured code style and component-specific guides in `docs/core/`.
4. Separate functional changes from docs/config in distinct commits.
5. Include `Co-Authored-By:` lines when collaborating with AI agents.
6. Publish a Collaboration Report on the issue upon completion.
