# Mappers in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The mappers layer (`tiferet.mappers`) provides the bridge between persistent configuration and runtime domain objects. It introduces two base classes:

1. **Aggregate**  
   - Extends `DomainObject` (which extends `pydantic.BaseModel`).
   - Inherits the strict `extra='forbid'` and `validate_assignment=True` config from `DomainObject`.
   - Provides mutation-safe attribute updates via `set_attribute`, converting a Pydantic `ValidationError` into a `ModelError`.
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
        '''Update an attribute, converting a validation failure into a model error.'''

        # Apply the update, converting validation failures into a model error.
        try:
            setattr(self, attribute, value)

        # An unknown attribute or an invalid value both surface here; the
        # raiser classifies which of the two occurred and describes this
        # aggregate as the offending instance.
        except ValidationError as error:
            ModelError.raise_for_validation(
                error,
                model=self,
                attribute=attribute,
            )
```

Key characteristics:
- Aggregates are instantiated directly via the Pydantic constructor: `ErrorAggregate(id='...', name='...')`.
- **`set_attribute`** relies on Pydantic rather than a hand-rolled existence check: `extra='forbid'` and `validate_assignment=True` (both inherited from `DomainObject`) reject an unknown field and an invalid value alike, and the resulting `ValidationError` is converted.
- Invalid attribute mutations raise `ModelError` — **not** a `TiferetError`. `ModelError.raise_for_validation` selects the code itself: `INVALID_MODEL_ATTRIBUTE_ID` when Pydantic reports a `no_such_attribute` violation, otherwise `INVALID_MODEL_VALUE_ID`. The original `ValidationError` is preserved as the exception cause.
- Passing `model=self` describes the offending aggregate onto the error (`type`, `module`, and any declared `id` / `name` / `key`), so the leaked defect names *which* aggregate refused the mutation and not merely which attribute. The gated `set_attribute` overrides pass the same. See [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) for `describe_model`.
- The error vocabulary lives in `tiferet/domain/core.py`, so the `mappers` layer imports only `domain` — there is no `mappers` → `events` or `mappers` → `assets` edge.

### Why `ModelError` and not `TiferetError`

A model inconsistency is a **consumer defect**, not a domain outcome. `ModelError` is therefore a standalone `Exception`: it is not catalogued in `assets/error.py`, not localized, not formatted into a `TiferetAPIError`, and not skippable via a step's `pass_on_error` flag. It carries its own message and leaks to the top of the call stack as the intended defect signal.

A third constant, `ATTRIBUTE_NOT_SETTABLE_ID`, covers the distinct case where a field exists but a dedicated mutator owns it — see the gated `set_attribute` pattern in [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md).

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
- `# * method: <name>` — instance or class methods.

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
- Use `set_attribute` for validated mutations; it converts a Pydantic failure into a `ModelError`.
- Define `_ROLES` ClassVar on all transfer objects for role-based serialization.
- Use `model_dump` kwargs (`exclude`, `by_alias`, `include`) in `_ROLES` definitions.

## Testing Mappers

Tests validate construction, mutation, mapping, serialization, and error handling using pytest (optional extra; runner for `tests/`). Bind a variant tester context with `@use_tester` / `build_tester_context`. Full conventions: [testing.md](testing.md).

**Test-module groups:** `# *** fixtures` → `# *** tests` (functions) → `# *** testers` (`Test*` tester classes). Tester members are `# * fixture:` / `# * test:` only. Bulk remediating existing `tests/mappers/` files is not required of this documentation pass.

**Aggregate testers** (`type='aggregate'` → `AggregateTesterContext`):
- Pass `target_cls`, `sample_data`, `equality_fields`, and `set_attribute_params` as `(attr, value, expect_error_code | None)`.
- Call `test_ctx.assert_new()` and `test_ctx.assert_set_attribute()`. Domain-specific mutations use `test_ctx.make_target()`.
- Invalid `set_attribute` rows expect a `ModelError` whose `error_code` is `INVALID_MODEL_ATTRIBUTE_ID`, `INVALID_MODEL_VALUE_ID`, or `ATTRIBUTE_NOT_SETTABLE_ID` (import from `tiferet.domain`).

**Transfer-object testers** (`type='transfer_object'` → `TransferObjectTesterContext`):
- Pass `target_cls`, `aggregate_cls` (or `aggregate_module_path` / `aggregate_class_name`), `sample_data`, `aggregate_sample_data`, `equality_fields`; optional `field_normalizers`, `map_kwargs`.
- Call `test_ctx.assert_map()`, `test_ctx.assert_from_model()`, `test_ctx.assert_round_trip()`.

```python
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject
from tiferet.blueprints.tester import use_tester

# *** testers

# ** tester: test_error_aggregate
@use_tester(
    type='aggregate',
    target_cls=ErrorAggregate,
    sample_data=ERROR_SAMPLE_DATA,
    equality_fields=EQUALITY_FIELDS,
    set_attribute_params=[
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
class TestErrorAggregate:

    # * test: new
    def test_new(self, test_ctx):
        test_ctx.assert_new()

    # * test: rename
    def test_rename(self, test_ctx):
        aggregate = test_ctx.make_target()
        aggregate.rename('Renamed Error')
        assert aggregate.name == 'Renamed Error'

# ** tester: test_error_config_object
@use_tester(
    type='transfer_object',
    target_cls=ErrorConfigObject,
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_SAMPLE_DATA,
    aggregate_sample_data=ERROR_SAMPLE_DATA,
    equality_fields=EQUALITY_FIELDS,
)
class TestErrorConfigObject:

    # * test: map
    def test_map(self, test_ctx):
        test_ctx.assert_map()
```

### Key Patterns

#### Module-Level Constants
Shared sample data, equality fields, and normalizers are defined as module-level constants under `# *** constants`. This avoids duplication when both the Aggregate and TransferObject testers need the same data.

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
When a TransferObject contains nested child mappers (e.g., `AppServiceDependencyConfigObject` inside `AppSessionConfigObject`), test the child within the parent's test class under a `# *** child mapper: <ChildName>` sub-section.

#### Standalone Tests
Small leaf-level mappers without mutation logic (e.g., `ErrorMessageConfigObject`) may use standalone `# ** test:` functions instead of a bound tester, placed under `# *** tests`.

## Package Layout

Mappers are defined in `tiferet/mappers/`:

- `core.py` — `Aggregate` and `TransferObject` base classes + constants.
- `app.py` — `AppSessionAggregate`, `AppSessionConfigObject`.
- `cli.py` — `CliArgumentAggregate`, `CliCommandAggregate`, `CliCommandConfigObject`.
- `di.py` — `ServiceRegistrationAggregate`, `ServiceRegistrationConfigObject`.
- `error.py` — `ErrorAggregate`, `ErrorConfigObject`, `ErrorMessageConfigObject`.
- `feature.py` — `FeatureAggregate`, `FeatureConfigObject`, `EventFeatureStepAggregate`, `EventFeatureStepConfigObject`.
- `logging.py` — `FormatterAggregate`, `HandlerAggregate`, `LoggerAggregate`, and their ConfigObject counterparts.
- `tester.py` — `TesterAggregate`, `TesterConfigObject`.
- `__init__.py` — Public exports.

Tests live in `tests/mappers/`.

## Conclusion

The mappers layer provides the structural bridge between persistent configuration and runtime domain objects, with clear separation between mutation (`Aggregate`) and serialization (`TransferObject`). This design enables:
- Validated, mutation-safe domain updates.
- Role-based serialization for multiple output formats.

Explore source in `tiferet/mappers/` and tests in `tests/mappers/` for implementation details.
