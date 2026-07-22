---
name: tiferet-code-domain
description: Apply domain object conventions when adding or modifying domain objects in a Tiferet-family repo. Covers the DomainObject base class, Pydantic field declarations, model validators, read-only design, and package layout.
---

# Domain Objects Code Style – Tiferet

## When to use
- When adding a new domain object or modifying an existing one in `tiferet/domain/`.
- When defining a new field, a derivation validator, or a read-only behavior method on a domain class.
- When creating domain objects for a Tiferet-family application (e.g. a calculator result, an order item).
- Do NOT use for mutation logic — that belongs in Aggregates (`tiferet-code-mappers`).

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** models             ← construct group for this skill
# *** exports            ← __init__.py only
```

Model-specific labels:
```
# *** models                              ← artifact section
# ** model: <snake_case_name>             ← artifact
# * attribute: <name>                     ← artifact member: Pydantic Field(...) annotation
# * method: <name>                        ← artifact member: read-only domain behavior
# * method: _derive_<name> (validator)    ← artifact member: @model_validator derivation logic
```

Import artifact groups: `# ** core` (stdlib), `# ** infra` (pydantic), `# ** app` (framework).

## Key conventions

- **Layer boundary — valid `# ** app` imports:** `assets` sub-modules only (e.g. `from .. import assets as a`). Never import from `events`, `mappers`, `interfaces`, `repos`, `utils`, `contexts`, or `blueprints`.
- Extend `DomainObject` from `tiferet.domain.core` (which extends `pydantic.BaseModel`).
- `DomainObject` config: `extra='forbid'`, `populate_by_name=True`, `validate_assignment=True`, `arbitrary_types_allowed=True`, `coerce_numbers_to_str=True`.
- Declare all fields with `pydantic.Field(...)` including a `description` kwarg.
- Instantiate via the Pydantic constructor: `Feature(id='calc.add', name='Add')`.
- Use `model_validate(data_dict)` for external/untrusted data.
- Domain objects are **read-only** at the domain layer — place all mutation in Aggregates.
- Use `@model_validator(mode='before')` for pre-construction derivation logic (e.g. deriving `error_code` from `id`); label with `# * method: _derive_<name> (validator)`.
- Keep domain methods focused on **structure and read-only behavior** (formatting, lookups, derived values).
- Naming: PascalCase class names matching the domain concept (`AppSession`, `Feature`, `Error`, `CliCommand`).

## Example

```python
# *** imports

# ** core
from typing import List, Optional

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain.core import DomainObject

# *** models

# ** model: calculator_result
class CalculatorResult(DomainObject):
    '''
    Stores the result of a calculator computation.
    '''

    # * attribute: id
    id: str = Field(..., description='The unique result identifier.')

    # * attribute: operation
    operation: str = Field(..., description='The operation that produced this result.')

    # * attribute: value
    value: float = Field(..., description='The computed result value.')

    # * attribute: display_label
    display_label: str = Field(
        default='',
        description='Auto-derived display label (e.g. "add: 42.00").',
    )

    # * method: _derive_display_label (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_display_label(cls, values: dict) -> dict:
        '''
        Derive the display_label from operation and value when not supplied.

        :param values: The raw field values before construction.
        :type values: dict
        :return: The updated field values dict.
        :rtype: dict
        '''

        # Derive the display label if not explicitly provided.
        if not values.get('display_label') and values.get('operation') and values.get('value') is not None:
            values['display_label'] = f"{values['operation']}: {float(values['value']):.2f}"

        # Return the updated values.
        return values

    # * method: format_result
    def format_result(self, precision: int = 2) -> str:
        '''
        Format the result for display.

        :param precision: The decimal precision to use.
        :type precision: int
        :return: A formatted result string.
        :rtype: str
        '''

        # Return the formatted operation and value.
        return f'{self.operation}: {self.value:.{precision}f}'
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md
