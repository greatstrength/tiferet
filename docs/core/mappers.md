# Mappers in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The mappers layer (`tiferet.mappers`) provides the bridge between persistent configuration and runtime domain objects. It introduces two base classes:

1. **Aggregate**  
   - Extends `schematics.Model`.
   - Provides a static factory (`Aggregate.new`) and mutation-safe attribute updates (`set_attribute`) with validation via `RaiseError`.
   - Concrete aggregates combine a domain object with `Aggregate` to add mutation logic (e.g., `ErrorAggregate(Error, Aggregate)`).

2. **TransferObject**  
   - Extends `schematics.Model`.
   - Manages role-based serialization, mapping, and transformation between configuration data and runtime models.
   - Provides `map`, `from_model`, `from_data`, `allow`, and `deny` methods.
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

`Aggregate` extends `schematics.Model` and provides:

```python
# tiferet/mappers/settings.py

class Aggregate(Model):
    '''
    A data representation of an aggregate object.
    '''

    # * method: new
    @staticmethod
    def new(
        aggregate_type: type,
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'Aggregate':
        '''Initializes a new aggregate object.'''
        aggregate_object = aggregate_type(dict(**kwargs), strict=strict)
        if validate:
            aggregate_object.validate()
        return aggregate_object

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''Update an attribute with validation.'''
        if not hasattr(self, attribute):
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                attribute=attribute,
            )
        setattr(self, attribute, value)
        self.validate()
```

Key characteristics:
- **`Aggregate.new(Type, **kwargs)`** is the standard factory for all aggregates.
- **`set_attribute`** validates the attribute exists before mutation and re-validates after update.
- Invalid attribute mutations raise `TiferetError` via `RaiseError.execute` with `INVALID_MODEL_ATTRIBUTE_ID`.

## The TransferObject Base Class

`TransferObject` extends `schematics.Model` and provides:

- **`map(type, role, validate, **kwargs)`** — Serializes via `to_primitive(role)`, merges kwargs, attempts `type.new(...)` then falls back to `Aggregate.new(...)`.
- **`from_model(transfer_obj, aggregate, validate, **kwargs)`** — Creates a transfer object from an aggregate's primitive data.
- **`from_data(data, **kwargs)`** — Creates a transfer object from a raw dictionary.
- **`allow(*args)`** — Creates a whitelist transform (or wholelist if no args).
- **`deny(*args)`** — Creates a blacklist transform.

### Role-Based Serialization

Transfer objects use Schematics `Options.roles` to control which fields are serialized for different contexts:

```python
class ErrorYamlObject(Error, TransferObject):
    class Options:
        serialize_when_none = False
        roles = {
            'to_data.yaml': TransferObject.deny('id', 'error_code'),
            'to_model': TransferObject.allow(),
        }
```

### Role Naming Conventions

- **`to_data.yaml`** — Serialization for YAML persistence. Typically excludes derived or identity fields (e.g., `id`, computed codes) that are inferred from the YAML structure.
- **`to_model`** — Serialization for mapping to an Aggregate or DomainObject. May exclude nested collections that require special mapping logic (e.g., `arguments`, `dependencies`).

JSON-specific roles (`to_data.json`) have been removed. Use `to_data.yaml` for all persistence serialization.

## Structured Code Design

Mapper classes follow the standard Tiferet artifact comment structure:

- `# *** mappers` — top-level section for mapper modules.
- `# ** mapper: <name>` — individual mapper (snake_case).
- `# * attribute: <name>` — instance attributes (Schematics types).
- `# * method: <name>` — instance or static methods.

Use `# *** classes` in `settings.py` for the base classes themselves.

**Spacing rules:**
- One empty line between `# *** mappers` and first `# ** mapper`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating and Extending Mappers

### 1. Define an Aggregate
- Combine domain object + `Aggregate`.
- Add mutation methods under `# * method: <name>`.

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
        self.set_attribute('name', name)
```

### 2. Define a TransferObject
- Combine domain object + `TransferObject`.
- Define `Options.roles` for serialization.
- Use `serialized_name` and `deserialize_from` for attribute aliasing.

**Example** – `FeatureYamlObject`:
```python
# ** mapper: feature_yaml_object
class FeatureYamlObject(Feature, TransferObject):
    '''
    YAML transfer object for the Feature domain object.
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_data.yaml': TransferObject.deny('id'),
            'to_model': TransferObject.deny('steps'),
        }
```

### 3. Use in Repositories
Repositories use transfer objects to load from configuration and map to aggregates/domain objects.

### Best Practices
- Use artifact comments consistently (`# *** mappers`, `# ** mapper:`, `# *`).
- Keep aggregates focused on mutation; keep transfer objects focused on serialization.
- Use `Aggregate.new` for factory instantiation.
- Use `set_attribute` for validated mutations.
- Define `Options.roles` on all transfer objects.
- Use `allow`/`deny` for role definitions.

## Testing Mappers

Mapper tests use a shared test harness defined in `mappers/tests/settings.py` and `mappers/tests/conftest.py`. The harness provides base classes that automatically generate standard tests for Aggregate and TransferObject components, while allowing domain-specific tests to be added alongside them.

The base class tests in `test_settings.py` cover the `Aggregate` and `TransferObject` base classes themselves using standalone functions. Concrete mapper tests should use the harness-based class style described below.

### Test Harness Components

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
- `test_new` — Verifies `Aggregate.new()` instantiation and field values.
- `test_set_attribute` — Parametrized test for valid and invalid attribute mutations. Parametrization is driven by `conftest.pytest_generate_tests`.

**Override hook:**
- `make_aggregate(data=None)` — Override when the aggregate has a custom `new()` signature (e.g., `AppInterfaceAggregate.new(app_interface_data=...)` instead of `Aggregate.new(cls, **kwargs)`).

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
- `test_map` — Verifies `from_data()` → `map()` produces a valid aggregate.
- `test_from_model` — Verifies aggregate → TransferObject conversion.
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
        '''Override for custom new() signature.'''
        return SomeAggregate.new(
            some_data=(data if data is not None else self.sample_data).copy()
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
        '''Override for custom new() signature.'''
        return SomeAggregate.new(
            some_data=(data if data is not None else self.aggregate_sample_data).copy()
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
- `test_app.py`, `test_cli.py`, `test_di.py`, `test_error.py`

The following use the legacy standalone style and are candidates for migration:
- `test_container.py`, `test_feature.py`, `test_logging.py`

`test_settings.py` tests the base classes themselves and appropriately uses standalone functions.

## Package Layout

Mappers are defined in `tiferet/mappers/`:

- `settings.py` — `Aggregate` and `TransferObject` base classes + constants.
- `app.py` — `AppInterfaceAggregate`, `AppInterfaceYamlObject`, `AppServiceDependencyYamlObject`.
- `cli.py` — `CliArgumentAggregate`, `CliCommandAggregate`, `CliCommandYamlObject`.
- `container.py` — `ContainerAttributeAggregate`, `ContainerAttributeYamlObject`, `FlaggedDependencyYamlObject` (legacy).
- `di.py` — `FlaggedDependencyAggregate`, `FlaggedDependencyYamlObject`, `ServiceConfigurationAggregate`, `ServiceConfigurationYamlObject`.
- `error.py` — `ErrorAggregate`, `ErrorYamlObject`, `ErrorMessageYamlObject`.
- `feature.py` — `FeatureAggregate`, `FeatureEventAggregate`, `FeatureYamlObject`, `FeatureEventYamlObject`.
- `logging.py` — `FormatterAggregate`, `HandlerAggregate`, `LoggerAggregate`, `FormatterYamlObject`, `HandlerYamlObject`, `LoggerYamlObject`, `LoggingSettingsYamlObject`.
- `__init__.py` — Public exports.

Tests live in `tiferet/mappers/tests/`:

- `settings.py` — `MapperAssertions`, `AggregateTestBase`, `TransferObjectTestBase` harness classes.
- `conftest.py` — `pytest_generate_tests` hook for dynamic `set_attribute` parametrization.
- `test_settings.py` — Base class tests (standalone functions).
- `test_app.py`, `test_cli.py`, `test_di.py`, `test_error.py` — Harness-based concrete mapper tests.
- `test_container.py`, `test_feature.py`, `test_logging.py` — Legacy standalone concrete mapper tests.

## Migration from DataObject

The `Aggregate` and `TransferObject` classes together replace the legacy `DataObject` (`tiferet.data.settings`):

- `DataObject.map` → `TransferObject.map` (now targets `Aggregate` instead of `ModelObject`)
- `DataObject.from_model` → `TransferObject.from_model` (parameter names updated to `transfer_obj`/`aggregate`)
- `DataObject.from_data` → `TransferObject.from_data`
- `DataObject.allow` / `DataObject.deny` → `TransferObject.allow` / `TransferObject.deny`
- Mutation logic (previously inline in domain objects) → `Aggregate.set_attribute`

The `tiferet.data` package remains fully functional during the migration period. Concrete mappers will be migrated incrementally in subsequent stories.

## Conclusion

The mappers layer provides the structural bridge between persistent configuration and runtime domain objects, with clear separation between mutation (`Aggregate`) and serialization (`TransferObject`). This design enables:
- Validated, mutation-safe domain updates.
- Role-based serialization for multiple output formats.
- Incremental migration from the legacy `DataObject` pattern.

Explore source in `tiferet/mappers/` and tests in `tiferet/mappers/tests/` for implementation details.
