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
            'to_data': TransferObject.allow('id', 'name', 'message'),
            'to_model': TransferObject.allow('id', 'name', 'message'),
        }
```

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
            'to_data': TransferObject.allow('id', 'name', 'description'),
            'to_model': TransferObject.allow('id', 'name', 'description'),
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

Tests validate factory creation, mutation, mapping, serialization, and error handling using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Example** – Aggregate tests cover `new` (with/without validation, strict/non-strict), `set_attribute` (success and invalid attribute error).

**Example** – TransferObject tests cover `from_data`, `from_model` (with/without kwargs), `map` (custom new and fallback), `allow`/`deny` transforms.

## Package Layout

Mappers are defined in `tiferet/mappers/`:

- `settings.py` — `Aggregate` and `TransferObject` base classes + constants.
- `__init__.py` — Public exports.

Tests live in `tiferet/mappers/tests/`.

Concrete mappers (e.g., `error.py`, `feature.py`) will be added in future stories as they are migrated from `tiferet.data`.

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
