---
name: tiferet-code-mappers
description: Apply mapper conventions when adding or modifying Aggregates or TransferObjects (ConfigObjects) in a Tiferet-family repo. Covers the Aggregate/TransferObject base classes, _ROLES serialization, aliasing, and the AggregateTestBase/TransferObjectTestBase harnesses.
---

# Mappers Code Style – Tiferet

## When to use
- When adding or modifying an Aggregate or TransferObject in `tiferet/mappers/`.
- When adding mutation methods to a domain aggregate.
- When defining serialization roles for domain objects going to and from any persistence or transport layer (config files, databases, REST, etc.). `ConfigObject` is the framework's own example of the pattern.
- Pair with `tiferet-code-domain` (field shapes) and `tiferet-code-testing` (harness details).

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** mappers            ← construct group for this skill
# *** exports            ← __init__.py only
```

Mapper-specific labels:
```
# *** mappers                       ← artifact section
# ** mapper: <snake_case_name>      ← artifact (Aggregate or TransferObject)
# * attribute: <name>               ← artifact member: Pydantic Field or ClassVar
# * method: <name>                  ← artifact member: mutation methods (Aggregate) or map/from_model (TransferObject)
```

Use `# *** classes` in `core.py` for the `Aggregate` and `TransferObject` base classes themselves.

## Key conventions

**Layer boundary — valid `# ** app` imports:** `domain` (the domain object being extended), `events` (`RaiseError`, `a`). Never import from `interfaces`, `repos`, `utils`, `contexts`, or `blueprints`.

**Naming:**
- `<Domain>Aggregate` — mutable extension of a domain object (e.g. `ErrorAggregate`, `FeatureAggregate`).
- `<Domain>TransferObject` — default name for a serialization transfer object when the backing medium is not known or is general-purpose.
- Use a precision suffix when the backing medium is specific: `<Domain>ConfigObject` (YAML/JSON config), `<Domain>SqliteObject` (SQLite). These replace `TransferObject` in the class name when the medium is known.

**Aggregate:**
- Combine the domain object + `Aggregate`: `class ErrorAggregate(Error, Aggregate)`.
- Instantiate via direct Pydantic constructor: `ErrorAggregate(id='ERR', name='Error')`.
- Add mutation methods; `validate_assignment=True` (inherited) triggers field validation on every `setattr`.
- Use `set_attribute(attr, value)` for safe mutations with unknown-field checking; raises `INVALID_MODEL_ATTRIBUTE_ID` for unknown attrs.
- No `Aggregate.new()` factory — use the constructor directly.
- `to_dict(role=None, **overrides)` — serialize an aggregate to a dict; mirrors `TransferObject.to_primitive` for consistent serialization without going through a transfer object.

**TransferObject (ConfigObject):**
- Combine the domain object + `TransferObject`: `class ErrorConfigObject(Error, TransferObject)`.
- Lenient config: `extra='ignore'`, `validate_assignment=False`.
- Declare a `_ROLES: ClassVar[Dict[str, Dict[str, Any]]]` mapping role names to `model_dump` kwargs.
  - `'to_model'` — for mapping to an aggregate (typically excludes nested child lists already mapped).
  - `'to_data'` — for serializing back to configuration file format.
- `to_primitive(role, **overrides)` — serializes with `model_dump` + role kwargs; defaults to `exclude_none=True`.
- `map(**overrides)` — serializes via `to_model` role then constructs the target aggregate.
- `from_model(cls, model, **overrides)` — `@classmethod` creating a ConfigObject from a domain model or aggregate.
- Attribute aliasing: `serialization_alias` for output aliasing, `validation_alias=AliasChoices(...)` for multiple input names.

## Example

```python
# *** imports

# ** core
from typing import ClassVar, Dict, Any, List

# ** infra
from pydantic import Field, AliasChoices

# ** app
from ..domain.feature import Feature, EventFeatureStep
from ..mappers.core import Aggregate, TransferObject

# *** mappers

# ** mapper: feature_aggregate
class FeatureAggregate(Feature, Aggregate):
    '''
    Mutable aggregate for the Feature domain object.
    '''

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the feature.

        :param name: The new feature name.
        :type name: str
        '''

        # Assign the new name; validate_assignment=True re-validates.
        self.name = name


# ** mapper: feature_config_object
class FeatureConfigObject(Feature, TransferObject):
    '''
    Configuration data representation of the Feature domain object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'steps'}},
        'to_data': {
            'by_alias': True,
            'exclude': {'feature_key', 'group_id', 'id'},
        },
    }

    # * attribute: steps
    steps: List[EventFeatureStepConfigObject] = Field(
        default_factory=list,
        validation_alias=AliasChoices('handlers', 'functions', 'commands', 'steps'),
        description='The step workflow for the feature.',
    )

    # * method: map
    def map(self, **overrides) -> FeatureAggregate:
        '''
        Map the feature configuration data to a FeatureAggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped FeatureAggregate.
        :rtype: FeatureAggregate
        '''

        # Map each step then delegate to the base map.
        return super().map(
            FeatureAggregate,
            steps=[step.map() for step in (self.steps or [])],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, feature: Feature, **overrides) -> 'FeatureConfigObject':
        '''
        Create a FeatureConfigObject from a Feature model.

        :param feature: The Feature domain object.
        :type feature: Feature
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed FeatureConfigObject.
        :rtype: FeatureConfigObject
        '''

        # Convert each step then delegate to the base from_model.
        return super().from_model(
            feature,
            steps=[EventFeatureStepConfigObject.from_model(s) for s in feature.steps],
            **overrides,
        )
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md
