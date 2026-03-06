```markdown
# Domain – Feature: FeatureStep, FeatureEvent, and Feature

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 06, 2026  
**Version:** 2.0.0a2

## Overview

The Feature domain defines the structural foundation for workflow orchestration in Tiferet. A `Feature` represents a complete workflow definition — a named, identifiable unit composed of ordered steps that execute domain events from the dependency injection container. Each step is described by a `FeatureEvent`, which carries container resolution metadata, flags, parameters, result routing, and error handling configuration.

All domain objects in this module are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing steps, renaming, reordering) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/feature.py`

> **Rename note (v2.0a2):** `FeatureCommand` has been renamed to `FeatureEvent` to align with the `Command` → `DomainEvent` transition. The polymorphic `FeatureStep` base class is new in v2.0a2.

## Domain Objects

### FeatureStep

Base class for steps in a feature workflow. Provides a `type` discriminator for future polymorphism (e.g., `FeatureCondition`, `FeatureLoop`).

| Attribute | Type         | Required | Default   | Description                        |
|-----------|--------------|----------|-----------|------------------------------------|
| `type`    | `StringType` | No       | `'event'` | The type of the feature step.      |
| `name`    | `StringType` | Yes      | —         | The name of the feature step.      |

Currently the only supported `type` value is `'event'`, constrained via `choices=['event']`.

### FeatureEvent

Concrete step type that extends `FeatureStep`. Represents the execution of a domain event resolved from the DI container.

| Attribute        | Type                    | Required | Default | Description                                                        |
|------------------|-------------------------|----------|---------|--------------------------------------------------------------------|
| `attribute_id`   | `StringType`            | Yes      | —       | The container attribute ID for the domain event.                   |
| `flags`          | `ListType(StringType)`  | No       | `[]`    | Feature flags that activate this event.                            |
| `parameters`     | `DictType(StringType)`  | No       | `{}`    | Custom parameters for the event.                                   |
| `return_to_data` | `BooleanType`           | No       | `False` | Whether to return the result to the feature data context (obsolete). |
| `data_key`       | `StringType`            | No       | —       | Data key to store the result in if `return_to_data` is True.       |
| `pass_on_error`  | `BooleanType`           | No       | `False` | Whether to continue the workflow if the event fails.               |

Inherits `type` (defaults to `'event'`) and `name` from `FeatureStep`.

#### Parameter Resolution

Parameters support two value modes:

- **Static values** — literal strings provided directly in configuration (e.g., `b: '0.5'`).
- **Request-backed values** — prefixed with `$r.` to indicate the value is resolved from the incoming request data at runtime (e.g., `$r.user_id`).

### Feature

Immutable value object representing a complete feature workflow definition.

| Attribute      | Type                            | Required | Default | Description                                          |
|----------------|---------------------------------|----------|---------|------------------------------------------------------|
| `id`           | `StringType`                    | Yes      | —       | The unique identifier (`group_id.feature_key`).      |
| `name`         | `StringType`                    | Yes      | —       | The name of the feature.                             |
| `flags`        | `ListType(StringType)`          | No       | `[]`    | Feature flags that activate this entire feature.     |
| `description`  | `StringType`                    | No       | —       | The description of the feature.                      |
| `group_id`     | `StringType`                    | Yes      | —       | The context group identifier for the feature.        |
| `feature_key`  | `StringType`                    | Yes      | —       | The key of the feature.                              |
| `steps`        | `ListType(ModelType(FeatureEvent))` | No   | `[]`    | The ordered step workflow for the feature.            |
| `log_params`   | `DictType(StringType)`          | No       | `{}`    | Parameters to log for the feature.                   |

#### Methods

**`get_step(position: int) -> FeatureStep | None`**

Returns the step at the given index, or `None` if the index is out of range or invalid (e.g., non-integer):

```python
feature = DomainObject.new(Feature, id='calc.add', name='Add', group_id='calc', feature_key='add', steps=[...])
step = feature.get_step(0)    # First step
step = feature.get_step(99)   # None (out of range)
step = feature.get_step('x')  # None (invalid type)
```

## Runtime Role

The Feature domain objects participate in runtime workflow execution through the following flow:

1. `FeatureContext.execute_feature(feature_id, data)` receives a feature ID from the application interface.
2. The `Feature` is loaded from the `FeatureService` (backed by `feature.yml` configuration).
3. `FeatureContext` iterates over `feature.steps`, resolving each `FeatureEvent.attribute_id` from the DI container.
4. Each resolved domain event is executed with the merged request data and step parameters.
5. If `data_key` is set, the result is stored back into the data context under that key for downstream steps.
6. If `pass_on_error` is `True`, errors from that step are caught and the workflow continues.

## Configuration Mapping

Features are defined in `app/configs/feature.yml`. Each group contains keyed features:

```yaml
features:
  calc:
    add:
      name: 'Add Number'
      description: 'Adds one number to another'
      commands:
        - attribute_id: add_number_event
          name: Add `a` and `b`
    sqrt:
      name: 'Square Root'
      description: 'Calculates the square root of a number'
      commands:
        - attribute_id: exponentiate_number_event
          name: Calculate square root of `a`
          params:
            b: '0.5'
```

The `commands` key in YAML maps to `steps` (list of `FeatureEvent`) on the domain object. The `params` key maps to `parameters`.

## Domain Events

The following domain events interact with `Feature`, `FeatureStep`, and `FeatureEvent`:

| Event               | Description                                          |
|---------------------|------------------------------------------------------|
| `GetFeature`        | Retrieves a `Feature` by ID.                         |
| `AddFeature`        | Creates and persists a new `Feature`.                |
| `AddFeatureCommand` | Adds a `FeatureEvent` step to an existing `Feature`. |
| `RenameFeature`     | Renames an existing `Feature` via aggregate.         |

These events depend on the `FeatureService` interface for persistence operations.

## Service Interface

**`FeatureService`** (`tiferet/interfaces/feature.py`) defines the abstract contract for Feature domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> Feature`
- `list() -> List[Feature]`
- `save(feature) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `FeatureYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `FeatureContext` is loaded as part of the application interface bootstrap, receiving `FeatureService` and container resolution via dependency injection.
- **DI:** `FeatureEvent.attribute_id` references a `ServiceConfiguration` entry in `container.yml`, which is resolved at runtime by the DI container.
- **Error:** Domain events use `verify()` and `raise_error()` to raise `TiferetError` when features are not found or parameters are invalid. These are resolved to `Error` domain objects for formatted responses.
- **CLI:** CLI commands map to features via `group_key` and `key`, enabling command-line execution of feature workflows.

## Instantiation

```python
from tiferet.domain import DomainObject, Feature, FeatureEvent

step = DomainObject.new(
    FeatureEvent,
    name='Add a and b',
    attribute_id='add_number_event',
    parameters={'b': '0.5'},
)

feature = DomainObject.new(
    Feature,
    id='calc.add',
    name='Add Number',
    group_id='calc',
    feature_key='add',
    description='Adds one number to another',
    steps=[step],
)

# feature.get_step(0).attribute_id == 'add_number_event'
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
- [docs/guides/domain/error.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/error.md) — Error domain guide
- [docs/guides/domain/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/di.md) — DI domain guide
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
```
