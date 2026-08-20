# Mappers in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Splendor is form-giving: the same noun, given a body that can change or a face that can cross a boundary. A mapper extends a domain type and adds either mutation or representation. That position is **Hod**. Gevurah names the fact. Hod lets the fact be edited inside the system, or shown to a file, a database, or a response, without the noun learning either trade. See [architecture.md](architecture.md).

Legal `# ** app` imports: `domain` only. Used by `events`, `interfaces`, `utils`, and `repos`. A mapper method may accept a `Callable` and receive a util function at runtime. Mappers do not import `utils`. That visitor is reverse shape (3), not a general exemption.

## Life in the system

Two classes share the package, and they must not be collapsed.

**Aggregate** is internal state. `ErrorAggregate(Error, Aggregate)` inherits the fields and adds `rename`, `set_message`, `set_attribute`. Assignment re-validates because `validate_assignment=True` is inherited from `DomainObject`. A failed mutation becomes a `ModelError` (`INVALID_MODEL_ATTRIBUTE_ID` or `INVALID_MODEL_VALUE_ID`), not a `TiferetError`. Model errors are deliberately uncatalogued. They are form failing to hold, not a named domain outcome.

**TransferObject** is cross-platform state. `ErrorConfigObject(Error, TransferObject)` loosens the config (`extra='ignore'`, `validate_assignment=False`) so a foreign document can be read without pretending it was born as a noun. `_ROLES` maps role names to `model_dump` kwargs. `to_model` feeds an aggregate. `to_data` feeds a file. `map` and `from_model` are the round trip.

An event that needs to change an error constructs an aggregate, mutates, and saves through a service. A repo that needs to persist one maps through the transfer object and never lets the loader leak upward. Interfaces type their outputs as aggregates when an aggregate exists, because the implementor will be a repo that returns mutable form, not a frozen noun.

Hod does not import Yesod. If a mapper needs a computational visitor — a normalizer, a hash, a render function — the method takes a `Callable`. The util arrives at runtime. Importing `YamlLoader` into `mappers/` would turn form-giving into foundation.

## The two bases

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

What the reader just saw: mutation is a checked assignment, not a free `setattr` on a dict. Unknown fields and bad values fail as `ModelError`. Construct aggregates directly: `ErrorAggregate(id='...', name='...')`. There is no `Aggregate.new()`.

A transfer object declares how the same fields look in another medium:

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

`to_primitive(role)` merges `exclude_none=True` with the role and any caller overrides, then `model_dump`s. Nested children (`FeatureConfigObject.steps`) map themselves before the parent `map`s. Aliases (`serialization_alias`, `AliasChoices`) absorb the several names a config file has used for the same field. The noun never learns those names.

Naming: `<Domain>Aggregate`; `<Domain>TransferObject` when the medium is general; a precision suffix when it is not (`ErrorConfigObject`, `FormulaSqliteObject`). `ConfigObject` is the framework’s own example of the pattern, not the only transfer object.

## Structured code design

Use `# *** mappers` / `# ** mapper:` (and `# *** classes` in `core.py`). Tests use `AggregateTestBase` and `TransferObjectTestBase` from `tiferet/testing/`. Full grammar: [code_style.md](code_style.md). Role-by-role walkthroughs live in [docs/guides/mappers.md](../guides/mappers.md).

## In short

- Mappers give form: mutate inside, represent across a boundary. That splendor is Hod.
- Import `domain` only. Never import `utils`; accept a `Callable` visitor instead.
- Aggregates mutate and raise `ModelError`. Transfer objects serialize by role.
- Used by events, interfaces, utils, and repos. Not by contexts or blueprints.
- If the method is a read on the noun, it still belongs on the domain object.
