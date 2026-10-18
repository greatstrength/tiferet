# Mappers in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The mappers layer (`tiferet.mappers`) provides the bridge between persistent configuration and runtime domain objects. It introduces two base classes:

1. **Aggregate**  
   - Extends `DomainObject` (which extends `pydantic.BaseModel`).
   - Inherits the strict `extra='forbid'` and `validate_assignment=True` config from `DomainObject`.
   - Provides mutation-safe attribute updates via `set_attribute`, converting any resulting `ValidationError` into a `ModelError` via `ModelError.raise_for_validation`.
   - Concrete aggregates combine a domain object with `Aggregate` to add mutation logic (e.g., `ErrorAggregate(Error, Aggregate)`).

2. **TransferObject**  
   - Extends `DomainObject` with a lenient `ConfigDict` (`extra='ignore'`, `validate_assignment=False`).
   - Manages role-based serialization via a `_ROLES` ClassVar mapping role names to `model_dump` kwargs.
   - Provides `to_primitive(role)`, `map(target)`, and `from_model` classmethod for mapping and transformation.
   - Concrete transfer objects combine a domain object with `TransferObject` to add serialization roles (e.g., `ErrorConfigObject(Error, TransferObject)`).

Together, these classes provide a clear separation of mutation (Aggregate) and serialization (TransferObject) concerns.

### Example: Error Domain

- **Aggregate Use** (`ErrorAggregate`):
  ```python
  class ErrorAggregate(Error, Aggregate):
      # Inherits fields/validation from Error
      # Adds mutation methods (rename, set_message, remove_message)
  ```

- **TransferObject Use** (`ErrorConfigObject`):
  ```python
  class ErrorConfigObject(Error, TransferObject):
      # Inherits fields/validation from Error
      # Adds serialization roles and mapping logic
  ```

## The Aggregate Base Class

`Aggregate` extends `DomainObject` and provides mutation-safe attribute updates:

```python
# tiferet/mappers/core.py

class Aggregate(DomainObject):
    '''
    A mutable, validated representation of a domain aggregate.
    '''

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''Update an attribute, converting any validation failure into a ModelError.'''

        # Apply the update; validate_assignment=True triggers field validation.
        try:
            setattr(self, attribute, value)
        except ValidationError as error:
            ModelError.raise_for_validation(error, model=self, attribute=attribute)
```

Key characteristics:
- Aggregates are instantiated directly via the Pydantic constructor: `ErrorAggregate(id='...', name='...')`.
- **`set_attribute`** relies on `validate_assignment=True` (inherited from `DomainObject`) to trigger field validation on every `setattr`, and converts the resulting Pydantic `ValidationError` into a `ModelError` via `ModelError.raise_for_validation`.
- Invalid attribute mutations (unknown field or invalid value) raise a `ModelError` — not a `TiferetError` — classified as `INVALID_MODEL_ATTRIBUTE_ID` or `INVALID_MODEL_VALUE_ID`. See [docs/guides/errors.md](../guides/errors.md) for why `ModelError` is a deliberately uncatalogued, unrelated exception family.

## The TransferObject Base Class

`TransferObject` extends `DomainObject` with a lenient config and provides:

- **`to_primitive(role, **overrides)`** — Serializes via `model_dump`, applying role-specific kwargs from `_ROLES` and caller overrides.
- **`map(target, **overrides)`** — Serializes via the `to_model` role, merges overrides, and constructs the target aggregate.
- **`from_model(model, **overrides)`** — Classmethod that creates a transfer object from a domain model or aggregate via `model_dump` + `model_validate`.

### Role-Based Serialization

Transfer objects use a `_ROLES` ClassVar to control which fields are serialized for different contexts. Each role maps to a dict of `model_dump` kwargs:

```python
class ErrorConfigObject(Error, TransferObject):
    '''
    A configuration data representation of an error object.
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
- `# * init` — constructor, when the class has one.
- `# * method: <name> (property)` — a descriptive `@property`, after `init` and before mutation or mapping methods. Getter only. No setter.
- `# * method: <name>` — mutation methods on an aggregate, or `map` / `from_model` on a transfer object.

Use `# *** classes` in `core.py` for the base classes themselves.

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

**Example** – `FeatureConfigObject`:
```python
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
        '''Maps the feature data to a feature aggregate.'''
        return super().map(
            FeatureAggregate,
            steps=[step.map() for step in (self.steps or [])],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, feature: Feature, **overrides) -> 'FeatureConfigObject':
        '''Creates a FeatureConfigObject from a Feature model.'''
        return super().from_model(
            feature,
            steps=[
                EventFeatureStepConfigObject.from_model(step)
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
- Instantiate aggregates directly via the Pydantic constructor.
- Use `set_attribute` for validated mutations with unknown-field checking.
- Define `_ROLES` ClassVar on all transfer objects for role-based serialization.
- Use `model_dump` kwargs (`exclude`, `by_alias`, `include`) in `_ROLES` definitions.

## Testing Mappers

Tests validate factory creation, mutation, mapping, serialization, and error handling using `pytest`.

Mapper tests use the `@use_tester` harness ([testing.md](testing.md)). After the preamble, a module holds `# *** fixtures`, `# *** tests`, and `# *** testers` in that order (omit an empty kind).

- **`type='aggregate'`** binds an `AggregateTesterContext`. Declare `target_cls`, `sample_data`, `equality_fields`, `set_attribute_params` (a list of `(attr, value, expect_error_code | None)` tuples), and optionally `field_normalizers`. The context provides `make_target(data=None)`, `assert_new()`, and `assert_set_attribute()`.
- **`type='transfer_object'`** binds a `TransferObjectTesterContext`. Declare `target_cls` (the transfer object), `aggregate_cls`, `sample_data` (configuration format), `aggregate_sample_data`, `equality_fields`, and optionally `field_normalizers` and `map_kwargs`. The context provides `assert_map()`, `assert_from_model()`, and `assert_round_trip()`; its `make_target` constructs the **aggregate**.

### Test File Structure

Mirrors `tests/mappers/test_error.py`:

```python
"""Tiferet Error Mapper Tests"""

# *** imports

# ** app
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject
from tiferet.blueprints.tester import use_tester

# *** constants

# ** constant: error_sample_data
ERROR_SAMPLE_DATA = {
    'id': 'TEST_ERROR',
    'name': 'TEST_ERROR',
    'error_code': 'TEST_ERROR',
    'message': [
        {'lang': 'en', 'text': 'Test error message.'},
    ],
}

# ** constant: error_equality_fields
ERROR_EQUALITY_FIELDS = [
    'id',
    'name',
    'error_code',
]

# *** testers

# ** tester: test_error_aggregate
@use_tester(
    type='aggregate',
    target_cls=ErrorAggregate,
    sample_data=ERROR_SAMPLE_DATA,
    equality_fields=ERROR_EQUALITY_FIELDS,
    set_attribute_params=[
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
class TestErrorAggregate:
    '''
    Tests for ErrorAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * test: new
    def test_new(self, test_ctx):
        '''
        Verify aggregate construction against declared expected data.
        '''

        # Assert construction against the declared sample.
        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''
        Verify declared set_attribute cases.
        '''

        # Assert each declared set_attribute case.
        test_ctx.assert_set_attribute()

    # * test: rename
    def test_rename(self, test_ctx):
        '''
        Test that rename() updates the error name.
        '''

        # Construct the aggregate under test.
        aggregate = test_ctx.make_target()

        # Rename the error.
        aggregate.rename('Renamed Error')

        # Assert the name was updated.
        assert aggregate.name == 'Renamed Error'

# ** tester: test_error_config_object
@use_tester(
    type='transfer_object',
    target_cls=ErrorConfigObject,
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_SAMPLE_DATA,
    aggregate_sample_data=ERROR_SAMPLE_DATA,
    equality_fields=ERROR_EQUALITY_FIELDS,
)
class TestErrorConfigObject:
    '''
    Tests for ErrorConfigObject mapping and round-trip.
    '''

    # * test: round_trip
    def test_round_trip(self, test_ctx):
        '''
        Verify aggregate to transfer object to aggregate preserves data.
        '''

        # Assert the round trip.
        test_ctx.assert_round_trip()
```

### Key Patterns

#### Module-Level Constants
Shared sample data, equality fields, and normalizers are defined as module-level constants under `# *** constants`. This avoids duplication when both the aggregate and transfer object testers need the same data.

#### Normalizer Functions
For fields containing nested domain objects (e.g., lists of services, arguments, dependencies), pass `field_normalizers` that convert both dicts and domain objects into comparable tuples:

```python
# *** constants

# ** constant: field_normalizers
FIELD_NORMALIZERS = {
    'services': lambda svcs: tuple(sorted(svc_tuple(s) for s in (svcs or []))),
}

# *** functions

# ** function: svc_tuple
def svc_tuple(s) -> tuple:
    '''
    Normalize a service (dict or domain object) into a comparable tuple.

    :param s: The service as a dict or a domain object.
    :type s: dict | AppServiceDependency
    :return: A comparable tuple of the service fields.
    :rtype: tuple
    '''

    # Normalize a dict-shaped service.
    if isinstance(s, dict):
        return (s['service_id'], s['module_path'], s['class_name'],
                tuple(sorted(s.get('parameters', {}).items())))

    # Normalize a domain-object service.
    return (s.service_id, s.module_path, s.class_name,
            tuple(sorted((s.parameters or {}).items())))
```

The lambda resolves `svc_tuple` at call time, so the constant can precede the function and the preamble order (`constants` → `functions`) holds.

#### Child Mapper Tests
When a TransferObject contains nested child mappers (e.g., `AppServiceDependencyConfigObject` inside `AppSessionConfigObject`), test the child with `# * test:` members on the parent's tester, or with module-level `# *** tests` functions.

#### Standalone Tests
Small leaf-level mappers without mutation logic (e.g., `ErrorMessageConfigObject`) may use module-level `# *** tests` functions instead of a tester; they sit before `# *** testers`.

## Package Layout

Mappers are defined in `tiferet/mappers/`:

- `core.py` — `Aggregate` and `TransferObject` base classes + constants.
- `app.py` — `AppSessionAggregate`, `AppSessionConfigObject`.
- `cli.py` — `CliArgumentAggregate`, `CliCommandAggregate`, `CliCommandConfigObject`.
- `di.py` — `ServiceRegistrationAggregate`, `ServiceRegistrationConfigObject`.
- `error.py` — `ErrorAggregate`, `ErrorConfigObject`, `ErrorMessageConfigObject`.
- `feature.py` — `FeatureAggregate`, `FeatureConfigObject`, `EventFeatureStepAggregate`, `EventFeatureStepConfigObject`.
- `logging.py` — `FormatterAggregate`, `HandlerAggregate`, `LoggerAggregate`, and their ConfigObject counterparts.
- `__init__.py` — Public exports.

Tests live in `tests/mappers/`.

## Conclusion

The mappers layer provides the structural bridge between persistent configuration and runtime domain objects, with clear separation between mutation (`Aggregate`) and serialization (`TransferObject`). This design enables:
- Validated, mutation-safe domain updates.
- Role-based serialization for multiple output formats.

Explore source in `tiferet/mappers/` and tests in `tests/mappers/` for implementation details.
