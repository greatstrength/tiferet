# Domain – App: AppSession and AppServiceDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The App domain defines the structural foundation for application entry points in Tiferet. Every runnable session — whether a REST API, CLI, background worker, or custom context — is described by an `AppSession` domain object. Each session declares logging configuration, dependency-resolution flags, static constants, and a list of injectable service dependency bindings (`AppServiceDependency`). The context implementation used to run the session (e.g. the generic `AppSessionContext` or the CLI-oriented `CliSessionContext`) is selected by which blueprint entrypoint the caller invokes, not declared as an attribute on the session itself.

`AppSession` is a **read-only value object**: it exposes only the `get_service` query and carries no mutation methods. All state changes (adding/removing services, updating constants, renaming) occur exclusively through `AppSessionAggregate` in the mappers layer. The previous domain-level `apply_defaults` mutator has no replacement on the domain object — default service/constant merging now happens at the blueprint layer via `build_app_service_container`.

**Module:** `tiferet/domain/app.py`

## Domain Objects

### AppServiceDependency

Represents a single injectable service dependency binding for an application session.

| Attribute      | Type                   | Required | Default | Description                                                                      |
|----------------|------------------------|----------|---------|------------------------------------------------------------------------------------|
| `module_path`  | `str`                  | Yes      | —       | The module path for the service dependency.                                       |
| `class_name`   | `str`                  | Yes      | —       | The class name for the service dependency.                                        |
| `service_id`   | `str`                  | Yes      | —       | The canonical service id for the application dependency.                          |
| `parameters`   | `Dict[str, str]`       | No       | `{}`    | The parameters for the service dependency.                                        |

No methods. Pure data structure.

#### Rename Note: AppAttribute → AppServiceDependency

In v1.x, service dependency bindings were called `AppAttribute`. In v2.0, the class is renamed to `AppServiceDependency` to better reflect its role as a service dependency binding rather than a generic attribute. The field set and semantics are unchanged.

### AppSession

Represents the complete configuration of an application session — the runtime entry point.

| Attribute      | Type                                | Required | Default       | Description                                           |
|----------------|-------------------------------------|----------|---------------|--------------------------------------------------------|
| `id`           | `str`                               | Yes      | —             | The unique identifier for the application session.     |
| `name`         | `str`                               | Yes      | —             | The name of the application session.                   |
| `description`  | `str \| None`                       | No       | `None`        | The description of the application session.            |
| `logger_id`    | `str`                               | No       | `'default'`   | The logger ID for the application session.             |
| `flags`        | `List[str]`                         | No       | `['default']` | The DI flags for the application session.              |
| `services`     | `List[AppServiceDependency]`        | No       | `[]`          | The application session service dependencies.          |
| `constants`    | `Dict[str, str]`                    | No       | `{}`          | The application session dependency constants.          |

#### Methods

**`get_service(service_id: str) -> AppServiceDependency | None`**

Returns the `AppServiceDependency` whose `service_id` matches the given value, or `None` if no match is found.

```python
service = app_session.get_service('cli_repo')
if service:
    print(service.module_path, service.class_name)
```

## Runtime Role

The `build_app` blueprint (`tiferet/blueprints/core.py`) is the primary consumer of the App domain at runtime. The flow is:

1. **`App('basic_calc', app_config='config.yml')`** calls `build_app`, which builds the bootstrap cache and resolves the app session.
2. **`get_app_session(interface_id, cache, ...)`** retrieves the `AppSession` via the `GetAppSession` domain event, preferring a cache-seeded default session when present.
3. **`build_app_session_context(app_session, cache)`** merges the session's own services/constants with the cache-seeded framework defaults (the session wins on a conflict), composes the service resolver, and wires the five required template-method handlers.
4. The resulting **`AppSessionContext`** is returned, bound to the loaded `AppSession` and ready to execute features via `run()`.

```python
# Simplified runtime flow
from tiferet import App

app = App('basic_calc', app_config='config.yml')  # resolves the session, wires dependencies
result = app.run('calc.add', data={'a': 1, 'b': 2})  # executes features via the wired context
```

## Configuration Mapping

Application sessions are defined in the `sessions` section of the configuration file (typically `config.yml`). Each top-level key under `sessions` maps to an `AppSession`, and nested `attrs` entries map to `AppServiceDependency` objects. Each key under `attrs` becomes the `service_id` of the corresponding `AppServiceDependency`:

```yaml
sessions:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
  basic_calc_cli:
    name: Calculator CLI
    description: Perform basic calculator operations via CLI
    attrs:
      cli_repo:
        module_path: tiferet.repos.cli
        class_name: CliConfigRepository
        params:
          cli_config: config.yml
```

## Domain Events

The following domain events interact with `AppSession` and `AppServiceDependency` (see [docs/guides/events/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/events/app.md) for the complete set):

| Event                | Description                                       |
|----------------------|-----------------------------------------------------|
| `AddAppSession`      | Creates and persists a new `AppSession`.            |
| `GetAppSession`      | Retrieves an `AppSession` by ID.                    |
| `UpdateAppSession`   | Modifies scalar attributes of an existing `AppSession` via aggregate. |
| `RemoveAppSession`   | Removes an `AppSession` by ID (idempotent).         |

These events depend on the `AppService` interface for persistence operations.

## Service Interface

**`AppService`** (`tiferet/interfaces/app.py`) defines the abstract contract for App domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> AppSessionAggregate`
- `list() -> List[AppSessionAggregate]`
- `save(session: AppSessionAggregate) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `AppConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **Dependency Injection:** `AppServiceDependency` entries reference service registrations that are resolved at runtime via the `ServiceResolver`.
- **Feature:** Once a session is loaded and its context instantiated, features defined in the configuration are executed through the `FeatureContext`.
- **Logging:** `AppSession.logger_id` references a logger configuration from the Logging domain.

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

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
