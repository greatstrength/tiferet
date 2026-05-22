# Events – App Interface Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/app.py`  
**Version:** 2.0.0

## Overview

The app event module provides the full CRUD surface for `AppInterface` configurations — the blueprints that define how a Tiferet application is assembled at runtime. Every event in this module depends on an injected `AppService` and operates on `AppInterface` domain objects through the `AppInterfaceAggregate` mapper.

These events are consumed by `AppManagerContext` during bootstrapping and by management tooling that creates, updates, and removes interface configurations.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddAppInterface` | Create | `id`, `name`, `module_path`, `class_name` | `AppInterface` |
| `GetAppInterface` | Read | `interface_id` | `AppInterface` |
| `ListAppInterfaces` | Read (all) | *(none)* | `List[AppInterface]` |
| `UpdateAppInterface` | Update (scalar) | `id`, `attribute` | `str` (ID) |
| `SetAppConstants` | Update (constants) | `id` | `str` (ID) |
| `SetServiceDependency` | Update (service dep) | `id`, `service_id`, `module_path`, `class_name` | `str` (ID) |
| `RemoveServiceDependency` | Delete (service dep) | `id`, `service_id` | `str` (ID) |
| `RemoveAppInterface` | Delete | `id` | `str` (ID) |

## Dependency

All events inject a single dependency:

- **`app_service: AppService`** — the service interface for persisting and retrieving `AppInterface` configurations.

## Event Details

### AddAppInterface

Creates a new `AppInterface` and persists it via `AppService.save()`.

**Required:** `id`, `name`, `module_path`, `class_name`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `description` | `str \| None` | `None` | Human-readable description |
| `logger_id` | `str` | `'default'` | Logger configuration identifier |
| `flags` | `List[str]` | `['default']` | Flags for dependency resolution |
| `services` | `List[Dict]` | `[]` | Service dependency definitions (each dict has `service_id`, `module_path`, `class_name`, optional `parameters`) |
| `constants` | `Dict[str, str]` | `{}` | Constant values for the DI injector |

**Returns:** The created `AppInterface` instance.

**Behavior:**
1. Collects all parameters into a data dict.
2. Creates an `AppInterfaceAggregate` via the Pydantic constructor for creation and validation.
3. Saves via `app_service.save(interface)`.

```python
result = DomainEvent.handle(
    AddAppInterface,
    dependencies={'app_service': app_service},
    id='my_app',
    name='My Application',
    module_path='myapp.contexts.main',
    class_name='MainContext',
    services=[{
        'service_id': 'db_service',
        'module_path': 'myapp.repos.db',
        'class_name': 'DbRepository',
        'parameters': {'connection_string': 'sqlite:///app.db'},
    }],
)
```

### GetAppInterface

Retrieves an `AppInterface` by ID. Optionally merges default services into the result for any `service_id` not already present on the interface.

**Required:** `interface_id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `default_services` | `List[AppServiceDependency]` | `[]` | Default service dependencies to merge if their `service_id` is missing |

**Returns:** The loaded `AppInterface` instance.

**Error:** Raises `APP_INTERFACE_NOT_FOUND` if the interface does not exist.

**Behavior:**
1. Retrieves the interface via `app_service.get(interface_id)`.
2. Raises a structured error if `None`.
3. If `default_services` is provided, iterates them and adds any whose `service_id` is not already present on the interface.

```python
interface = DomainEvent.handle(
    GetAppInterface,
    dependencies={'app_service': app_service},
    interface_id='my_app',
    default_services=[default_error_repo, default_feature_repo],
)
```

### ListAppInterfaces

Lists all configured app interfaces. No required parameters.

**Returns:** `List[AppInterface]` — may be empty.

```python
interfaces = DomainEvent.handle(
    ListAppInterfaces,
    dependencies={'app_service': app_service},
)
```

### UpdateAppInterface

Updates a single scalar attribute on an existing app interface. The attribute is updated via `AppInterfaceAggregate.set_attribute()`, which enforces a gated allowlist of mutable fields.

**Required:** `id`, `attribute`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `value` | `Any` | — | The new value for the attribute |

**Returns:** `str` — the interface ID.

**Errors:**
- `APP_INTERFACE_NOT_FOUND` if the interface does not exist.
- `INVALID_MODEL_ATTRIBUTE` if the attribute name is not in the supported set.
- `INVALID_APP_INTERFACE_TYPE` if `module_path` or `class_name` is set to an empty string.

**Supported attributes:** `name`, `description`, `module_path`, `class_name`, `logger_id`, `flags`.

```python
DomainEvent.handle(
    UpdateAppInterface,
    dependencies={'app_service': app_service},
    id='my_app',
    attribute='description',
    value='Updated description',
)
```

### SetAppConstants

Sets, merges, or clears constants on an app interface.

**Required:** `id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `constants` | `dict[str, Any] \| None` | `None` | Constants to apply. `None` clears all constants. Dict keys with `None` values are removed; others are merged. |

**Returns:** `str` — the interface ID.

**Error:** Raises `APP_INTERFACE_NOT_FOUND` if the interface does not exist.

**Merge semantics** (delegated to `AppInterfaceAggregate.set_constants`):
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

Adds or updates a service dependency on an app interface. Uses PUT semantics — if the `service_id` already exists, the dependency is updated in place with parameter merge-and-prune; if it does not exist, a new dependency is created.

**Required:** `id`, `service_id`, `module_path`, `class_name`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `parameters` | `dict[str, Any] \| None` | `None` | Parameters for the service dependency. `None` clears existing parameters. Dict keys with `None` values are pruned. |

**Returns:** `str` — the interface ID.

**Error:** Raises `APP_INTERFACE_NOT_FOUND` if the interface does not exist.

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

Removes a service dependency from an app interface by `service_id`. The operation is **idempotent** — removing a non-existent service does not raise an error.

**Required:** `id`, `service_id`

**Returns:** `str` — the interface ID.

**Error:** Raises `APP_INTERFACE_NOT_FOUND` if the interface does not exist.

```python
DomainEvent.handle(
    RemoveServiceDependency,
    dependencies={'app_service': app_service},
    id='my_app',
    service_id='cache_service',
)
```

### RemoveAppInterface

Deletes an entire app interface configuration by ID. The operation is **idempotent** — removing a non-existent interface does not raise an error.

**Required:** `id`

**Returns:** `str` — the removed interface ID.

```python
DomainEvent.handle(
    RemoveAppInterface,
    dependencies={'app_service': app_service},
    id='my_app',
)
```

## Common Patterns

### Retrieve → Verify → Mutate → Save

Most mutation events follow the same four-step pattern:

1. **Retrieve** the `AppInterface` via `app_service.get(id)`.
2. **Verify** it exists using `self.verify()` or `self.raise_error()`.
3. **Mutate** the aggregate via its domain methods (`set_attribute`, `set_service`, `set_constants`, etc.).
4. **Save** the updated aggregate via `app_service.save(interface)`.

This pattern ensures that domain rules are enforced by the aggregate, not the event, and that persistence is always explicit.

### Idempotent Deletes

Both `RemoveServiceDependency` and `RemoveAppInterface` are idempotent — they succeed silently if the target does not exist. This simplifies orchestration workflows where deletions may be retried.

### Default Service Merging

`GetAppInterface` supports a `default_services` list that is merged into the loaded interface. This is used by `AppManagerContext` to inject framework-level defaults (error repository, feature repository, etc.) that the user doesn't need to declare explicitly.

## Related Documentation

- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain objects
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md) — Mapper strategies
