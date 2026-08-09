# Domain – App: AppSession and AppServiceDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

The App domain defines the structural foundation for application entry points in Tiferet. Every runnable interface — whether a REST API, CLI, background worker, or custom context — is described by an `AppSession` domain object (renamed from `AppInterface` in the v2.0.0b9 declarative-context migration). Each session declares its context implementation, logging configuration, dependency-resolution flags, static constants, and a list of injectable service dependency bindings (`AppServiceDependency`).

`AppSession` is a **read-only value object at the domain level**: it carries one read-only query method (`get_service`) and no mutation methods. All state changes (adding/removing services, updating constants, renaming) occur exclusively through `AppSessionAggregate` in the mappers layer.

**Module:** `tiferet/domain/app.py`
**Vision:** See the `AppSession` class docstring in `tiferet/domain/app.py` for the value statement this guide distills.

## Ubiquitous Language

- **App session** — a declared, runnable application entry point (the framework's "declared application" concept); the current name for what earlier framework versions called an app interface.
- **Service dependency** — one entry in `AppSession.services`, naming a service's module/class/parameters and the `service_id` a feature step resolves it by.
- **Session id** — the unique `AppSession.id`, used to look it up via `AppService`/`GetAppSession` and to key it in the bootstrap session cache.
- **Flags** — the ordered list of DI flag names (`AppSession.flags`) combined with feature/step-level flags at dependency-resolution time.

## Domain Objects

### AppServiceDependency

Extends `ServiceDependency` (`tiferet/domain/core.py`) with the one identity field a bare `ServiceDependency` lacks: the `service_id` a feature step or context collaborator resolves it by.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="appservicedependency-service-id"></a>`service_id` | `str` | Yes | — | The service id for the application dependency. |
| <a id="appservicedependency-module-path"></a>`module_path` | `str` | Yes | — | Inherited from `ServiceDependency`. The module path for the service dependency. |
| <a id="appservicedependency-class-name"></a>`class_name` | `str` | Yes | — | Inherited from `ServiceDependency`. The class name for the service dependency. |
| <a id="appservicedependency-parameters"></a>`parameters` | `Dict[str, str]` | No | `{}` | Inherited from `ServiceDependency`. The parameters for the service dependency. |

No methods beyond the inherited `get_service_type()` (see [docs/guides/domain/core.md](core.md#servicedependency-get-service-type)).

### AppSession

The complete, declared configuration of one application entry point.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="appsession-id"></a>`id` | `str` | Yes | — | The unique identifier for the application session. |
| <a id="appsession-name"></a>`name` | `str` | Yes | — | The name of the application session. |
| <a id="appsession-description"></a>`description` | `str \| None` | No | `None` | The description of the application session. |
| <a id="appsession-logger-id"></a>`logger_id` | `str` | No | `'default'` | The logger ID for the application instance. |
| <a id="appsession-flags"></a>`flags` | `List[str]` | No | `['default']` | The flags for the application session. |
| <a id="appsession-services"></a>`services` | `List[AppServiceDependency]` | No | `[]` | The application instance service dependencies. |
| <a id="appsession-constants"></a>`constants` | `Dict[str, str]` | No | `{}` | The application dependency constants. |

Note: unlike the retired `AppInterface`, `AppSession` carries no `module_path`/`class_name` context-implementation fields directly on the domain object — the declared context class is resolved from configuration at the blueprint layer (see Runtime Role below), not stored as an `AppSession` attribute.

#### Methods

<a id="appsession-get-service"></a>
**`get_service(service_id: str) -> AppServiceDependency | None`**

Returns the first `AppServiceDependency` whose `service_id` matches the given value, or `None` if no match is found. Checks `service_id` only — there is no `attribute_id` fallback; that field was retired along with `AppInterface`.

```python
service = app_session.get_service('cli_repo')
if service:
    print(service.module_path, service.class_name)
```

## Runtime Role

The `build_app` blueprint (`tiferet/blueprints/core.py`, exported as `App`) is the primary consumer of the App domain at runtime. The flow is:

1. **`App('basic_calc', app_config='config.yml')`** calls `core.build_app`, which chains `build_cache`, `get_app_session`, and `build_app_session_context`.
2. **`get_app_session(interface_id, cache, ...)`** composes the app service and retrieves the `AppSession` via the `GetAppSession` event, raising `APP_SESSION_NOT_FOUND` when absent.
3. **`build_app_session_context(app_session, cache)`** merges cache-seeded framework defaults with the session's own services and constants (`build_app_service_container`), composes a `ServiceResolver` (`build_service_resolver`), imports the declared context class, resolves its event collaborators from the app container, and constructs the context via `BaseContext.from_domain`, injecting `resolver.get_dependency`.
4. The resulting `AppSessionContext` is validated and returned, ready to execute features.

```python
# Simplified runtime flow
from tiferet import App

app = App('basic_calc', app_config='config.yml')  # resolves session, wires dependencies
result = app.run('calc.add', data={'a': 1, 'b': 2})  # executes features via the wired context
```

## Configuration Mapping

Application sessions are defined in the `interfaces` section of the configuration file (typically `config.yml`) — the config-file section name is unchanged even though the domain object is now `AppSession`. Each top-level key under `interfaces` maps to an `AppSession`, and nested `attrs` entries map to `AppServiceDependency` objects. Each key under `attrs` becomes the `service_id` of the corresponding `AppServiceDependency`:

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
  basic_calc_cli:
    name: Calculator CLI
    description: Perform basic calculator operations via CLI
    module_path: tiferet.contexts.cli
    class_name: CliContext
    attrs:
      cli_repo:
        module_path: tiferet.repos.cli
        class_name: CliConfigRepository
        params:
          cli_config: config.yml
```

CLI interfaces declare `module_path: tiferet.contexts.cli` / `class_name: CliContext` to opt into the CLI context; the `build_cli` blueprint realizes that context and delegates argv parsing to `CliContext.run_cli`.

## Domain Events

The following domain events (`tiferet/events/app.py`) interact with `AppSession` and `AppServiceDependency` — note these are `*AppSession` names throughout, not the retired `*AppInterface` names:

| Event | Description |
|---|---|
| `AddAppSession` | Creates and persists a new `AppSession`. |
| `GetAppSession` | Retrieves an `AppSession` by ID, raising `APP_SESSION_NOT_FOUND` if absent. |
| `UpdateAppSession` | Updates a scalar attribute (`name`, `description`, `logger_id`, `flags`) via `AppSessionAggregate.set_attribute`. |
| `SetAppConstants` | Sets or clears constants on a session via `AppSessionAggregate.set_constants`. |
| `ListAppSessions` | Lists all configured app sessions. |
| `SetServiceDependency` | Sets or updates a service dependency (PUT semantics) via `AppSessionAggregate.set_service`. |
| `RemoveServiceDependency` | Removes a service dependency by `service_id` (idempotent) via `AppSessionAggregate.remove_service`. |
| `RemoveAppSession` | Removes an entire app session by ID (idempotent). |

These events depend on the shared `AppService` interface for persistence operations.

## Service Interface

**`AppService`** (`tiferet/interfaces/app.py`) defines the abstract contract for App domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> AppSessionAggregate`
- `list() -> List[AppSessionAggregate]`
- `save(session: AppSessionAggregate) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `AppConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **Core:** `AppServiceDependency` extends `ServiceDependency` (`docs/guides/domain/core.md`), reusing its `module_path`/`class_name`/`parameters` shape and `get_service_type()` method rather than redeclaring them.
- **Mappers:** `AppSessionAggregate` (`tiferet/mappers/app.py`) owns all mutation — `add_service`, `remove_service`, `set_service`, `set_constants`, and a whitelist-gated `set_attribute` that raises `ATTRIBUTE_NOT_SETTABLE` (via `ModelError`, not a domain-level rejection) for `id`/`services`/`constants`, which have their own dedicated mutators.
- **Dependency Injection:** `AppSession.services` entries declare the session's events and repositories; feature-step service registrations are resolved at runtime by `ServiceResolver` via the injected `get_dependency` handler.
- **Feature:** Once a session is loaded and its context instantiated, features defined in the configuration are executed through the `FeatureContext`.
- **Logging:** `AppSession.logger_id` references a logger configuration from the Logging domain (`docs/guides/domain/logging.md`).

## Boundaries

**Inside this domain:** the declared shape of an application entry point (`AppSession`) and its injectable service dependency bindings (`AppServiceDependency`).
**Outside this domain:** mutation logic (owned by `AppSessionAggregate` in `mappers`), resolving a service dependency into a live instance (`ServiceResolver`/`DIDynamicServiceResolver`, `docs/guides/di.md`), and the context class the session's configuration ultimately instantiates (`docs/core/contexts.md`) — `AppSession` itself carries no `module_path`/`class_name` context fields.

## Instantiation

Both domain objects are instantiated directly via the Pydantic constructor:

```python
from tiferet.domain import AppServiceDependency, AppSession

dep = AppServiceDependency(
    service_id='cli_repo',
    module_path='tiferet.repos.cli',
    class_name='CliConfigRepository',
    parameters={'cli_config': 'config.yml'},
)

session = AppSession(
    id='basic_calc_cli',
    name='Calculator CLI',
    services=[dep],
)
```

## Related Documentation

- [docs/guides/domain/core.md](core.md) — `ServiceDependency`, the base class `AppServiceDependency` extends
- [docs/guides/di.md](../di.md) — how a declared service dependency is resolved into a live instance
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
