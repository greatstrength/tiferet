# Domain – Core: DomainObject, ModelError, and ServiceDependency

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Version:** 2.0.0

## Overview

`tiferet/domain/core.py` is the abstract core of the domain layer — the base every other domain object extends, and the vocabulary for describing a model-level defect. It has zero framework imports, making the domain layer's "no framework dependencies" rule literally true. This guide gives `core.py` its own home (distinct from [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md)'s code-style conventions) because it is depended on by every other domain module in this package and by the mappers layer beyond it.

**Module:** `tiferet/domain/core.py`  
**Vision:** See the `DomainObject` and `ModelError` class docstrings in `tiferet/domain/core.py` for their value statements.

## Ubiquitous Language

- **Model defect** — an inconsistency *within* a single model instance (an unknown field or an invalid value), as opposed to a domain outcome or an infrastructural failure.
- **Descriptor** — the serializable, reference-free summary of an offending model instance (`type`, `module`, plus any of `id`/`name`/`key` it declares), produced by `describe_model`.
- **Violation** — one flattened Pydantic validation failure (`field`, `type`, `message`), produced by `unpack_validation_error`.
- **Core service dependency** — the minimal `module_path` + `class_name` + `parameters` shape needed to dynamically import and describe a service implementation.

## Domain Objects

### DomainObject

The base domain model class every other domain object in the framework extends, backed by `pydantic.BaseModel` with a shared `ConfigDict`.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="domainobject-model-config"></a>`model_config` | `ConfigDict` | — | — | `extra='forbid'`, `populate_by_name=True`, `validate_assignment=True`, `arbitrary_types_allowed=True`, `coerce_numbers_to_str=True`. |

No methods — `DomainObject` is pure configuration. Subclasses declare fields with idiomatic `name: T = Field(...)` annotations and are read-only at the base level; mutation logic lives on `Aggregate` subclasses in `tiferet.mappers`. Because `coerce_numbers_to_str=True`, assignment validation is coercing rather than strict — `setattr(obj, 'name', 123)` succeeds as `'123'`.

### ServiceDependency

The core, minimal shape describing "a service implementation, named" — reused wherever the framework needs to dynamically import and describe a service.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="servicedependency-module-path"></a>`module_path` | `str` | Yes | — | The module path for the service dependency. |
| <a id="servicedependency-class-name"></a>`class_name` | `str` | Yes | — | The class name for the service dependency. |
| <a id="servicedependency-parameters"></a>`parameters` | `Dict[str, str]` | No | `{}` | The parameters for the service dependency. |

#### Methods

<a id="servicedependency-get-service-type"></a>
**`get_service_type() -> type`**

Dynamically imports `module_path` and returns the `class_name` attribute from it — the single point where a declared dependency becomes an actual importable Python type.

```python
dep = ServiceDependency(module_path='tiferet.repos.error', class_name='ErrorConfigRepository')
dep.get_service_type()  # <class 'tiferet.repos.error.ErrorConfigRepository'>
```

## The Model Error Protocol

`core.py` owns the vocabulary for describing a defect *within* a single model — distinct from, and unrelated to, the catalogued `TiferetError` vocabulary (see [docs/guides/errors.md](../errors.md) for how the three exception families relate).

### Constants

| Constant | Value | Meaning |
|---|---|---|
| <a id="core-invalid-model-attribute-id"></a>`INVALID_MODEL_ATTRIBUTE_ID` | `'INVALID_MODEL_ATTRIBUTE'` | No such field on the model. |
| <a id="core-invalid-model-value-id"></a>`INVALID_MODEL_VALUE_ID` | `'INVALID_MODEL_VALUE'` | The field exists but the assigned value failed field validation. |
| <a id="core-attribute-not-settable-id"></a>`ATTRIBUTE_NOT_SETTABLE_ID` | `'ATTRIBUTE_NOT_SETTABLE'` | The field exists but is not directly settable; a dedicated mutator owns it. |
| <a id="core-model-identity-fields"></a>`MODEL_IDENTITY_FIELDS` | `('id', 'name', 'key')` | The identity fields `describe_model` reports when a model declares them. |

### Functions

<a id="core-describe-model"></a>
**`describe_model(model: Any) -> Dict[str, Any]`**

Summarizes the offending instance's type identity plus whichever `MODEL_IDENTITY_FIELDS` it declares as primitive values, skipping absent fields and non-primitive values — deliberately holding no reference to the instance and never serializing its whole state.

```python
describe_model(command_aggregate)
# {'type': 'CliCommandAggregate', 'module': 'tiferet.mappers.cli', 'id': 'calc.add', 'name': 'Add Number Command'}
```

<a id="core-unpack-validation-error"></a>
**`unpack_validation_error(error: ValidationError) -> List[Dict[str, Any]]`**

Flattens Pydantic's `error.errors()` into `{'field', 'type', 'message'}` dicts via direct key access (`err['loc']`, `err['type']`, `err['msg']`). Called by `ModelError.raise_for_validation` on the mutation path (`Aggregate.set_attribute`). The request-validation path (`RequestSpecification.validate` in `domain/feature.py`) implements the same flattening shape inline rather than calling this function — see [docs/guides/errors.md](../errors.md) for why the two paths resolve to different exception families despite the shared shape.

### ModelError

A **standalone `Exception`, deliberately not a `TiferetError`**. A model inconsistency is a consumer defect, not a domain outcome — it is never catalogued, never resolved through the `Error` catalog, and never formatted as a `TiferetAPIError`.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="modelerror-error-code"></a>`error_code` | `str` | Yes | — | The model error code. |
| <a id="modelerror-model"></a>`model` | `Dict[str, Any] \| None` | No | `None` | The offending instance's descriptor, as produced by `describe_model`, when supplied. |
| <a id="modelerror-violations"></a>`violations` | `List[Dict[str, Any]] \| None` | No | `None` | Structured field violations, when available. |
| <a id="modelerror-kwargs"></a>`kwargs` | `Dict[str, Any]` | No | `{}` | Additional error context. |

#### Methods

<a id="modelerror-raise-error"></a>
**`raise_error(error_code, message=None, model=None, **kwargs) -> None`** *(classmethod)*

Raises a `ModelError`, describing `model` via `describe_model` when supplied.

<a id="modelerror-raise-for-validation"></a>
**`raise_for_validation(error: ValidationError, message=None, model=None, **kwargs) -> None`** *(classmethod)*

Takes **no** `error_code` — it classifies the failure itself from the flattened violations: `INVALID_MODEL_ATTRIBUTE_ID` when any violation reports Pydantic's `no_such_attribute` type, otherwise `INVALID_MODEL_VALUE_ID`. Falls back to `error.title` for the descriptor when no `model` instance is supplied, and chains the original `ValidationError` as the exception cause.

```python
# tiferet/mappers/core.py — Aggregate.set_attribute
try:
    setattr(self, attribute, value)
except ValidationError as error:
    ModelError.raise_for_validation(error, model=self, attribute=attribute)
```

## Relationships to Other Domains

- **Mappers:** `Aggregate.set_attribute` ([docs/guides/mappers.md](../mappers.md)) wraps `setattr` and converts any resulting `ValidationError` via `raise_for_validation`.
- **Contexts/Feature:** `RequestSpecification.validate` (`domain/feature.py`) flattens Pydantic violations inline (the same shape as `unpack_validation_error`, but not a shared call) and raises `REQUEST_VALIDATION_FAILED` — a catalogued `TiferetError`, unlike `ModelError` itself.
- **Errors:** see [docs/guides/errors.md](../errors.md) for how `ModelError` relates to `TiferetError` and `ServiceError` as the framework's third, unrelated error family.

## Boundaries

**Inside this domain:** the base `DomainObject` configuration every domain object shares, the `ServiceDependency` shape, and the vocabulary for describing a model-level defect (`ModelError`, `describe_model`, `unpack_validation_error`).
**Outside this domain:** mutation logic (owned by `Aggregate` subclasses in `mappers`), catalogued domain outcomes (`TiferetError`, see [docs/guides/errors.md](../errors.md)), and infrastructural failures (`ServiceError`, same guide). `ModelError` is deliberately excluded from all of those — it leaks as an unhandled exception by design.

## Instantiation

```python
from tiferet.domain import DomainObject, ServiceDependency, ModelError

dep = ServiceDependency(module_path='tiferet.repos.error', class_name='ErrorConfigRepository')
service_type = dep.get_service_type()

try:
    setattr(some_aggregate, 'unknown_field', 'x')
except ModelError as e:
    print(e.error_code, e.model)  # 'INVALID_MODEL_ATTRIBUTE', {'type': ..., 'id': ...}
```

## Related Documentation

- [docs/guides/errors.md](../errors.md) — The three unrelated error families (`TiferetError`, `ServiceError`, `ModelError`) and when each applies
- [docs/guides/mappers.md](../mappers.md) — `Aggregate.set_attribute` and the gated-attribute pattern
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model code-style conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
