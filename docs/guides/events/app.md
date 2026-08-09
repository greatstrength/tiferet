# Events – App Session Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/app.py`  
**Version:** 2.0.0

## Overview

The app event module provides the CRUD surface for `AppSession` configurations — the declared entry points that define how a Tiferet application is assembled at runtime. Every event in this module extends the shared `AppEvent` base event (which injects `AppService`) and operates on `AppSession` domain objects through the `AppSessionAggregate` mapper. **Vision:** see the `AppEvent` class docstring in `tiferet/events/app.py` for the value statement this guide distills.

These events are consumed by `core.build_app`/`cli.build_app` during session resolution (`GetAppSession`) and by management tooling that creates, updates, and removes session configurations.

## Ubiquitous Language

- **App session** — an `AppSession` domain object: a declared application entry point with an id, service dependencies, and constants, resolved by `GetAppSession` at bootstrap.
- **Service dependency** — one `AppServiceDependency` entry (`service_id`, `module_path`, `class_name`, `parameters`) on a session's `services` list, mutated as a unit via `set_service`/`remove_service`.
- **Constants** — the session-level `constants` dict merged beneath (i.e. overridden by) the framework's `CORE_DEFAULT_CONSTANTS` when `build_app_service_container` composes the app-level container.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddAppSession` | Create | `id`, `name` | `AppSession` |
| `GetAppSession` | Read | `id` | `AppSession` |
| `ListAppSessions` | Read (all) | *(none)* | `List[AppSession]` |
| `UpdateAppSession` | Update (scalar) | `id`, `attribute` | `str` (ID) |
| `SetAppConstants` | Update (constants) | `id` | `str` (ID) |
| `SetServiceDependency` | Update (service dep) | `id`, `service_id`, `module_path`, `class_name` | `str` (ID) |
| `RemoveServiceDependency` | Delete (service dep) | `id`, `service_id` | `str` (ID) |
| `RemoveAppSession` | Delete | `id` | `str` (ID) |

## Dependency

<a id="appevent"></a>
All events extend the shared `AppEvent` base event, which injects a single dependency:

- **`app_service: AppService`** — the service interface for persisting and retrieving `AppSession` configurations.

## Event Details

### AddAppSession

Creates a new `AppSession` and persists it via `AppService.save()`.

**Required:** `id`, `name`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `description` | `str \| None` | `None` | Human-readable description |
| `logger_id` | `str` | `'default'` | Logger configuration identifier |
| `flags` | `List[str]` | `['default']` | Flags for dependency resolution |
| `services` | `List[Dict]` | `[]` | Service dependency definitions (each dict has `service_id`, `module_path`, `class_name`, optional `parameters`) |
| `constants` | `Dict[str, str]` | `{}` | Constant values for the DI injector |

**Returns:** The created `AppSession` instance.

**Behavior:**
1. Coerces argparse-style `None` optionals back to their declared defaults.
2. Creates an `AppSessionAggregate` via the Pydantic constructor for creation and validation.
3. Saves via `app_service.save(session)`.

```python
result = DomainEvent.handle(
    AddAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
    name='My Application',
    services=[{
        'service_id': 'db_service',
        'module_path': 'myapp.repos.db',
        'class_name': 'DbRepository',
        'parameters': {'connection_string': 'sqlite:///app.db'},
    }],
)
```

### GetAppSession

Retrieves an `AppSession` by ID from the app service. It is a repo-only read — it does not consult the built-in bootstrap catalog seeded into the shared cache by `build_cache`; `core.get_app_session` calls this event only after that cache lookup misses.

**Required:** `id`

**Returns:** The loaded `AppSession` instance.

**Error:** Raises `APP_SESSION_NOT_FOUND` if the session does not exist.

**Behavior:**
1. Retrieves the session via `app_service.get(id)`.
2. Raises a structured error if `None`.
3. Returns the loaded session.

```python
session = DomainEvent.handle(
    GetAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
)
```

### ListAppSessions

Lists all configured app sessions. No required parameters.

**Returns:** `List[AppSession]` — may be empty.

```python
sessions = DomainEvent.handle(
    ListAppSessions,
    dependencies={'app_service': app_service},
)
```

### UpdateAppSession

Updates a single scalar attribute on an existing app session. The attribute is updated via `AppSessionAggregate.set_attribute()`, which enforces a gated allowlist of mutable fields.

**Required:** `id`, `attribute`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `value` | `Any` | — | The new value for the attribute |

**Returns:** `str` — the session ID.

**Errors:**
- `APP_SESSION_NOT_FOUND` if the session does not exist.
- `ATTRIBUTE_NOT_SETTABLE` if the attribute name is not in the supported set. This is a `ModelError`, not a `TiferetError`, so it leaks to the caller unformatted rather than being resolved through the error catalog.

**Supported attributes:** `name`, `description`, `logger_id`, `flags`. The `id` identity field and the `services`/`constants` collections (owned by `add_service`/`set_service`/`set_constants`) are refused as mutation-policy violations.

```python
DomainEvent.handle(
    UpdateAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
    attribute='description',
    value='Updated description',
)
```

### SetAppConstants

Sets, merges, or clears constants on an app session.

**Required:** `id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `constants` | `dict[str, Any] \| None` | `None` | Constants to apply. `None` clears all constants. Dict keys with `None` values are removed; others are merged. |

**Returns:** `str` — the session ID.

**Error:** Raises `APP_SESSION_NOT_FOUND` if the session does not exist.

**Merge semantics** (delegated to `AppSessionAggregate.set_constants`):
- `constants=None` → clears all constants.
- `constants={'KEY': 'val'}` → merges into existing; existing keys are overwritten.
- `constants={'KEY': None}` → removes `KEY` from the constants dict.

```python
# Merge new constants
DomainEvent.handle(
    SetAppConstants,
    dependencies={'app_service': app_service},
    id='my_app',
    constants={'DB_HOST': 'localhost', 'DB_PORT': '5432'},
)

# Clear all constants
DomainEvent.handle(
    SetAppConstants,
    dependencies={'app_service': app_service},
    id='my_app',
    constants=None,
)
```

### SetServiceDependency

Adds or updates a service dependency on an app session. Uses PUT semantics — if the `service_id` already exists, the dependency is updated in place with parameter merge-and-prune (delegated to `AppSessionAggregate.set_service`); if it does not exist, a new dependency is created.

**Required:** `id`, `service_id`, `module_path`, `class_name`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `parameters` | `dict[str, Any] \| None` | `None` | Parameters for the service dependency. `None` clears existing parameters. Dict keys with `None` values are pruned. |

**Returns:** `str` — the session ID.

**Error:** Raises `APP_SESSION_NOT_FOUND` if the session does not exist.

```python
DomainEvent.handle(
    SetServiceDependency,
    dependencies={'app_service': app_service},
    id='my_app',
    service_id='cache_service',
    module_path='myapp.services.cache',
    class_name='RedisCacheService',
    parameters={'host': 'localhost', 'port': '6379'},
)
```

### RemoveServiceDependency

Removes a service dependency from an app session by `service_id`, delegating to `AppSessionAggregate.remove_service`. The operation is **idempotent** — removing a non-existent service does not raise an error.

**Required:** `id`, `service_id`

**Returns:** `str` — the session ID.

**Error:** Raises `APP_SESSION_NOT_FOUND` if the session does not exist.

```python
DomainEvent.handle(
    RemoveServiceDependency,
    dependencies={'app_service': app_service},
    id='my_app',
    service_id='cache_service',
)
```

### RemoveAppSession

Deletes an entire app session configuration by ID. The operation is **idempotent** — removing a non-existent session does not raise an error.

**Required:** `id`

**Returns:** `str` — the removed session ID.

```python
DomainEvent.handle(
    RemoveAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
)
```

## Common Patterns

### Retrieve → Verify → Mutate → Save

Most mutation events follow the same four-step pattern:

1. **Retrieve** the `AppSession` via `app_service.get(id)`.
2. **Verify** it exists using `self.verify()` or `self.raise_error()`.
3. **Mutate** the aggregate via its domain methods (`set_attribute`, `set_service`, `set_constants`, etc.).
4. **Save** the updated aggregate via `app_service.save(session)`.

This pattern ensures that domain rules are enforced by the aggregate, not the event, and that persistence is always explicit.

### Idempotent Deletes

Both `RemoveServiceDependency` and `RemoveAppSession` are idempotent — they succeed silently if the target does not exist. This simplifies orchestration workflows where deletions may be retried.

### Bootstrap Session Seeding

Unlike error/feature/CLI-command catalogs, built-in app sessions (e.g. `tiferet_cli`) are seeded directly into the shared cache by `add_default_app_sessions` (`tiferet/contexts/app.py`) rather than resolved through a fallback event parameter. `core.get_app_session` checks that cache first and only calls `GetAppSession` on a miss — this event never sees or merges bootstrap defaults itself.

## Boundaries

**Inside this domain:** the CRUD operations for `AppSession` configurations — create, read, list, scalar/constants/service-dependency updates, and idempotent deletes.
**Outside this domain:** the declared `AppSession`/`AppServiceDependency` shape itself ([docs/guides/domain/app.md](../domain/app.md)); bootstrap cache-seeding and session resolution (`core.get_app_session`, `add_default_app_sessions` — [docs/guides/blueprints.md](../blueprints.md)); composing the app-level DI container from a resolved session's services/constants (`build_app_service_container` — [docs/guides/di.md](../di.md)).

## Related Documentation

- [docs/guides/domain/app.md](../domain/app.md) — `AppSession`/`AppServiceDependency` domain objects
- [docs/guides/blueprints.md](../blueprints.md) — `core.build_app`'s session resolution and cache-seeding
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md) — Mapper strategies
