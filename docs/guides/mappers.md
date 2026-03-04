# Mappers – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/mappers/`  
**Version:** 2.0.0a2

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

**Rule of thumb:** if you need `DomainObject.new(SubType, ...)` to create it and nothing else, you don't need an aggregate for it.

## The `new` Factory Pattern

Every aggregate provides a static `new` method. There are two common signatures:

### Pass-through factory
Delegates directly to `Aggregate.new` with no additional logic. Used when the domain object's fields are sufficient as-is.

```python
@staticmethod
def new(validate=True, strict=True, **kwargs) -> 'ErrorAggregate':
    return Aggregate.new(ErrorAggregate, validate=validate, strict=strict, **kwargs)
```

### Derivation factory
Computes or derives fields before delegating. Used when the aggregate needs to normalize inputs, compute IDs, or provide defaults.

```python
@staticmethod
def new(name=None, group_id=None, feature_key=None, id=None, ...) -> 'FeatureAggregate':
    # Derive group_id and feature_key from id if provided.
    if id and '.' in id and (not group_id or not feature_key):
        group_id, feature_key = id.split('.', 1)
    # ...
    return Aggregate.new(FeatureAggregate, id=id, name=name, ...)
```

### Dict-wrapper factory
Accepts a single data dict and unpacks it. Used when the caller already has a dict (e.g., from YAML loading).

```python
@staticmethod
def new(app_interface_data: Dict[str, Any], validate=True, strict=True, **kwargs):
    return Aggregate.new(AppInterfaceAggregate, **app_interface_data, **kwargs)
```

Choose the pattern that fits the domain. Derivation factories are useful when an ID is composed from multiple parts; dict-wrapper factories are useful when the aggregate is populated from configuration data.

## Nested Sub-Objects Without Aggregates

When a domain object has no aggregate, the parent aggregate creates instances via `DomainObject.new()` and mutates them directly. The parent transfer object handles all structural transformation.

### Creation in the parent aggregate

```python
# AppInterfaceAggregate.add_service
dependency = DomainObject.new(
    AppServiceDependency,
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

Transfer objects use Schematics role-based serialization to control which fields appear in different contexts. Tiferet defines three standard roles:

| Role | Purpose |
|---|---|
| `to_model` | Fields included when mapping to an aggregate or domain object |
| `to_data.yaml` | Fields included when serializing to YAML configuration |
| `to_data.json` | Fields included when serializing to JSON |

### Deny vs Allow

- **`deny`** (blacklist) is the default strategy. Start with all fields and exclude the ones that don't belong in the role.
- **`allow`** (whitelist) is used when the domain object is simple enough that listing included fields is clearer, or when you want a full pass-through (`allow()` with no arguments).

### Common deny patterns

**Deny the ID on data roles.** The ID is typically derived from the YAML dictionary key, not stored as a field in the YAML value:

```python
roles = {
    'to_data.yaml': TransferObject.deny('id'),
    'to_data.json': TransferObject.deny('id'),
}
```

**Deny nested collections on `to_model`.** Nested sub-objects need custom mapping (e.g., dict→list conversion), so they are excluded from the primitive and composed manually in `map()`:

```python
roles = {
    'to_model': TransferObject.deny('services', 'constants', 'module_path', 'class_name'),
}
```

The fields denied from `to_model` are then passed explicitly in `map()` with the correct transformation applied.

### The map/deny handshake

The `map()` method and `to_model` role work together. Whatever `to_model` denies, `map()` must supply:

```python
def map(self, **kwargs) -> ErrorAggregate:
    return super().map(
        ErrorAggregate,
        message=[msg.map() for msg in self.message],   # denied from to_model
        **self.to_primitive('to_model'),                # everything else
        **kwargs
    )
```

This pattern ensures the transfer object's role controls what gets auto-serialized, while `map()` handles custom transformations for the excluded fields.

## Attribute Aliasing

Transfer objects support `serialized_name` and `deserialize_from` for mapping between YAML/JSON field names and domain attribute names. Domain objects must **not** use aliasing — only transfer objects.

Common aliases:

| Domain field | YAML alias | `deserialize_from` |
|---|---|---|
| `parameters` | `params` | `['params', 'parameters']` |
| `module_path` | `module` | `['module_path', 'module']` |
| `class_name` | `class` | `['class_name', 'class']` |
| `services` | `attrs` | `['attrs', 'services', 'dependencies', 'attributes']` |
| `dependencies` | `deps` | `['deps', 'dependencies', 'flags']` |
| `steps` | `commands` | `['handlers', 'functions', 'commands', 'steps']` |

Broad `deserialize_from` lists provide backward compatibility with older configuration formats. The `serialized_name` controls the canonical output key.

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

These composite transfer objects override `from_data` to handle sub-object hydration:

```python
@staticmethod
def from_data(**data) -> 'LoggingSettingsYamlObject':
    return TransferObject.from_data(
        LoggingSettingsYamlObject,
        formatters={id: TransferObject.from_data(FormatterYamlObject, **d, id=id)
                    for id, d in data.get('formatters', {}).items()},
        # ...
    )
```

Use this pattern when a YAML file contains multiple related configuration sections that are loaded together.

## Custom `to_primitive` Overrides

When the standard role-based serialization isn't sufficient, transfer objects can override `to_primitive` to produce a custom dictionary. `CliCommandYamlObject` does this to handle argument serialization:

```python
def to_primitive(self, role='to_data.yaml', **kwargs) -> Dict[str, Any]:
    return dict(
        **super().to_primitive(role=role, **kwargs),
        args=[arg.to_primitive() for arg in self.arguments]
    )
```

Use sparingly — prefer role-based deny/allow when possible.

## Related Documentation

- [docs/core/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md) — Aggregate and TransferObject base class reference
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
