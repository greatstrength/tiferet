# Mappers in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Mappers are a core component of the Tiferet framework, encapsulating data mappings between Domain Objects and persisted or response data. The mappers layer splits the responsibilities of the legacy `DataObject` into two distinct classes:

1. **Aggregate** — a mutable data representation that extends domain objects with mutation logic (e.g., `set_attribute`, `rename`, `add_command`). Aggregates are used by repositories and commands to modify and persist domain state.

2. **TransferObject** — a serialization and mapping layer that transforms configuration data (e.g., YAML, JSON) into Aggregates or Domain Objects, and vice versa. TransferObjects handle role-based serialization (`to_data`, `to_model`), field whitelisting/blacklisting, and round-trip mapping.

Both classes extend `schematics.Model` and are defined in `tiferet/mappers/settings.py`.

### Role in Runtime

- **Aggregates** are used by repositories and commands to perform mutations on domain data. They bridge the gap between read-only domain objects and the mutable operations needed for persistence.
- **TransferObjects** are used by repositories to map configuration data (e.g., `error.yml`, `feature.yml`) into Aggregates or Domain Objects, and to serialize Aggregates back to configuration format.
- Together, they enable reliable round-trip mapping between persistent configuration and runtime domain models.

### Example: Error Domain

- **Aggregate** (`ErrorAggregate`):
  ```python
  class ErrorAggregate(Error, Aggregate):
      # Inherits fields/validation from Error domain object
      # Adds mutation methods (rename, set_message, remove_message)
  ```

- **TransferObject** (`ErrorYamlObject`):
  ```python
  class ErrorYamlObject(Error, TransferObject):
      # Inherits fields/validation from Error domain object
      # Adds serialization roles and mapping logic

      class Options:
          serialize_when_none = False
          roles = {
              'to_data': TransferObject.deny('id', 'error_code'),
              'to_model': TransferObject.allow()
          }
  ```

  Configuration (`error.yml`) maps through `ErrorYamlObject` to `ErrorAggregate`, which converts to/from the runtime `Error` domain object.

## The Aggregate Base Class

`Aggregate` extends `schematics.Model` and provides:

- **`Aggregate.new(aggregate_type, validate=True, strict=True, **kwargs)`** — static factory that instantiates, optionally validates, and returns an aggregate.
- **`set_attribute(attribute, value)`** — safely updates an attribute, raising `INVALID_MODEL_ATTRIBUTE` via `RaiseError` if the attribute does not exist, and re-validates after mutation.

```python
# tiferet/mappers/settings.py

class Aggregate(Model):
    '''
    A data representation of an aggregate object.
    '''

    # * method: new
    @staticmethod
    def new(aggregate_type, validate=True, strict=True, **kwargs):
        aggregate_object = aggregate_type(dict(**kwargs), strict=strict)
        if validate:
            aggregate_object.validate()
        return aggregate_object

    # * method: set_attribute
    def set_attribute(self, attribute, value):
        if not hasattr(self, attribute):
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                attribute=attribute,
            )
        setattr(self, attribute, value)
        self.validate()
```

## The TransferObject Base Class

`TransferObject` extends `schematics.Model` and provides methods for data transformation:

- **`map(type, role='to_model', validate=True, **kwargs)`** — serializes the TransferObject via `to_primitive(role)`, merges with kwargs, and maps to an Aggregate or Domain Object. Tries a custom `new()` factory first, falling back to `Aggregate.new()`.
- **`from_model(transfer_obj, aggregate, validate=True, **kwargs)`** — creates a TransferObject from an Aggregate's primitive data, with kwargs taking priority.
- **`from_data(data, **kwargs)`** — creates a TransferObject directly from a dictionary.
- **`allow(*args)`** — creates a whitelist (or wholelist if no args) transform for role-based serialization.
- **`deny(*args)`** — creates a blacklist transform for role-based serialization.

## Structured Code Design

Mappers follow the same artifact comment structure as other Tiferet components:

- `# *** mappers` — top-level section.
- `# ** mapper: <name>` — individual mapper (snake_case).
- `# * attribute: <name>` — instance attributes (Schematics types).
- `# * method: <name>` — methods.

**Spacing rules:**
- One empty line between `# *** mappers` and first `# ** mapper`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating and Extending Mappers

### 1. Define an Aggregate

- Extend both the Domain Object and `Aggregate`.
- Add mutation methods under `# * method`.
- Use `set_attribute` for safe, validated updates.

**Example** — `CalculatorResultAggregate`:
```python
# *** imports

# ** app
from tiferet.domain.calculator import CalculatorResult
from tiferet.mappers.settings import Aggregate

# *** mappers

# ** mapper: calculator_result_aggregate
class CalculatorResultAggregate(CalculatorResult, Aggregate):
    '''
    Mutable aggregate for calculator results.
    '''

    # * method: update_value
    def update_value(self, new_value: float) -> None:
        '''
        Updates the result value.
        '''
        self.set_attribute('value', new_value)
```

### 2. Define a TransferObject

- Extend both the Domain Object and `TransferObject`.
- Define an `Options` inner class with `serialize_when_none` and `roles`.
- Use `allow()` and `deny()` for role-based field control.
- Override `map()` or `to_primitive()` for custom mapping logic.

**Example** — `CalculatorResultYamlObject`:
```python
# *** imports

# ** app
from tiferet.domain.calculator import CalculatorResult
from tiferet.mappers.settings import TransferObject

# *** mappers

# ** mapper: calculator_result_yaml_object
class CalculatorResultYamlObject(CalculatorResult, TransferObject):
    '''
    YAML serialization for calculator results.
    '''

    class Options:
        '''
        Options for the transfer object.
        '''

        serialize_when_none = False
        roles = {
            'to_data': TransferObject.deny('id'),
            'to_model': TransferObject.allow('value', 'operation')
        }

    # * method: map
    def map(self, **kwargs) -> CalculatorResult:
        '''
        Maps the YAML data to a calculator result.
        '''
        return super().map(type=CalculatorResultAggregate, role='to_model')
```

### 3. Attribute Aliasing

TransferObjects support `serialized_name` and `deserialize_from` for attribute aliasing, which is not permitted in Domain Objects. This enables flexible mapping between external data formats and internal field names:

```python
# * attribute: arguments
arguments = ListType(
    ModelType(CliArgument),
    serialized_name='args',
    deserialize_from=['args', 'arguments'],
    default=[],
)
```

### Best Practices

- Use artifact comments (`# * attribute`, `# * method`) consistently.
- Define attributes with Schematics types and metadata.
- Use `allow()` and `deny()` in `Options.roles` for field control.
- Override `map()` or `to_primitive()` for custom transformations.
- Keep mutation logic in Aggregates, serialization logic in TransferObjects.
- Domain Objects remain read-only; all mutation goes through Aggregates.

## Testing Mappers

Tests validate instantiation, mapping, mutation, and serialization using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Invocation**: Use `Aggregate.new()` and `TransferObject.from_data()` / `TransferObject.from_model()` in tests.

**Example** — Aggregate tests:
```python
def test_aggregate_new(test_aggregate):
    aggregate = Aggregate.new(
        test_aggregate,
        id='test_id',
        name='Test Aggregate'
    )
    assert isinstance(aggregate, test_aggregate)
    assert aggregate.id == 'test_id'

def test_aggregate_set_attribute_invalid(test_aggregate):
    aggregate = Aggregate.new(test_aggregate, id='test_id', name='Test')
    with pytest.raises(TiferetError) as exc_info:
        aggregate.set_attribute('invalid_attribute', 'value')
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'
```

**Example** — TransferObject tests:
```python
def test_data_object_from_data(test_data_object):
    data_object = TransferObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Data'}
```

### Best Practices

- Mock Domain Objects when testing `from_model`.
- Test `Aggregate.new` with validation on/off and strict/non-strict modes.
- Test `set_attribute` for both valid and invalid attributes.
- Verify role-based serialization with `allow` and `deny`.

## Migration from DataObject

In v2.0, the single `DataObject` class (`tiferet/data/settings.py`) was split into two classes:

- **`Aggregate`** — carries the `new()` factory from `DataObject` plus the new `set_attribute()` mutation method. Domain-specific aggregates add further mutation methods (e.g., `rename`, `add_command`).
- **`TransferObject`** — carries the `map()`, `from_model()`, `from_data()`, `allow()`, and `deny()` methods from `DataObject`.

The `DataObject` class remains available in `tiferet/data/settings.py` for backward compatibility. New code should use `Aggregate` and `TransferObject` from `tiferet/mappers/settings.py`.

## Package Layout

Mappers are defined in `tiferet/mappers/`:

- `settings.py` — `Aggregate` and `TransferObject` base classes.
- `app.py` — `AppInterfaceAggregate`, `AppInterfaceYamlObject`.
- `cli.py` — `CliCommandAggregate`, `CliCommandYamlObject`.
- `container.py` — `ContainerAttributeAggregate`, `ContainerAttributeYamlObject`, etc.
- `error.py` — `ErrorAggregate`, `ErrorYamlObject`, `ErrorMessageYamlObject`.
- `feature.py` — `FeatureAggregate`, `FeatureYamlObject`, etc.
- `logging.py` — `FormatterAggregate`, `HandlerAggregate`, `LoggerAggregate`, etc.
- `__init__.py` — Public exports for all mapper classes.

Tests live in `tiferet/mappers/tests/`.

## Conclusion

Mappers provide the **data transformation layer** for the Tiferet framework, cleanly separating mutation (Aggregates) from serialization (TransferObjects). This split enables:
- Safe, validated mutations on domain data.
- Flexible, role-based serialization for persistence and response formatting.
- Reliable round-trip mapping between configuration files and runtime domain objects.
- A clear boundary between read-only domain objects and mutable data representations.

Explore source in `tiferet/mappers/` and tests in `tiferet/mappers/tests/` for implementation details.
