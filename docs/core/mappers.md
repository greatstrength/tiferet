# Mappers in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The mappers layer (`tiferet.mappers`) provides the bridge between persistent configuration and runtime domain objects. It introduces two base classes:

1. **Aggregate**  
   - Extends `DomainObject` (which extends `pydantic.BaseModel`).
   - Inherits the strict `extra='forbid'` and `validate_assignment=True` config from `DomainObject`.
   - Provides mutation-safe attribute updates via `set_attribute` with validation using `model_fields` and `RaiseError`.
   - Concrete aggregates combine a domain object with `Aggregate` to add mutation logic (e.g., `ErrorAggregate(Error, Aggregate)`).

2. **TransferObject**  
   - Extends `DomainObject` with a lenient `ConfigDict` (`extra='ignore'`, `validate_assignment=False`).
   - Manages role-based serialization via a `_ROLES` ClassVar mapping role names to `model_dump` kwargs.
   - Provides `to_primitive(role)`, `map(target)`, and `from_model` classmethod for mapping and transformation.
   - Concrete transfer objects combine a domain object with `TransferObject` to add serialization roles (e.g., `ErrorYamlObject(Error, TransferObject)`).

Together, these classes replace the legacy `DataObject` (`tiferet.data.settings`) with a clearer separation of mutation (Aggregate) and serialization (TransferObject) concerns.

### Example: Error Domain

- **Aggregate Use** (`ErrorAggregate`):
  ```python
  class ErrorAggregate(Error, Aggregate):
      # Inherits fields/validation from Error
      # Adds mutation methods (rename, set_message, remove_message)
  ```

- **TransferObject Use** (`ErrorYamlObject`):
  ```python
  class ErrorYamlObject(Error, TransferObject):
      # Inherits fields/validation from Error
      # Adds serialization roles and mapping logic
  ```

## The Aggregate Base Class

`Aggregate` extends `DomainObject` and provides mutation-safe attribute updates:

```python
# tiferet/mappers/settings.py

class Aggregate(DomainObject):
    '''
    A mutable, validated representation of a domain aggregate.
    '''

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''Update an attribute, raising an error if it is unknown.'''

        # Reject unknown attribute names by raising a structured error.
        if attribute not in type(self).model_fields:
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                attribute=attribute,
            )

        # Apply the update; validate_assignment=True triggers field validation.
        setattr(self, attribute, value)
```

Key characteristics:
- Aggregates are instantiated directly via the Pydantic constructor: `ErrorAggregate(id='...', name='...')`.
- **`set_attribute`** checks `model_fields` to verify the attribute exists before mutation; `validate_assignment=True` (inherited from `DomainObject`) triggers field validation on every `setattr`.
- Invalid attribute mutations raise `TiferetError` via `RaiseError.execute` with `INVALID_MODEL_ATTRIBUTE_ID`.

## The TransferObject Base Class

`TransferObject` extends `DomainObject` with a lenient config and provides:

- **`to_primitive(role, **overrides)`** — Serializes via `model_dump`, applying role-specific kwargs from `_ROLES` and caller overrides.
- **`map(target, **overrides)`** — Serializes via the `to_model` role, merges overrides, and constructs the target aggregate.
- **`from_model(model, **overrides)`** — Classmethod that creates a transfer object from a domain model or aggregate via `model_dump` + `model_validate`.

### Role-Based Serialization

Transfer objects use a `_ROLES` ClassVar to control which fields are serialized for different contexts. Each role maps to a dict of `model_dump` kwargs:

```python
class ErrorYamlObject(Error, TransferObject):
    '''
    A YAML data representation of an error object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'message'}},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }
```

The `to_primitive` method delegates to Pydantic `model_dump`, defaulting to `exclude_none=True` and merging role-specific and caller-supplied kwargs:

```python
def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {'exclude_none': True}
    if role and role in type(self)._ROLES:
        kwargs.update(type(self)._ROLES[role])
    kwargs.update(overrides)
    return self.model_dump(**kwargs)
```

## Structured Code Design

Mapper classes follow the standard Tiferet artifact comment structure:

- `# *** mappers` — top-level section for mapper modules.
- `# ** mapper: <name>` — individual mapper (snake_case).
- `# * attribute: <name>` — instance attributes (Pydantic `Field(...)` annotations or `ClassVar`).
- `# * method: <name>` — instance or class methods.

Use `# *** classes` in `settings.py` for the base classes themselves.

**Spacing rules:**
- One empty line between `# *** mappers` and first `# ** mapper`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating and Extending Mappers

### 1. Define an Aggregate
- Combine domain object + `Aggregate`.
- Add mutation methods under `# * method: <name>`.
- Instantiate directly via the Pydantic constructor.

**Example** – `FeatureAggregate`:
```python
# *** mappers

# ** mapper: feature_aggregate
class FeatureAggregate(Feature, Aggregate):
    '''
    Aggregate for the Feature domain object.
    '''

    # * method: rename
    def rename(self, name: str) -> None:
        '''Rename the feature.'''
        # validate_assignment=True handles re-validation.
        self.name = name
```

### 2. Define a TransferObject
- Combine domain object + `TransferObject`.
- Define `_ROLES` ClassVar for role-based serialization with `model_dump` kwargs.
- Use `serialization_alias` and `AliasChoices` / `validation_alias` for attribute aliasing.
- Override `map()` to specify the target aggregate and handle nested mapping.
- Override `from_model()` as a `@classmethod` to handle nested conversions.

**Example** – `FeatureYamlObject`:
```python
# ** mapper: feature_yaml_object
class FeatureYamlObject(Feature, TransferObject):
    '''
    YAML transfer object for the Feature domain object.
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
    steps: List[FeatureEventYamlObject] = Field(
        default_factory=list,
        validation_alias=AliasChoices('handlers', 'functions', 'commands', 'steps'),
        description='The step workflow for the feature.',
    )

    # * method: map
    def map(self, **overrides) -> FeatureAggregate:
        '''Maps the feature data to a feature aggregate.'''
        return super().map(
            FeatureAggregate,
            steps=[step.map() for step in (self.steps or [])],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, feature: Feature, **overrides) -> 'FeatureYamlObject':
        '''Creates a FeatureYamlObject from a Feature model.'''
        return super().from_model(
            feature,
            steps=[
                FeatureEventYamlObject.from_model(step)
                for step in feature.steps
            ],
            **overrides,
        )
```

### 3. Attribute Aliasing

TransferObjects support `serialization_alias` for output aliasing and `validation_alias` (with `AliasChoices`) for accepting multiple input field names:

```python
# * attribute: parameters
parameters: Dict[str, str] = Field(
    default_factory=dict,
    serialization_alias='params',
    validation_alias=AliasChoices('params', 'parameters'),
    description='The parameters for the feature event.',
)
```

### 4. Use in Repositories
Repositories use transfer objects to load from configuration and map to aggregates/domain objects.

### Best Practices
- Use artifact comments consistently (`# *** mappers`, `# ** mapper:`, `# *`).
- Keep aggregates focused on mutation; keep transfer objects focused on serialization.
- Instantiate aggregates directly via the Pydantic constructor — there is no `Aggregate.new()` factory.
- Use `set_attribute` for validated mutations with unknown-field checking.
- Define `_ROLES` ClassVar on all transfer objects for role-based serialization.
- Use `model_dump` kwargs (`exclude`, `by_alias`, `include`) in `_ROLES` definitions.

## Testing Mappers

Tests validate factory creation, mutation, mapping, serialization, and error handling using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Example** – Aggregate tests cover constructor instantiation, `set_attribute` (success and invalid attribute error).

#### `MapperAssertions` (mixin)
Provides shared assertion helpers used by both base classes:
- **`assert_model_matches(model, sample, equality_fields, field_normalizers)`** — Compares model attributes against a sample dict using configured fields. Per-field normalizers allow custom comparison logic for complex types.
- **`assert_nested_list_matches(actual_list, expected_list, key_field, compare_fields)`** — Compares lists of domain objects by a key field (e.g., `service_id`, `flag`), useful for verifying nested collections through round-trips.

#### `AggregateTestBase`
Base class for testing Aggregate components. Subclasses define class attributes and inherit automatic tests.

**Required class attributes:**
- `aggregate_cls` — The Aggregate class under test.
- `sample_data` — Dict of aggregate-format sample data.
- `equality_fields` — List of field names to compare.
- `set_attribute_params` — List of `(attr, value, expect_error_code | None)` tuples.

**Optional class attributes:**
- `field_normalizers` — Dict mapping field names to normalizer callables for complex comparisons.

**Inherited tests:**
- `test_new` — Verifies direct constructor instantiation and field values.
- `test_set_attribute` — Parametrized test for valid and invalid attribute mutations. Parametrization is driven by `conftest.pytest_generate_tests`.

**Override hook:**
- `make_aggregate(data=None)` — Override when the aggregate has a custom constructor signature. The default implementation uses the standard Pydantic constructor: `self.aggregate_cls(**data)`.

#### `TransferObjectTestBase`
Base class for testing TransferObject components.

**Required class attributes:**
- `transfer_cls` — The TransferObject class under test.
- `aggregate_cls` — The target Aggregate class.
- `sample_data` — Dict of YAML-format sample data (as it appears in configuration).
- `aggregate_sample_data` — Dict of aggregate-format expected data (with defaults filled in, lists instead of dicts, etc.).
- `equality_fields` — List of field names to compare.

**Optional class attributes:**
- `field_normalizers` — Per-field normalizer callables.
- `map_kwargs` — Extra kwargs to pass to `.map()`.

**Inherited tests:**
- `test_map` — Verifies `model_validate()` → `map()` produces a valid aggregate.
- `test_from_model` — Verifies aggregate → TransferObject conversion via `from_model()` classmethod.
- `test_round_trip` — Verifies aggregate → TransferObject → aggregate preserves data.

**Override hook:**
- `make_aggregate(data=None)` — Same purpose as `AggregateTestBase`.

#### `conftest.py` Hook
The `pytest_generate_tests` hook dynamically parametrizes `test_set_attribute` for any `AggregateTestBase` subclass, reading from the class's `set_attribute_params` attribute.

### Test File Structure

Harness-based test files follow this structure:

```python
"""Tiferet <Domain> Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import TransferObject
from ..<domain> import SomeAggregate, SomeYamlObject
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = { ... }

# ** constant: equality_fields
EQUALITY_FIELDS = [ ... ]

# ** constant: item_tuple
def ITEM_TUPLE(item):
    '''Normalize a nested item (dict or domain object) into a comparable tuple.'''
    ...

# ** constant: field_normalizers
FIELD_NORMALIZERS = {
    'items': lambda items: tuple(sorted(ITEM_TUPLE(i) for i in (items or []))),
}


# *** classes

# ** class: TestSomeAggregate
class TestSomeAggregate(AggregateTestBase):
    '''Tests for SomeAggregate.'''

    aggregate_cls = SomeAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS
    field_normalizers = FIELD_NORMALIZERS

    set_attribute_params = [
        ('name',         'Updated Name',  None),
        ('invalid_attr', 'value',         'INVALID_MODEL_ATTRIBUTE'),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data=None):
        '''Override for custom constructor signature.'''
        return SomeAggregate(
            **(data if data is not None else self.sample_data)
        )

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test domain-specific mutation.'''
        aggregate.rename('New Name')
        assert aggregate.name == 'New Name'


# ** class: TestSomeYamlObject
class TestSomeYamlObject(TransferObjectTestBase):
    '''Tests for SomeYamlObject.'''

    transfer_cls = SomeYamlObject
    aggregate_cls = SomeAggregate
    sample_data = { ... }  # YAML-format
    aggregate_sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS
    field_normalizers = FIELD_NORMALIZERS

    # * method: make_aggregate
    def make_aggregate(self, data=None):
        '''Override for custom constructor signature.'''
        return SomeAggregate(
            **(data if data is not None else self.aggregate_sample_data)
        )

    # *** child mapper: ChildYamlObject

    # ** test: child_yaml_map_basic
    def test_child_yaml_map_basic(self):
        '''Test child mapper mapping.'''
        ...
```

### Key Patterns

#### Module-Level Constants
Shared sample data, equality fields, and normalizers are defined as module-level constants under `# *** constants`. This avoids duplication when both the Aggregate and TransferObject test classes need the same data.

#### Normalizer Functions
For fields containing nested domain objects (e.g., lists of services, arguments, dependencies), define a normalizer function that converts both dicts and domain objects into comparable tuples:

```python
# ** constant: svc_tuple
def SVC_TUPLE(s):
    '''Normalize a service (dict or domain object) into a comparable tuple.'''
    if isinstance(s, dict):
        return (s['service_id'], s['module_path'], s['class_name'],
                tuple(sorted(s.get('parameters', {}).items())))
    return (s.service_id, s.module_path, s.class_name,
            tuple(sorted((s.parameters or {}).items())))

# ** constant: field_normalizers
FIELD_NORMALIZERS = {
    'services': lambda svcs: tuple(sorted(SVC_TUPLE(s) for s in (svcs or []))),
}
```

#### Child Mapper Tests
When a TransferObject contains nested child mappers (e.g., `AppServiceDependencyYamlObject` inside `AppInterfaceYamlObject`), test the child within the parent's test class under a `# *** child mapper: <ChildName>` sub-section.

#### Standalone Tests
Small leaf-level mappers without mutation logic (e.g., `ErrorMessageYamlObject`) may use standalone test functions instead of the harness, placed after the class-based tests.

### Migration Status

The following test modules have been migrated to the harness-based style:
- `test_app.py`, `test_cli.py`, `test_di.py`, `test_error.py`, `test_feature.py`, `test_logging.py`

The following use the legacy standalone style and are candidates for migration:
- `test_container.py`

`test_settings.py` tests the base classes themselves and appropriately uses standalone functions.

## Package Layout

Mappers are defined in `tiferet/mappers/`:

- `settings.py` — `Aggregate` and `TransferObject` base classes + constants.
- `app.py` — `AppInterfaceAggregate`, `AppInterfaceYamlObject`.
- `cli.py` — `CliArgumentAggregate`, `CliCommandAggregate`, `CliCommandYamlObject`.
- `di.py` — `ServiceConfigurationAggregate`, `ServiceConfigurationYamlObject`.
- `error.py` — `ErrorAggregate`, `ErrorYamlObject`, `ErrorMessageYamlObject`.
- `feature.py` — `FeatureAggregate`, `FeatureYamlObject`, `FeatureEventAggregate`, `FeatureEventYamlObject`.
- `logging.py` — `FormatterAggregate`, `HandlerAggregate`, `LoggerAggregate`, and their YamlObject counterparts.
- `__init__.py` — Public exports.

Tests live in `tiferet/mappers/tests/`.

## Migration from Schematics to Pydantic v2

The mappers layer was migrated from `schematics.Model` to Pydantic v2:

- `Aggregate.new(Type, **kwargs)` → Direct Pydantic constructor: `Type(**kwargs)`.
- `set_attribute` now checks `model_fields` instead of `hasattr`; `validate_assignment=True` handles re-validation.
- `TransferObject.from_data(Type, **kwargs)` → `Type.model_validate(data_dict)`.
- `TransferObject.allow()` / `deny()` / `class Options` / `serialize_when_none` → `_ROLES` ClassVar with `model_dump` kwargs (`include`, `exclude`, `by_alias`, `exclude_none`).
- `to_primitive(role)` now delegates to `model_dump` with role-resolved kwargs.
- `from_model` is now a `@classmethod` on `TransferObject` using `model_dump(by_alias=False)` + `model_validate`.
- Attribute aliasing: `serialized_name` → `serialization_alias`; `deserialize_from` → `validation_alias` with `AliasChoices`.

## Conclusion

The mappers layer provides the structural bridge between persistent configuration and runtime domain objects, with clear separation between mutation (`Aggregate`) and serialization (`TransferObject`). This design enables:
- Validated, mutation-safe domain updates.
- Role-based serialization for multiple output formats.
- Incremental migration from the legacy `DataObject` pattern.

Explore source in `tiferet/mappers/` and tests in `tiferet/mappers/tests/` for implementation details.
