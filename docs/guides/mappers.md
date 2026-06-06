# Mappers – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/mappers/`  
**Version:** 2.0.0

## Overview

The mappers layer bridges persistent configuration (YAML, JSON) and runtime domain objects. Every mapper module pairs two complementary classes:

- **Aggregate** — extends a domain object with mutation logic.
- **TransferObject** — extends a domain object with serialization roles and configuration mapping.

This guide covers the cross-cutting strategies and design decisions that apply to all mapper modules, rather than any single domain.

## When to Create an Aggregate

An aggregate is warranted when the domain object needs **mutation methods** beyond simple attribute assignment — methods that enforce invariants, compose nested objects, or coordinate multi-field updates.

If a domain object is only ever used as a **nested sub-object** inside a parent aggregate, and its fields map 1:1 with no special mutation logic, skip the aggregate. The parent aggregate owns the mutation responsibility, and the raw domain object is used directly.

### Examples

| Domain Object | Has Aggregate? | Reason |
|---|---|---|
| `AppInterface` | Yes (`AppInterfaceAggregate`) | Multi-field mutations (`set_service`, `set_constants`, gated `set_attribute`) |
| `AppServiceDependency` | No | 1:1 field mapping; parent manages mutations |
| `Feature` | Yes (`FeatureAggregate`) | Complex `new` factory with ID derivation; step ordering and insertion |
| `FeatureEvent` | Yes (`FeatureEventAggregate`) | Specialized setters for `pass_on_error` and parameter merging |
| `Error` | Yes (`ErrorAggregate`) | Message list management (`set_message`, `remove_message`) |
| `ErrorMessage` | No | 1:1 mapping; parent manages the list |
| `CliArgument` | Yes (`CliArgumentAggregate`) | Gated `set_attribute` for mutable fields; serves as return type for `CliService.get_parent_arguments()` |
| `FlaggedDependency` | Yes (`FlaggedDependencyAggregate`) | Parameter merge-and-prune logic |
| `Formatter`, `Handler`, `Logger` | Yes (thin aggregates) | Provide `new` factory for consistent instantiation |

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
aggregate = AppInterfaceAggregate(**app_interface_data)
```

Choose the pattern that fits the domain. Derivation via `@model_validator` is useful when an ID is composed from multiple parts; dict-wrapper construction is useful when the aggregate is populated from configuration data.

## Nested Sub-Objects Without Aggregates

When a domain object has no aggregate, the parent aggregate creates instances directly via the Pydantic constructor and mutates them. The parent transfer object handles all structural transformation.

### Creation in the parent aggregate

```python
# AppInterfaceAggregate.add_service
dependency = AppServiceDependency(
    module_path=module_path,
    class_name=class_name,
    attribute_id=attribute_id,
    parameters=parameters,
)
self.services.append(dependency)
```

### Transformation in the parent transfer object

The transfer object is responsible for any structural differences between the configuration format and the domain model. The most common pattern is **dict↔list conversion**, where YAML stores sub-objects as a dictionary keyed by an identifier, but the domain model stores them as a list with that identifier as a field.

```python
# AppInterfaceYamlObject.map — dict keys become attribute_id fields
services=[dep.map(attribute_id=dep_id) for dep_id, dep in self.services.items()]

# AppInterfaceYamlObject.from_model — list items become dict entries
services={
    dep.attribute_id: TransferObject.from_model(AppServiceDependencyYamlObject, dep)
    for dep in app_interface.services
}
```

This pattern appears in every domain that nests sub-objects: services in app interfaces, dependencies in service configurations, messages in errors, steps in features.

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

Broad `AliasChoices` lists provide backward compatibility with older configuration formats. The `serialization_alias` controls the canonical output key.

## Gated `set_attribute` Pattern

Some aggregates override `set_attribute` with a gated version that restricts which attributes can be updated. This prevents accidental mutation of identity fields or fields that have dedicated mutation methods.

```python
def set_attribute(self, attribute: str, value: Any) -> None:
    supported = {'name', 'description', 'module_path', 'class_name', 'logger_id', 'flags'}
    if attribute not in supported:
        RaiseError.execute(
            error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
            attribute=attribute,
            supported=', '.join(sorted(supported)),
        )
    setattr(self, attribute, value)
    self.validate()
```

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
Aggregate → from_model → YamlObject → map → Aggregate
```

Tests validate this by asserting field equality after a round trip:

```python
def test_round_trip(aggregate):
    yaml_obj = YamlObject.from_model(aggregate)
    round_tripped = yaml_obj.map()
    assert round_tripped.id == aggregate.id
    assert round_tripped.name == aggregate.name
    # ...
```

When the transfer object performs structural transformations (dict↔list), both `map` and `from_model` must apply the inverse transformation so the round trip is complete.

## Composite Transfer Objects

Some transfer objects don't extend a domain object — they compose multiple domain objects into a single configuration structure. `LoggingSettingsYamlObject` is the canonical example: it holds dicts of `FormatterYamlObject`, `HandlerYamlObject`, and `LoggerYamlObject`, representing the entire `logging.yml` file.

These composite transfer objects use `model_validate` with custom hydration logic:

```python
@classmethod
def hydrate(cls, **data) -> 'LoggingSettingsYamlObject':
    return cls.model_validate(dict(
        formatters={id: FormatterYamlObject.model_validate({**d, 'id': id})
                    for id, d in data.get('formatters', {}).items()},
        # ...
    ))
```

Use this pattern when a YAML file contains multiple related configuration sections that are loaded together.

## Custom `to_primitive` Overrides

When the standard role-based serialization isn't sufficient, transfer objects can override `to_primitive` to produce a custom dictionary. `CliCommandYamlObject` does this to handle argument serialization:

```python
def to_primitive(self, role='to_data', **kwargs) -> Dict[str, Any]:
    return dict(
        **super().to_primitive(role=role, **kwargs),
        args=[arg.model_dump(exclude_none=True) for arg in self.arguments]
    )
```

Use sparingly — prefer role-based `_ROLES` exclude/include when possible.

## Related Documentation

- [docs/core/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md) — Aggregate and TransferObject base class reference
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
