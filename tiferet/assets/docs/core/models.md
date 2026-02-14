# Models in Tiferet – Dual Role: Runtime Domain Objects & Data Layer Mapping

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Models in Tiferet serve a **dual role** that is central to the framework’s design:

1. **Runtime Domain Objects**  
   - Active participants in application execution.
   - Returned by commands (e.g., `GetError` returns an `Error` model).
   - Used by Contexts to perform domain-specific work (e.g., `ErrorContext` retrieves and formats an `Error` for response generation).

2. **Data Layer Structural Base**  
   - Serve as the foundation for configuration-backed `DataObject` classes (e.g., `ErrorConfigData` extends `Error` + `DataObject`).
   - Define the shape mirrored in YAML/JSON configuration files.
   - Enable reliable round-trip mapping between persistent configuration and runtime models.

This duality ensures a single source of truth for domain structure and behavior, reducing duplication and maintaining consistency across runtime execution and persistent configuration.

### Example: Error Domain

- **Runtime Use** (`ErrorContext`):
  ```python
  error = self.get_error_handler(error_code, include_defaults=True)
  formatted = error.format_response(lang=lang, **exception.kwargs)
  ```
  The `Error` model is retrieved via command and actively formats responses.

- **Data Layer Use** (`ErrorConfigData`):
  ```python
  class ErrorConfigData(Error, DataObject):
      # Inherits fields/validation from Error
      # Adds serialization roles and mapping logic
  ```
  Configuration (`error.yml`) maps to `ErrorConfigData`, which converts to/from the runtime `Error`.

## Structured Code Design of Models

Models follow a strict artifact comment structure for consistency and AI/human readability:

- `# *** models` – top-level section.
- `# ** model: <name>` – individual model (snake_case).
- `# * attribute: <name>` – instance attributes (Schematics types).
- `# * method: <name>` – domain methods.
- `# * method: new` – optional custom factory.

**Spacing rules:**
- One empty line between `# *** models` and first `# ** model`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating and Extending Models

### 1. Define the Model
- Extend `ModelObject` from `tiferet.models.settings`.
- Use Schematics types with metadata.
- Prefer `ModelObject.new()` for instantiation; add `# * method: new` for custom logic.

**Example** – `CalculatorResult`:
```python
# *** imports

# ** app
from tiferet import (
    ModelObject, 
    FloatType, 
    StringType
)

# *** models

# ** model: calculator_result
class CalculatorResult(ModelObject):
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
Models are consumed by Contexts (via command results) or directly in command logic.

### Best Practices
- Use artifact comments consistently.
- Define validation/metadata on attributes.
- Keep mutation helpers (e.g., `rename`, `add_command`) for command use.
- Use `ModelObject.new` unless custom factory needed.

## Testing Models

Tests validate instantiation, behavior, and edge cases using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Example** – Error model tests cover `new`, formatting, and multilingual support.

## Conclusion

Tiferet models balance **active runtime participation** (via commands and contexts) with **passive configuration mapping** (via `DataObject` extensions). This dual role enables:
- Dynamic domain behavior.
- Reliable persistent configuration.
- Consistent patterns across all domains (error, container, feature, app, CLI).

Explore source in `tiferet/models/` and tests in `tiferet/models/tests/` for implementation details.