# Events – Error Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/error.py`  
**Version:** 2.0.0a6

## Overview

The error event module provides the full CRUD surface for `Error` domain objects — the structured error definitions that power Tiferet's multilingual error handling. Every event in this module depends on an injected `ErrorService` and operates on `Error` domain objects through the `ErrorAggregate` mapper.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddError` | Create | `id`, `name`, `message` | `Error` |
| `GetError` | Read (single) | *(none)* | `Error` |
| `ListErrors` | Read (all) | *(none)* | `List[Error]` |
| `RenameError` | Update (name) | `new_name` | `Error` |
| `SetErrorMessage` | Update (message) | `message` | `str` (ID) |
| `RemoveErrorMessage` | Delete (message) | *(none)* | `str` (ID) |
| `RemoveError` | Delete | `id` | `str` (ID) |

## Dependency

All events inject a single dependency:

- **`error_service: ErrorService`** — the service interface for persisting and retrieving `Error` objects.

## Event Details

### AddError

Creates a new `Error` with a primary message and optional additional language messages, then persists it via `ErrorService.save()`.

**Required:** `id`, `name`, `message`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `lang` | `str` | `'en_US'` | Language code for the primary message |
| `additional_messages` | `List[Dict[str, Any]]` | `[]` | Additional messages (each with `lang` and `text`) |

**Returns:** The created `Error` instance.

**Errors:**
- `ERROR_ALREADY_EXISTS` if an error with the given ID already exists.

```python
result = DomainEvent.handle(
    AddError,
    dependencies={'error_service': error_service},
    id='CUSTOM_VALIDATION_ERROR',
    name='Custom Validation Error',
    message='Input validation failed for field {field}.',
    additional_messages=[
        {'lang': 'es_ES', 'text': 'La validación falló para el campo {field}.'}
    ],
)
```

### GetError

Retrieves an `Error` by ID from the repository. Optionally falls back to built-in default errors defined in `assets/constants.py`.

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | — | The error identifier |
| `include_defaults` | `bool` | `False` | If `True`, search `DEFAULT_ERRORS` when not found in repository |

**Returns:** The `Error` instance.

**Errors:**
- `ERROR_NOT_FOUND` if the error is not found in the repository (and not in defaults when `include_defaults=True`).

**Behavior:**
1. Attempts to retrieve from the repository via `error_service.get(id)`.
2. If not found and `include_defaults=True`, checks `DEFAULT_ERRORS`.
3. If still not found, raises `ERROR_NOT_FOUND`.

```python
# From repository only
error = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    id='CUSTOM_VALIDATION_ERROR',
)

# With default fallback
error = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    id='COMMAND_PARAMETER_REQUIRED',
    include_defaults=True,
)
```

### ListErrors

Lists all `Error` objects from the repository. Optionally merges with built-in defaults, where repository errors override defaults with the same ID.

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `include_defaults` | `bool` | `False` | If `True`, merge repository errors with `DEFAULT_ERRORS` |

**Returns:** `List[Error]` — the list of error objects.

**Merge semantics:**
- Defaults are loaded first as a base dict keyed by ID.
- Repository errors are merged on top, overriding any defaults with matching IDs.

```python
# Repository only
errors = DomainEvent.handle(
    ListErrors,
    dependencies={'error_service': error_service},
)

# Including defaults
errors = DomainEvent.handle(
    ListErrors,
    dependencies={'error_service': error_service},
    include_defaults=True,
)
```

### RenameError

Renames an existing error by updating its `name` attribute.

**Required:** `new_name`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | — | The error identifier |

**Returns:** The updated `Error` instance.

**Errors:**
- `ERROR_NOT_FOUND` if the error does not exist.

```python
DomainEvent.handle(
    RenameError,
    dependencies={'error_service': error_service},
    id='CUSTOM_VALIDATION_ERROR',
    new_name='Field Validation Error',
)
```

### SetErrorMessage

Sets or updates the message text for a specific language on an existing error. If the language already exists, the text is replaced; otherwise a new message is added.

**Required:** `message`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | — | The error identifier |
| `lang` | `str` | `'en_US'` | The language code for the message |

**Returns:** `str` — the error ID.

**Errors:**
- `ERROR_NOT_FOUND` if the error does not exist.

```python
DomainEvent.handle(
    SetErrorMessage,
    dependencies={'error_service': error_service},
    id='CUSTOM_VALIDATION_ERROR',
    message='Validation failed for {field}.',
    lang='en_US',
)
```

### RemoveErrorMessage

Removes a message for a specific language from an existing error. Post-removal validation ensures at least one message remains.

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | — | The error identifier |
| `lang` | `str` | `'en_US'` | The language code of the message to remove |

**Returns:** `str` — the error ID.

**Errors:**
- `ERROR_NOT_FOUND` if the error does not exist.
- `NO_ERROR_MESSAGES` if removing the message would leave the error with no messages.

```python
DomainEvent.handle(
    RemoveErrorMessage,
    dependencies={'error_service': error_service},
    id='CUSTOM_VALIDATION_ERROR',
    lang='es_ES',
)
```

### RemoveError

Deletes an entire error by ID. The operation is **idempotent** — the underlying service handles non-existent IDs gracefully.

**Required:** `id`

**Returns:** `str` — the removed error ID.

```python
DomainEvent.handle(
    RemoveError,
    dependencies={'error_service': error_service},
    id='CUSTOM_VALIDATION_ERROR',
)
```

## Common Patterns

### Retrieve → Verify → Mutate → Save

Most mutation events (`RenameError`, `SetErrorMessage`, `RemoveErrorMessage`) follow a four-step pattern:

1. **Retrieve** the error via `error_service.get(id)`.
2. **Verify** it exists using `self.verify()`.
3. **Mutate** the aggregate via its domain methods (`rename`, `set_message`, `remove_message`).
4. **Save** the updated aggregate via `error_service.save(error)`.

### Message Invariant

An error must always have at least one message. This invariant is enforced after message removal (`RemoveErrorMessage`) via a `verify` check on `len(error.message) > 0`.

### Default Error Fallback

`GetError` and `ListErrors` support an `include_defaults` flag that incorporates the built-in `DEFAULT_ERRORS` dict from `tiferet/assets/constants.py`. Repository errors always take precedence over defaults with the same ID.

## Related Documentation

- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md) — Mapper strategies
