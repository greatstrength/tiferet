# Domain – Feature: FeatureStep, EventFeatureStep, and Feature

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The Feature domain defines the structural foundation for workflow orchestration in Tiferet. A `Feature` represents a complete workflow definition — a named, identifiable unit composed of ordered steps that execute domain events from the dependency injection container. Each step is described by an `EventFeatureStep`, which carries container resolution metadata, flags, parameters, result routing, and error handling configuration.

All domain objects in this module are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing steps, renaming, reordering) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/feature.py`

> **Rename note (v2.0a2):** `FeatureCommand` was renamed to `FeatureEvent` to align with the `Command` → `DomainEvent` transition. The polymorphic `FeatureStep` base class is new in v2.0a2.
>
> **Rename note (v2.0.0b10):** the concrete step domain object `FeatureEvent` was renamed to `EventFeatureStep` (current mappers `EventFeatureStepAggregate`/`EventFeatureStepConfigObject`) to free the `FeatureEvent` name for the new per-module base domain event (`FeatureEvent(DomainEvent)` in `tiferet/events/feature.py`).

## Domain Objects

### FeatureStep

Base class for steps in a feature workflow. Provides a `type` discriminator for future polymorphism (e.g., `FeatureCondition`, `FeatureLoop`).

| Attribute | Type         | Required | Default   | Description                        |
|-----------|--------------|----------|-----------|------------------------------------|
| `type`    | `Literal['event']` | No | `'event'` | The type of the feature step.      |
| `name`    | `str`        | Yes      | —         | The name of the feature step.      |

Currently the only supported `type` value is `'event'`, constrained via `Literal['event']`.

### EventFeatureStep

Concrete step type that extends `FeatureStep`. Represents the execution of a domain event resolved via the injected service-resolution handler.

| Attribute        | Type                    | Required | Default | Description                                                        |
|------------------|-------------------------|----------|---------|--------------------------------------------------------------------|
| `service_id`     | `str`                   | Yes      | —       | The service registration ID for the feature event.                |
| `flags`          | `List[str]`             | No       | `[]`    | Feature flags that activate this event.                            |
| `parameters`     | `Dict[str, str]`        | No       | `{}`    | Custom parameters for the event.                                   |
| `return_to_data` | `bool`                  | No       | `False` | Whether to return the result to the feature data context (obsolete). |
| `data_key`       | `str \| None`           | No       | `None`  | Data key to store the result in.                                   |
| `pass_on_error`  | `bool`                  | No       | `False` | Whether to continue the workflow if the event fails.               |
| `condition`      | `str \| None`           | No       | `None`  | Boolean expression evaluated against request data before execution. If `False`, the step is silently skipped. |
| `middleware`     | `List[str]`             | No       | `[]`    | Ordered middleware service IDs applied to this step.               |

Inherits `type` (defaults to `'event'`) and `name` from `FeatureStep`.

#### Parameter Resolution

Parameters support two value modes:

- **Static values** — literal strings provided directly in configuration (e.g., `b: '0.5'`).
- **Request-backed values** — prefixed with `$r.` to indicate the value is resolved from the incoming request data at runtime (e.g., `$r.user_id`).

#### Conditional Execution

The optional `condition` field supports boolean expression strings evaluated against request data before the step executes. The `$r.` prefix references values from `request.data` (e.g., `$r.b != 0`, `$r.mode == 'advanced'`). When `condition` is `None` or empty, the step always executes. When it evaluates to `False`, the step is silently skipped.

### Feature

Immutable value object representing a complete feature workflow definition.

| Attribute      | Type                            | Required | Default | Description                                          |
|----------------|---------------------------------|----------|---------|------------------------------------------------------|
| `id`           | `str`                           | Yes      | —       | The unique identifier (`group_id.feature_key`).      |
| `name`         | `str`                           | Yes      | —       | The name of the feature.                             |
| `flags`        | `List[str]`                     | No       | `[]`    | Feature flags that activate this entire feature.     |
| `description`  | `str \| None`                   | No       | `None`  | The description of the feature.                      |
| `group_id`     | `str`                           | Yes      | —       | The context group identifier for the feature.        |
| `feature_key`  | `str`                           | Yes      | —       | The key of the feature.                              |
| `steps`        | `List[EventFeatureStep]`        | No       | `[]`    | The ordered step workflow for the feature.            |
| `is_async`     | `bool`                          | No       | `False` | Whether the feature executes its steps asynchronously (selects `AsyncFeatureContext`). |
| `log_params`   | `Dict[str, str]`                | No       | `{}`    | Parameters to log for the feature.                   |

#### Methods

**`get_step(position: int) -> FeatureStep | None`**

Returns the step at the given index, or `None` if the index is out of range or invalid (e.g., non-integer):

```python
feature = Feature(id='calc.add', name='Add', group_id='calc', feature_key='add', steps=[...])
step = feature.get_step(0)    # First step
step = feature.get_step(99)   # None (out of range)
step = feature.get_step('x')  # None (invalid type)
```

## Runtime Role

The Feature domain objects participate in runtime workflow execution through the following flow:

1. `FeatureContext.execute_feature(feature_id, data)` receives a feature ID from the application interface.
2. The `Feature` is loaded from the `FeatureService` (backed by `feature.yml` configuration).
3. `FeatureContext` iterates over `feature.steps`, resolving each `EventFeatureStep.service_id` via the injected `get_dependency` handler.
4. Each resolved domain event is executed with the merged request data and step parameters.
5. If `data_key` is set, the result is stored back into the data context under that key for downstream steps.
6. If `pass_on_error` is `True`, errors from that step are caught and the workflow continues.

When `feature.is_async` is `True`, the application interface hub selects the `AsyncFeatureContext` (a subclass of `FeatureContext`) and awaits each step via `execute_feature_async`; otherwise the synchronous `FeatureContext` is used. The public `run()` entry point remains synchronous in both cases.

## Configuration Mapping

Features are defined in the `features` section of the configuration file (typically `config.yml`, though per-file configs such as `feature.yml` are also supported). Each group contains keyed features:

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

The `commands` key in YAML maps to `steps` (list of `EventFeatureStep`) on the domain object. The `params` key maps to `parameters`.

## Domain Events

The following domain events interact with `Feature`, `FeatureStep`, and `EventFeatureStep`:

| Event               | Description                                          |
|---------------------|------------------------------------------------------|
| `GetFeature`        | Retrieves a `Feature` by ID.                         |
| `AddFeature`        | Creates and persists a new `Feature`.                |
| `AddFeatureStep`    | Adds an `EventFeatureStep` step to an existing `Feature`. |
| `UpdateFeature`     | Updates an existing `Feature`'s metadata via aggregate.   |

These events depend on the `FeatureService` interface for persistence operations.

## Service Interface

**`FeatureService`** (`tiferet/interfaces/feature.py`) defines the abstract contract for Feature domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> Feature`
- `list() -> List[Feature]`
- `save(feature) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `FeatureConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `FeatureContext` is loaded as part of the application interface bootstrap, receiving `FeatureService` and container resolution via dependency injection.
- **DI:** `EventFeatureStep.service_id` references a `ServiceRegistration` entry (in the `services` section of the configuration), resolved at runtime via the injected `get_dependency` handler.
- **Error:** Domain events use `verify()` and `raise_error()` to raise `TiferetError` when features are not found or parameters are invalid. These are resolved to `Error` domain objects for formatted responses.
- **CLI:** CLI commands map to features via `group_key` and `key`, enabling command-line execution of feature workflows.

## Instantiation

```python
from tiferet.domain import Feature, EventFeatureStep

step = EventFeatureStep(
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

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
- [docs/guides/domain/error.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/error.md) — Error domain guide
- [docs/guides/domain/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/di.md) — DI domain guide
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
