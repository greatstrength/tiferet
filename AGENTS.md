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
├── contexts/             # Runtime orchestration: BaseContext registry + AppSessionContext hub (Feature, Error, Logging) + CliContext
├── di/                   # DI: core.py ABCs + dependency_injector.py impls (DIAppServiceContainer, DIDynamicServiceResolver) + legacy settings.py
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

- **DomainObject** (`domain/core.py`): Base domain model class extending `pydantic.BaseModel`. Instantiate via direct Pydantic constructors (e.g., `Feature(id='calc.add', ...)`). Use `model_construct()` to skip validation. Domain objects are read-only; mutation goes through Aggregates.
- **DomainEvent** (`events/settings.py`): Base class for domain operations. Receives dependencies via constructor injection. Entry point is `execute(**kwargs)`. Use `@DomainEvent.parameters_required([...])` for declarative input validation. Use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` for invocation in tests. Each single-service event module defines a per-module base event (e.g., `ErrorEvent`, `FeatureEvent`) that holds the shared service injection; concrete events extend the base and define only `execute`.
- **Service** (`interfaces/settings.py`): Abstract base class (`ABC`) for all service contracts. All vertical concerns (data access, config, utilities) are unified under Service.
- **MiddlewareService** (`interfaces/middleware.py`): Abstract callable that wraps domain event execution. Implement `__call__(self, event, kwargs, next_fn)` for sync middleware or `async def __call__` for async. Resolved from the DI container by `service_id` and composed into an ordered chain by `FeatureContext`.
- **Aggregate** (`mappers/settings.py`): Mutable extension of domain objects. Instantiate via direct constructors. Provides `set_attribute()` for validated mutation with `validate_assignment=True`.
- **TransferObject** (`mappers/settings.py`): Serialization layer with role-based field control via `_ROLES` ClassVar. Methods: `to_primitive(role)`, `map(target)`, `@classmethod from_model()`. Uses lenient config (`extra='ignore'`).
- **BaseContext** (`contexts/settings.py`): Base class for all contexts, with a `ContextMeta` metaclass registry keyed by `domain_type`. `BaseContext.for_domain(DomainType)` resolves the registered context class; `BaseContext.from_domain(domain_obj, **kwargs)` constructs a context and binds the domain object as `ctx.domain`. The base holds no cache; contexts that need a `CacheContext` (e.g., `AppSessionContext`, `FeatureContext`) wire it themselves. The `AppSessionContext` hub binds the loaded `AppSession` and builds its sub-contexts on demand.

### Runtime Flow

1. `App(interface_id)` (alias for `core.build_app`) resolves the app session and returns an `AppSessionContext`.
2. `core.build_app` builds the shared cache (`build_cache`), composes the app service and resolves the session via the `GetAppSession` event (`get_app_session`), then constructs the context via `build_app_session_context`: it builds the app service container by merging cache defaults with the session's own constants/services (`build_app_service_container`), composes a `ServiceResolver` (`build_service_resolver`), resolves the hub's event collaborators from the app container, and constructs the `AppSessionContext` via `BaseContext.from_domain(app_session, get_dependency=resolver.get_dependency, ...)` — the context graph itself is not DI-resolved. No `apply_defaults` is called on the core path.
3. `AppSessionContext.run(feature_id, data={})` builds a logger, parses the request, loads the `Feature` domain object, executes it, and returns the response.
4. The hub builds its sub-contexts (`FeatureContext`, `ErrorContext`, `LoggingContext`) on demand; `FeatureContext.execute_feature(feature, request)` resolves each step's service via the injected `get_dependency` handler (from `ServiceResolver`) and executes it sequentially. When the loaded `Feature` has `is_async` set, the hub instead selects `AsyncFeatureContext` (a `FeatureContext` subclass) and drives `execute_feature_async` to completion via a `_run_coroutine` helper, keeping `run()` synchronous.
5. Each step is a `DomainEvent` subclass that receives injected services and performs domain logic.
6. Results flow back through `RequestContext` and `handle_response()`.

### Blueprints

Blueprints (`tiferet/blueprints/`) are module-level functions that orchestrate application bootstrapping and execution. They replace the previous class-based `AppBuilder`/`CliBuilder` pattern from v2.0.0b2.

- `build_app(interface_id, ...)` is defined in `tiferet/blueprints/core.py` and exported as `App` from `tiferet/__init__.py`. It chains `build_cache()` → `get_app_session(id, cache, ...)` → `build_app_session_context(session, cache)` → `INVALID_APP_SESSION_TYPE` validation, returning a fully wired `AppSessionContext`. (The former `blueprints/main.py` was retired in the Chapter M cleanup.)
- `build_cli(interface_id, ...)` is defined in `tiferet/blueprints/cli.py` and exported as `CLI` from `tiferet/__init__.py`. It is a thin entrypoint that calls `core.build_app(...)` (the interface must point at `CliContext`) and delegates `argv` parsing and feature dispatch to `CliContext.run_cli`.
- `build_tiferet_app` / `build_tiferet_cli` (`tiferet/blueprints/tiferet_app.py` / `tiferet_cli.py`, exported as `TiferetApp` / `TiferetCLI`) bootstrap the built-in `tiferet_app` / `tiferet_cli` sessions that are not in the consumer config; they resolve through the shared module-private `_resolve_bootstrap_session` in `tiferet_cli.py` (default-session fallback + `apply_defaults`).

**Core composition functions in `core.py` (`# *** blueprints`):**
- `build_cache()` — builds the shared cache pre-seeded with default errors, app services, and constants.
- `create_app_service(...)` — composes the app service via a single-use dynamic container.
- `get_app_session(interface_id, cache, ...)` — resolves the app session via the `GetAppSession` event (raises `APP_SESSION_NOT_FOUND` when absent; no core fallback). The `cache` parameter is a build-ordering seam (`# ++ todo:` — default sessions are not yet cache-seeded).
- `build_app_service_container(cache, app_instance)` — builds the singleton app service container by merging cache defaults with the session's own constants/services **before** building (session wins), so overrides reach default services the session does not redeclare.
- `build_service_resolver(app_container)` — composes the feature-level `ServiceResolver`, caching the app container under the `app` flag.
- `build_app_session_context(app_session, cache)` — imports the declared context class, resolves its collaborators from the app container, wires the four hub handlers, and constructs via `BaseContext.from_domain`.
- `build_app(interface_id, ...)` — the single-call entry point chaining the above.

**Relocated legacy feature-DI bootstrap (module-private in `tiferet/blueprints/tiferet_cli.py`):** `_wire_services`, `_resolve_ctor_kwargs`, `_build_wiring_constants`, `_resolve_collaborators`, `_load_app_instance`, and the shared `_resolve_bootstrap_session`. Retained only for `build_tiferet_cli`, which still composes the resolver via the `CreateServiceResolver` bootstrap event; the standard app/CLI path uses the core compose path instead.

**CLI blueprint function in `cli.py`:**
- `build_app(interface_id, argv, ...)` — Thin CLI entrypoint: calls `core.build_app(...)` (a `CliContext`) and delegates to `cli_context.run_cli(argv)`. Exported as `build_cli` / `CLI`.

CLI parsing is owned by `CliContext` (`tiferet/contexts/cli.py`): the side-effect-free module-level helpers `group_commands_by_key`, `build_parser`, and `derive_feature_request`, plus the `get_commands` / `parse_cli_request` / `run_cli` methods. Per-argument argparse translation lives on `CliArgument.to_argparse_kwargs()`. Consumer CLI interfaces opt in by pointing their config at `tiferet.contexts.cli` / `CliContext`.

### Dependency Injection

As of v2.0.0b10, DI is provided by two classes in `tiferet/di/settings.py` (the previous `ServiceProvider` ABC, `DynamicServiceProvider`, `DependenciesServiceProvider` alias, and the feature-level `DIContext` have all been removed):

- **`ServiceContainer`** — the low-level engine, backed by `dependency-injector`'s `DynamicContainer`. Registers class types as `Factory` providers and scalars/callables as `Object` providers, and resolves instances via `get_service`. `build_factory(service_type)` wires each constructor parameter to a sibling provider via the shared `injectable_parameter_names` helper.
- **`ServiceResolver`** — the application's single public provider. It takes a `DIService` and a `parse_parameter` callable as direct dependencies, reads service registrations and constants (merging bootstrap defaults via `merge_settings`), assembles a per-flag type map and constant set, and builds and caches a `ServiceContainer` per flag set. Its bound `get_dependency(registration_id, *flags)` method is injected into `AppSessionContext` and forwarded to each `FeatureContext` to resolve feature-step events and middleware.

The DI layer is **event-free and asset-free** (it imports only stdlib, `dependency-injector`, `..domain`, and `..interfaces.di`); it assumes best-case inputs, raises raw exceptions for callers with event access to convert, and receives parameter parsing as the injected `parse_parameter` callable. `tiferet/di/settings.py` also exposes pure `# *** functions` — `injectable_parameter_names`, `normalize_flags`, `create_cache_key`, and `merge_settings` — exported from `tiferet/di/__init__.py`.

Interface wiring is declarative: `wire_services` instantiates the interface's events and repositories into a name-to-value registry (no app-level container), and `load_app_instance` composes the `ServiceResolver` via the `CreateServiceResolver` bootstrap event (`tiferet/events/blueprint.py`) and injects `resolver.get_dependency`.

A DI refactor (see Migration Notes) introduces an abstract, domain-only contract in `tiferet/di/core.py` (the `ServiceContainer` and `ServiceResolver` ABCs, plus `injectable_parameter_names` / `normalize_flags`) and concrete `dependency_injector`-backed implementations in `tiferet/di/dependency_injector.py` (`DIDynamicServiceContainer`, the Singleton `DIAppServiceContainer`, and the per-flag `DIDynamicServiceResolver`). These coexist with the legacy `tiferet/di/settings.py` classes above, which `build_app` still wires.

## Structured Code Style

All code follows a strict artifact comment hierarchy. **This is mandatory.**

### Comment Levels

- `# *** <section>` — Top-level: `imports`, `exports`, `models`, `events`, `contexts`, `interfaces`, `mappers`, `repos`, `constants`, `functions`, `classes`, `blueprints`
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

### Annotation Artifacts

Two transient lifecycle markers sit below the structural hierarchy and signal outstanding work or deprecated code:

- **`# ++ todo: <message>`** — deferred work attached to an artifact (`++` = something to add/grow). Remove when resolved.
- **`# -- obsolete: <reason>`** — deprecated artifact slated for removal (`--` = something to reduce/remove). Remove together with the artifact when retired.

Both appear immediately after the `# *` / `# **` / `# ***` comment they annotate, before the code body. The `(obsolete)` parenthetical suffix on a `# *` label remains valid shorthand when no reason is needed.

**Before starting any implementation session**, scan affected files for open annotations:

```bash
grep -rn "# ++\|# --" tiferet/
```

Full grammar and resolution expectations: [`docs/core/code_style.md § Annotation Artifacts`](docs/core/code_style.md).

### Code Style Skills

The `tiferet-code-*` skill suite provides self-contained, offline-capable style guidance for each component layer. Skills embed key conventions and a working example — no external URLs required. Install them from `docs/collab/agents/skills/` (see that folder's README for activation instructions).

**Read `tiferet-code-style` at the start of every implementation session** (same standing as `tiferet-annotation-artifacts`). **Read `tiferet-code-architecture` before any multi-component implementation.**

| Skill | When to use |
|---|---|
| **`tiferet-code-architecture`** | Any multi-component task — layer graph, import rules, runtime flow |
| **`tiferet-code-style`** | Every implementation session — read first |
| **`tiferet-code-domain`** | Adding or modifying domain objects |
| **`tiferet-code-events`** | Adding or modifying domain events |
| **`tiferet-code-mappers`** | Adding or modifying aggregates or transfer objects |
| **`tiferet-code-interfaces`** | Adding or modifying service interfaces |
| **`tiferet-code-contexts`** | Adding or modifying contexts |
| **`tiferet-code-repos`** | Adding or modifying repositories |
| **`tiferet-code-assets`** | Adding or modifying assets constants, errors, or exceptions |
| **`tiferet-code-blueprints`** | Adding or modifying blueprints |
| **`tiferet-code-utils`** | Adding or modifying utilities |
| **`tiferet-code-di`** | Adding or modifying DI layer classes or functions |
| **`tiferet-code-testing`** | Writing or extending tests using the harness |

**Fallback rule:** if a skill is not installed, read `docs/core/<component>.md` directly — the full-detail guides are the canonical source of truth.

## Domain Events

Domain events are the primary operational units. Key patterns:

- Extend the module's per-module base event (e.g., `ErrorEvent`, `FeatureEvent`, `AppEvent`, `CliEvent`, `DIEvent`, `LoggingEvent`, `SqliteEvent`), which holds the shared service; extend `DomainEvent` from `tiferet/events/settings.py` directly only when defining a new base event or a service-less event.
- Dependencies via constructor injection (usually a Service), declared on the base event.
- `execute(**kwargs)` is the entry point.
- `@DomainEvent.parameters_required(['param1', 'param2'])` for declarative input validation (decorator on `execute`).
- `self.verify(expression, error_code, message, **kwargs)` for domain rule enforcement.
- `self.raise_error(error_code, message, **kwargs)` for direct error raising.
- Return domain models or identifiers.

### Static Events

`ParseParameter`, `ImportDependency`, `RaiseError` in `events/static.py` are utility events called with static `.execute()` methods.

### Bootstrap Events

`CreateServiceResolver` in `events/blueprint.py` is a bootstrap domain event that composes a fully wired `ServiceResolver` from an `AppSession`: it locates the `di_service` dependency, constructs the DI repository, builds the typed default-config index, and injects `ParseParameter.execute` so the DI layer never imports the parameter parser itself. It is invoked by `load_app_instance` via `DomainEvent.handle`.

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

- Extend `DomainObject` from `tiferet/domain/core.py`.
- `DomainObject` extends `pydantic.BaseModel` with `ConfigDict(extra='forbid', populate_by_name=True, validate_assignment=True)`.
- Declare fields with idiomatic Pydantic annotations: `name: str = Field(...)`.
- Instantiate via direct constructors: `Error(id='invalid_input', name='Invalid Input')`.
- Use `model_construct()` to skip validation where needed.
- Use `@model_validator(mode='before')` for custom factory/derivation logic (replaces the old `DomainObject.new()` / custom `new()` factories).
- Use `model_validate(data)` to construct from dicts with validation.
- Use `model_dump()` to serialize to dicts.
- Domain objects are **read-only**; place mutation logic in Aggregates (`mappers/`).

### Domain Modules

- `domain/core.py` — `DomainObject`, `ServiceDependency`
- `domain/app.py` — `AppSession`, `AppServiceDependency`
- `domain/cli.py` — `CliCommand`, `CliArgument`
- `domain/di.py` — `ServiceRegistration` (with `resolve_service` / `get_service_type`), `FlaggedDependency`
- `domain/error.py` — `Error`, `ErrorMessage`
- `domain/feature.py` — `Feature`, `FeatureStep`, `EventFeatureStep`
- `domain/logging.py` — `Formatter`, `Handler`, `Logger`, `LoggingSettings`

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

- `<Domain>Aggregate` (e.g., `FeatureAggregate`, `ErrorAggregate`, `ServiceRegistrationAggregate`)
- `<Domain>ConfigObject` (e.g., `FeatureConfigObject`, `ErrorConfigObject`, `ServiceRegistrationConfigObject`)

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
- `services` — Feature-level DI service registrations (module_path, class_name, parameters, flagged dependencies)
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
- `tiferet/domain/core.py` — `DomainObject` base class (extends `pydantic.BaseModel`) and `ServiceDependency` core model
- `tiferet/events/settings.py` — `DomainEvent` base class (execute, verify, parameters_required, handle)
- `tiferet/mappers/settings.py` — `Aggregate` and `TransferObject` base classes
- `tiferet/interfaces/settings.py` — `Service` (ABC) base class
- `tiferet/di/core.py` — `ServiceContainer` / `ServiceResolver` ABCs + `injectable_parameter_names` / `normalize_flags`
- `tiferet/di/dependency_injector.py` — `DIDynamicServiceContainer` (Factory), `DIAppServiceContainer` (Singleton), `DIDynamicServiceResolver` (per-flag)
- `tiferet/di/settings.py` — legacy `ServiceContainer` (DI engine) and `ServiceResolver` (public provider), still wired by `build_app`
- `tiferet/blueprints/core.py` — `build_app` (public app orchestration entry point, exported as `App`) plus the composition chain: `build_cache`, `create_app_service`, `get_app_session`, `build_app_service_container`, `build_service_resolver`, `build_app_session_context`
- `tiferet/blueprints/cli.py` — `build_cli` (CLI orchestration entry point, exported as `CLI`; calls `core.build_app` then `run_cli`)
- `tiferet/blueprints/tiferet_cli.py` — `build_tiferet_cli` (`TiferetCLI`) plus the relocated module-private legacy feature-DI bootstrap (`_wire_services`, `_load_app_instance`, `_resolve_collaborators`, `_resolve_bootstrap_session`, ...)
- `tiferet/blueprints/tiferet_app.py` — `build_tiferet_app` (`TiferetApp`; core compose path + shared default-session fallback)
- `tiferet/contexts/settings.py` — `BaseContext` and `ContextMeta` (domain→context registry, `for_domain`, `from_domain`)
- `tiferet/contexts/app.py` — `AppSessionContext` (minimal declarative hub bound to the loaded `AppSession`)
- `tiferet/contexts/cli.py` — `CliContext` (CLI high-level context: argparse parsing helpers + `get_commands`/`parse_cli_request`/`run_cli`)
- `tiferet/contexts/feature.py` — `FeatureContext` (sync feature execution engine) and `AsyncFeatureContext` (async subclass selected when `Feature.is_async` is set)
- `tiferet/assets/constants.py` — Error codes plus the `create_default_error` / `create_app_service_dependency` factories
- `tiferet/assets/app.py` — Default interface definitions and the `CORE_DEFAULT_SERVICES` / `CORE_DEFAULT_CONSTANTS` bootstrap catalogs
- `tiferet/assets/exceptions.py` — `TiferetError` and `TiferetAPIError`
- `tiferet/repos/settings.py` — `ConfigurationRepository` base class (format-agnostic config I/O)
- `examples/basic_calculator/` — Working calculator application example

## Migration Notes

### Chapter M: Retire `main.py`, promote `core.build_app`

The Chapter M cleanup makes `tiferet/blueprints/core.py` own the public `build_app` entry point and deletes `tiferet/blueprints/main.py`. Key changes:

- **`core.build_app`** — New single-call entry point (exported as `App`), ordered `build_cache()` → `get_app_session(id, cache, ...)` → `build_app_session_context(session, cache)` → `INVALID_APP_SESSION_TYPE` validation. It never calls `apply_defaults` / `resolve_default_interface`; all framework defaults come from the cache seeded by `build_cache`.
- **`core.get_app_session`** — Gained an optional `cache` build-ordering seam (`# ++ todo:` — default sessions are not yet cache-seeded; kept `= None` so the obsolete `get_app_interface` alias still resolves). The obsolete `core.execute_feature` was removed.
- **`core.build_app_service_container`** — Now merges the framework default services/constants (from the cache) with the session's own **before** building the container (single `from_dependencies` call) instead of layering overrides onto an already-built container. This fixes the stale-singleton wiring finding for the core path, which no longer passes a defaults-applied session: an interface constant override reaches default services the session does not redeclare.
- **`cli.build_app`** — Rewritten to call `core.build_app(...)` then `cli_context.run_cli(argv)`.
- **`tiferet_app.build_tiferet_app`** — Repointed onto the core compose path with the shared default-session fallback.
- **Relocation** — The legacy declarative feature-DI bootstrap (`wire_services`, `resolve_ctor_kwargs`, `build_wiring_constants`, `resolve_collaborators`, `load_app_instance`) plus a shared `_resolve_bootstrap_session` (relocated `resolve_interface` logic: `get_app_session` → `resolve_default_interface` fallback → `apply_defaults`) moved (module-private, underscore-prefixed) into `tiferet/blueprints/tiferet_cli.py`. `build_tiferet_cli` still needs them; the standard app/CLI path does not.
- **Removal** — `tiferet/blueprints/main.py` deleted; `blueprints/__init__.py` imports `build_app` / `App` from `core`. `apply_defaults` (`domain/app.py`) and `resolve_default_interface` (`contexts/app.py`) are now downstream-only, used solely by the relocated bootstrap path.
- **Deferred** — Seeding default app *sessions* into the cache (so the built-in bootstrappers can drop the fallback and call `core.build_app` directly); removing `apply_defaults` / `resolve_default_interface`; deep `build_tiferet_cli` feature-DI parity; N4 (`CreateServiceResolver` disposition); N5 (`di/settings.py` consolidation).

### DI App Service Container & Feature Service Resolver

This cycle introduces an app-level service container and a feature-level service resolver alongside a DI-layer refactor, all additive (the legacy `tiferet/di/settings.py` remains wired by `build_app`):

- **Abstract DI contract** (`tiferet/di/core.py`) — Adds the `ServiceContainer` and `ServiceResolver` ABCs. `ServiceResolver` owns a per-flag container cache plus a template-method `get_dependency`, leaving `build_container` abstract. `normalize_flags` is relocated here (canonical) alongside `injectable_parameter_names`; `settings.py` re-imports `normalize_flags`, and `tiferet/di/__init__.py` repoints it to `core.py`.
- **Dependency-injector implementations** (`tiferet/di/dependency_injector.py`) — `DIDynamicServiceContainer` (Factory scope); `DIAppServiceContainer` (Singleton scope, `build_singleton`, and a `from_dependencies` classmethod keyed by `service_id`); and `DIDynamicServiceResolver` (holds a `DIService` + injected `parse_parameter`, implements `build_container`). `DIAppServiceContainer` is exported from `tiferet/di/__init__.py`.
- **`ServiceRegistration.resolve_service`** (`tiferet/domain/di.py`) — Centralizes the flagged-override → default → None precedence, returning the effective core `ServiceDependency` for a flag set; `get_service_type` now delegates to it.
- **Cache enumeration** — `CacheContext.get_by_prefix(prefix)` (`tiferet/contexts/cache.py`) returns all entries whose keys start with a prefix. `contexts/app.py` adds `get_default_app_services` / `get_default_app_constants` getters that read the `app_service_` / `app_constant_` cache prefixes seeded by the existing `add_default_app_*` decorators.
- **Blueprint helpers** (`tiferet/blueprints/core.py`) — `build_app_service_container(cache, app_instance, service_container=DIAppServiceContainer)` composes the app service container from cache-seeded defaults plus interface overrides; `parse_parameter` is a thin wrapper over the `ParseParameter` static event for injection into the resolver.
- **Deferred** — Wiring the new resolver / app container into `build_app`, consolidating the legacy `settings.py` (including its duplicate `ServiceContainer`), and reconciling `tiferet/di/__init__.py` exports remain follow-ups.

### v2.0.0b13: Bootstrap/Default Configuration Finalization

The v2.0.0b13 cycle finalizes the bootstrap/default configuration architecture and applies a behavior-preserving naming refactor. Key changes:

- **`ServiceConfiguration` → `ServiceRegistration`** — The DI domain concept (`domain/di.py`) is renamed to `ServiceRegistration` (it models a DI registration). Mappers become `ServiceRegistrationAggregate`/`ServiceRegistrationConfigObject`; `DIService`/`DIConfigRepository` methods become `registration_exists`, `get_registration`, `save_registration`, `delete_registration` (param `registration_id`); the resolver's `get_dependency(registration_id, *flags)` param is renamed to match; events become `AddServiceRegistration`/`SetDefaultServiceRegistration`/`RemoveServiceRegistration`; error constants become `INVALID_SERVICE_REGISTRATION`, `SERVICE_REGISTRATION_NOT_FOUND`, `SERVICE_REGISTRATION_ALREADY_EXISTS`; bootstrap service ids become `add_service_registration_evt`/`set_default_service_registration_evt`/`remove_service_registration_evt`. `ListAllSettings`, `SetServiceDependency`, `RemoveServiceDependency`, `SetServiceConstants`, the `di_list_all_configs_evt` id, and the persisted `services:` config section are unchanged.
- **`*YamlObject` → `*ConfigObject`** — All transfer objects are renamed from the `*YamlObject` suffix to `*ConfigObject` (configs load as YAML or JSON by registered extension, completing the b7 `*ConfigRepository` direction): e.g., `FeatureYamlObject` → `FeatureConfigObject`, `ErrorYamlObject` → `ErrorConfigObject`, `ServiceRegistrationConfigObject`, `LoggingSettingsYamlObject` → `LoggingSettingsConfigObject`, plus the non-exported child objects. The `# ** mapper: *_yaml_object` artifact comments become `*_config_object` and "YAML data representation" docstrings become "configuration data representation".
- **Default configuration hoisting** — The listing/lookup events are now repo-only: `GetFeature`, `ListCliCommands`, `ListAllSettings`, and `GetAppInterface` no longer accept `default_*` params (and `GetAppInterface.get_from_defaults` is removed). Bootstrap defaults are id-keyed asset mappings (`assets/feature.py` `DEFAULT_TIFERET_CLI_FEATURES` and `assets/cli_commands.py` `DEFAULT_TIFERET_CLI_COMMANDS` are now `Dict[str, dict]`) materialized by the pure builders `build_feature_index` / `build_command_list` in `contexts/app.py`. The fallback/merge moves to the orchestration layer: `AppInterfaceContext.load_feature_domain` falls back to the default feature index, `CliContext.get_commands` falls back to the default command list, and the blueprint's `resolve_interface` applies the interface fallback via the context helper `resolve_default_interface` (`contexts/app.py`, beside `build_feature_index` / `build_command_list`) and the service/constant merge via the non-mutating `AppInterface.apply_defaults` domain method (`domain/app.py`); neither imports the `AppInterfaceAggregate`. Consumer-facing `cli list-commands` / `service list` now return repo-only results.
- **`LoggingSettings` value object** — A runtime value object (`domain/logging.py`, exported from `domain/__init__.py`) bundles `formatters`/`handlers`/`loggers` plus `version`/`disable_existing_loggers` and owns the `format_config()` dictConfig assembly (including the `root` entry drawn from the `is_root` logger). `LoggingContext.build_logger` now constructs a `LoggingSettings` from the `ListAllLoggingConfigs` lists (applying the built-in defaults as the per-section fallback) and calls `settings.format_config()` then `create_logger`; the context's inline `format_config` method is removed. The `logging_list_all_evt` collaborator and `logger_id` handling are unchanged, the value object is runtime-only (no Aggregate/TransferObject), and `logger_id` stays out of it.
- **Bootstrap service/constant catalogs moved to `assets/app.py`** — The bootstrap service-wiring list and config constants were reshaped from `assets/blueprints.py` (`DEFAULT_SERVICES: List[Tuple]` / `DEFAULT_CONSTANTS: Dict`) into id/model/group constants in `assets/app.py` (exported as `a.app`), mirroring the default-error catalog: a new `create_app_service_dependency` factory (`assets/constants.py`), id and model constants, and the `CORE_DEFAULT_SERVICES` (keyed by service id) / `CORE_DEFAULT_CONSTANTS` (keyed by config id) group mappings. `load_default_services` now builds via `AppServiceDependency.model_validate` over `a.app.CORE_DEFAULT_SERVICES.values()`, and both `resolve_interface`'s `apply_defaults` and the `tiferet_cli` bootstrap merge read `a.app.CORE_DEFAULT_CONSTANTS`; `assets/blueprints.py` retains only `DEFAULT_APP_SERVICE_MODULE_PATH` / `DEFAULT_APP_SERVICE_CLASS_NAME`. The core `build_cache` (`blueprints/core.py`) additionally pre-seeds these catalogs via new `add_default_app_services` / `add_default_app_constants` decorators (`contexts/app.py`), namespacing errors, services, and constants under the `error_`, `app_service_`, and `app_constant_` cache-key prefixes (the `main.py` / `admin.py` `build_cache` variants are unchanged).

### v2.0.0b11: CliContext Reincorporation

The v2.0.0b11 cycle reincorporates `CliContext` as a high-level context and slims both CLI blueprints to thin entrypoints. Key changes:

- **`CliContext`** (`tiferet/contexts/cli.py`) — Extends `AppInterfaceContext` with command-line concerns: `get_commands`, `parse_cli_request`, and `run_cli`, orchestrating the side-effect-free module-level helpers `group_commands_by_key`, `build_parser`, and `derive_feature_request`. It intentionally omits `domain_type`, so the `ContextMeta` registry still maps `AppInterface` to `AppInterfaceContext`; the CLI context is selected via the interface's `module_path`/`class_name`.
- **Generalized collaborator wiring** — `resolve_collaborators(context_cls, registry)` now inspects the realized context class's injectable constructor parameters (skipping `get_dependency`/`cache` and `default_*`), so a `CliContext` receives `list_commands_evt`/`get_parent_args_evt` while the generic `AppInterfaceContext` still resolves only its original three. `load_app_instance` imports the context class before resolving collaborators.
- **Slim CLI blueprints** — `tiferet/blueprints/cli.py` (`build_cli`/`CLI`) reduces to resolve → realize → `cli_context.run_cli(argv)`; the old `get_commands`/`get_parent_arguments`/`build_argument_kwargs`/`build_parser`/`parse_argv`/`derive_feature_request` helpers were removed (the shared logic lives in `tiferet/contexts/cli.py`). `tiferet/blueprints/tiferet_cli.py` drops `_build_tiferet_command_map` and the mapper import, seeds bootstrap commands via `default_commands`, and decodes JSON args after `parse_cli_request` before `run`.
- **Built-in CLI interface** — `DEFAULT_TIFERET_CLI_INTERFACE` (`tiferet/assets/app.py`) now points at `tiferet.contexts.cli` / `CliContext`. Consumer CLI interfaces must likewise opt in.
- **`CliArgument.to_argparse_kwargs()`** — Per-argument argparse translation moved onto the `CliArgument` domain model (co-located with `get_type()`), replacing the module-level `build_argument_kwargs`.

### v2.0.0b10: DI Redesign, Per-Module Base Events, and Async Feature Split

The v2.0.0b10 cycle reworks dependency injection, introduces per-module base domain events, and splits async feature execution. Key changes:

- **DI redesign** — The `ServiceProvider` ABC, `DynamicServiceProvider`, the `DependenciesServiceProvider` alias, and the feature-level `DIContext` (`tiferet/contexts/di.py`) have been removed. DI now lives in `tiferet/di/settings.py` as `ServiceContainer` (the `dependency-injector`-backed engine) and `ServiceResolver` (the application's single public provider, which takes `DIService` directly and caches a `ServiceContainer` per flag set). `AppInterfaceContext` and `FeatureContext` consume an injected `get_dependency` callable. The blueprint wires the interface declaratively via `wire_services` (no app-level container) and composes the `ServiceResolver` via the `CreateServiceResolver` bootstrap event in `load_app_instance`. The `create_service_provider` blueprint factory was removed.
- **Per-module base events** — Each single-service event module defines a base event holding the shared service: `ErrorEvent`, `FeatureEvent`, `AppEvent`, `CliEvent`, `DIEvent`, `LoggingEvent`, `SqliteEvent`. Concrete events extend the base and keep only their `execute` (and `@DomainEvent.parameters_required`). Static events (`events/static.py`) are unchanged.
- **Domain object rename** — The feature step domain object `FeatureEvent` was renamed to `EventFeatureStep` (mappers `FeatureEventAggregate`/`FeatureEventYamlObject` → `EventFeatureStepAggregate`/`EventFeatureStepYamlObject`) to free the `FeatureEvent` name for the new base event.
- **Async feature split** — Async step execution moved into `AsyncFeatureContext(FeatureContext)`; a `Feature.is_async` flag selects it, and the hub drives it via `_run_coroutine` while keeping `run()` synchronous.
- **Code style** — A new `# *** functions` module preamble section documents side-effect-free module-level functions (e.g., the SQLite identifier helper in `events/sqlite.py`).
- **Event-free DI + resolver composition event** — `tiferet/di/settings.py` is now event-free and asset-free: `ServiceContainer.get_service` and `ServiceResolver.build_type_map` assume best-case inputs and let raw exceptions surface; the `container_factory`/`default_container` indirection was removed in favor of an injected `parse_parameter` callable (default identity). The defaults-merge and signature/flag/cache helpers were extracted as pure `# *** functions` (`merge_settings`, `injectable_parameter_names`, `normalize_flags`, `create_cache_key`) and exported from `tiferet/di/__init__.py`. `ServiceResolver` construction moved into the new `CreateServiceResolver` bootstrap event (`tiferet/events/blueprint.py`); the blueprint's `build_config_index` helper was removed and `main.py` gained a `# *** functions` section (`resolve_ctor_kwargs`, `build_wiring_constants`, `resolve_collaborators`). `FeatureContext.load_feature_middleware` now raises a new `MIDDLEWARE_LOADING_FAILED` error, and the dead `AppInterface.service_provider_path` / `service_provider_class_name` fields were removed. `ListAllSettings` (wired as `di_list_all_configs_evt`) is retained and refactored to delegate to `merge_settings`.

### v2.0.0b9: Declarative Context Architecture (Minimal Hub)

The v2.0.0b9 release standardizes contexts under a `BaseContext` registry and makes the application interface context a minimal, declaratively-constructed hub. Key changes:

- **`BaseContext` + `ContextMeta`** (`tiferet/contexts/base.py`) — New base class and metaclass. Contexts declare a `domain_type` ClassVar; the metaclass registers each `{domain_type: context_class}` pair (own-namespace declarations only, so subclasses do not clobber base registrations). `BaseContext.for_domain(DomainType)` resolves the registered class (raising `CONTEXT_NOT_FOUND` when missing); `BaseContext.from_domain(domain_obj, **kwargs)` constructs the context and binds the object as `ctx.domain`.
- **`AppInterfaceContext` is now a minimal hub** — It no longer stores `interface_id`/`features`/`errors`/`logging`. Its constructor takes collaborators (`get_feature_evt`, `get_error_evt`, `di_list_all_configs_evt`, `logging_list_all_evt`, `create_service_provider`, `cache`) plus bootstrap defaults (`default_features`, `default_commands`, `default_configurations`, `default_constants`). It binds the loaded `AppInterface` via `from_domain` and reads `self.domain.id` / `self.domain.logger_id` on demand. The `FeatureContext` and `ErrorContext` are built on demand (resolved via `BaseContext.for_domain`) inside `execute_feature` / `handle_error`; the shared `DIContext` and `LoggingContext` remain lazily cached (`load_logging_context`). Domain objects are loaded and cached via `load_feature_domain` / `load_error_domain`, all sharing one `CacheContext`. Response handling delegates directly to `RequestContext.handle_response()` — the hub no longer defines its own `handle_response`.
- **Declarative construction** — `load_app_instance` resolves the events/repos by name from the DI container, imports the context class from the interface's `module_path`/`class_name` (custom contexts like `FlaskApiContext` still work), and constructs it via `from_domain`. The dependency type mapping is built by the static `AppInterfaceContext.get_service_type_mapping(app_interface)` (moved off the `AppInterface` domain model, which retains only `AppServiceDependency.get_service_type()`); it does not add an `app_context` entry, and `DEFAULT_SERVICES` no longer registers the `services`/`features`/`errors`/`logging` contexts.
- **Specialized contexts are pure operational behavior** — `FeatureContext.execute_feature(feature, request)` (and async/`resolve_feature_steps`) accept a pre-loaded `Feature`; feature retrieval moved to the hub. The feature-step executor is `handle_feature_step` / `handle_feature_step_async` (renamed from `handle_command`). `ErrorContext.format_response(error, exception, lang)` assembles the structured response from a pre-loaded `Error` via `Error.format_message` — response assembly was moved off the `Error` domain model (which keeps `format_message`; `ErrorMessage.format` is unchanged). The b9 `set_default_*` setters were removed; bootstrap defaults are seeded on the hub initializer and threaded through `realize_interface(..., default_*=...)`. Only `BaseContext` and `ContextMeta` are exported from `tiferet/contexts/__init__.py`; domain contexts are imported from their submodules.

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
