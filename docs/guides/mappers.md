# Mappers – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/mappers/`  
**Version:** 2.0.0

## Overview

The mappers layer bridges persistent configuration (YAML, JSON) and runtime domain objects. Every mapper module pairs two complementary classes: an **Aggregate** (mutation logic) and a **TransferObject**, precision-suffixed `ConfigObject` when the backing medium is a config file (serialization roles and configuration mapping). This guide covers the cross-cutting strategies and design decisions that apply to all mapper modules, rather than any single domain. **Vision:** see the `Aggregate` and `TransferObject` class docstrings in `tiferet/mappers/core.py` for the value statements this guide distills.

## Ubiquitous Language

- **Aggregate** — a mutable extension of a domain object (`extra='forbid'`, `validate_assignment=True`, inherited from `DomainObject`); mutation goes through dedicated methods or the base `set_attribute`, which converts a Pydantic `ValidationError` into a `ModelError`.
- **ConfigObject** — the framework's own `TransferObject` specialization for YAML/JSON-backed configuration (lenient `extra='ignore'`, `validate_assignment=False`); other backing media would earn their own suffix (e.g. a hypothetical `SqliteObject`).
- **`_ROLES`** — a `ClassVar[Dict[str, Dict[str, Any]]]` on a `TransferObject` mapping role names to `model_dump` kwargs; `to_model` and `to_data` are the two standard roles every `ConfigObject` declares.
- **The map/exclude handshake** — the rule that whatever a `_ROLES['to_model']` entry excludes, the class's own `map()` override must supply explicitly (see below).

<a id="aggregate"></a>
## When to Create an Aggregate

An aggregate is warranted when the domain object needs **mutation methods** beyond simple attribute assignment — methods that enforce invariants, compose nested objects, or coordinate multi-field updates.

If a domain object is only ever used as a **nested sub-object** inside a parent aggregate, and its fields map 1:1 with no special mutation logic, skip the aggregate. The parent aggregate owns the mutation responsibility, and the raw domain object is used directly.

### Examples

| Domain Object | Has Aggregate? | Reason |
|---|---|---|
| `AppSession` | Yes (`AppSessionAggregate`) | Multi-field mutations (`add_service`/`set_service`/`remove_service`, `set_constants`, gated `set_attribute`) |
| `AppServiceDependency` | No | 1:1 field mapping; parent manages mutations |
| `Feature` | Yes (`FeatureAggregate`) | Step insertion/removal/reordering (`add_step`, `remove_step`, `reorder_step`), metadata mutation |
| `EventFeatureStep` | Yes (`EventFeatureStepAggregate`) | Specialized setters for `pass_on_error` and parameter merge-and-prune |
| `Error` | Yes (`ErrorAggregate`) | Message list management (`set_message`, `remove_message`) |
| `ErrorMessage` | No | 1:1 mapping; parent manages the list |
| `CliArgument` | Yes (`CliArgumentAggregate`) | Gated `set_attribute` for mutable fields; serves as the return type for `CliService.get_parent_arguments()` |
| `FlaggedDependency` | Yes (`FlaggedDependencyAggregate`) | Parameter merge-and-prune logic |
| `ServiceRegistration` | Yes (`ServiceRegistrationAggregate`) | Default-type and flagged-dependency mutation (`set_default_type`, `set_dependency`, `remove_dependency`) |
| `Formatter`, `Handler`, `Logger` | Yes (thin, no added methods) | Exist purely so `LoggingService` has a uniform mutable return type per domain, even without dedicated mutation logic yet |

**Rule of thumb:** if you only need `SubType(...)` to create it and nothing else, you don't need an aggregate for it.

## Instantiation Pattern

Aggregates are instantiated directly via the Pydantic constructor. There are two common patterns:

### Direct construction
Used when the domain object's fields are sufficient as-is:

```python
aggregate = ErrorAggregate(id='invalid_input', name='Invalid Input', message=[...])
```

### Derivation via `@model_validator`
Used when the aggregate needs to normalize inputs, compute IDs, or provide defaults. A `@model_validator(mode='before')` on the domain object handles derivation automatically:

```python
# FeatureAggregate inherits the @model_validator from Feature,
# which derives group_id and feature_key from id if provided.
aggregate = FeatureAggregate(id='calc.add', name='Add Number')
# aggregate.group_id == 'calc'
# aggregate.feature_key == 'add'
```

### Dict-wrapper construction
Used when the caller already has a dict (e.g., from YAML loading):

```python
aggregate = AppSessionAggregate(**app_session_data)
```

Choose the pattern that fits the domain. Derivation via `@model_validator` is useful when an ID is composed from multiple parts; dict-wrapper construction is useful when the aggregate is populated from configuration data.

## Nested Sub-Objects Without Aggregates

When a domain object has no aggregate, the parent aggregate creates instances directly via the Pydantic constructor and mutates them via list reassignment (so `validate_assignment=True` fires). The parent transfer object handles all structural transformation.

### Creation in the parent aggregate

```python
# AppSessionAggregate.add_service
dependency = AppServiceDependency(
    service_id=service_id,
    module_path=module_path,
    class_name=class_name,
    parameters=parameters or {},
)
self.services = list(self.services) + [dependency]
```

### Transformation in the parent transfer object

The transfer object is responsible for any structural differences between the configuration format and the domain model. The most common pattern is **dict↔list conversion**, where YAML stores sub-objects as a dictionary keyed by an identifier, but the domain model stores them as a list with that identifier as a field.

```python
# AppSessionConfigObject.map — dict keys become service_id fields
services=[dep.map(service_id=dep_id) for dep_id, dep in (self.services or {}).items()]

# AppSessionConfigObject.from_model — list items become dict entries
services={
    dep.service_id: AppServiceDependencyConfigObject.from_model(dep)
    for dep in app_session.services
}
```

This pattern appears in every domain that nests sub-objects: services in app sessions, dependencies in service registrations, messages in errors, steps in features.

<a id="transferobject"></a>
## Transfer Object Role Strategy

Transfer objects use a `_ROLES` ClassVar to control which fields appear in different serialization contexts. Each role maps to a dict of `model_dump` kwargs. Tiferet defines three standard roles:

| Role | Purpose |
|---|---|
| `to_model` | Fields included when mapping to an aggregate or domain object |
| `to_data` | Fields included when serializing to configuration files |

### Exclude vs Include

- **`exclude`** (blacklist) is the default strategy. Start with all fields and exclude the ones that don't belong in the role.
- **`include`** (whitelist) is used when the domain object is simple enough that listing included fields is clearer.

### Common exclude patterns

**Exclude the ID on data roles.** The ID is typically derived from the YAML dictionary key, not stored as a field in the YAML value:

```python
_ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
    'to_data': {'by_alias': True, 'exclude': {'id'}},
    'to_data': {'exclude': {'id'}},
}
```

**Exclude nested collections on `to_model`.** Nested sub-objects need custom mapping (e.g., dict→list conversion), so they are excluded from the dump and composed manually in `map()`:

```python
_ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
    'to_model': {'exclude': {'services', 'constants', 'module_path', 'class_name'}},
}
```

The fields excluded from `to_model` are then passed explicitly in `map()` with the correct transformation applied.

### The map/exclude handshake

The `map()` method and `to_model` role work together. Whatever `to_model` excludes, `map()` must supply:

```python
def map(self, **overrides) -> ErrorAggregate:
    return super().map(
        ErrorAggregate,
        message=[msg.map() for msg in self.message],   # excluded from to_model
        **overrides
    )
```

This pattern ensures the transfer object's role controls what gets auto-serialized, while `map()` handles custom transformations for the excluded fields.

## Attribute Aliasing

Transfer objects support `serialization_alias` and `validation_alias=AliasChoices(...)` for mapping between YAML/JSON field names and domain attribute names. Domain objects must **not** use aliasing — only transfer objects.

Common aliases:

| Domain field | YAML alias (`serialization_alias`) | `validation_alias` (AliasChoices) |
|---|---|---|
| `parameters` | `params` | `AliasChoices('params', 'parameters')` |
| `module_path` | `module` | `AliasChoices('module_path', 'module')` |
| `class_name` | `class` | `AliasChoices('class_name', 'class')` |
| `services` | `attrs` | `AliasChoices('attrs', 'services', 'dependencies', 'attributes')` |
| `dependencies` | `deps` | `AliasChoices('deps', 'dependencies', 'flags')` |
| `steps` | `commands` | `AliasChoices('handlers', 'functions', 'commands', 'steps')` |

Wide `AliasChoices` lists accept multiple YAML field names for the same attribute. The `serialization_alias` controls the canonical output key.

## Gated `set_attribute` Pattern

Some aggregates override `set_attribute` with a gated version that restricts which attributes can be updated. This prevents accidental mutation of identity fields or fields that have dedicated mutation methods.

```python
def set_attribute(self, attribute: str, value: Any) -> None:
    supported = {'name', 'description', 'logger_id', 'flags'}
    if attribute not in supported:
        supported_names = ', '.join(sorted(supported))
        ModelError.raise_error(
            ATTRIBUTE_NOT_SETTABLE_ID,
            message=f'Invalid attribute: {attribute}. Supported attributes are {supported_names}.',
            model=self,
            attribute=attribute,
            supported=supported_names,
        )
    setattr(self, attribute, value)
```

The gate raises `ATTRIBUTE_NOT_SETTABLE_ID`, not `INVALID_MODEL_ATTRIBUTE_ID`: the field usually **does** exist on the model, so the refusal expresses mutation policy rather than a model inconsistency. The whitelist is deliberately narrower than `model_fields`, which is why Pydantic cannot subsume the check. Passing `model=self` describes the refusing aggregate onto the error, so the leaked defect identifies the instance as well as the attribute.

**When to gate:** when the aggregate has fields that should only change through dedicated methods (e.g., `services` via `add_service`/`remove_service`, `constants` via `set_constants`).

**When to use the base `set_attribute`:** when any field on the model is fair game for direct update, or the aggregate is simple enough that gating adds no value.

## Parameter Merge-and-Prune Pattern

Several aggregates manage `parameters` dictionaries with merge semantics: new values override existing ones, and keys set to `None` are removed. This pattern appears in `set_constants`, `set_service`, `set_parameters`, and `set_default_type`.

```python
def set_constants(self, constants: Dict[str, Any] | None = None) -> None:
    if constants is None:
        self.constants = {}
    else:
        self.constants.update(constants)
        self.constants = {k: v for k, v in self.constants.items() if v is not None}
```

The convention is:
- `None` argument → clear all.
- Dict argument → merge, then prune `None`-valued keys.

## Round-Trip Mapping

Every transfer object pair (`map` + `from_model`) should support lossless round-trip conversion:

```
Aggregate → from_model → ConfigObject → map → Aggregate
```

Tests validate this by asserting field equality after a round trip:

```python
def test_round_trip(aggregate):
    yaml_obj = ConfigObject.from_model(aggregate)
    round_tripped = yaml_obj.map()
    assert round_tripped.id == aggregate.id
    assert round_tripped.name == aggregate.name
    # ...
```

When the transfer object performs structural transformations (dict↔list), both `map` and `from_model` must apply the inverse transformation so the round trip is complete.

## Composite Transfer Objects

Some transfer objects don't extend a domain object — they compose multiple domain objects into a single configuration structure. `LoggingSettingsConfigObject` (`mappers/logging.py`) is the canonical example: it extends `TransferObject` directly and holds dicts of `FormatterConfigObject`, `HandlerConfigObject`, and `LoggerConfigObject`, representing the entire `logging` configuration section.

These composite transfer objects use a `from_data` classmethod that threads each section's dict key onto the contained config objects as `id` before validating:

```python
@classmethod
def from_data(cls, **data) -> 'LoggingSettingsConfigObject':
    return cls.model_validate({
        'formatters': {
            key: {**(formatter_data or {}), 'id': key}
            for key, formatter_data in data.get('formatters', {}).items()
        },
        # 'handlers' and 'loggers' follow the same shape
    })
```

Use this pattern when a config file section contains multiple related sub-sections keyed by id that are loaded together.

## Aliasing Beyond the Field Level

Most transfer objects only need `serialization_alias`/`validation_alias` per field (see Attribute Aliasing above). `CliCommandConfigObject.arguments` is a representative example: `validation_alias=AliasChoices('args', 'arguments')` accepts either input key, and `serialization_alias='args'` controls the canonical output key — no `to_primitive` override is needed for this case, since the alias mechanism alone is sufficient.

## Boundaries

**Inside this domain:** the Aggregate/TransferObject split, role-based serialization (`_ROLES`, `to_primitive`/`to_dict`), the `map`/`from_model` round trip, and the dict↔list nested-object transformation pattern.
**Outside this domain:** the declared domain object shapes mappers extend (`docs/guides/domain/*.md`); persisting a `ConfigObject` to disk (`ConfigurationRepository` — [docs/guides/repos.md](repos.md)); the model-defect vocabulary (`ModelError`, raised by `set_attribute`/`raise_for_validation` — [docs/guides/errors.md](errors.md)).

## Related Documentation

- [docs/core/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md) — Aggregate and TransferObject base class reference
- [docs/guides/repos.md](repos.md) — `ConfigurationRepository`, which persists `ConfigObject` instances
- [docs/guides/errors.md](errors.md) — `ModelError`, raised by aggregate mutation failures
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
