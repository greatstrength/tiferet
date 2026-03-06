**This conversation is part of the Tiferet Framework project.**  
**Repository:** https://github.com/greatstrength/tiferet – Tiferet Framework  

```markdown
# Domain – Error: ErrorMessage and Error

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 06, 2026  
**Version:** 2.0.0a2

## Overview

The Error domain defines the structural foundation for structured error handling in Tiferet. Every error definition is described by an `Error` domain object, which holds a unique identifier, error code, name, and one or more localized `ErrorMessage` translations. This enables consistent, multilingual error formatting across all application interfaces.

Both domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries and formatting methods. All state changes (renaming, adding/removing messages) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/error.py`

## Domain Objects

### ErrorMessage

Represents a single localized error message.

| Attribute | Type         | Required | Default | Description                         |
|-----------|--------------|----------|---------|-------------------------------------|
| `lang`    | `StringType` | Yes      | —       | The language of the error message.   |
| `text`    | `StringType` | Yes      | —       | The error message text (may contain format placeholders). |

#### Methods

**`format(**kwargs) -> str`**

Returns the raw `text` when no kwargs are provided. When kwargs are given, performs Python string formatting:

```python
msg = DomainObject.new(ErrorMessage, lang='en_US', text='Value {value} is invalid')
msg.format()                    # 'Value {value} is invalid'
msg.format(value='abc')         # 'Value abc is invalid'
```

### Error

Represents a named error definition with multilingual message support.

| Attribute    | Type                              | Required | Default | Description                                   |
|--------------|-----------------------------------|----------|---------|-----------------------------------------------|
| `id`         | `StringType`                      | Yes      | —       | The unique identifier of the error.            |
| `name`       | `StringType`                      | Yes      | —       | The name of the error.                         |
| `description`| `StringType`                      | No       | —       | The description of the error.                  |
| `error_code` | `StringType`                      | No       | —       | The unique code of the error (derived from id).|
| `message`    | `ListType(ModelType(ErrorMessage))`| Yes     | —       | The error message translations.                |

#### Methods

**`new(name, id, message=[], **kwargs) -> Error`** (static)

Custom factory that derives `error_code` by uppercasing `id` and replacing spaces with underscores:

```python
error = Error.new(id='invalid_input', name='Invalid Input', message=[...])
assert error.error_code == 'INVALID_INPUT'
```

**`format_message(lang='en_US', **kwargs) -> str`**

Finds the first `ErrorMessage` matching the given `lang` and formats it. Returns `None` if no message matches the language.

**`format_response(lang='en_US', **kwargs) -> dict`**

Returns a structured error response dict with `error_code`, `name`, `message`, and any additional kwargs. Returns `None` if the language is not supported.

```python
response = error.format_response('en_US', value='abc')
# {'error_code': 'invalid_input', 'name': 'Invalid Input', 'message': 'Value abc is invalid', 'value': 'abc'}
```

## Error Formatting Flow

The error formatting flow in Tiferet follows this path:

1. A domain event calls `self.verify(expression, error_code, ...)` or `self.raise_error(error_code, ...)`.
2. A `TiferetError` is raised with the `error_code` and contextual kwargs.
3. The application context catches the error and delegates to `ErrorContext.handle_error()`.
4. `ErrorContext` retrieves the `Error` domain object via `ErrorService.get(error_code)`.
5. `Error.format_response(lang, **kwargs)` produces the structured error response.
6. The response is returned to the caller (API response, CLI output, etc.).

## Built-In Defaults

Tiferet provides built-in error definitions in `assets/constants.py::DEFAULT_ERRORS`. These cover framework-level errors such as:

- `COMMAND_PARAMETER_REQUIRED` — missing required parameters
- `FEATURE_NOT_FOUND` — unknown feature ID
- `INVALID_MODEL_ATTRIBUTE` — invalid attribute on a domain object

Application-specific errors are defined in `app/configs/error.yml` and loaded via `ErrorService`.

## Configuration Mapping

Errors are defined in `app/configs/error.yml`. Each top-level key maps to an `Error`:

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

## Domain Events

The following domain events interact with `Error` and `ErrorMessage`:

| Event         | Description                                       |
|---------------|---------------------------------------------------|
| `GetError`    | Retrieves an `Error` by ID.                       |
| `AddError`    | Creates and persists a new `Error`.                |
| `RenameError` | Renames an existing `Error` via aggregate.         |
| `SetErrorMessage` | Sets/updates a message translation via aggregate. |
| `RemoveErrorMessage` | Removes a message translation via aggregate.  |

These events depend on the `ErrorService` interface for persistence operations.

## Service Interface

**`ErrorService`** (`tiferet/interfaces/error.py`) defines the abstract contract for Error domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> Error`
- `list() -> List[Error]`
- `save(error) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `ErrorYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **All Domains:** Every domain event uses `verify()` and `raise_error()` to raise `TiferetError`, which is resolved to an `Error` for formatting.
- **App:** `ErrorContext` is loaded as part of the application interface bootstrap, receiving `ErrorService` via dependency injection.
- **DI:** `ErrorService` is wired through the DI container (`ServiceConfiguration` entries in `container.yml`).

## Instantiation

```python
from tiferet.domain import DomainObject, ErrorMessage, Error

msg_en = DomainObject.new(ErrorMessage, lang='en_US', text='Value {value} is invalid')
msg_es = DomainObject.new(ErrorMessage, lang='es_ES', text='El valor {value} no es válido')

error = Error.new(
    id='invalid_input',
    name='Invalid Input',
    message=[msg_en, msg_es],
)
# error.error_code == 'INVALID_INPUT'
# error.format_message('es_ES', value='abc') == 'El valor abc no es válido'
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
- [docs/guides/domain/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/di.md) — DI domain guide
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
```
