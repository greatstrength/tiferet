# Domain Objects in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Severity is form: the noun that will not change itself. Domain objects house data and offer read-only behavior. They do not mutate. That position is **Gevurah**. A `rename` or `set_*` on a domain object is in the wrong package. Mutation is Hod’s job, on the aggregate in `mappers`. See [architecture.md](architecture.md).

Legal `# ** app` imports: none of the framework. Used by `contexts`, `events`, and `di`. Blueprints reference domain types only through context re-exports (Da'ath). Current `tiferet/domain/` has no `from ..` imports. That is not an accident. A noun that imported a service or an event would already be doing someone else’s work.

## Life in the system

Every domain concept — errors, features, app sessions, CLI commands, logging settings — extends `DomainObject` from `tiferet.domain.core`. The class is a Pydantic v2 model with a strict config: unknown fields are forbidden, assignment re-validates, names populate either by field or by alias. You construct it directly: `Error(id='invalid_input', name='Invalid Input')`. You do not call a framework factory. Derivation that used to live on `new()` now lives on `@model_validator(mode='before')`.

The noun has a dual life, and both lives are read-only from its own point of view.

At runtime it is what an event prefers to return and what a context binds. `GetError` returns an `Error`. `ErrorContext.format_response` calls `error.format_message(lang, **exception.kwargs)` — a read, not a write. The hub loaded the noun; the context presents it.

As structure it is what Hod extends. `ErrorAggregate(Error, Aggregate)` inherits the fields and adds mutation. `ErrorConfigObject(Error, TransferObject)` inherits the fields and adds serialization roles. Configuration maps through the transfer object to the aggregate and back to the runtime noun. One shape, three lives: read, mutate, represent. Gevurah owns only the first.

That is the balance. Form without mutation keeps the ubiquitous language stable. If `Error` could rename itself, every reader of the noun would have to wonder whether they were holding a fact or a draft. The draft belongs on the aggregate.

## The DomainObject base

```python
# tiferet/domain/core.py

from pydantic import BaseModel, ConfigDict

class DomainObject(BaseModel):
    '''
    The base domain model object for Tiferet, backed by Pydantic v2.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
    )
```

What the reader just saw: `extra='forbid'` rejects surprise fields so a config typo cannot silently become state. `validate_assignment=True` is why an aggregate’s `setattr` is safe — the check is inherited, not reimplemented. Transfer objects later loosen this (`extra='ignore'`, `validate_assignment=False`) because representation must tolerate foreign shapes. The noun itself does not.

Read-only behavior is allowed. Formatting, lookup, a derived display string — these do not change the object. `Error.format_message` is Gevurah. `ErrorAggregate.rename` is Hod.

A consumer noun looks like this:

```python
# *** models

# ** model: calculator_result
class CalculatorResult(DomainObject):
    '''
    Stores calculator computation results.
    '''

    # * attribute: value
    value: float = Field(..., description='The computed result value.')

    # * attribute: operation
    operation: str = Field(..., description='The operation that produced this result.')

    # * method: format_result
    def format_result(self, precision: int = 2) -> str:
        '''
        Formats the result.
        '''
        return f'{self.operation}: {self.value:.{precision}f}'
```

`format_result` reads. If the next method were `set_value`, the class would need to move.

## Structured code design

Use `# *** models`, `# ** model: <name>` in snake_case, `# * attribute` for `Field(...)` declarations, `# * method` for read-only behavior, and `# * method: _derive_* (validator)` for `@model_validator` derivation. Spacing matches [code_style.md](code_style.md). Tests live in `tests/domain/` and cover construction, read behavior, and edge cases — not response assembly, which is a context test.

## Package layout

- `core.py` — `DomainObject`, `ServiceDependency`
- `app.py` — `AppSession`, `AppServiceDependency`
- `cli.py` — `CliCommand`, `CliArgument`
- `di.py` — `ServiceRegistration`, `FlaggedDependency`
- `error.py` — `Error`, `ErrorMessage`
- `feature.py` — `Feature`, `FeatureStep`, `EventFeatureStep`
- `logging.py` — `Formatter`, `Handler`, `Logger`, `LoggingSettings`

## In short

- Domain objects are read-only nouns. That form is Gevurah.
- No framework imports. Blueprints see these types only through context re-exports.
- Construct with the Pydantic constructor or `model_validate`. Derive with `@model_validator`, not a custom `new()`.
- Read-only behavior stays here. Mutation and representation live on mappers.
- Prefer returning this noun from an event when one exists.
