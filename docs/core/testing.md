# Testing Harness

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** September 11, 2026
**Version:** 2.1.0

## Overview

v2.1.0 unit tests name a component with one `TesterObject`, bind it to a `TesterContext` (or a type-specific variant that omits `domain_type`), and drive checks through a `TestSessionContext` that *is* a `RequestContext`. The public decorator is `@use_tester`. It injects `test_ctx` and `session` by parameter name and strips those names from the wrapper signature so pytest does not treat them as fixtures.

This document has two parts:

1. **The v2.1.0 unit-test model** — `TesterObject`, tester contexts, `TestSessionContext`, `@use_tester`, and the eight `type` values.
2. **The leftover `tiferet.testing` harness** — `AggregateTestBase`, `DomainEventTestBase`, and related bases still in the tree until a later freeze deletes them.

Do not delete `tiferet/testing/` in this cycle. Existing mapper and event tests that still subclass those bases are not a migration target here.

**Modules:** `tiferet/domain/tester.py`, `tiferet/contexts/tester.py`, `tiferet/blueprints/tester.py`, `tiferet/assets/tester.py`

## Part 1 — The v2.1.0 unit-test model

### One TesterObject

There is a single domain model, `TesterObject` (`tiferet/domain/tester.py`). It is not subclassed per type. A `Literal` `type` field discriminates behavior:

`domain` | `aggregate` | `transfer_object` | `domain_event` | `service_event` | `generic` | `repo` | `context`

`type` defaults to `'generic'`. Identity is `id` plus `module_path` / `class_name`. Type-specific assertion payloads (description cases, `set_attribute` cases, event kwargs, repo CRUD cases, context registry cases, …) live as optional fields on the same object.

`Verification` is a separate runtime value: one queued check against a session outcome (`predicate`, optional `message`, original `source`). It is not a tester catalog row.

Distillation: [docs/guides/domain/tester.md](../guides/domain/tester.md).

### TesterContext and omitting-`domain_type` variants

`TesterContext` (`tiferet/contexts/tester.py`) is the master context. It declares `domain_type = TesterObject` in its own namespace, so `ContextMeta` maps `TesterObject` → `TesterContext`.

Specialized variants extend `TesterContext` and **omit** `domain_type` from their own namespace, the same way `CliSessionContext` omits it so `AppSession` stays mapped to `AppSessionContext`:

| `type` | Context class | Extra surface |
| --- | --- | --- |
| `domain` | `DomainTesterContext` | `assert_description` |
| `aggregate` | `AggregateTesterContext` | `assert_set_attribute` |
| `transfer_object` | `TransferObjectTesterContext` | `assert_map`, `assert_from_model`, `assert_round_trip` |
| `domain_event` | `DomainEventTesterContext` | `handle`, `mock_dependencies`, `assert_missing_required_params` |
| `service_event` | `ServiceEventTesterContext` | plus `assert_not_found`, `get_service_mock` |
| `generic` | `GenericTesterContext` | `get_target` via `make_target`, `assert_contract` |
| `repo` | `RepoTesterContext` | `make_target(config_file=)`, CRUD asserts |
| `context` | `ContextTesterContext` | `assert_from_domain`, `assert_domain_type`, `assert_for_domain` |

`build_tester_context(tester)` (`tiferet/blueprints/tester.py`) selects the class from `tester.type` and binds with `from_domain`.

Variants must not declare `domain_type = TesterObject` (that would clobber the master registration) and must not declare `Request` or `AppSession` (those registry entries belong to `RequestContext` and `AppSessionContext`).

### TestSessionContext is a RequestContext

`TestSessionContext` extends `RequestContext`. It is not an `AppSessionContext` and is not a mini-App. Like `CliRequestContext`, it omits `domain_type` so `Request` stays mapped to `RequestContext`.

Fluent verbs live on the session, not on `TesterContext`:

```python
session.given(a=1, b=2).verify(3).run(target=_add)
```

- `given(**state)` / `invoke(**params)` merge last-write-wins onto `session.data`.
- They never copy into `tester.sample_data`.
- `verify(assertion, message=None)` queues a `Verification`.
- `run()` overlays `{**sample, **session.data}` without mutating the sample dict, exercises the bound tester, then evaluates the queue.

`run(target=...)` is valid only when `tester.type == 'generic'`. Specialized types raise `ValueError`.

Repo tests construct with `test_ctx.make_target(config_file=...)` and call CRUD asserts on that instance. They do not use `session.run` as a feature pipeline.

Context tests prove `from_domain` binding, own-namespace `domain_type` versus omission, and `BaseContext.for_domain`. They do not steal `Request` or `AppSession` registry entries.

Distillation: [docs/guides/contexts.md](../guides/contexts.md) (registry and overlay) and [docs/guides/blueprints/tester.md](../guides/blueprints/tester.md) (per-type algorithms and `@use_tester`).

### `@use_tester` and `test_ctx` + `session`

```python
from tiferet import use_tester
from tiferet.domain.error import ErrorMessage

@use_tester(type='domain', target_cls=ErrorMessage, sample_data={...})
class TestErrorMessage:

    def test_format(self, test_ctx, session):
        test_ctx.assert_new()
        test_ctx.assert_description()
```

Rules verified against `tiferet/blueprints/tester.py`:

- Decorate a class or a function. On a class, **wrap-all**: every own-namespace member whose signature declares `test_ctx` or `session` is wrapped, including helpers not named `test_*`.
- Injection is **by parameter name**. A method that only declares `session` gets a session; one that only declares `test_ctx` gets the master context.
- The wrapper **strips** `test_ctx` and `session` from `__signature__` so pytest does not look them up as fixtures.
- One master `TesterContext` is built at decoration time and reused. Each call gets a fresh `TestSessionContext`.
- `type` defaults to `'generic'`.
- `target_cls` fills `module_path` / `class_name` when those fields are unset. `aggregate_cls` and `domain_cls` fill the matching import-coordinate fields.
- `id` defaults to `{type}.{class_name}` when omitted.
- The tester blueprint module does not import pytest. Duck-typed fixture objects are unwrapped via `_fixture_function` / `func` / `__wrapped__` without importing pytest.

**Forbidden** (absent from `tiferet/blueprints/tester.py`): `test_case`, `Tester()`, `resolve_tester`, `tester_config`, a `testers:` YAML section, stacking tester seeders on `tiferet/blueprints/core.py`.

`tiferet.blueprints.tester.build_cache` wraps `core.build_cache` and seeds `CORE_DEFAULT_TESTERS` plus the built-in tester session. That wrapping is tester-scoped, not stacked on `core.py`.

Export: `from tiferet import use_tester` and `from tiferet.blueprints import use_tester`.

### Catalog rows versus decorator-supplied fields

`CORE_DEFAULT_TESTERS` (`tiferet/assets/tester.py`) is a cache catalog, not YAML. Rows are built with `create_default_tester_data` (`tiferet/assets/core.py`) and omit `id`; `add_default_testers` re-injects the group-dict key. `assets.__all__` does not export the tester module.

`@use_tester(...)` constructs a `TesterObject` from decorator kwargs at decoration time. Catalog rows and decorator fields are the same model; they are two ways to fill it.

### Artifact comments in tester-decorated tests

```
# *** testers
# ** tester: TestErrorMessage
class TestErrorMessage:
    # * method: test_format
    def test_format(self, test_ctx, session):
        ...
```

Class names stay `Test*`. Standalone functions that are not a decorated harness may still use `# *** tests` / `# ** test:`.

### Per-type algorithms (summary)

| Type | How you exercise it |
| --- | --- |
| `domain` | `assert_new` + `assert_description` |
| `aggregate` | `assert_new` + `assert_set_attribute` |
| `transfer_object` | `assert_map` / `assert_from_model` / `assert_round_trip` (constructs the **aggregate**, not the transfer object, in `make_target`) |
| `domain_event` | `handle` / `assert_missing_required_params` via `DomainEvent.handle` |
| `service_event` | same, plus `assert_not_found` |
| `generic` | `get_target` + `assert_contract`; `session.run(target=fn)` invokes a non-class callable with `session.data` as kwargs |
| `repo` | `make_target(config_file=)` then `assert_exists` / `assert_get` / `assert_list` / `assert_save` / `assert_delete` / `assert_format_dispatch` |
| `context` | `assert_from_domain` / `assert_domain_type` / `assert_for_domain` |

Full walkthroughs: [docs/guides/blueprints/tester.md](../guides/blueprints/tester.md).

## Part 2 — Leftover `tiferet.testing` harness

The `tiferet.testing` package is still in the tree. Mapper and event unit tests that subclass these bases continue to work. This section documents that leftover surface. It is not the v2.1.0 unit-test model, and this document does not ask you to migrate `tests/events` or `tests/mappers`.

**Module:** `tiferet/testing/`

### Exports

- `MapperAssertions` — mixin with shared assertion helpers for comparing domain objects.
- `AggregateTestBase` — base class for Aggregate tests (instantiation, `set_attribute` validation).
- `TransferObjectTestBase` — base class for TransferObject tests (`map`, `from_model`, round-trip).
- `DomainEventTestBase` — base class for DomainEvent tests (auto-mocked dependencies, required param validation).
- `ServiceEventTestBase` — extended base for events with service get/save/delete patterns.
- `register_mapper_hooks` — conftest hook for parametrizing `AggregateTestBase.test_set_attribute`.
- `register_event_hooks` — conftest hook for parametrizing `DomainEventTestBase.test_missing_required_params`.

These modules import pytest. The v2.1.0 tester layer in `tiferet/blueprints/tester.py` and `tiferet/contexts/tester.py` does not.

### Mapper leftover

`AggregateTestBase` expects class attributes `aggregate_cls`, `sample_data`, `equality_fields`, `set_attribute_params` (optional `field_normalizers`) and provides `test_new` / `test_set_attribute`.

`TransferObjectTestBase` expects `transfer_cls`, `aggregate_cls`, `sample_data`, `aggregate_sample_data`, `equality_fields` (optional `field_normalizers`, `map_kwargs`) and provides `test_map` / `test_from_model` / `test_round_trip`.

Parametrization of `test_set_attribute` is driven by `register_mapper_hooks` in `conftest.py`.

### Event leftover

`DomainEventTestBase` expects `event_cls`, `dependencies`, `sample_kwargs`, `required_params`. Use `self.handle(mock_dependencies, **overrides)` to invoke `DomainEvent.handle`. `test_missing_required_params` is parametrized by `register_event_hooks`.

`ServiceEventTestBase` adds `service_attr`, `not_found_error_code`, `not_found_kwargs`, and `test_not_found`.

### Package layout

```
tiferet/testing/
├── __init__.py    — Public exports
├── mappers.py     — MapperAssertions, AggregateTestBase, TransferObjectTestBase
├── domain.py      — DomainEventTestBase, ServiceEventTestBase
└── hooks.py       — register_mapper_hooks, register_event_hooks
```

A later freeze deletes this package. Until then, leave it in place.

## Related Documentation

- [docs/guides/domain/tester.md](../guides/domain/tester.md) — `TesterObject` and `Verification`
- [docs/guides/blueprints/tester.md](../guides/blueprints/tester.md) — `@use_tester` cookbook and per-type algorithms
- [docs/guides/contexts.md](../guides/contexts.md) — tester context registry and `TestSessionContext`
- [docs/guides/blueprints.md](../guides/blueprints.md) — tester-scoped `build_cache`
- [docs/guides/assets.md](../guides/assets.md) — `CORE_DEFAULT_TESTERS` catalog pattern
- [docs/core/code_style.md](code_style.md) — Artifact comments (`# *** testers` / `# ** tester:`)
- [docs/core/mappers.md](mappers.md) — Aggregate and TransferObject conventions
- [docs/core/events.md](events.md) — Domain event patterns
