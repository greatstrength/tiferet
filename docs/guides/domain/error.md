# Domain – Error (Structured Error Handling)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0b1

## Overview

The Error domain defines **how failures are communicated**. Every `TiferetError` raised anywhere in the application — whether from a domain event's `verify()`, a `raise_error()` call, or a utility's `RaiseError.execute()` — ultimately flows through the Error domain to produce a structured, multilingual response.

An `Error` is a named error definition with a unique identifier, a human-readable name, and one or more `ErrorMessage` translations. When an exception is caught at the interface level, the framework looks up the `Error` by code, formats the message for the requested language, and returns a structured response with error code, name, and localized message.

## Domain Objects

### ErrorMessage

Represents a single localized error message.

| Attribute | Type         | Required | Default | Description                         |
|-----------|--------------|----------|---------|-------------------------------------|
| `lang`    | `str`        | Yes      | —       | The language of the error message.   |
| `text`    | `str`        | Yes      | —       | The error message text (may contain format placeholders). |

#### Methods

**`format(**kwargs) -> str`**

Returns the raw `text` when no kwargs are provided. When kwargs are given, performs Python string formatting:

```python
msg = ErrorMessage(lang='en_US', text='Value {value} is invalid')
msg.format()                    # 'Value {value} is invalid'
msg.format(value='abc')         # 'Value abc is invalid'
```

### Error

A named error definition with multilingual message support.

| Attribute    | Type                              | Required | Default | Description                                   |
|--------------|-----------------------------------|----------|---------|-----------------------------------------------|
| `id`         | `str`                             | Yes      | —       | The unique identifier of the error.            |
| `name`       | `str`                             | Yes      | —       | The name of the error.                         |
| `description`| `str \| None`                     | No       | `None`  | The description of the error.                  |
| `error_code` | `str \| None`                     | No       | —       | The unique code of the error (derived from id via `@model_validator`).|
| `message`    | `List[ErrorMessage]`              | Yes      | —       | The error message translations.                |

**Custom factory:**

**ID Derivation via `@model_validator`**

The `error_code` is automatically derived by a `@model_validator(mode='before')` that uppercases `id` and replaces spaces with underscores:

```python
error = Error(id='invalid_input', name='Invalid Input', message=[...])
assert error.error_code == 'INVALID_INPUT'
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

Concrete implementations (e.g., `ErrorYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **All Domains:** Every domain event uses `verify()` and `raise_error()` to raise `TiferetError`, which is resolved to an `Error` for formatting.
- **App:** `ErrorContext` is loaded as part of the application interface bootstrap, receiving `ErrorService` via dependency injection.
- **DI:** `ErrorService` is wired through the DI container (`ServiceConfiguration` entries in `container.yml`).

## Instantiation

```python
from tiferet.domain import ErrorMessage, Error

msg_en = ErrorMessage(lang='en_US', text='Value {value} is invalid')
msg_es = ErrorMessage(lang='es_ES', text='El valor {value} no es válido')

error = Error(
    id='invalid_input',
    name='Invalid Input',
    message=[msg_en, msg_es],
)
# error.error_code == 'INVALID_INPUT' (derived via @model_validator)
# error.format_message('es_ES', value='abc') == 'El valor abc no es válido'
```

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns (verify, raise_error)
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
