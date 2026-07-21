---
name: tiferet-code-mappers
description: Apply mapper conventions when adding or modifying Aggregates or TransferObjects (ConfigObjects) in a Tiferet-family repo. Covers the Aggregate/TransferObject base classes, _ROLES serialization, aliasing, and the AggregateTestBase/TransferObjectTestBase harnesses.
---

# Mappers Code Style – Tiferet

## When to use
- When adding or modifying an Aggregate or TransferObject (ConfigObject) in `tiferet/mappers/`.
- When adding mutation methods to a domain aggregate.
- When defining serialization roles for a configuration object.
- Pair with `tiferet-code-domain` (field shapes) and `tiferet-code-testing` (harness details).

## Artifact comment structure

```
# *** mappers                       ← top-level for mapper modules
# ** mapper: <snake_case_name>      ← individual mapper (Aggregate or ConfigObject)
# * attribute: <name>               ← Pydantic Field or ClassVar
# * method: <name>                  ← mutation methods (Aggregate) or map/from_model (ConfigObject)
```

Use `# *** classes` in `settings.py` for the `Aggregate` and `TransferObject` base classes themselves.

## Key conventions

**Naming:**
- `<Domain>Aggregate` — mutable extension of a domain object (e.g. `ErrorAggregate`, `FeatureAggregate`).
- `<Domain>ConfigObject` — serialization transfer object (e.g. `ErrorConfigObject`, `FeatureConfigObject`).

**Aggregate:**
- Combine the domain object + `Aggregate`: `class ErrorAggregate(Error, Aggregate)`.
- Instantiate via direct Pydantic constructor: `ErrorAggregate(id='ERR', name='Error')`.
- Add mutation methods; `validate_assignment=True` (inherited) triggers field validation on every `setattr`.
- Use `set_attribute(attr, value)` for safe mutations with unknown-field checking; raises `INVALID_MODEL_ATTRIBUTE_ID` for unknown attrs.
- No `Aggregate.new()` factory — use the constructor directly.

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
from ..mappers.settings import Aggregate, TransferObject

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
