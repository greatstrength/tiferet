# Domain Objects in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

> Severity does not condemn or punish but is rather the indispensable defender of justice.

Severity is form: the noun that will not change itself. Domain objects house data and offer read-only behavior. They do not mutate. That position is **Gevurah**. A `rename` or `set_*` on a domain object is in the wrong package. Mutation is Hod’s job, on the aggregate in `mappers`. See [architecture.md](architecture.md).

Legal `# ** app` imports: none of the framework. Used by `contexts`, `events`, and `di`. Blueprints reference domain types only through context re-exports (Da'ath). Current `tiferet/domain/` has no `from ..` imports. That is not an accident. A noun that imported a service or an event would already be doing someone else’s work.

## Mechanical correctness is not semantic correctness

This is what makes the position load-bearing rather than merely strict, so it comes first.

Infrastructure can only ever verify **shape**. The resolution tier matches a service by name and by flag and forms no opinion about whether the thing it handed back means anything. A loader round-trips a structure and cannot tell a corrupted domain from a clean one. Every position below the veil is in the same condition, by design — that indifference is exactly what makes those tiers reusable.

Which leaves exactly one position answerable for **meaning**, and it is this one. Gevurah is required to be right in both registers at once and is forbidden to trade either for the other. A model can be perfectly valid and still wrong about the world; nothing else in the framework is in a position to notice.

The claim is structural rather than asserted, and the fingerprint is checkable: **`domain` and `assets` are the only two packages in the framework with zero outbound framework imports.** Both are pure sources. There is nothing here to defer to and nothing here to blame. That also makes the independence literal rather than aspirational — a tier that imports nothing survives the framework that runs it, which is precisely what lets the model be the thing every other layer is written *against*.

The distinction generalizes well past this package and belongs in the reader's hands early: `di` staying event-free, `contexts` declining to construct their own handlers, and a name failing to survive a context boundary are all the same fact wearing different clothes.

## Life in the system

Every domain concept — errors, features, app sessions, CLI commands, logging settings — extends `DomainObject` from `tiferet.domain.core`. The class is a Pydantic v2 model with a strict config: unknown fields are forbidden, assignment re-validates, names populate either by field or by alias. You construct it directly: `Error(id='invalid_input', name='Invalid Input')`. You do not call a framework factory. Derivation that used to live on `new()` now lives on `@model_validator(mode='before')`.

The noun has a dual life, and both lives are read-only from its own point of view.

At runtime it is what an event prefers to return and what a context binds. `GetError` returns an `Error`. `ErrorContext.format_response` calls `error.format_message(lang, **exception.kwargs)` — a read, not a write. The hub loaded the noun; the context presents it.

As structure it is what Hod extends. `ErrorAggregate(Error, Aggregate)` inherits the fields and adds mutation. `ErrorConfigObject(Error, TransferObject)` inherits the fields and adds serialization roles. Configuration maps through the transfer object to the aggregate and back to the runtime noun. One shape, three lives: read, mutate, represent. Gevurah owns only the first.

That is the balance. Form without mutation keeps the ubiquitous language stable. If `Error` could rename itself, every reader of the noun would have to wonder whether they were holding a fact or a draft. The draft belongs on the aggregate.

### Power is refusal

The position contributes by what it will not allow. That is its mode of action, not a limitation on it — and reading it as a limitation is how strictness starts to feel like bureaucracy instead of load-bearing structure.

Read-only is the operative rule. A noun that grows a `set_*` has defected to Hod, and the fix is a move rather than an argument.

### Validation is a guarantee, not a gate

The constraint does not exist to reject input for its own sake. It exists so that everything downstream can trust what it receives **without re-checking it**. That is the whole return on strictness, and it is what makes an event's declared return type worth anything at all: when `GetError` says it returns an `Error`, no caller has to defensively re-validate.

### Honest ontology

Measure limits, accept restriction, refuse unnecessary accumulation. Concretely: **a model that claims more than it enforces is worse than a narrow one**, because it advertises guarantees that nothing keeps.

The characteristic failure is optional-everything — a model where every field is nullable, which is a model that has declined to say anything. Speculative fields are the same failure in slower motion: each one becomes an obligation no code honors, and readers cannot tell the load-bearing fields from the aspirational ones.

### Where semantic friction becomes visible

Two contexts joined by a decision neither of them made will end up sharing nouns whose meanings differ. Two types can be mechanically identical and semantically incompatible — same fields, same types, different referents.

Strict form does not *create* that conflict. The conflict is prior and genuinely semantic. What strictness does is make it undeniable at the boundary, instead of letting it surface three layers later as corrupted data. And the mismatch is the earned consequence of two models evolving independently and correctly, not evidence that someone was careless.

The translation labor belongs elsewhere — at Hod, where a transfer object fits a noun to a foreign shape, and at Malkuth, where it lands. Gevurah's whole contribution is declining to blur. See [mappers.md](mappers.md).

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
- Infrastructure verifies shape; this is the one position answerable for meaning, and it may not trade either register for the other.
- Zero outbound framework imports — shared only with `assets`. A tier that imports nothing survives the framework that runs it.
- Power is refusal. The position acts by what it declines to allow; a noun that grows a `set_*` has defected to Hod.
- Validation is a guarantee, not a gate. It exists so downstream code never re-checks, which is what makes a declared return type worth anything.
- Honest ontology: a model claiming more than it enforces is worse than a narrow one. Optional-everything is the characteristic failure.
- Strict form does not create semantic friction; it makes it undeniable at the boundary. Translation is Hod's and Malkuth's work.
- No framework imports. Blueprints see these types only through context re-exports.
- Construct with the Pydantic constructor or `model_validate`. Derive with `@model_validator`, not a custom `new()`.
- Read-only behavior stays here. Mutation and representation live on mappers.
- Prefer returning this noun from an event when one exists.
