# Domain Objects in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Domain objects are the structural core of the Tiferet framework. Every domain concept — errors, features, containers, app interfaces, CLI commands, and logging configurations — is expressed as a class extending `DomainObject` from `tiferet.domain.core`.

Domain objects serve a **dual role**:

1. **Runtime Domain Models**  
   - Active participants in application execution.
   - Returned by domain events and commands (e.g., `GetError` returns an `Error`).
   - Used by Contexts to perform domain-specific work (e.g., `ErrorContext` retrieves and formats an `Error` for response generation).

2. **Structural Foundation for the Mappers Layer**  
  - Aggregates extend domain objects with mutation logic (e.g., `ErrorAggregate(Error, Aggregate)`).
  - TransferObjects extend domain objects with serialization roles (e.g., `ErrorConfigObject(Error, TransferObject)`).
   - Define the field shape mirrored in YAML/JSON configuration files.
   - Enable reliable round-trip mapping between persistent configuration and runtime models.

This duality ensures a single source of truth for domain structure and behavior, reducing duplication and maintaining consistency across runtime execution and persistent configuration.

### Example: Error Domain

- **Runtime Use** (`ErrorContext`):
  ```python
  # The hub loads the Error; the context formats the response from it.
  error_message = error.format_message(lang, **exception.kwargs)
  ```
  The `Error` domain object is retrieved via the hub's `get_error` (cache-first) and used by `ErrorContext.format_response` to assemble the structured response.

- **Mapper Layer Use** (`ErrorAggregate`, `ErrorConfigObject`):
  ```python
  class ErrorAggregate(Error, Aggregate):
      # Inherits fields/validation from Error
      # Adds mutation methods (rename, set_message, remove_message)

  class ErrorConfigObject(Error, TransferObject):
      # Inherits fields/validation from Error
      # Adds serialization roles and mapping logic
  ```
  Configuration (`config.yml` errors section) maps through `ErrorConfigObject` to `ErrorAggregate`, which converts to/from the runtime `Error`.

## The DomainObject Base Class

`DomainObject` extends `pydantic.BaseModel` with a shared `ConfigDict`:

```python
# tiferet/domain/core.py

from pydantic import BaseModel, ConfigDict

class DomainObject(BaseModel):
    '''
    The base domain model object for Tiferet, backed by Pydantic v2.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
    )
```

Key characteristics:
- **`extra='forbid'`** rejects unknown fields by default; subclasses may override (e.g., `TransferObject` uses `extra='ignore'`).
- **`validate_assignment=True`** triggers field validation on every `setattr`, ensuring aggregates stay consistent after mutation.
- **`populate_by_name=True`** allows construction by canonical field name even when aliases are defined.
- Instantiate domain objects directly via the Pydantic constructor: `Error(id='invalid_input', name='Invalid Input')`.
- For input from untrusted/external sources, use `model_validate(data_dict)` which applies all validators.
- Domain-specific derivation logic uses `@model_validator(mode='before')` instead of custom factory methods (e.g., `Error._derive_error_code` computes `error_code` from `id`).

## The Model Error Protocol

`tiferet/domain/core.py` also owns the framework's **model error protocol** — the vocabulary for describing an inconsistency *within* a single model. It lives in `domain` rather than `assets` so that lower layers extending domain objects (notably `mappers`) can report a bad mutation without importing an upper layer. This is what makes `domain`'s "no framework dependencies" rule literally true and removes the layer graph's only Infrastructure→Actor edge.

### Constants (`# *** constants`)

| Constant | Value | Meaning |
|---|---|---|
| `INVALID_MODEL_ATTRIBUTE_ID` | `'INVALID_MODEL_ATTRIBUTE'` | No such field on the model. |
| `INVALID_MODEL_VALUE_ID` | `'INVALID_MODEL_VALUE'` | The field exists but the assigned value failed field validation. |
| `ATTRIBUTE_NOT_SETTABLE_ID` | `'ATTRIBUTE_NOT_SETTABLE'` | The field exists but is not directly settable; a dedicated mutator owns it. |
| `MODEL_IDENTITY_FIELDS` | `('id', 'name', 'key')` | The identity fields `describe_model` reports when a model declares them. |

### `describe_model` (`# *** functions`)

A pure helper summarizing the instance a violation originated from, so a model error names *which* model failed and not merely which field:

```python
descriptor = describe_model(command_aggregate)
# {'type': 'CliCommandAggregate', 'module': 'tiferet.mappers.cli', 'id': 'calc.add', 'name': 'Add Number Command'}
```

The descriptor reports the type identity plus whichever of `MODEL_IDENTITY_FIELDS` the model declares, skipping absent fields and any non-primitive value. It deliberately holds **no reference** to the instance and never serializes its whole state, so the descriptor remains JSON-serializable error context.

### `unpack_validation_error` (`# *** functions`)

A pure helper flattening Pydantic's `error.errors()` into `{'field', 'type', 'message'}` dicts, so violations can travel as structured error context without exposing the Pydantic error object:

```python
violations = unpack_validation_error(error)
# [{'field': 'name', 'type': 'string_type', 'message': 'Input should be a valid string'}]
```

It is shared by the mutation path (`Aggregate.set_attribute`) and the request-validation path (`contexts/feature.py::validate_request`).

### `ModelError` (`# *** classes`)

```python
class ModelError(Exception):
    def __init__(self, error_code, message=None, model=None, violations=None, **kwargs): ...

    @classmethod
    def raise_error(cls, error_code, message=None, model=None, **kwargs) -> None: ...

    @classmethod
    def raise_for_validation(cls, error, message=None, model=None, **kwargs) -> None: ...
```

`ModelError` is a **standalone `Exception`, deliberately not a `TiferetError`**. A model inconsistency is a consumer defect, not a domain outcome, so it is not catalogued in `assets/error.py`, never resolved through the `Error` catalog, never formatted as a `TiferetAPIError`, and not skippable by a feature step's `pass_on_error`. It carries its own message and leaks to the top as the intended defect signal.

Both raisers follow the classmethod-constructor convention. `raise_for_validation` takes **no** `error_code`: it flattens the violations, then classifies the failure itself — `INVALID_MODEL_ATTRIBUTE_ID` when any violation reports Pydantic's `no_such_attribute` type, otherwise `INVALID_MODEL_VALUE_ID` — and chains the original `ValidationError` as the exception cause. No call site ever chooses between the two codes.

### Naming the offending instance

Because a `ModelError` is read as a **defect report** rather than a response, it also carries the metadata a catalogued `TiferetError` never needs: which instance raised it. Both raisers accept the live model as `model` and store the `describe_model` descriptor on the error's `model` attribute, which is serialized into the exception message alongside the code and violations:

```python
# tiferet/mappers/core.py — Aggregate.set_attribute
except ValidationError as error:
    ModelError.raise_for_validation(
        error,
        model=self,
        attribute=attribute,
    )
```

`raise_for_validation` falls back to the type name Pydantic's `ValidationError.title` reports when no instance is supplied, so the descriptor is never empty on the conversion path, and its derived message leads with that type (`'CliCommandAggregate validation failed: [...]'`). The `__init__` parameter takes the **descriptor**; the raisers take the **instance** and describe it — mirroring the split between `violations` and the `ValidationError` they are flattened from.

> **Note on assignment strictness.** `DomainObject` sets `coerce_numbers_to_str=True`, so assignment validation is coercing rather than strict: `setattr(obj, 'name', 123)` succeeds as `'123'`. "Validated on mutation" is therefore weaker than it sounds — the value branch fires only for genuinely non-coercible values.

## Structured Code Design

Domain objects follow a strict artifact comment structure for consistency and AI/human readability:

- `# *** models` – top-level section for domain object modules.
- `# ** model: <name>` – individual domain object (snake_case).
- `# * attribute: <name>` – instance attributes (Pydantic `Field(...)` annotations).
- `# * method: <name>` – domain methods.
- `# * method: _derive_* (validator)` – optional `@model_validator` for derivation logic.

**Spacing rules:**
- One empty line between `# *** models` and first `# ** model`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating and Extending Domain Objects

### 1. Define the Domain Object
- Extend `DomainObject` from `tiferet.domain.core`.
- Declare fields with Pydantic `Field(...)` annotations.
- Instantiate directly via the constructor or `model_validate()`.
- Use `@model_validator(mode='before')` for domain-specific derivation logic.

**Example** – `CalculatorResult`:
```python
# *** imports

# ** infra
from pydantic import Field

# ** app
from tiferet import DomainObject

# *** models

# ** model: calculator_result
class CalculatorResult(DomainObject):
    '''
    Stores calculator computation results.
    '''

    # * attribute: value
    value: float = Field(..., description='The computed result value.')

    # * attribute: operation
    operation: str = Field(..., description='The operation that produced this result.')

    # * method: format_result
    def format_result(self, precision: int = 2) -> str:
        '''
        Formats the result.
        '''
        return f'{self.operation}: {self.value:.{precision}f}'
```

### 2. Use in Context/Command
Domain objects are consumed by Contexts (via command results) or directly in command and domain event logic.

### 3. Extend in Mappers Layer
Domain objects are extended in the mappers layer as Aggregates (with mutation methods) and TransferObjects (with serialization roles). See `tiferet/mappers/` for examples.

### Best Practices
- Use artifact comments consistently.
- Declare fields with `Field(...)` including `description` metadata.
- Keep domain objects focused on **structure and read-only behavior** (formatting, lookups).
- Place **mutation logic** (e.g., `rename`, `add_command`, `set_message`) in Aggregate classes in the mappers layer.
- Instantiate directly via the constructor or `model_validate()`.
- Use `@model_validator(mode='before')` for domain-specific derivation logic (e.g., `Error._derive_error_code` computes `error_code` from `id`).

## Testing Domain Objects

Tests validate instantiation, behavior, and edge cases using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Example** – Error domain object tests cover constructor instantiation, `format_message`, and multilingual support (structured response assembly is tested in `ErrorContext`).

## Package Layout

Domain objects are defined in `tiferet/domain/`:

- `core.py` – `DomainObject` base class (extends `pydantic.BaseModel` with `ConfigDict`), the shared `ServiceDependency` core model, and the model error protocol (`ModelError`, `unpack_validation_error`, and the three model error constants).
- `app.py` – `AppSession`, `AppServiceDependency`.
- `cli.py` – `CliCommand`, `CliArgument`.
- `di.py` – `ServiceRegistration`, `FlaggedDependency`.
- `error.py` – `Error`, `ErrorMessage`.
- `feature.py` – `Feature`, `FeatureStep`, `EventFeatureStep`.
- `logging.py` – `Formatter`, `Handler`, `Logger`, `LoggingSettings`.
- `__init__.py` – Public exports for all domain objects.

Tests live in `tests/domain/`.

## Conclusion

Domain objects provide the **structural foundation** for the entire Tiferet framework. They define the canonical shape of every domain concept, enabling:
- Consistent runtime behavior via commands and contexts.
- Reliable persistent configuration via Aggregate and TransferObject extensions.
- A single source of truth shared across all layers.

Explore source in `tiferet/domain/` and tests in `tests/domain/` for implementation details.
