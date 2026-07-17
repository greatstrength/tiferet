# Events – DI Service Registration Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/di.py`  
**Version:** 2.0.0

## Overview

The DI event module provides the full CRUD surface for `ServiceRegistration` objects — the dependency injection blueprints that define how services are resolved and wired at runtime. Every event in this module depends on an injected `DIService` and operates on `ServiceRegistration` domain objects through the `ServiceRegistrationAggregate` mapper.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddServiceRegistration` | Create | `id` | `ServiceRegistration` |
| `SetDefaultServiceRegistration` | Update (default type) | *(none — `id` is positional)* | `ServiceRegistration` |
| `SetServiceDependency` | Update (flagged dep) | `flag` | `str` (ID) |
| `RemoveServiceDependency` | Delete (flagged dep) | `flag` | `str` (ID) |
| `RemoveServiceRegistration` | Delete | `id` | `str` (ID) |
| `SetServiceConstants` | Update (constants) | *(none)* | `Dict[str, Any]` |
| `ListAllSettings` | Read (all) | *(none)* | `Tuple[List[ServiceRegistration], Dict]` |

## Dependency

All events inject a single dependency:

- **`di_service: DIService`** — the service interface for persisting and retrieving `ServiceRegistration` objects and constants.

## Event Details

### AddServiceRegistration

Creates a new `ServiceRegistration` and persists it via `DIService.save_registration()`. A registration must define at least one type source: either a default type (`module_path` + `class_name`) or one or more flagged dependencies.

**Required:** `id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `module_path` | `str \| None` | `None` | Default module path for the service class |
| `class_name` | `str \| None` | `None` | Default class name for the service class |
| `parameters` | `Dict[str, Any]` | `{}` | Default registration parameters |
| `flagged_dependencies` | `List[Dict[str, Any]]` | `[]` | List of flagged dependency dicts (each with `flag`, `module_path`, `class_name`, optional `parameters`) |

**Returns:** The created `ServiceRegistration` instance.

**Errors:**
- `SERVICE_REGISTRATION_ALREADY_EXISTS` if a registration with the given ID already exists.
- `INVALID_SERVICE_REGISTRATION` if neither a default type nor dependencies are provided.

**Behavior:**
1. Verifies the ID does not already exist via `di_service.registration_exists(id)`.
2. Validates that at least one type source is provided.
3. Creates a `ServiceRegistrationAggregate` via its constructor.
4. Saves via `di_service.save_registration(registration)`.

```python
result = DomainEvent.handle(
    AddServiceRegistration,
    dependencies={'di_service': di_service},
    id='error_repo',
    module_path='myapp.repos.error',
    class_name='ErrorConfigRepository',
    parameters={'error_config': 'app/configs/error.yml'},
)
```

### SetDefaultServiceRegistration

Sets or updates the default module/class and parameters for an existing service registration.

**Required:** `id` (positional)

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `module_path` | `str \| None` | `None` | New default module path |
| `class_name` | `str \| None` | `None` | New default class name |
| `parameters` | `Dict[str, Any] \| None` | `None` | New parameters. `None` clears all parameters. |

**Returns:** The updated `ServiceRegistration` instance.

**Errors:**
- `SERVICE_REGISTRATION_NOT_FOUND` if the registration does not exist.
- `INVALID_SERVICE_REGISTRATION` if only one of `module_path` or `class_name` is provided (both must be provided for an atomic type update).

**Behavior:**
- If both `module_path` and `class_name` are provided, updates the default type and parameters.
- If neither is provided, only parameters are updated (or cleared) while keeping the existing type.
- Parameters with `None` values are removed from the dict.

```python
DomainEvent.handle(
    SetDefaultServiceRegistration,
    dependencies={'di_service': di_service},
    id='error_repo',
    module_path='myapp.repos.error',
    class_name='ErrorConfigRepository',
    parameters={'error_config': 'app/configs/error.json'},
)
```

### SetServiceDependency

Adds or updates a flagged dependency on an existing service registration. Uses PUT semantics — if the flag already exists, the dependency is updated in place with parameter merge-and-prune; if it does not exist, a new dependency is created.

**Required:** `flag`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | — | The service registration identifier |
| `module_path` | `str` | — | The module path for the dependency |
| `class_name` | `str` | — | The class name for the dependency |
| `parameters` | `Dict[str, Any]` | `{}` | Parameters for the dependency. Keys with `None` values are pruned during merge. |

**Returns:** `str` — the service registration ID.

**Errors:**
- `INVALID_FLAGGED_DEPENDENCY` if either `module_path` or `class_name` is empty.
- `SERVICE_REGISTRATION_NOT_FOUND` if the registration does not exist.

```python
DomainEvent.handle(
    SetServiceDependency,
    dependencies={'di_service': di_service},
    id='error_repo',
    flag='json',
    module_path='myapp.repos.error',
    class_name='ErrorConfigRepository',
    parameters={'error_config': 'app/configs/error.json'},
)
```

### RemoveServiceDependency

Removes a flagged dependency from an existing service registration by flag. The removal is **idempotent** at the model level — removing a non-existent flag does not raise an error. However, post-removal validation ensures at least one type source remains.

**Required:** `flag`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | — | The service registration identifier |

**Returns:** `str` — the service registration ID.

**Errors:**
- `SERVICE_REGISTRATION_NOT_FOUND` if the registration does not exist.
- `INVALID_SERVICE_REGISTRATION` if removing the dependency would leave no type source (no default type and no remaining dependencies).

```python
DomainEvent.handle(
    RemoveServiceDependency,
    dependencies={'di_service': di_service},
    id='error_repo',
    flag='json',
)
```

### RemoveServiceRegistration

Deletes an entire service registration by ID. The operation is **idempotent** — the underlying service handles non-existent IDs gracefully.

**Required:** `id`

**Returns:** `str` — the removed registration ID.

```python
DomainEvent.handle(
    RemoveServiceRegistration,
    dependencies={'di_service': di_service},
    id='error_repo',
)
```

### SetServiceConstants

Sets, merges, or clears service-level constants. Constants are global key-value pairs stored alongside service registrations.

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `constants` | `Dict[str, Any] \| None` | `{}` | Constants to apply. `None` clears all. Dict keys with `None` values are removed; others are merged. |

**Returns:** `Dict[str, Any]` — the updated constants dictionary.

**Merge semantics:**
- `constants=None` → clears all constants.
- `constants={'KEY': 'val'}` → merges into existing; existing keys are overwritten.
- `constants={'KEY': None}` → removes `KEY` from the constants dict.
- `constants={}` → no-op; existing constants are preserved.

```python
# Merge new constants
DomainEvent.handle(
    SetServiceConstants,
    dependencies={'di_service': di_service},
    constants={'APP_DIR': 'app', 'DEBUG': 'true'},
)

# Clear all constants
DomainEvent.handle(
    SetServiceConstants,
    dependencies={'di_service': di_service},
    constants=None,
)
```

### ListAllSettings

Lists all service registrations and constants. No required parameters.

**Returns:** `Tuple[List[ServiceRegistration], Dict[str, Any]]` — the list of registrations and the constants dictionary.

```python
registrations, constants = DomainEvent.handle(
    ListAllSettings,
    dependencies={'di_service': di_service},
)
```

## Common Patterns

### Retrieve → Verify → Mutate → Save

Most mutation events (`SetDefaultServiceRegistration`, `SetServiceDependency`, `RemoveServiceDependency`) follow a four-step pattern:

1. **Retrieve** the registration via `di_service.get_registration(id)`.
2. **Verify** it exists using `self.verify()`.
3. **Mutate** the aggregate via its domain methods (`set_default_type`, `set_dependency`, `remove_dependency`).
4. **Save** the updated aggregate via `di_service.save_registration(registration)`.

### Type Source Invariant

A service registration must always have at least one type source — either a default type (`module_path` + `class_name`) or at least one flagged dependency. This invariant is enforced during creation (`AddServiceRegistration`) and after dependency removal (`RemoveServiceDependency`).

### Idempotent Deletes

Both `RemoveServiceDependency` (at the model level) and `RemoveServiceRegistration` are idempotent — they succeed silently if the target does not exist.

## Related Documentation

- [docs/guides/domain/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/di.md) — DI domain objects
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md) — Mapper strategies
