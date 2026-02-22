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
  error = self.get_error_handler(error_code, include_defaults=True)
  formatted = error.format_response(lang=lang, **exception.kwargs)
  ```
  The `Error` domain object is retrieved via command and actively formats responses.

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

`DomainObject` extends `schematics.Model` and provides a static factory method for consistent instantiation:

```python
# tiferet/domain/settings.py

class DomainObject(Model):
    '''
    A domain model object.
    '''

    # * method: new
    @staticmethod
    def new(
        model_type: type,
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'DomainObject':
        '''
        Initializes a new domain object.
        '''

        # Create a new domain object.
        domain_object = model_type(dict(**kwargs), strict=strict)

        # Validate if specified.
        if validate:
            domain_object.validate()

        # Return the new domain object.
        return domain_object
```

Key characteristics:
- **`DomainObject.new(Type, **kwargs)`** is the standard factory for all domain objects.
- Validation is enabled by default; pass `validate=False` to skip.
- Strict mode is enabled by default; pass `strict=False` to allow extra fields.
- Domain-specific models may override `new` with custom factory logic (e.g., `Error.new` derives `error_code` from `id`).

## Structured Code Design

Domain objects follow a strict artifact comment structure for consistency and AI/human readability:

- `# *** models` – top-level section (retained for backward compatibility; these are domain objects).
- `# ** model: <name>` – individual domain object (snake_case).
- `# * attribute: <name>` – instance attributes (Schematics types).
- `# * method: <name>` – domain methods.
- `# * method: new` – optional custom factory.

**Spacing rules:**
- One empty line between `# *** models` and first `# ** model`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating and Extending Domain Objects

### 1. Define the Domain Object
- Extend `DomainObject` from `tiferet.domain.settings`.
- Use Schematics types with metadata.
- Prefer `DomainObject.new()` for instantiation; add `# * method: new` for custom logic.

**Example** – `CalculatorResult`:
```python
# *** imports

# ** app
from tiferet import (
    DomainObject, 
    FloatType, 
    StringType
)

# *** models

# ** model: calculator_result
class CalculatorResult(DomainObject):
    '''
    Stores calculator computation results.
    '''

    # * attribute: value
    value = FloatType(required=True)

    # * attribute: operation
    operation = StringType(required=True)

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
- Define validation/metadata on attributes.
- Keep domain objects focused on **structure and read-only behavior** (formatting, lookups).
- Place **mutation logic** (e.g., `rename`, `add_command`, `set_message`) in Aggregate classes in the mappers layer.
- Use `DomainObject.new` unless a custom factory is needed.
- Override `new` as a `@staticmethod` when domain-specific derivation is required (e.g., `Error.new` computes `error_code`).

## Testing Domain Objects

Tests validate instantiation, behavior, and edge cases using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Example** – Error domain object tests cover `new`, `format_message`, `format_response`, and multilingual support.

## Package Layout

Domain objects are defined in `tiferet/domain/`:

- `settings.py` – `DomainObject` base class and Schematics type wrappers.
- `app.py` – `AppInterface`, `AppAttribute`.
- `cli.py` – `CliCommand`, `CliArgument`.
- `container.py` – `ContainerAttribute`, `FlaggedDependency`.
- `error.py` – `Error`, `ErrorMessage`.
- `feature.py` – `Feature`, `FeatureCommand`.
- `logging.py` – `Formatter`, `Handler`, `Logger`.
- `__init__.py` – Public exports for all domain objects and types.

Tests live in `tiferet/domain/tests/`.

## Migration from ModelObject

In v2.0, `ModelObject` was renamed to `DomainObject` and the `tiferet/entities/` package was renamed to `tiferet/domain/`. All import paths and references throughout the framework (domain, events, mappers, repos, contexts, and top-level exports) have been updated accordingly. The API is identical — only the names have changed.

## Conclusion

Domain objects provide the **structural foundation** for the entire Tiferet framework. They define the canonical shape of every domain concept, enabling:
- Consistent runtime behavior via commands and contexts.
- Reliable persistent configuration via Aggregate and TransferObject extensions.
- A single source of truth shared across all layers.

Explore source in `tiferet/domain/` and tests in `tiferet/domain/tests/` for implementation details.
