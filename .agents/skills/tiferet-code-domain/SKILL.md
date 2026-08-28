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
# * property: <name>                      ← artifact member: parameter-free description
# * method: <name>                        ← artifact member: parameterized description
# * method: _<verb>_<name> (field validator)
# * method: _<verb>_<name> (model validator)
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
- Expose a domain object's **methods of description** without changing its state:
  - Use a getter-only `@property` when the description is deterministic from `self` and takes no caller input. Do not define a setter. Examples: `display_label`, `is_complete`, or a derived identifier.
  - Use an instance method when the caller supplies an input that changes the description, such as formatting precision, language, or a lookup key. Examples: `format_result(precision)` and `get_service(service_id)`.
  - Keep both forms pure: they may inspect fields and perform local computation, but must not assign fields, call services, perform I/O, depend on time or randomness, or conceal a domain operation. Put those operations in an event, context, or utility.
  - Model a value as a `Field` rather than a property when it is supplied, persisted, serialized, or independently validated. A property is derived presentation or interpretation, not shadow state.
- Naming: PascalCase class names matching the domain concept (`AppSession`, `Feature`, `Error`, `CliCommand`).
## Validator selection

Choose the narrowest validation mechanism that expresses the rule. Validators preserve a model's construction contract; they are not substitutes for descriptive properties or methods.

1. **No validator:** Prefer the field annotation and `Field(...)` constraints when Pydantic can express the rule directly: requiredness, optionality, nested model type, `Literal` choices, numeric bounds, length, pattern, or a default/default factory.
2. **`@field_validator`:** Use when the input, normalization, or invariant concerns one declared field (or the same independent rule genuinely applies to named fields). Prefer the default `mode='after'`, where Pydantic has already produced a typed value. Use `mode='before'` only when a raw external form must be normalized before field parsing. Return the field value. Do not use a field validator to coordinate peer fields; field ordering makes that coupling fragile.
3. **`@model_validator`:** Use only when the rule needs the whole input:
   - `mode='before'` canonicalizes alternate input shapes or derives one or more persisted fields from several raw inputs. Accept `Any`, leave non-dict input unchanged, and copy a dict before modifying it.
   - `mode='after'` verifies an invariant across already validated fields. Write it as an instance method and return `self`.
   - Do not use `mode='wrap'` or `mode='plain'` unless the requirement explicitly needs to surround or replace Pydantic's normal validation.

Name and label validators for their action: `_normalize_<field>` for field normalization, `_validate_<field>` for a field invariant, `_derive_<name>` for model-level derivation, and `_validate_<rule>` for a model-level invariant.

## Example

```python
# *** imports

# ** core
from typing import Any

# ** infra
from pydantic import Field, field_validator

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

    # * property: display_label
    @property
    def display_label(self) -> str:
        '''
        Describe the result with the default display precision.

        :return: The derived display label.
        :rtype: str
        '''

        # Return the parameter-free description.
        return self.format_result()

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

    # * method: _normalize_operation (field validator)
    @field_validator('operation')
    @classmethod
    def _normalize_operation(cls, value: str) -> str:
        '''
        Normalize the independently meaningful operation field.

        :param value: The typed operation value.
        :type value: str
        :return: The normalized operation value.
        :rtype: str
        '''

        # Return the normalized operation value.
        return value.strip().lower()
```
Use a model validator only when it has model-wide work to do. This compact
pattern derives a persisted identifier from two peer inputs; it is distinct
from the non-persisted `display_label` property above:

```python
# ** infra
from pydantic import model_validator

# * method: _derive_id (model validator)
@model_validator(mode='before')
@classmethod
def _derive_id(cls, data: Any) -> Any:
    '''Derive a persisted id from the raw group and key inputs.'''

    # Leave non-mapping input for Pydantic to handle.
    if not isinstance(data, dict):
        return data

    # Copy before deriving a missing persisted field.
    data = dict(data)
    if not data.get('id') and data.get('group_id') and data.get('key'):
        data['id'] = f"{data['group_id']}.{data['key']}"

    # Return the canonicalized raw input.
    return data
```

## Docstrings & guides

- **Docstrings & guides:** A domain class's docstring opens with a 1–2 sentence vision-tier value statement (why the concept exists), linked via a `# >> see: @guides/domain/<module>.md#<anchor>` tag to the corresponding `docs/guides/domain/*.md` entry, which carries the full distillation-tier detail. See `tiferet-guide-docs` for the complete convention.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md
