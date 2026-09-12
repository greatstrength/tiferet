# Domain – Tester: TesterObject and Verification

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** September 11, 2026
**Version:** 2.1.0

## Overview

The tester domain names a specialized component under test and queues checks against a session outcome. One `TesterObject` carries identity, import coordinates, and optional assertion payloads. A `type` discriminator selects which payloads matter; there are no per-type subclass models (`DomainTesterObject`, `RepoTesterObject`, and the rest do not exist). `Verification` is a runtime value for one queued check — not a catalog row and not a tester type.

**Module:** `tiferet/domain/tester.py`
**Vision:** See the `TesterObject` and `Verification` class docstrings in `tiferet/domain/tester.py` for the value statements this guide distills.

## Ubiquitous Language

- **Tester object** — one domain object that names the component under test (`id`, `module_path`, `class_name`) plus optional assertion payloads.
- **Type discriminator** — the `Literal` `type` field (`domain`, `aggregate`, `transfer_object`, `domain_event`, `service_event`, `generic`, `repo`, `context`). Defaults to `generic`.
- **Target** — the live class, instance, callable, or attribute identified by `module_path` / `class_name`.
- **Sample data** — declaration-time constructor payload. Overlay at run time goes on `TestSessionContext.data`, never back into this dict.
- **Catalog row** — a `CORE_DEFAULT_TESTERS` dict built by `create_default_tester_data`, keyed by an id constant, with no `id` inside the value.
- **Decorator-supplied fields** — the same model fields passed to `@use_tester(...)` at decoration time.
- **Verification** — one queued predicate (or literal equality) evaluated against the session outcome.

## Domain Objects

### Verification

A runtime value for one queued check against a session outcome. Built by `TestSessionContext.verify`, not by the tester catalog.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="verification-predicate"></a>`predicate` | `Callable[[Any], bool]` | Yes | — | Evaluated against the session outcome. |
| <a id="verification-message"></a>`message` | `str \| None` | No | `None` | Optional failure label. |
| <a id="verification-source"></a>`source` | `Any` | Yes | — | The original callable or literal the caller supplied. |

Literals are wrapped as equality predicates (`outcome == expected`) before construction. Callables are stored as-is.

### TesterObject

One domain object for every tester type. Unused type-specific fields stay at their defaults.

#### Identity and discriminator

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="testerobject-type"></a>`type` | `Literal[...]` | No | `'generic'` | Discriminator. Rejects unknown keys (there is no `'callable'` type). |
| <a id="testerobject-id"></a>`id` | `str` | Yes | — | Unique tester identifier. Catalog rows omit this; the cache seeder re-injects the group-dict key. `@use_tester` derives `{type}.{class_name}` when omitted. |
| <a id="testerobject-module-path"></a>`module_path` | `str` | Yes | — | Module path of the target. |
| <a id="testerobject-class-name"></a>`class_name` | `str` | Yes | — | Target class, function, or attribute name. |

#### Shared construction and comparison

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="testerobject-sample-data"></a>`sample_data` | `Dict[str, Any]` | No | `{}` | Constructor / comparison sample. |
| <a id="testerobject-expected-data"></a>`expected_data` | `Dict[str, Any] \| None` | No | derived | Defaults to `sample_data` (or `{}`) when absent or falsy, via `_derive_expected_data`. |
| <a id="testerobject-equality-fields"></a>`equality_fields` | `List[str]` | No | `[]` | Field names compared by `assert_model_matches`. |
| <a id="testerobject-field-normalizers"></a>`field_normalizers` | `Dict[str, Callable]` | No | `{}` | Per-field normalizers applied to both sides before comparison. |

#### Domain / aggregate / transfer-object payloads

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="testerobject-description-cases"></a>`description_cases` | `List[Tuple[str, Tuple, Any]]` | No | `[]` | `(name, args, expected)` rows for `assert_description`. |
| <a id="testerobject-set-attribute-params"></a>`set_attribute_params` | `List[Tuple[str, Any, str \| None]]` | No | `[]` | `(attr, value, expect_error_code_or_None)` rows for `assert_set_attribute`. |
| <a id="testerobject-aggregate-module-path"></a>`aggregate_module_path` | `str \| None` | No | `None` | Aggregate module path (transfer-object and repo testers). |
| <a id="testerobject-aggregate-class-name"></a>`aggregate_class_name` | `str \| None` | No | `None` | Aggregate class name. |
| <a id="testerobject-aggregate-sample-data"></a>`aggregate_sample_data` | `Dict[str, Any]` | No | `{}` | Aggregate-format expected data. |
| <a id="testerobject-map-kwargs"></a>`map_kwargs` | `Dict[str, Any]` | No | `{}` | Extra kwargs for `TransferObject.map`. |

#### Event payloads

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="testerobject-dependencies"></a>`dependencies` | `Dict[str, ServiceDependency]` | No | `{}` | Constructor-parameter name → `ServiceDependency`. |
| <a id="testerobject-sample-kwargs"></a>`sample_kwargs` | `Dict[str, Any]` | No | `{}` | Default kwargs for `execute` / `handle`. |
| <a id="testerobject-required-params"></a>`required_params` | `List[str]` | No | `[]` | Names that must raise `COMMAND_PARAMETER_REQUIRED` when missing or empty. |
| <a id="testerobject-service-attr"></a>`service_attr` | `str \| None` | No | `None` | Primary service mock name (service-event). |
| <a id="testerobject-not-found-error-code"></a>`not_found_error_code` | `str \| None` | No | `None` | Error code when the primary service `get` returns `None`. |
| <a id="testerobject-not-found-kwargs"></a>`not_found_kwargs` | `Dict[str, Any]` | No | `{}` | Not-found kwargs; empty means use `sample_kwargs`. |

#### Repo payloads

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="testerobject-config-parameter"></a>`config_parameter` | `str \| None` | No | `None` | Repository constructor keyword for the config file path. |
| <a id="testerobject-exists-cases"></a>`exists_cases` | `List[Tuple[str, bool]]` | No | `[]` | `(id, expected)` rows for `assert_exists`. |
| <a id="testerobject-get-cases"></a>`get_cases` | `List[Tuple[str, Dict \| None]]` | No | `[]` | `(id, expected_data_or_None)` rows for `assert_get`. |
| <a id="testerobject-list-ids"></a>`list_ids` | `List[str]` | No | `[]` | Expected ids from unfiltered `list()`. |
| <a id="testerobject-delete-ids"></a>`delete_ids` | `List[str]` | No | `[]` | Ids to delete, assert missing, then delete again. |

#### Context payloads

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="testerobject-domain-module-path"></a>`domain_module_path` | `str \| None` | No | `None` | Module path of the domain object type under test. |
| <a id="testerobject-domain-class-name"></a>`domain_class_name` | `str \| None` | No | `None` | Domain object class name under test. |
| <a id="testerobject-from-domain-cases"></a>`from_domain_cases` | `List[Dict[str, Any]]` | No | `[]` | Cases for `assert_from_domain`. |
| <a id="testerobject-domain-type-cases"></a>`domain_type_cases` | `List[Dict[str, Any]]` | No | `[]` | Cases for `assert_domain_type` (`declares: True/False`). |
| <a id="testerobject-for-domain-cases"></a>`for_domain_cases` | `List[Dict[str, str]]` | No | `[]` | Cases for `assert_for_domain` (import coordinates for domain and context classes). |

#### Methods

<a id="testerobject-derive-expected-data"></a>
**`_derive_expected_data(data) -> Any`** *(model validator, `mode='before'`)*

When input is a mapping and `expected_data` is absent or falsy, copies the dict and sets `expected_data` to `sample_data` or `{}`. Non-mapping input is left for Pydantic.

<a id="testerobject-get-target-type"></a>
**`get_target_type() -> type`**

Imports `module_path` and returns the named `class_name` attribute as a type. Does not construct an instance.

```python
tester.get_target_type()  # ErrorMessage
```

<a id="testerobject-get-target"></a>
**`get_target() -> Any`**

Imports the named attribute, then:

1. Returns a non-class callable as-is (functions).
2. Returns an ABC class (non-empty `__abstractmethods__`) without instantiating it.
3. Constructs a concrete class from a **copy** of `sample_data`.
4. Returns constants and other attributes as-is.

This is the generic live-object algorithm. Specialized contexts that need an instance usually call `get_target_type()(**payload)` via `make_target` instead.

<a id="testerobject-get-aggregate-type"></a>
**`get_aggregate_type() -> type`**

Imports `aggregate_module_path` / `aggregate_class_name`. Used by transfer-object and repo testers. Passing `None` coordinates raises at import time.

<a id="testerobject-get-domain-type"></a>
**`get_domain_type() -> type`**

Imports `domain_module_path` / `domain_class_name`. Used by context testers. Distinct from `get_target_type` (the context class) and from `TesterContext.domain_type` (always `TesterObject`).

## Catalog Rows versus Decorator-Supplied Fields

Same model, two fill paths.

**Catalog row.** `create_default_tester_data(type, module_path, class_name, sample_data, equality_fields, **variant_kwargs)` in `tiferet/assets/core.py` builds a dict **without** `id`. `CORE_DEFAULT_TESTERS` in `tiferet/assets/tester.py` keys each row by an id constant. `add_default_testers` reconstitutes `TesterObject` instances under `TESTER_CACHE_PREFIX = ('app', 'testers')`, re-injecting `id` from the key. This is a cache declaration, not a `testers:` YAML section. `tiferet/assets/__init__.py` `__all__` does not export the tester module.

**Decorator-supplied fields.** `@use_tester(type='generic', target_cls=..., id=None, **fields)` constructs one `TesterObject` at decoration time. `target_cls` fills `module_path` / `class_name`. `aggregate_cls` / `domain_cls` fill the matching import coordinates when unset. Remaining kwargs are `TesterObject` fields (`sample_data`, `equality_fields`, …).

Do not invent a third path (`tester_config`, YAML, `Tester()` constructor helpers). Those symbols are absent from `tiferet/blueprints/tester.py`.

## No Subclass Models

These names are not in `tiferet/domain/tester.py`: `DomainTesterObject`, `AggregateTesterObject`, `TransferObjectTesterObject`, `DomainEventTesterObject`, `ServiceEventTesterObject`, `RepoTesterObject`, `ContextTesterObject`. Type-specific behavior lives on context variants, selected from `tester.type`.

## Relationships to Other Domains

- **Core:** `TesterObject` and `Verification` extend `DomainObject`. Event testers store `ServiceDependency` values in `dependencies`.
- **Contexts:** `TesterContext.domain_type = TesterObject`. `TestSessionContext` queues `Verification` values. See [docs/guides/contexts.md](../contexts.md).
- **Blueprints:** `@use_tester` and `build_tester_context` consume `TesterObject`. See [docs/guides/blueprints/tester.md](../blueprints/tester.md).
- **Assets:** `CORE_DEFAULT_TESTERS` / `create_default_tester_data`. See [docs/guides/assets.md](../assets.md).
- **Request:** `TestSessionContext` is a `RequestContext`; overlay lives on `session.data`, not on `sample_data`.

## Boundaries

**Inside this domain:** `TesterObject` (one model, type discriminator, import helpers) and `Verification` (queued check value).
**Outside this domain:** tester context variants and fluent `given` / `invoke` / `verify` / `run` ([docs/guides/contexts.md](../contexts.md), [docs/guides/blueprints/tester.md](../blueprints/tester.md)); leftover `tiferet.testing` bases ([docs/core/testing.md](../../core/testing.md)); YAML configuration (there is no `testers:` section); a `tiferet/tester/` package (does not exist); feature E2E through tester sessions.

## Instantiation

```python
from tiferet.domain import TesterObject, Verification

tester = TesterObject(
    type='domain',
    id='domain.ErrorMessage',
    module_path='tiferet.domain.error',
    class_name='ErrorMessage',
    sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
    equality_fields=['lang', 'text'],
)
assert tester.get_target_type().__name__ == 'ErrorMessage'
assert tester.expected_data == tester.sample_data
```

## Related Documentation

- [docs/core/testing.md](../../core/testing.md) — v2.1.0 unit-test model and leftover `tiferet.testing`
- [docs/guides/blueprints/tester.md](../blueprints/tester.md) — `@use_tester` and per-type algorithms
- [docs/guides/contexts.md](../contexts.md) — `TesterContext` registry and `TestSessionContext`
- [docs/guides/assets.md](../assets.md) — `CORE_DEFAULT_TESTERS` catalog pattern
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments
