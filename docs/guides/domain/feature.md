# Domain – Feature (Workflow Orchestration)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0b1

## Overview

The Feature domain defines **what the application does**. While the App domain assembles the runtime and the DI domain wires up services, the Feature domain describes the user-facing units of execution — the workflows that transform input into output.

A `Feature` is a named workflow composed of ordered steps. Each step references a domain event registered in the DI container and carries orchestration metadata — parameters, result routing, error handling behavior, and flag-based resolution. When a user calls `app.run('basic_calc', 'calc.add', data={'a': 1, 'b': 2})`, the framework loads the `calc.add` feature and executes its steps in sequence.

## Domain Objects

### FeatureStep

Base class for steps in a feature workflow. Provides a `type` discriminator for future polymorphism (e.g., `FeatureCondition`, `FeatureLoop`).

| Attribute | Type         | Required | Default   | Description                        |
|-----------|--------------|----------|-----------|------------------------------------|
| `type`    | `Literal['event']` | No | `'event'` | The type of the feature step.      |
| `name`    | `str`        | Yes      | —         | The name of the feature step.      |

Currently the only supported `type` value is `'event'`, constrained via `Literal['event']`.

### FeatureEvent

Concrete step type that extends `FeatureStep`. Represents the execution of a domain event resolved from the DI container.

| Attribute        | Type                    | Required | Default | Description                                                        |
|------------------|-------------------------|----------|---------|--------------------------------------------------------------------|
| `service_id`     | `str \| None`           | No *(todo: required)* | `None` | The service configuration ID for the feature event.          |
| `attribute_id`   | `str \| None`           | No *(obsolete)*       | `None` | The container attribute ID for the domain event. Replaced by `service_id`. |
| `flags`          | `List[str]`             | No       | `[]`    | Feature flags that activate this event.                            |
| `parameters`     | `Dict[str, str]`        | No       | `{}`    | Custom parameters for the event.                                   |
| `return_to_data` | `bool`                  | No       | `False` | Whether to return the result to the feature data context (obsolete). |
| `data_key`       | `str \| None`           | No       | `None`  | Data key to store the result in if `return_to_data` is True.       |
| `pass_on_error`  | `bool`                  | No       | `False` | Whether to continue the workflow if the event fails.               |

Inherits `type` (defaults to `'event'`) and `name` from `FeatureStep`.

#### Parameter Resolution

Parameters support two value modes:

- **Static values** — literal strings provided directly in configuration (e.g., `b: '0.5'`).
- **Request-backed values** — prefixed with `$r.` to indicate the value is resolved from the incoming request data at runtime (e.g., `$r.user_id`).

### Feature

The top-level workflow definition. A feature groups a sequence of steps under a composite identifier (`group_id.feature_key`).

| Attribute      | Type                            | Required | Default | Description                                          |
|----------------|---------------------------------|----------|---------|------------------------------------------------------|
| `id`           | `str`                           | Yes      | —       | The unique identifier (`group_id.feature_key`).      |
| `name`         | `str`                           | Yes      | —       | The name of the feature.                             |
| `flags`        | `List[str]`                     | No       | `[]`    | Feature flags that activate this entire feature.     |
| `description`  | `str \| None`                   | No       | `None`  | The description of the feature.                      |
| `group_id`     | `str`                           | Yes      | —       | The context group identifier for the feature.        |
| `feature_key`  | `str`                           | Yes      | —       | The key of the feature.                              |
| `steps`        | `List[FeatureEvent]`            | No       | `[]`    | The ordered step workflow for the feature.            |
| `log_params`   | `Dict[str, str]`                | No       | `{}`    | Parameters to log for the feature.                   |

**Behavior method:**

- `get_step(position)` — retrieves the step at a given index, returning `None` for out-of-range positions. Used by events that update or remove individual steps.

### FeatureStep (base class)

```python
feature = Feature(id='calc.add', name='Add', group_id='calc', feature_key='add', steps=[...])
step = feature.get_step(0)    # First step
step = feature.get_step(99)   # None (out of range)
step = feature.get_step('x')  # None (invalid type)
```

## Runtime Role

`FeatureContext` is the sole consumer of the Feature domain at runtime. The execution flow is:

1. `FeatureContext.execute_feature(feature_id, data)` receives a feature ID from the application interface.
2. The `Feature` is loaded from the `FeatureService` (backed by `feature.yml` configuration).
3. `FeatureContext` iterates over `feature.steps`, resolving each `FeatureEvent.service_id` (with `attribute_id` fallback during migration) from the DI container.
4. Each resolved domain event is executed with the merged request data and step parameters.
5. If `data_key` is set, the result is stored back into the data context under that key for downstream steps.
6. If `pass_on_error` is `True`, errors from that step are caught and the workflow continues.

```python
# A feature with two steps — the second step uses the result of the first
# feature.yml:
#   calc.add_and_double:
#     steps:
#       - service_id: add_number_event
#         name: Add a and b
#         data_key: sum_result
#       - service_id: multiply_number_event
#         name: Double the sum
#         params:
#           a: $r.sum_result
#           b: '2'
```

## Configuration

Features are defined in `app/configs/feature.yml`:

```yaml
features:
  calc:
    add:
      name: 'Add Number'
      description: 'Adds one number to another'
      commands:
        - service_id: add_number_event
          name: Add `a` and `b`
    sqrt:
      name: 'Square Root'
      description: 'Calculates the square root of a number'
      commands:
        - service_id: exponentiate_number_event
          name: Calculate square root of `a`
          params:
            b: '0.5'
```

The two-level nesting (`calc.add`) becomes the composite `Feature.id`. The `commands` list maps to `steps`. Each step's `service_id` references a `ServiceConfiguration` in the DI container. The `sqrt` feature demonstrates parameter reuse — `exponentiate_number_event` is shared with the `exp` feature but configured with a fixed `b: '0.5'`.

## Domain Events

| Event | Purpose |
|-------|---------|
| `GetFeature` | Retrieve a feature by ID (used during execution) |
| `AddFeature` | Create a new feature configuration |
| `UpdateFeature` | Update name or description |
| `RemoveFeature` | Delete a feature configuration |
| `ListFeatures` | List features, optionally filtered by group |
| `AddFeatureCommand` | Append or insert a step into a feature's workflow |
| `UpdateFeatureCommand` | Update an attribute on a step at a given position |
| `RemoveFeatureCommand` | Remove a step by position |
| `ReorderFeatureCommand` | Move a step from one position to another |

## Service Interface

`FeatureService` (`tiferet/interfaces/feature.py`) — abstracts CRUD access to feature configurations.

## Relationship to Other Domains

Concrete implementations (e.g., `FeatureYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `FeatureContext` is loaded as part of the application interface bootstrap, receiving `FeatureService` and container resolution via dependency injection.
- **DI:** `FeatureEvent.service_id` references a `ServiceConfiguration` entry in `di.yml`, which is resolved at runtime by the DI container. During migration, `attribute_id` is supported as a fallback.
- **Error:** Domain events use `verify()` and `raise_error()` to raise `TiferetError` when features are not found or parameters are invalid. These are resolved to `Error` domain objects for formatted responses.
- **CLI:** CLI commands map to features via `group_key` and `key`, enabling command-line execution of feature workflows.

## Instantiation

```python
from tiferet.domain import Feature, FeatureEvent

step = FeatureEvent(
    name='Add a and b',
    service_id='add_number_event',
    parameters={'b': '0.5'},
)

feature = Feature(
    id='calc.add',
    name='Add Number',
    group_id='calc',
    feature_key='add',
    description='Adds one number to another',
    steps=[step],
)

# feature.get_step(0).service_id == 'add_number_event'
```

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns
- [docs/guides/domain/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/di.md) — DI domain guide
