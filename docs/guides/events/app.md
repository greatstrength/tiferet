# Events – App Session Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/app.py`  
**Version:** 2.0.0

## Overview

The app event module provides the full CRUD surface for `AppSession` configurations — the runtime entry-point definitions that describe how a Tiferet application session is assembled. Every event in this module depends on an injected `AppService` and operates on `AppSession` domain objects through the `AppSessionAggregate` mapper.

These events are consumed by the `build_app` blueprint chain during bootstrapping and by management tooling that creates, updates, and removes session configurations.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddAppSession` | Create | `id`, `name` | `AppSession` |
| `GetAppSession` | Read | `id` | `AppSession` |
| `UpdateAppSession` | Update (scalar) | `id` | `AppSession` |
| `ListAppSessions` | Read (all) | *(none)* | `List[AppSession]` |
| `RemoveAppSession` | Delete | `id` | `None` |
| `SetAppConstants` | Update (constants) | `id` | `str` (ID) |
| `SetServiceDependency` | Update (service dep) | `id`, `service_id`, `module_path`, `class_name` | `str` (ID) |
| `RemoveServiceDependency` | Delete (service dep) | `id`, `service_id` | `str` (ID) |

## Dependency

All events inject a single dependency:

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
1. Coerces optional arguments that argparse may pass as `None` to their defaults.
2. Creates an `AppSessionAggregate` via the Pydantic constructor for creation and validation.
3. Saves via `app_service.save(app_session)`.

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

Retrieves an `AppSession` by ID via the `AppService` abstraction.

**Required:** `id`

**Returns:** The loaded `AppSession` instance.

**Error:** Raises `APP_SESSION_NOT_FOUND` if the session does not exist.

**Behavior:**
1. Retrieves the session via `app_service.get(id)`.
2. Raises a structured error if `None`.
3. Returns the loaded session.

```python
app_session = DomainEvent.handle(
    GetAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
)
```

### UpdateAppSession

Updates scalar attributes of an existing app session. Each provided attribute is updated via `AppSessionAggregate.set_attribute()`, which enforces a gated allowlist of mutable fields.

**Required:** `id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str \| None` | `None` | The new name value, or `None` to leave unchanged |
| `description` | `str \| None` | `None` | The new description value, or `None` to leave unchanged |
| `logger_id` | `str \| None` | `None` | The new logger id value, or `None` to leave unchanged |

**Returns:** The updated `AppSession` instance.

**Error:** Raises `APP_SESSION_NOT_FOUND` if the session does not exist.

```python
DomainEvent.handle(
    UpdateAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
    description='Updated description',
)
```

### ListAppSessions

Lists all configured application sessions. No required parameters.

**Returns:** `List[AppSession]` — may be empty.

```python
app_sessions = DomainEvent.handle(
    ListAppSessions,
    dependencies={'app_service': app_service},
)
```

### RemoveAppSession

Removes an app session configuration by ID. The operation is **idempotent** — removing a non-existent session does not raise an error.

**Required:** `id`

**Returns:** `None`

```python
DomainEvent.handle(
    RemoveAppSession,
    dependencies={'app_service': app_service},
    id='my_app',
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

Adds or updates a service dependency on an app session. Uses PUT semantics — if the `service_id` already exists, the dependency is updated in place with parameter merge-and-prune; if it does not exist, a new dependency is created.

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

Removes a service dependency from an app session by `service_id`. The operation is **idempotent** — removing a non-existent service does not raise an error.

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

## Common Patterns

### Retrieve → Verify → Mutate → Save

Most mutation events follow the same four-step pattern:

1. **Retrieve** the `AppSession` via `app_service.get(id)`.
2. **Verify** it exists using `self.verify()`.
3. **Mutate** the aggregate via its domain methods (`set_attribute`, `set_service`, `set_constants`, etc.).
4. **Save** the updated aggregate via `app_service.save(app_session)`.

This pattern ensures that domain rules are enforced by the aggregate, not the event, and that persistence is always explicit.

### Idempotent Deletes

Both `RemoveServiceDependency` and `RemoveAppSession` are idempotent — they delegate to `AppService.delete()`/aggregate removal, which succeeds silently if the target does not exist. This simplifies orchestration workflows where deletions may be retried.

## Related Documentation

- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain objects
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md) — Mapper strategies
