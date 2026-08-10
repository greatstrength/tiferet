# Domain – Error: ErrorMessage and Error

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

The Error domain defines the structural foundation for structured error handling in Tiferet. Every error definition is described by an `Error` domain object, which holds a unique identifier, error code, name, and one or more localized `ErrorMessage` translations. This enables consistent, multilingual error formatting across all application interfaces.

Both domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries and formatting methods. All state changes (renaming, adding/removing messages) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/error.py`
**Vision:** See the `Error` class docstring in `tiferet/domain/error.py` for the value statement this guide distills.

## Ubiquitous Language

- **Catalogued error** — an `Error` resolvable through `ErrorService`/`ErrorContext`, formatted as a `TiferetAPIError`.
- **Error code** — the derived, uppercased identifier (`INVALID_INPUT`) used to key the catalog.
- **Message translation** — one localized `ErrorMessage` entry keyed by `lang`.

## Domain Objects

### ErrorMessage

Represents a single localized error message.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="errormessage-lang"></a>`lang` | `str` | Yes | — | The language of the error message. |
| <a id="errormessage-text"></a>`text` | `str` | Yes | — | The error message text (may contain format placeholders). |

#### Methods

<a id="errormessage-format"></a>
**`format(**kwargs) -> str`**

Returns the raw `text` when no kwargs are provided. When kwargs are given, performs Python string formatting:

```python
msg = ErrorMessage(lang='en_US', text='Value {value} is invalid')
msg.format()                    # 'Value {value} is invalid'
msg.format(value='abc')         # 'Value abc is invalid'
```

### Error

Represents a named error definition with multilingual message support.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="error-id"></a>`id` | `str` | Yes | — | The unique identifier of the error. |
| <a id="error-name"></a>`name` | `str` | Yes | — | The name of the error. |
| <a id="error-description"></a>`description` | `str \| None` | No | `None` | The description of the error. |
| <a id="error-error-code"></a>`error_code` | `str \| None` | No | — | The unique code of the error (derived from `id` via `@model_validator`). |
| <a id="error-message"></a>`message` | `List[ErrorMessage]` | Yes | — | The error message translations. |

#### Methods

<a id="error-derive-error-code"></a>
**ID Derivation via `@model_validator`**

The `error_code` is automatically derived by a `@model_validator(mode='before')` that uppercases `id` and replaces spaces with underscores:

```python
error = Error(id='invalid_input', name='Invalid Input', message=[...])
assert error.error_code == 'INVALID_INPUT'
```

<a id="error-format-message"></a>
**`format_message(lang='en_US', **kwargs) -> str`**

Finds the first `ErrorMessage` matching the given `lang` and formats it. Returns `None` if no message matches the language.

**Response formatting (moved to `ErrorContext`)**

`Error` no longer defines `format_response`. Structured response assembly lives in `ErrorContext.format_response(error, exception, lang='en_US')`, where `exception` is the raised `TiferetError`; it calls `Error.format_message` and adds `error_code`, `name`, and the error's `kwargs` (read directly off the `TiferetError`). Keeping response shaping in the context layer lets interface-specific contexts (e.g. Flask, FastAPI) override it polymorphically, while `Error.format_message` and `ErrorMessage.format` remain on the domain objects.

## Error Formatting Flow

The error formatting flow in Tiferet follows this path:

1. A domain event calls `self.verify(expression, error_code, ...)` or `self.raise_error(error_code, ...)`.
2. A `TiferetError` is raised with the `error_code` and contextual kwargs.
3. `AppSessionContext.run()` catches the `TiferetError` and calls `self.handle_error(e)`, which delegates to the injected `raise_error_handler` (built by the `raise_error_handler`/`get_error` blueprints in `tiferet/blueprints/core.py`).
4. The `get_error`-built handler resolves the `Error` domain object by `error_code`, checking the shared cache (pre-seeded with the framework defaults under the `('app', 'errors')` prefix) first and falling back to the `GetError`/`ErrorService` event on a miss, caching the result.
5. `ErrorContext.format_response(error, exception)` produces the structured error response from the loaded `Error` and the raised `TiferetError`.
6. The response is wrapped in `TiferetAPIError` and returned to the caller (API response, CLI output, etc.).

## Built-In Defaults

Tiferet provides built-in error definitions in `assets/error.py`'s `CORE_DEFAULT_ERRORS` / `ADMIN_DEFAULT_ERRORS` catalogs (see [docs/guides/assets.md](../assets.md) for the catalog pattern). These cover framework-level errors such as:

- `COMMAND_PARAMETER_REQUIRED` — missing required parameters
- `FEATURE_NOT_FOUND` — unknown feature ID
- `REQUEST_VALIDATION_FAILED` — request data that fails a feature's `params_schema`

Application-specific errors are defined in the `errors` section of the configuration file (typically `config.yml`, though per-file configs such as `error.yml` are also supported) and loaded via `ErrorService`.

## Configuration Mapping

Errors are defined in the `errors` section of the configuration file (typically `config.yml`). Each top-level key maps to an `Error`:

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

| Event | Description |
|---|---|
| `AddError` | Creates and persists a new `Error`. |
| `GetError` | Retrieves an `Error` by ID. |
| `ListErrors` | Lists all `Error` entries. |
| `RenameError` | Renames an existing `Error` via aggregate. |
| `SetErrorMessage` | Sets/updates a message translation via aggregate. |
| `RemoveErrorMessage` | Removes a message translation via aggregate. |

These events depend on the `ErrorService` interface for persistence operations.

## Service Interface

**`ErrorService`** (`tiferet/interfaces/error.py`) defines the abstract contract for Error domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> Error`
- `list() -> List[Error]`
- `save(error) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `ErrorConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **All Domains:** Every domain event uses `verify()` and `raise_error()` to raise `TiferetError`, which is resolved to an `Error` for formatting.
- **Core/Errors:** `ModelError` and `ServiceError` are the framework's other two exception families — see [docs/guides/errors.md](../errors.md) for how all three relate.
- **App:** `raise_error_handler` and `get_error` are wired onto the `AppSessionContext` hub by `build_app_session_context`; error retrieval and the shared, default-seeded error cache are owned by these blueprint-composed handlers, not the hub itself.
- **DI:** `ErrorService` is wired through the DI container (`ServiceRegistration` entries in the `services` section of the configuration).

## Boundaries

**Inside this domain:** defining a catalogued error's identity, code derivation, and multilingual message formatting.
**Outside this domain:** model defects (`ModelError` — see [docs/guides/domain/core.md](core.md)) are deliberately uncatalogued and never reach this domain's resolution path; response envelope assembly lives in `ErrorContext`, not here; infrastructural failures (`ServiceError`) are a third, unrelated family — see [docs/guides/errors.md](../errors.md).

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

- [docs/guides/errors.md](../errors.md) — The three unrelated exception families (`TiferetError`, `ServiceError`, `ModelError`) and when each applies
- [docs/guides/domain/core.md](core.md) — `ModelError`, deliberately excluded from this catalog
- [docs/guides/assets.md](../assets.md) — The `CORE_DEFAULT_ERRORS`/`ADMIN_DEFAULT_ERRORS` catalog pattern
- [docs/guides/domain/app.md](app.md) — App domain guide
- [docs/guides/domain/di.md](di.md) — DI domain guide
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
