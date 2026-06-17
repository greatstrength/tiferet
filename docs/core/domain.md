# Domain Objects in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Domain objects are the structural core of the Tiferet framework. Every domain concept — errors, features, containers, app interfaces, CLI commands, and logging configurations — is expressed as a class extending `DomainObject` from `tiferet.domain.settings`.

Domain objects serve a **dual role**:

1. **Runtime Domain Models**  
   - Active participants in application execution.
   - Returned by domain events and commands (e.g., `GetError` returns an `Error`).
   - Used by Contexts to perform domain-specific work (e.g., `ErrorContext` retrieves and formats an `Error` for response generation).

2. **Structural Foundation for the Mappers Layer**  
   - Aggregates extend domain objects with mutation logic (e.g., `ErrorAggregate(Error, Aggregate)`).
   - TransferObjects extend domain objects with serialization roles (e.g., `ErrorYamlObject(Error, TransferObject)`).
   - Define the field shape mirrored in YAML/JSON configuration files.
   - Enable reliable round-trip mapping between persistent configuration and runtime models.

This duality ensures a single source of truth for domain structure and behavior, reducing duplication and maintaining consistency across runtime execution and persistent configuration.

### Example: Error Domain

- **Runtime Use** (`ErrorContext`):
  ```python
  # The hub loads the Error; the context formats the response from it.
  error_message = error.format_message(lang, **getattr(exception, 'kwargs', {}))
  ```
  The `Error` domain object is retrieved via the hub's `load_error_domain` and used by `ErrorContext.format_response` to assemble the structured response.

- **Mapper Layer Use** (`ErrorAggregate`, `ErrorYamlObject`):
  ```python
  class ErrorAggregate(Error, Aggregate):
      # Inherits fields/validation from Error
      # Adds mutation methods (rename, set_message, remove_message)

  class ErrorYamlObject(Error, TransferObject):
      # Inherits fields/validation from Error
      # Adds serialization roles and mapping logic
  ```
  Configuration (`error.yml`) maps through `ErrorYamlObject` to `ErrorAggregate`, which converts to/from the runtime `Error`.

## The DomainObject Base Class

`DomainObject` extends `pydantic.BaseModel` with a shared `ConfigDict`:

```python
# tiferet/domain/settings.py

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

## Structured Code Design

Domain objects follow a strict artifact comment structure for consistency and AI/human readability:

- `# *** models` – top-level section (retained for backward compatibility; these are domain objects).
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
- Extend `DomainObject` from `tiferet.domain.settings`.
- Declare fields with Pydantic `Field(...)` annotations.
- Instantiate directly via the constructor or `model_validate()`.
- Use `@model_validator(mode='before')` for derivation logic that was previously in custom `new()` factories.

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
- Instantiate directly via the constructor or `model_validate()` — there is no `DomainObject.new()` factory.
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

- `settings.py` – `DomainObject` base class (extends `pydantic.BaseModel` with `ConfigDict`).
- `app.py` – `AppInterface`, `AppServiceDependency`.
- `cli.py` – `CliCommand`, `CliArgument`.
- `di.py` – `ServiceConfiguration`, `FlaggedDependency`.
- `error.py` – `Error`, `ErrorMessage`.
- `feature.py` – `Feature`, `FeatureStep`, `FeatureEvent`.
- `logging.py` – `Formatter`, `Handler`, `Logger`.
- `__init__.py` – Public exports for all domain objects.

Tests live in `tiferet/domain/tests/`.

## Migration from Schematics to Pydantic v2

In v2.0, the domain layer was migrated from `schematics.Model` to `pydantic.BaseModel`:

- `DomainObject` now extends `pydantic.BaseModel` with a shared `ConfigDict` instead of `schematics.Model`.
- Schematics type descriptors (`StringType`, `IntegerType`, `FloatType`, etc.) are replaced with standard Python type annotations and `pydantic.Field(...)`.
- The `DomainObject.new(Type, **kwargs)` static factory is removed; use the Pydantic constructor directly or `model_validate()` for external data.
- Custom `new()` factory methods with derivation logic are replaced by `@model_validator(mode='before')` class methods.
- `tiferet/entities/` was renamed to `tiferet/domain/`, and `ModelObject` was renamed to `DomainObject`.

## Conclusion

Domain objects provide the **structural foundation** for the entire Tiferet framework. They define the canonical shape of every domain concept, enabling:
- Consistent runtime behavior via commands and contexts.
- Reliable persistent configuration via Aggregate and TransferObject extensions.
- A single source of truth shared across all layers.

Explore source in `tiferet/domain/` and tests in `tiferet/domain/tests/` for implementation details.
