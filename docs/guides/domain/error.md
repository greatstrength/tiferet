# Domain – Error (Structured Error Handling)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/domain/error.py`  
**Version:** 2.0.0a2

## Overview

The Error domain defines **how failures are communicated**. Every `TiferetError` raised anywhere in the application — whether from a domain event's `verify()`, a `raise_error()` call, or a utility's `RaiseError.execute()` — ultimately flows through the Error domain to produce a structured, multilingual response.

An `Error` is a named error definition with a unique identifier, a human-readable name, and one or more `ErrorMessage` translations. When an exception is caught at the interface level, the framework looks up the `Error` by code, formats the message for the requested language, and returns a structured response with error code, name, and localized message.

## Domain Objects

### Error

A named error definition with multilingual message support.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Unique identifier (e.g., `invalid_input`, `division_by_zero`) |
| `name` | `str` (required) | Human-readable name (e.g., `Invalid Numeric Input`) |
| `description` | `str` | Optional description |
| `error_code` | `str` | Derived uppercase code (e.g., `INVALID_INPUT`) |
| `message` | `List[ErrorMessage]` (required) | Localized message translations |

**Custom factory:**

- `Error.new(name, id, message, **kwargs)` — derives `error_code` from `id` by upper-casing and replacing spaces with underscores. This is one of the few domain objects with a custom `new()` override rather than using `DomainObject.new()` directly.

**Behavior methods:**

- `format_message(lang='en_US', **kwargs)` — finds the `ErrorMessage` matching the requested language and formats it with the provided keyword arguments. Returns the formatted string, or `None` if no matching language is found.
- `format_response(lang='en_US', **kwargs)` — calls `format_message()` and wraps the result in a structured dict with `error_code`, `name`, `message`, and any additional kwargs. This dict is what `TiferetAPIError` ultimately carries to the caller.

### ErrorMessage

A single localized error message.

| Attribute | Type | Description |
|-----------|------|-------------|
| `lang` | `str` (required) | Language code (e.g., `en_US`, `es_ES`) |
| `text` | `str` (required) | Message text, optionally with `{}` or `{key}` format placeholders |

**Behavior method:**

- `format(**kwargs)` — applies Python string formatting to `text` with the provided keyword arguments. If no kwargs are provided, returns the raw text.

### Error Formatting Flow

When a domain event calls `self.verify(expression, error_code, message, **kwargs)` and the expression is falsy:

1. A `TiferetError` is raised with the `error_code` and `kwargs`.
2. The error propagates up to `AppInterfaceContext.handle_error()`.
3. `ErrorContext.handle_error(exception)` retrieves the `Error` by code.
4. `Error.format_response(lang, **exception.kwargs)` produces the structured dict.
5. A `TiferetAPIError` is raised with the formatted payload.

```python
# In a domain event:
self.verify(
    b_verified != 0,
    'DIVISION_BY_ZERO'  # error_code references an Error.id
)

# ErrorContext formats it:
# {
#     'error_code': 'division_by_zero',
#     'name': 'Division By Zero',
#     'message': 'Cannot divide by zero'
# }
```

## Built-in Defaults

The framework ships with a set of default error definitions in `assets/constants.py::DEFAULT_ERRORS`. These cover common framework-level errors (parameter required, feature not found, dependency import failed, etc.) and serve as fallbacks when an error code is not found in the application's `error.yml`.

`GetError` checks the configured repository first, then falls back to `DEFAULT_ERRORS` when `include_defaults=True`.

## Runtime Role

`ErrorContext` is the primary consumer of the Error domain at runtime:

1. **`handle_error(exception)`** receives a `TiferetError` with an `error_code` and `kwargs`.
2. **`get_error_by_code(error_code)`** retrieves the `Error` via `GetError`, falling back to defaults if needed.
3. **`error.format_response(lang, **kwargs)`** produces the structured response dict.
4. The response is returned to `AppInterfaceContext`, which raises `TiferetAPIError` with the formatted payload.

## Configuration

Errors are defined in `app/configs/error.yml`:

```yaml
errors:
  invalid_input:
    name: Invalid Numeric Input
    message:
      - lang: en_US
        text: 'Value {value} must be a number'
      - lang: es_ES
        text: 'El valor {value} debe ser un número'
  division_by_zero:
    name: Division By Zero
    message:
      - lang: en_US
        text: 'Cannot divide by zero'
      - lang: es_ES
        text: 'No se puede dividir por cero'
```

Each key under `errors` becomes the `Error.id`. The `message` list maps to `ErrorMessage` entries with language codes and format-string texts.

## Domain Events

| Event | Purpose |
|-------|---------|
| `GetError` | Retrieve an error by ID (with optional default fallback) |
| `AddError` | Create a new error definition |
| `RenameError` | Update the name of an existing error |
| `SetErrorMessage` | Set or update a message for a specific language |
| `RemoveErrorMessage` | Remove a message by language (validates at least one remains) |
| `RemoveError` | Delete an error definition |
| `ListErrors` | List all errors (with optional default merging) |

## Service Interface

`ErrorService` (`tiferet/interfaces/error.py`) — abstracts CRUD access to error definitions.

## Relationship to Other Domains

- **All domains** — Every domain event uses `verify()` and `raise_error()`, which raise `TiferetError` with error codes that reference `Error.id` values. The Error domain is the universal safety net.
- **App domain** — `AppInterfaceContext.handle_error()` is the catch point that delegates to `ErrorContext`. Different app interfaces may handle errors differently (e.g., CLI prints to stderr, a web interface returns HTTP error responses).
- **DI domain** — The `ErrorService` implementation (e.g., `ErrorYamlRepository`) is registered as a service configuration and resolved via the DI container.

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/events.md) — Domain event patterns (verify, raise_error)
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/guides/domain/app.md) — App domain guide
