# Domain – Feature: FeatureStep, EventFeatureStep, ParameterSpecification, RequestSpecification, and Feature

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

The Feature domain defines the structural foundation for workflow orchestration in Tiferet. A `Feature` represents a complete workflow definition — a named, identifiable unit composed of ordered steps that execute domain events from the dependency injection container. Each step is described by an `EventFeatureStep`, which carries container resolution metadata, flags, parameters, result routing, and error handling configuration. A `Feature` may also declare an optional `params_schema` (`RequestSpecification`), the request-validation schema machinery introduced during the Model Error Protocol migration that dynamically reconstitutes declared parameters (`ParameterSpecification`) into a Pydantic model for fail-fast request coercion.

All domain objects in this module are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing steps, renaming, reordering) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/feature.py`
**Vision:** See the `Feature` and `RequestSpecification` class docstrings in `tiferet/domain/feature.py` for the value statements this guide distills.

## Ubiquitous Language

- **Params schema** — a `Feature`'s optional `params_schema` (`RequestSpecification`), the declared request-validation contract applied before any step executes.
- **Parameter specification** — one `ParameterSpecification`: a single expected request parameter's declared type, requiredness, default, and validation constraints.
- **Effective required** — a parameter is only truly required when `required=True` **and** no `default` is set; a required parameter with a default is treated as optional for schema-building purposes.
- **Coercion** — `RequestSpecification.coerce`'s validate-and-merge step: request data validated against the dynamically built model, then merged with defaults over the original payload.
- **Ordinal priority** — the same flag-priority convention used elsewhere in the framework (see [docs/guides/domain/di.md](di.md)); `Feature.flags`/`EventFeatureStep.flags` combine additively rather than by priority, unlike `ServiceRegistration.get_dependency`.

## Domain Objects

### FeatureStep

Base class for steps in a feature workflow. Provides a `type` discriminator for future polymorphism (e.g., `FeatureCondition`, `FeatureLoop`).

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="featurestep-type"></a>`type` | `Literal['event']` | No | `'event'` | The type of the feature step. |
| <a id="featurestep-name"></a>`name` | `str` | Yes | — | The name of the feature step. |

Currently the only supported `type` value is `'event'`, constrained via `Literal['event']`.

### EventFeatureStep

Concrete step type that extends `FeatureStep`. Represents the execution of a domain event resolved via the injected service-resolution handler.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="eventfeaturestep-service-id"></a>`service_id` | `str` | Yes | — | The service registration ID for the feature event. |
| <a id="eventfeaturestep-flags"></a>`flags` | `List[str]` | No | `[]` | Feature flags that activate this event. |
| <a id="eventfeaturestep-parameters"></a>`parameters` | `Dict[str, str]` | No | `{}` | Custom parameters for the event. |
| <a id="eventfeaturestep-data-key"></a>`data_key` | `str \| None` | No | `None` | The key under which to store the step result in the request data. When `None`, the step result is set as the top-level response. |
| <a id="eventfeaturestep-pass-on-error"></a>`pass_on_error` | `bool` | No | `False` | Whether to continue the workflow if the event raises a **domain** error (`TiferetError`). Model and infrastructure defects always propagate — see [docs/guides/errors.md](../errors.md). |
| <a id="eventfeaturestep-is-async"></a>`is_async` | `bool` | No | `False` | Whether this step executes asynchronously. Only evaluated when the parent `Feature.is_async` is `False`; when the feature is async the entire step loop runs via `run_coroutine(_execute_async)` regardless of this flag. |
| <a id="eventfeaturestep-condition"></a>`condition` | `str \| None` | No | `None` | Boolean expression evaluated against request data before execution. If `False`, the step is silently skipped. |
| <a id="eventfeaturestep-middleware"></a>`middleware` | `List[str]` | No | `[]` | Ordered middleware service IDs applied to this step. Outermost wrapper first. |

Inherits `type` (defaults to `'event'`) and `name` from `FeatureStep`. Note: the `return_to_data` field documented by an earlier version of this guide does not exist in current source — it was superseded by `data_key`.

#### Parameter Resolution

Parameters support two value modes:

- **Static values** — literal strings provided directly in configuration (e.g., `b: '0.5'`).
- **Request-backed values** — prefixed with `$r.` to indicate the value is resolved from the incoming request data at runtime (e.g., `$r.user_id`).

#### Conditional Execution

The optional `condition` field supports boolean expression strings evaluated against request data before the step executes. The `$r.` prefix references values from `request.data` (e.g., `$r.b != 0`, `$r.mode == 'advanced'`). When `condition` is `None` or empty, the step always executes. When it evaluates to `False`, the step is silently skipped.

### ParameterSpecification

A value object describing one expected request parameter, including its declared type, requiredness, default, and validation constraints.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="parameterspecification-name"></a>`name` | `str` | Yes | — | The name of the request parameter. |
| <a id="parameterspecification-type"></a>`type` | `Literal['str', 'int', 'float', 'bool', 'list', 'dict']` | No | `'str'` | The declared type of the parameter. |
| <a id="parameterspecification-required"></a>`required` | `bool` | No | `True` | Whether the parameter is required. |
| <a id="parameterspecification-default"></a>`default` | `Any \| None` | No | `None` | The default value applied when the parameter is absent. |
| <a id="parameterspecification-description"></a>`description` | `str \| None` | No | `None` | A human-readable description of the parameter. |
| <a id="parameterspecification-minimum"></a>`minimum` | `float \| None` | No | `None` | Inclusive lower bound for numeric values (maps to `ge`). |
| <a id="parameterspecification-maximum"></a>`maximum` | `float \| None` | No | `None` | Inclusive upper bound for numeric values (maps to `le`). |
| <a id="parameterspecification-min-length"></a>`min_length` | `int \| None` | No | `None` | Minimum length for string or list values. |
| <a id="parameterspecification-max-length"></a>`max_length` | `int \| None` | No | `None` | Maximum length for string or list values. |
| <a id="parameterspecification-pattern"></a>`pattern` | `str \| None` | No | `None` | Regex pattern the value must match. |
| <a id="parameterspecification-choices"></a>`choices` | `List[Any] \| None` | No | `None` | Enumerated set of valid values. |

#### Methods

<a id="parameterspecification-get-type"></a>
**`get_type() -> type`**

Maps the declared `type` string (`'str'`, `'int'`, `'float'`, `'bool'`, `'list'`, `'dict'`) to its Python type, defaulting to `str` for any unrecognized value.

<a id="parameterspecification-field-definition"></a>
**`field_definition() -> Tuple[Any, Any]`**

Builds the `(annotation, default)` pair consumed by `pydantic.create_model`. Prefers a `Literal` of `choices` when present; wraps the annotation in `Optional` unless the parameter is *effectively required* (`required=True` and `default is None`); translates `minimum`/`maximum`/`min_length`/`max_length`/`pattern`/`description` into `Field` constraint keywords.

```python
spec = ParameterSpecification(name='b', type='float', required=False, default=0.5, minimum=0)
annotation, field = spec.field_definition()
```

### RequestSpecification

A feature-level Specification object that dynamically reconstitutes the request configuration as a Pydantic model to validate and coerce request data, failing fast with a single aggregated error. Runtime output (the step/feature *result*) is intentionally not modeled here — this object validates *input* only.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="requestspecification-parameters"></a>`parameters` | `List[ParameterSpecification]` | No | `[]` | The expected request parameters. |

#### Methods

<a id="requestspecification-normalize-parameters"></a>
**Config Normalization via `@model_validator`**

`normalize_parameters` accepts three ergonomic config forms and canonicalizes all of them into the `parameters` list: the canonical `{'parameters': [...]}` form, the shorthand keyed form (`{'a': 'int'}`), and the expanded keyed form (`{'b': {'type': 'float', 'required': False}}`). A list-valued `parameters` key is treated as already canonical — this lets a feature declare a request parameter literally named `parameters` without colliding with the canonical shape.

<a id="requestspecification-build-model"></a>
**`build_model(model_name: str = 'RequestModel') -> type`**

Dynamically creates a standalone `pydantic.BaseModel` (deliberately not a `DomainObject`, so `coerce_numbers_to_str` cannot corrupt numeric coercion) from each parameter's `field_definition()`, ignoring extra keys.

<a id="requestspecification-coerce"></a>
**`coerce(data: Dict[str, Any]) -> Dict[str, Any]`**

Validates and coerces `data` against the built model, returning the original request data merged with the coerced schema-covered fields and defaults; unspecified extra keys are preserved. Lets Pydantic's `ValidationError` propagate untouched — naming the failure as `REQUEST_VALIDATION_FAILED` is the orchestration layer's concern (`contexts/feature.py::validate_request`), so this domain object carries no framework error vocabulary.

<a id="requestspecification-is-satisfied-by"></a>
**`is_satisfied_by(data: Dict[str, Any]) -> bool`**

Reports whether `data` satisfies the specification by attempting `coerce` and treating a `ValidationError` as "not satisfied."

```python
spec = RequestSpecification(parameters=[ParameterSpecification(name='a', type='int')])
spec.is_satisfied_by({'a': '5'})   # True (coerced)
spec.is_satisfied_by({})           # False (missing required 'a')
```

### Feature

Immutable value object representing a complete feature workflow definition.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="feature-id"></a>`id` | `str` | Yes | — | The unique identifier (`group_id.feature_key`). |
| <a id="feature-name"></a>`name` | `str` | Yes | — | The name of the feature. |
| <a id="feature-flags"></a>`flags` | `List[str]` | No | `[]` | Feature flags that activate this entire feature. |
| <a id="feature-description"></a>`description` | `str \| None` | No | `None` | The description of the feature. |
| <a id="feature-group-id"></a>`group_id` | `str` | Yes | — | The context group identifier for the feature. |
| <a id="feature-feature-key"></a>`feature_key` | `str` | Yes | — | The key of the feature. |
| <a id="feature-steps"></a>`steps` | `List[EventFeatureStep]` | No | `[]` | The ordered step workflow for the feature. |
| <a id="feature-middleware"></a>`middleware` | `List[str]` | No | `[]` | Ordered middleware service IDs applied to every step in this feature. Outermost wrapper first. |
| <a id="feature-is-async"></a>`is_async` | `bool` | No | `False` | Whether `FeatureContext` drives the entire step loop asynchronously. |
| <a id="feature-log-params"></a>`log_params` | `Dict[str, str]` | No | `{}` | Parameters to log for the feature. |
| <a id="feature-params-schema"></a>`params_schema` | `RequestSpecification \| None` | No | `None` | Optional feature-level request validation schema applied to request data before step execution. |

#### Methods

<a id="feature-get-step"></a>
**`get_step(position: int) -> FeatureStep | None`**

Returns the step at the given index, or `None` if the index is out of range or invalid (e.g., non-integer):

```python
feature = Feature(id='calc.add', name='Add', group_id='calc', feature_key='add', steps=[...])
step = feature.get_step(0)    # First step
step = feature.get_step(99)   # None (out of range)
step = feature.get_step('x')  # None (invalid type)
```

## Request Validation Flow

When a `Feature` declares a `params_schema`, `contexts/feature.py::validate_request(feature, request)` runs before any step executes:

1. If `feature.params_schema` is `None`, the request is left unchanged and validation is a no-op.
2. Otherwise, `request.data = feature.params_schema.coerce(request.data)` replaces the request data with the coerced, merged result.
3. A `ValidationError` raised by `coerce` is caught, flattened via `unpack_validation_error` (`tiferet/domain/core.py`, shared with the `ModelError` mutation path — see [docs/guides/errors.md](../errors.md)), and re-raised as a single catalogued `REQUEST_VALIDATION_FAILED` `TiferetError` carrying the violations — not a `ModelError`, since a bad request payload is a domain outcome the caller needs resolved and localized.

## Runtime Role

The Feature domain objects participate in runtime workflow execution through the following flow:

1. The `Feature` is loaded from the `FeatureService` (backed by the configuration file) and bound to a `FeatureContext` via `from_domain`.
2. `FeatureContext.execute_feature(request)` reads that bound feature from `self.domain` and runs `validate_request` (see above) before any step executes.
3. `FeatureContext` iterates over `feature.steps`, resolving each `EventFeatureStep.service_id` via the injected `get_dependency` handler.
4. Each resolved domain event is executed with the merged request data and step parameters.
5. If `data_key` is set, the result is stored back into the data context under that key for downstream steps.
6. If `pass_on_error` is `True`, a `TiferetError` from that step is caught, the step result resolves to `None`, and the workflow continues. The flag passes on **domain** errors only: a `ModelError` or `ServiceError` (or any other non-`TiferetError` exception) is a defect rather than a domain outcome and propagates regardless — see [docs/guides/errors.md](../errors.md).

There is no separate async context class: when `feature.is_async` is `True`, `FeatureContext.execute_feature` itself drives the whole step loop through an internal coroutine (`_execute_async`), run to completion via the module-level `run_coroutine` helper; an individual `step.is_async=True` step within an otherwise synchronous feature is driven the same way, per step. The public `run()` entry point stays synchronous in every case.

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

The following domain events (`tiferet/events/feature.py`) interact with `Feature`, `FeatureStep`, and `EventFeatureStep`:

| Event | Description |
|---|---|
| `AddFeature` | Creates and persists a new `Feature`. |
| `GetFeature` | Retrieves a `Feature` by ID, with an optional default-feature-index fallback. |
| `ListFeatures` | Lists features, optionally filtered by `group_id`. |
| `RemoveFeature` | Removes an entire feature by ID (idempotent). |
| `UpdateFeature` | Updates a `Feature`'s `name` or `description` metadata via aggregate. |
| `AddFeatureStep` | Adds an `EventFeatureStep` to an existing `Feature`. |
| `UpdateFeatureStep` | Updates an attribute (`name`, `service_id`, `data_key`, `pass_on_error`, `parameters`) on a step at a given position. |
| `RemoveFeatureStep` | Removes a step by position (idempotent). |
| `ReorderFeatureStep` | Moves a step from one position to another. |

These events depend on the `FeatureService` interface for persistence operations.

## Service Interface

**`FeatureService`** (`tiferet/interfaces/feature.py`) defines the abstract contract for Feature domain persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> FeatureAggregate`
- `list(group_id: Optional[str] = None) -> List[FeatureAggregate]`
- `save(feature: FeatureAggregate) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `FeatureConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `FeatureContext` is loaded as part of the application session bootstrap, receiving `FeatureService` and container resolution via dependency injection.
- **DI:** `EventFeatureStep.service_id` references a `ServiceRegistration` entry (in the `services` section of the configuration), resolved at runtime via the injected `get_dependency` handler.
- **Core/Errors:** `RequestSpecification.coerce` shares `unpack_validation_error` with the `ModelError` mutation path but resolves to a catalogued `TiferetError` (`REQUEST_VALIDATION_FAILED`) instead — see [docs/guides/errors.md](../errors.md) for why the two paths diverge.
- **Error:** Domain events use `verify()` and `raise_error()` to raise `TiferetError` when features are not found or parameters are invalid. These are resolved to `Error` domain objects for formatted responses.
- **CLI:** CLI commands map to features via `group_key` and `key`, enabling command-line execution of feature workflows.

## Boundaries

**Inside this domain:** the declared shape of a feature workflow (`Feature`, `FeatureStep`, `EventFeatureStep`) and its optional request-validation schema (`ParameterSpecification`, `RequestSpecification`).
**Outside this domain:** actually resolving and executing a step's domain event (`FeatureContext`, `docs/core/contexts.md`), naming a coercion failure as a catalogued error (`contexts/feature.py::validate_request`, not this module), and mutation of a `Feature` (`FeatureAggregate` in `mappers`).

## Instantiation

```python
from tiferet.domain import Feature, EventFeatureStep, ParameterSpecification, RequestSpecification

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
    params_schema=RequestSpecification(parameters=[
        ParameterSpecification(name='a', type='float'),
        ParameterSpecification(name='b', type='float', required=False, default=0.5),
    ]),
)

# feature.get_step(0).service_id == 'add_number_event'
# feature.params_schema.coerce({'a': '3'}) == {'a': 3.0, 'b': 0.5}
```

## Related Documentation

- [docs/guides/errors.md](../errors.md) — Why `REQUEST_VALIDATION_FAILED` is a `TiferetError` while an `Aggregate` mutation is a `ModelError`
- [docs/guides/domain/core.md](core.md) — `unpack_validation_error`, shared by `RequestSpecification.coerce`'s caller
- [docs/guides/domain/app.md](app.md) — App domain guide
- [docs/guides/domain/error.md](error.md) — Error domain guide
- [docs/guides/domain/di.md](di.md) — DI domain guide
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
