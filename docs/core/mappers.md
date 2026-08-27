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

## Derivation is by extension, never duplication

This is the position's rejection criterion, and it is what separates the pattern here from the data-transfer object it superficially resembles.

An aggregate or a transfer object **is the domain type itself**, with mutation or representation added. Same substance. It is not a parallel class holding copied fields. `ErrorAggregate(Error, Aggregate)` inherits `Error`; it does not restate it.

Which is why the single legal import is mandatory rather than conventional. A duplicated structure sitting alongside the model is a *different substance*, and different substances drift — not as a risk but as a matter of course, the first time someone adds a field to one and not the other. Read a proposed mapper the way `interfaces.md` reads a proposed contract: if it restates the noun instead of extending it, reject it.

## Relevance comes from purpose, not from data

The noun holds no opinion about which of its parts matter. `Error` does not know that a config file wants its `name` and not its `id`, because nothing about being an error implies that.

So relevance has to be supplied from **outside**, by whatever the representation is for. That is precisely why `_ROLES` is declared rather than computed — there is nothing to compute it from. And it is the same reason the visitor reverse shape is safe: even when a util visits at runtime, the mapper is not deciding anything. It is applying a decision handed to it.

**One noun, many fitted forms.** Cardinality fans out here and nowhere else in quite this way: one domain type, usually one aggregate, and as many transfer forms as there are targets, none of them privileged over the others. Each preserves the original while adapting its presentation, which makes this staged lowering rather than conversion — the noun survives every stage intact.

The last stage is not this position's, though. Intermediate lowerings hand one representation to another *inside* the system's own vocabulary; the final crossing onto a substrate the system no longer controls belongs to Yesod. Hod declares the forms; Yesod performs the crossing. See [utils.md](utils.md).

### Chain of command on a boundary

A useful way to hold the three classes: models are the generals, aggregates the captains, transfer objects the troops.

The general never goes to the front. A domain object must never cross a boundary directly — which is exactly the Malkuth rule that `repos` may not import `domain` and must go through a mapper. Keep the framing, because it makes that rule **derivable** rather than memorized, and because the cardinality above follows the same shape: few generals, more captains, many troops.

### Commitment does not extend to this position

The question is a fair one, and worth answering rather than waving off: a transfer object does look like a promise to whichever technology it serves. Doesn't that make this a commitment tier too?

No — the obligation runs the wrong way, and the code states the difference outright.

Netzach **binds**: an ABC directs its implementors and its callers, is shaped by neither, and breaking it breaks a promise. Hod **conforms**: a mapper is derived from a noun it did not choose, fitted to a purpose supplied from outside, and binds nobody. Delete a transfer object and a representation path is lost — not a promise.

The configurations are the evidence. `DomainObject`, and therefore `Aggregate`, carries `extra='forbid'` with `validate_assignment=True`. `TransferObject` deliberately relaxes to `extra='ignore'` with `validate_assignment=False`, so unrecognized fields from a foreign source are dropped rather than rejected. **A tier whose defining configuration is *ignore what you do not recognize* is a tolerance surface, not a commitment surface.**

Note also that the relaxation splits the position: the mutation half is strict and the representation half is lenient, so no single layer name covers Hod uniformly anyway.

What the Commitment intuition is actually pointing at is **Published Language**. The `_ROLES` declaration *is* a published representation that external consumers depend on, which is a commitment in the ordinary sense — and it has its own Evans pattern, so prefer the specific name. This position is not short of anchors: Anticorruption Layer, Conformist, Published Language all land here. Reaching for Commitment would blur the one distinction that makes the Netzach chapter work.

So record the asymmetry instead, since it is the real finding: **Netzach promises inward and binds its implementors; Hod conforms outward and binds nothing.**

### Where anticorruption translation lands

The `TransferObject` description above says a noun may be represented for a foreign format "without breaking the model." That is Evans' anticorruption claim, arrived at from the inside.

When the foreign format is a *file* or a *database*, this is ordinary representation. When the foreign format is **another bounded context**, the same artifact is the translation site of an Anticorruption Layer — same mechanism, higher stakes, because what is being kept out is foreign *meaning* rather than a foreign shape. The full pattern decomposes across four positions, and this is the one that does the translating. See [architecture.md](architecture.md).

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
- Derivation is by extension, never duplication. A mapper *is* the noun with a trade added; a parallel class holding copied fields is a different substance and will drift.
- Relevance is supplied from outside by the purpose, which is why roles are declared rather than computed.
- One noun, many fitted forms, none privileged. Staged lowering, not conversion — and the final crossing onto a substrate belongs to Yesod.
- The general never goes to the front. That is why `repos` reaches `domain` only through a mapper, and the rule is derivable rather than memorized.
- Netzach promises inward and binds its implementors; Hod conforms outward and binds nothing. `extra='ignore'` is a tolerance surface, not a commitment surface.
- The promise intuition about `_ROLES` is real, and its name is Published Language.
- When the foreign format is another bounded context rather than a file, this is where an Anticorruption Layer does its translating.
- Import `domain` only. Never import `utils`; accept a `Callable` visitor instead.
- Aggregates mutate and raise `ModelError`. Transfer objects serialize by role.
- Used by events, interfaces, utils, and repos. Not by contexts or blueprints.
- If the method is a read on the noun, it still belongs on the domain object.
