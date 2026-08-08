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
- **ModelError** (`domain/core.py`): Standalone `Exception` (deliberately **not** a `TiferetError`) describing an inconsistency within a single model. Classmethod raisers `raise_error(error_code, message=None, model=None, **kwargs)` and `raise_for_validation(error, ..., model=None)`, the latter classifying a Pydantic `ValidationError` as `INVALID_MODEL_ATTRIBUTE_ID` or `INVALID_MODEL_VALUE_ID` and chaining the cause. Uncatalogued, never formatted as a `TiferetAPIError`, and never skippable via `pass_on_error` — a model defect is a consumer bug that leaks. `ATTRIBUTE_NOT_SETTABLE_ID` covers mutation-policy refusals. Both raisers accept the offending instance as `model` and store a serializable descriptor (`type`, `module`, plus any of `id` / `name` / `key` the model declares) built by the pure `describe_model` helper — the instance-identifying metadata a catalogued `TiferetError` has no need to carry. The pure `unpack_validation_error` helper flattens violations for both the mutation and request-validation paths.
- **DomainEvent** (`events/settings.py`): Base class for domain operations. Receives dependencies via constructor injection. Entry point is `execute(**kwargs)`. Use `@DomainEvent.parameters_required([...])` for declarative input validation. Use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` for invocation in tests. Each single-service event module defines a per-module base event (e.g., `ErrorEvent`, `FeatureEvent`) that holds the shared service injection; concrete events extend the base and define only `execute`.
- **Service** (`interfaces/core.py`): Abstract base class (`ABC`) for all service contracts. All vertical concerns (data access, config, utilities) are unified under Service.
- **ServiceError** (`interfaces/core.py`): The exception a service raises for an **infrastructural** failure — faulty configuration or a lost connection. Deliberately **not** a `TiferetError`, so it is never catalogued, localized, or formatted into an API response; an infrastructural failure that reaches the top is an unhandled exception by design. Raised via the `raise_for` classmethod, which derives the failing service's `module_path` / `class_name` / `target_method` and chains the underlying exception as `__cause__`. It lives beside `Service` because the failure is part of the service contract and every layer holding a service already imports `interfaces`.
- **MiddlewareService** (`interfaces/middleware.py`): Abstract callable that wraps domain event execution. Implement `__call__(self, event, kwargs, next_fn)` for sync middleware or `async def __call__` for async. Resolved from the DI container by `service_id` and composed into an ordered chain by `FeatureContext`.
- **Aggregate** (`mappers/settings.py`): Mutable extension of domain objects. Instantiate via direct constructors. Provides `set_attribute()` for validated mutation with `validate_assignment=True`, converting the resulting Pydantic `ValidationError` into a `ModelError`. The `mappers` layer imports `domain` only.
- **TransferObject** (`mappers/settings.py`): Serialization layer with role-based field control via `_ROLES` ClassVar. Methods: `to_primitive(role)`, `map(target)`, `@classmethod from_model()`. Uses lenient config (`extra='ignore'`).
- **BaseContext** (`contexts/settings.py`): Base class for all contexts, with a `ContextMeta` metaclass registry keyed by `domain_type`. `BaseContext.for_domain(DomainType)` resolves the registered context class; `BaseContext.from_domain(domain_obj, **kwargs)` constructs a context and binds the domain object as `ctx.domain`. The base holds no cache; contexts that need a `CacheContext` (e.g., `AppSessionContext`, `FeatureContext`) wire it themselves. The `AppSessionContext` hub binds the loaded `AppSession` and builds its sub-contexts on demand.

### Runtime Flow

1. `App(interface_id)` (alias for `core.build_app`) resolves the app session and returns an `AppSessionContext`.
2. `core.build_app` builds the shared cache (`build_cache`), composes the app service and resolves the session via the `GetAppSession` event (`get_app_session`), then constructs the context via `build_app_session_context`: it builds the app service container by merging cache defaults with the session's own constants/services (`build_app_service_container`), composes a `ServiceResolver` (`build_service_resolver`), resolves the hub's event collaborators from the app container, and constructs the `AppSessionContext` via `BaseContext.from_domain(app_session, get_dependency=resolver.get_dependency, ...)` — the context graph itself is not DI-resolved. No `apply_defaults` is called on the core path.
3. `AppSessionContext.run(feature_id, data={})` builds a logger, parses the request, loads the `Feature` domain object, executes it, and returns the response.
4. The hub builds its sub-contexts (`FeatureContext`, `ErrorContext`, `LoggingContext`) on demand; `FeatureContext.execute_feature(request)` reads the `Feature` bound as `self.domain` (the context is always constructed via `from_domain`), resolves each step's service via the injected `get_dependency` handler (from `ServiceResolver`) and executes it sequentially. When the loaded `Feature` has `is_async` set, the hub instead selects `AsyncFeatureContext` (a `FeatureContext` subclass) and drives `execute_feature_async` to completion via a `_run_coroutine` helper, keeping `run()` synchronous.
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

- `domain/core.py` — `DomainObject`, `ServiceDependency`, `ModelError`, `describe_model`, `unpack_validation_error`, `INVALID_MODEL_ATTRIBUTE_ID` / `INVALID_MODEL_VALUE_ID` / `ATTRIBUTE_NOT_SETTABLE_ID`
- `domain/app.py` — `AppSession`, `AppServiceDependency`
- `domain/cli.py` — `CliCommand`, `CliArgument`
- `domain/di.py` — `ServiceRegistration` (with `resolve_service` / `get_service_type`), `FlaggedDependency`
- `domain/error.py` — `Error`, `ErrorMessage`
- `domain/feature.py` — `Feature`, `FeatureStep`, `EventFeatureStep`, `ParameterSpecification`, `RequestSpecification` (with `coerce` / `is_satisfied_by`)
- `domain/logging.py` — `Formatter`, `Handler`, `Logger`, `LoggingSettings`

## Interfaces (Services)

- Extend `Service` (ABC) from `tiferet/interfaces/core.py`.
- All methods marked `@abstractmethod`.
- Artifact comments use `# *** interfaces` / `# ** interface: <name>`.
- Services: `AppService`, `CliService`, `ContainerService`, `ErrorService`, `FeatureService`, `FileService`, `LoggingService`, `SqliteService`, `CacheService`, `MiddlewareService`. A Service class outside `interfaces/core.py` with zero subclasses is suspect for removal; the config loaders declare only `FileLoader` and format dispatch belongs to `ConfigurationRepository`.
- **`ServiceError`** (`interfaces/core.py`, in a `# *** classes` section) is the exception every service raises for an infrastructural failure. See Error Handling.

## Mappers

Split into two classes:

- **Aggregate** — Extends domain object + `Aggregate`. Adds mutation methods (`rename()`, `add_command()`, `set_attribute()`). Inherits `validate_assignment=True` from `DomainObject`, so direct `setattr` triggers Pydantic field validation. `set_attribute()` wraps that `setattr` and converts a `ValidationError` via `ModelError.raise_for_validation`, passing `model=self` so the error names the offending aggregate; subclasses with a narrower settable set override it and raise `ATTRIBUTE_NOT_SETTABLE` with the same descriptor.
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

The framework has **three unrelated error families**, one per concern:

- `TiferetError` (`assets/core.py`): a **domain outcome**. Base exception with `error_code` and `kwargs`, plus a `raise_error(cls, error_code, message=None, **kwargs)` classmethod raiser. `TiferetAPIError` extends it with `name` (defaulting to `error_code`) and `message` for API responses; the classmethod raiser dispatches to whichever subclass it is called on. Codes are catalogued in `assets/error.py`, localized, and formatted by `AppSessionContext.run`. Access via `from .. import assets as a` then `a.error.ERROR_CODE_ID`.
- `ServiceError` (`interfaces/core.py`): an **infrastructural failure** — typically faulty configuration or a lost connection. Deliberately **not** a `TiferetError` subclass, so `run` never catches or formats it. Raised via the `raise_for(service, error_code, message, cause=None, **kwargs)` classmethod, which derives `module_path` / `class_name` / `target_method` from the failing service and the calling frame. Codes are **not** catalogued: each is an `_ID` constant in the module that raises it, with an inline English-only f-string message.
- `ModelError` (`domain/core.py`): a **model defect**. Also uncatalogued and never formatted. See Key Concepts.

Only `TiferetError` is catalogued. `pass_on_error` on a feature step passes on **domain** errors only — both step executors catch `TiferetError`, so a `ServiceError`, a `ModelError`, or any other exception propagates instead of resolving to `None`.

### Error Code Hosting

`assets/error.py` holds domain codes only: `CORE_DEFAULT_ERRORS` (15 entries) plus `ADMIN_DEFAULT_ERRORS` (13 of its own). The acceptance rule is that **every catalogued code has a raiser somewhere in `tiferet/`**; do not pre-create entries for anticipated needs.

Infrastructure codes live beside their raise sites:

- `utils/file.py` — `FILE_NOT_FOUND_ID`, `FILE_ALREADY_OPEN_ID`, `INVALID_FILE_ID`, `INVALID_FILE_MODE_ID`, `INVALID_ENCODING_ID`
- `utils/yaml.py` — `YAML_FILE_NOT_FOUND_ID`, `YAML_FILE_LOAD_ERROR_ID`, `YAML_FILE_SAVE_ERROR_ID`
- `utils/json.py` — `JSON_FILE_NOT_FOUND_ID`, `JSON_FILE_LOAD_ERROR_ID`, `JSON_FILE_SAVE_ERROR_ID`, `INVALID_JSON_PATH_ID`
- `utils/toml.py` — `TOML_FILE_NOT_FOUND_ID`, `TOML_FILE_LOAD_ERROR_ID`, `INVALID_TOML_FILE_ID`
- `utils/csv.py` — `CSV_FIELDNAMES_REQUIRED_ID`, `CSV_INVALID_READ_MODE_ID`, `CSV_INVALID_WRITE_MODE_ID`
- `utils/sqlite.py` — `SQLITE_CONN_FAILED_ID`, `SQLITE_CONN_ALREADY_OPEN_ID`, `SQLITE_CONN_NOT_INITIALIZED_ID`, `SQLITE_INVALID_MODE_ID`, `SQLITE_STATEMENT_FAILED_ID`, `SQLITE_QUERY_FAILED_ID`, `SQLITE_TRANSACTION_FAILED_ID`, `SQLITE_BACKUP_FAILED_ID`
- `repos/core.py` — `UNSUPPORTED_CONFIG_FILE_TYPE_ID`
- `di/dependency_injector.py` — `DI_DEPENDENCY_NOT_REGISTERED_ID`

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
- **Test location:** `tests/<component>/` at the repository root (e.g., `tests/domain/`, `tests/events/`, `tests/mappers/`).
- **Integration tests:** `tiferet/tests_int/`.
- **Run tests:** `pytest tests/` (or plain `pytest` per `pyproject.toml`) from project root (with venv activated).
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

**No `sqlite3` exception escapes the client.** Every driver call is wrapped as a `ServiceError`: `SQLITE_STATEMENT_FAILED` (`execute` / `executemany` / `executescript`), `SQLITE_QUERY_FAILED` (row retrieval in `fetch_one` / `fetch_all`), `SQLITE_TRANSACTION_FAILED` (`commit` / `rollback`), `SQLITE_CONN_FAILED` (connect), and `SQLITE_BACKUP_FAILED` (`backup`), each preserving the driver exception as `__cause__`. `sqlite3.IntegrityError` gets no special handling — a consumer needing domain semantics for a constraint violation catches the specific code inside its own event.

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
- `Service`, `ServiceError` (from `tiferet.interfaces`)

**Mappers:**
- `Aggregate`, `TransferObject` (from `tiferet.mappers`)

**Utils:**
- `File`/`FileLoader`, `Yaml`/`YamlLoader`, `Json`/`JsonLoader`, `Csv`/`CsvLoader`, `CsvDict`/`CsvDictLoader`, `Sqlite`/`SqliteClient`

## Key Files for Orientation

- `tiferet/__init__.py` — Version and public exports
- `tiferet/domain/core.py` — `DomainObject` base class (extends `pydantic.BaseModel`), the `ServiceDependency` core model, and the model error protocol (`ModelError`, `describe_model`, `unpack_validation_error`, model error constants)
- `tiferet/events/settings.py` — `DomainEvent` base class (execute, verify, parameters_required, handle)
- `tiferet/mappers/settings.py` — `Aggregate` and `TransferObject` base classes
- `tiferet/interfaces/core.py` — `Service` (ABC) base class and `ServiceError`
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
- `tiferet/assets/core.py` — Shared constants, the `create_default_error` / `create_app_service_dependency` factories, and the `TiferetError` / `TiferetAPIError` exception classes
- `tiferet/assets/app.py` — Default interface definitions and the `CORE_DEFAULT_SERVICES` / `CORE_DEFAULT_CONSTANTS` bootstrap catalogs
- `tiferet/repos/settings.py` — `ConfigurationRepository` base class (format-agnostic config I/O)
- `examples/basic_calculator/` — Working calculator application example

## Migration Notes

### Exception Asset Consolidation

This cycle retires the `assets`/`events` layering workaround the exception classes lived behind and gives `TiferetError` the same classmethod-raiser shape as `ModelError` and `ServiceError`:

- **`assets/exceptions.py` is deleted; `TiferetError` and `TiferetAPIError` move into a new `# *** classes` section in `assets/core.py`**, appended after `# *** functions`. `assets/__init__.py` now imports them from `.core`.
- **`TiferetError` gains a classmethod raiser** — `raise_error(cls, error_code, message=None, **kwargs)` — replacing the standalone `RaiseError` helper class. `raise cls(error_code, message, **kwargs)` dispatches to whichever subclass the method is called on, so `TiferetAPIError.raise_error(...)` raises a `TiferetAPIError` directly.
- **`TiferetAPIError.__init__` is normalized** to `(error_code, message=None, name=None, **kwargs)`, with `name` defaulting to `error_code`. This makes the signature positionally compatible with `TiferetError.__init__`, so the inherited `raise_error` classmethod needs no override.
- **`RaiseError` is retired outright** — `tiferet/events/static.py` and `tests/events/test_static.py` are deleted (the module's only remaining content, after HF-23/HF-24, was a `RaiseError` re-export). `events/__init__.py` drops the `RaiseError` export.
- **`DomainEvent.raise_error`** (`events/core.py`) is reduced to a one-line delegate to `TiferetError.raise_error`, keeping the same signature, `@staticmethod` form, and docstring contract — it remains the documented event-layer idiom (`self.raise_error(...)`).
- **The ten residual `RaiseError.execute` call sites** — seven in `contexts` (`core.py`, `logging.py` ×2, `feature.py` ×4/5 depending on branch state) and three in `blueprints` (`core.py` ×2, `admin.py` ×1) — convert to `TiferetError.raise_error`. `contexts/core.py` and `contexts/logging.py` replace `from ..events import RaiseError, a` with direct `assets` imports, removing the last `contexts` → `events` passthrough for `a`.
- **Zero behavior change** — `RaiseError.execute(error_code, message=None, **kwargs)` raised `TiferetError(error_code, message, **kwargs)`; `TiferetError.raise_error` raises `cls(error_code, message, **kwargs)` where `cls` is `TiferetError` at every converted call site (all pass `error_code` positionally), so the conversion is a pure receiver substitution.
- **Deferred** — `TiferetError.metadata`; the `TiferetError` → `DomainError` rename; an `error_type=` parameter on the raiser (unblocked but not needed, since `TiferetAPIError.raise_error(...)` already expresses it); the mirrored change on `main`.

### Service Error Protocol

This cycle gives `interfaces` its own error vocabulary and severs the last Infrastructure→Actor import edges:

- **`interfaces/core.py` owns `ServiceError`** — A new `# *** classes` section, inserted **between** `# *** imports` and `# *** interfaces`, holds `ServiceError(Exception)` with a `raise_for(service, error_code, message=None, cause=None, **kwargs)` classmethod. It is exported from `tiferet/interfaces/__init__.py`. Standalone by design: because `AppSessionContext.run` catches only `TiferetError`, the leak is structural and needs no change to `run`.
- **Provenance is derived, not hand-passed** — `raise_for` takes the failing service first and derives `module_path` / `class_name` from `type(service)` and `target_method` from the calling frame. Passing `self` names the runtime type, so an unsupported extension configured for the app repository reports `AppConfigRepository`, not the `ConfigurationRepository` mixin holding the raise site. A class may be passed at a static raise site. The `cause` parameter is an addition to the TRD's illustrative signature; it makes `raise ... from cause` explicit at each conversion rather than inferring the active exception from `sys.exc_info()`, which would mis-attribute a cause when a utility is called from inside an unrelated `except` block.
- **`utils` and `repos` no longer import `events`** — All 36 `utils` raise sites plus `repos/core.py` convert to `ServiceError.raise_for`; the `from ..events import RaiseError, a` and `from ..events.core import TiferetError` imports are gone. The documented "`utils` never imports `events`" rule is true for the first time.
- **Codes relocate to their raise sites** — 23 utility codes plus `UNSUPPORTED_CONFIG_FILE_TYPE` migrate out of `assets/error.py` into `# *** constants` sections of the modules that raise them. See Error Code Hosting.
- **The five structured-error passthroughs narrow** — `except TiferetError: raise` becomes `except ServiceError: raise` in `utils/{json,toml,yaml}.py`, keeping a missing file from being relabelled a parse failure.
- **The SQLite driver is fully wrapped** — `execute`, `executemany`, `executescript`, `fetch_one`, `fetch_all`, `commit`, and `rollback` were calling the driver bare; each now converts `sqlite3.Error` into a `ServiceError` with the driver exception as `__cause__`, under three new codes (`SQLITE_STATEMENT_FAILED`, `SQLITE_QUERY_FAILED`, `SQLITE_TRANSACTION_FAILED`). `open_file` widens from `sqlite3.OperationalError` to `sqlite3.Error`. Consequently **all seven `except sqlite3.Error` blocks in `events/sqlite.py` are deleted** along with the six `APP_ERROR` raises, the `SQLITE_BACKUP_FAILED` raise, and the `import sqlite3`; each `try` collapses to its body and a failure propagates unhandled. `events/sqlite.py` is no longer the only module in `events/` with an `except` clause.
- **`ConfigurationService` retired** — `interfaces/config.py` is deleted and the export removed. Zero implementers, zero consumers; the loaders declare only `FileLoader` and format dispatch belongs to `ConfigurationRepository`.
- **DI gains a named guard** — `DIDynamicServiceContainer.get_dependency` raises `DI_DEPENDENCY_NOT_REGISTERED` instead of letting `TypeError: 'NoneType' object is not callable` surface. This widens the documented `di` import allowance from `interfaces.di` to `interfaces`; the event-free/asset-free constraint is unaffected since `ServiceError` is neither.
- **Catalog reduction** — `CORE_DEFAULT_ERRORS` goes 36 → 15 (10 orphans, 10 migrated codes, `UNSUPPORTED_CONFIG_FILE_TYPE`); `ADMIN_DEFAULT_ERRORS` loses 3 of its own. The `SQLITE`/`TOML`/`CSV` group dicts and their `(ids_*)` / `(models_*)` sub-sections are deleted outright, collapsing `DEFAULT_ERRORS` to a `CORE` + `ADMIN` union. `SQLITE_BACKUP_FAILED` migrates out rather than moving into `CORE`, since its only raiser is now the utility. The acceptance criterion — every catalogued code has a raiser in `tiferet/` — holds.
- **Two latent defects fixed in passing** — `INVALID_FILE_MODE`'s catalog template carried a `{modes}` placeholder the raise site never supplied, making `KeyError: 'modes'` reachable; the inline f-string resolves it by construction. `utils/file.py` hardcoded `encoding=None`, so `INVALID_ENCODING` always read "Invalid encoding: None." regardless of the offending value.
- **Deferred** — Converting `ServiceDependency.get_service_type`'s dynamic import (`domain/core.py`) is excluded to keep `domain` framework-import-free; retiring `RaiseError` and consolidating `assets/exceptions.py` belong to the Exception Asset Consolidation item; the mirrored change on `main`.

### Model Error Protocol & Mapper Layer Independence

This cycle gives `domain` its own error vocabulary and removes the two layer-rule violations that depended on borrowing the Actor tier's:

- **`domain/core.py` owns the model error protocol** — New `# *** constants` (`INVALID_MODEL_ATTRIBUTE_ID`, `INVALID_MODEL_VALUE_ID`, `ATTRIBUTE_NOT_SETTABLE_ID`, `MODEL_IDENTITY_FIELDS`), two `# *** functions` helpers (`describe_model`, `unpack_validation_error`), and the `ModelError` class, all exported from `domain/__init__.py`. `ModelError` is a standalone `Exception`; `raise_for_validation` derives its own code from the Pydantic violation type rather than accepting one from the caller.
- **`ModelError` names the offending instance** — A `model` attribute carries a serializable descriptor (`type`, `module`, plus whichever of `id` / `name` / `key` the model declares) produced by `describe_model`, which skips non-primitive values so the descriptor stays JSON-serializable and holds no reference to the instance. Both raisers take the live instance as `model`; `raise_for_validation` falls back to `ValidationError.title` when none is supplied, and its derived message leads with the model type. Because a `ModelError` is read as a defect report rather than a response, this is metadata a catalogued `TiferetError` has no need to carry.
- **`Aggregate.set_attribute` converts instead of pre-checking** — The hand-rolled `model_fields` membership test is gone; `setattr` is wrapped and the `ValidationError` converted with `model=self`, so an invalid *value* is now caught as well as an unknown field. The three whitelist overrides (`CliArgumentAggregate`, `CliCommandAggregate`, `AppSessionAggregate`) raise `ATTRIBUTE_NOT_SETTABLE` with the same descriptor and now substitute their message placeholders, which the unformatted brace template never did.
- **`mappers` imports `domain` only** — The `mappers` → `events` (`RaiseError`, `a`) and `mappers` → `assets` edges are removed with no replacement, eliminating the layer graph's only Infrastructure→Actor edge.
- **Request validation relocated** — `RequestSpecification.validate` becomes `coerce(data)`, which lets Pydantic's `ValidationError` propagate untouched (the rename also retires a shadow of Pydantic's deprecated `BaseModel.validate`); `is_satisfied_by` catches `ValidationError`. Naming the failure `REQUEST_VALIDATION_FAILED` moves to `contexts/feature.py::validate_request`, which flattens violations via `unpack_validation_error`. `REQUEST_VALIDATION_FAILED` stays a catalogued `TiferetError`. **`domain` now has zero framework imports**, making its documented rule true for the first time; `contexts/feature.py` gains the first pydantic import in the `contexts` layer (`# ** infra`).
- **Catalog deletion** — `INVALID_MODEL_ATTRIBUTE`'s id constant, data constant, and `CORE_DEFAULT_ERRORS` entry are removed from `assets/error.py` (propagating to `DEFAULT_ERRORS` / `ADMIN_DEFAULT_ERRORS`). Safe because a `ModelError` never reaches `get_error_handler`, so no masked `ERROR_NOT_FOUND` lookup is possible — and any future attempt to format one now fails loudly.
- **`pass_on_error` narrowed** — `FeatureContext.execute_step` and `_execute_step_async` catch `TiferetError` instead of `Exception`. `pass_on_error` passes on **domain** errors only; a `ModelError` (and, later, a `ServiceError`) propagates, as does any arbitrary bug in an event that previously vanished into `result = None`.
- **Harness** — `AggregateTestBase.test_set_attribute` expects `ModelError` and `tiferet/testing/mappers.py` drops its `assets` dependency. The `set_attribute_params` tuple shape `(attr, value, expect_error_code | None)` is deliberately unchanged, so consumer parametrization rows still bind; consumer subclasses with invalid-case rows must update the expected exception type (the `INVALID_MODEL_ATTRIBUTE` code *value* is unchanged).
- **Deferred** — Formatting a `ModelError` as a `TiferetAPIError` (settled: it leaks); a request-specific error type; strict assignment validation (`coerce_numbers_to_str=True` keeps assignment lax and coercing); replacing the three whitelists with dispatch-to-mutator or a shared `_settable_attributes` ClassVar; the mirrored cleanup on `main`.

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
