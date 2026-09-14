# Blueprints – Tester: use_tester, build_cache, build_tester_context

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** September 11, 2026
**Version:** 2.1.0

## Overview

`tiferet/blueprints/tester.py` is the unit-test entrypoint: decorate a class or function with `@use_tester`, get a bound `TesterContext` as `test_ctx` and a fresh `TestSessionContext` as `session`. It is not a mini-App. It does not call `get_app_session` or `compose_session_context`. Tester-scoped `build_cache` wraps `core.build_cache`; it is not stacked on `tiferet/blueprints/core.py`.

Strategy (when to wrap, cache seeding as a pattern): [docs/guides/blueprints.md](../blueprints.md). Domain model: [docs/guides/domain/tester.md](../domain/tester.md). Registry and overlay: [docs/guides/contexts.md](../contexts.md).

**Module:** `tiferet/blueprints/tester.py`
**Vision:** See each blueprint's docstring in `tiferet/blueprints/tester.py` for its value statement.

## Ubiquitous Language

- **Wrap-all** — every own-namespace class member whose signature declares `test_ctx` or `session` is wrapped, including helpers not named `test_*`.
- **Signature strip** — the wrapper drops `test_ctx` and `session` from `__signature__` so pytest does not treat them as fixtures.
- **Master context** — one `TesterContext` built at decoration time and reused across calls.
- **Fresh session** — a new `TestSessionContext` per call.
- **Tester-scoped cache** — `tiferet.blueprints.tester.build_cache`, wrapping `core.build_cache` with `add_default_testers` / `add_default_app_sessions`.

## When should you reach for which one?

| Use case | Best choice | Why it fits |
|---|---|---|
| Write a unit test class | `@use_tester` | Injects `test_ctx` + `session` without pytest fixtures |
| Bind a `TesterObject` you already have | `build_tester_context` | Selects the variant from `tester.type` |
| Need a session for a bound context | `build_test_session` | Constructs `TestSessionContext(tester_ctx, **request_fields)` |
| Seed default testers in a cache | `tester.build_cache` | Wraps `core.build_cache`; do not decorate `core.py` |

## Quick example

```python
from tiferet import use_tester
from tiferet.domain.error import ErrorMessage

@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
    equality_fields=['lang', 'text'],
    description_cases=[('format', (), 'An error occurred.')],
)
class TestErrorMessage:

    def test_new_and_format(self, test_ctx, session):
        test_ctx.assert_new()
        test_ctx.assert_description()
```

## Domain Objects

The blueprints do not define domain classes. They construct `TesterObject` and bind `TesterContext` / `TestSessionContext`.

### use_tester

<a id="use-tester"></a>
**`use_tester(type='generic', target_cls=None, id=None, **fields) -> Callable`**

Decorate a test class or function with a bound tester context and session.

| Kwarg | Role |
|---|---|
| `type` | Tester type. Defaults to `'generic'`. |
| `target_cls` | Optional class/function used to fill `module_path` and `class_name`. |
| `id` | Optional tester id. Derived as `{type}.{class_name}` when omitted. |
| `aggregate_cls` | Popped before construction; fills `aggregate_module_path` / `aggregate_class_name` when unset. |
| `domain_cls` | Popped before construction; fills `domain_module_path` / `domain_class_name` when unset. |
| `**fields` | Remaining `TesterObject` fields (`sample_data`, `equality_fields`, `module_path`, `class_name`, …). |

Injection and wrapping:

- Parameter names `test_ctx` and `session` only. There is no `tester_ctx` injection name.
- Class wrap-all inspects `obj.__dict__` (own namespace), skips `__*` names, duck-types pytest fixtures without importing pytest.
- Function decoration wraps that one callable.

```python
from tiferet.blueprints import use_tester
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject
from tiferet.contexts.request import RequestContext
from tiferet.domain.request import Request

@use_tester(type='aggregate', target_cls=ErrorAggregate, sample_data={...})
class TestErrorAggregate:
    def test_set(self, test_ctx):
        test_ctx.assert_set_attribute()

@use_tester(
    type='transfer_object',
    target_cls=ErrorConfigObject,
    aggregate_cls=ErrorAggregate,
    sample_data={...},
    aggregate_sample_data={...},
)
class TestErrorConfigObject:
    def test_map(self, test_ctx):
        test_ctx.assert_map()

@use_tester(type='context', target_cls=RequestContext, domain_cls=Request)
class TestRequestContext:
    def test_from_domain(self, test_ctx):
        test_ctx.assert_from_domain()
```

**Forbidden:** `test_case`, `Tester()`, `resolve_tester`, `tester_config`, a `testers:` YAML section, `build_app` on this module, importing pytest from `tiferet/blueprints/tester.py`.

### build_cache

<a id="build-cache"></a>
**`build_cache(cache=None) -> CacheContext`**

```python
@add_default_app_sessions(CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(CORE_DEFAULT_TESTERS)
def build_cache(cache=None):
    return core.build_cache(cache)
```

Seeds testers under `TESTER_CACHE_PREFIX = ('app', 'testers')` and the built-in tester session (`id` `tester`) under `APP_SESSION_CACHE_PREFIX`. `core.build_cache` is not decorated with `add_default_testers`.

### build_tester_context

<a id="build-tester-context"></a>
**`build_tester_context(tester) -> TesterContext`**

Maps `tester.type` to the variant class and returns `context_cls.from_domain(tester)`. Unknown types raise `KeyError`.

### build_test_session

<a id="build-test-session"></a>
**`build_test_session(tester_ctx, **request_fields) -> TestSessionContext`**

Constructs `TestSessionContext(tester_ctx, **request_fields)`. Request fields include `session_id` and `data`.

## Per-type algorithms

These are sections on the same `type` discriminator — not new type keys.

### domain

`make_target` constructs `get_target_type()(**sample_data)`. `assert_new` checks instance type and `assert_model_matches` against `expected_data` or `sample_data`. `assert_description` walks `description_cases`; empty lists are no-ops.

### aggregate

Same `make_target` as domain. `assert_set_attribute` mutates a **fresh** target per case (never `self.domain`). A configured error code expects `ModelError.error_code`; otherwise the assigned value is asserted.

### transfer_object

`make_target` constructs the **aggregate** from `aggregate_sample_data` via `get_aggregate_type()`, not the transfer object. `assert_map` validates the transfer object from `sample_data` then `map(**map_kwargs)`. `assert_from_model` / `assert_round_trip` go through `from_model` then `map`.

### domain_event / service_event

`handle` mocks `dependencies` (or uses a supplied mapping), merges kwargs over `sample_kwargs`, and calls `DomainEvent.handle`. `session.run` overlays `session.data` onto `sample_kwargs` (not `sample_data`). `assert_missing_required_params` expects `COMMAND_PARAMETER_REQUIRED`. `ServiceEventTesterContext.assert_not_found` configures `service.get.return_value = None` and expects `not_found_error_code`; it is a no-op when `service_attr` or `not_found_error_code` is unset.

### generic

`make_target` delegates to `get_target()` when `data` is omitted. `assert_contract(target)` locks each `__abstractmethods__` name onto the inspected type; `None` / empty abstract sets are no-ops. `session.run(target=fn)`:

1. Resolves `tester.get_target()` when `target` is omitted.
2. Calls `assert_contract` on the resolved object.
3. Invokes a non-class callable with `session.data` as kwargs; otherwise returns the object.
4. Does not call the feature pipeline.

`run(target=...)` on a non-generic tester raises `ValueError('run(target=...) is only valid when tester type is generic.')`.

Fluent verbs `given` / `invoke` / `verify` / `run` are on `TestSessionContext`, not on `GenericTesterContext`.

### repo

`make_target(config_file, encoding='utf-8')` is required. It uses `config_parameter` when set; otherwise the first non-`self`/`encoding` init parameter. It does not mutate `sample_data`. Exercise CRUD on that instance: `assert_new(config_file)`, `assert_exists(repo)`, `assert_get(repo)`, `assert_list(repo)`, `assert_save(repo, entity=None)`, `assert_delete(repo)`, `assert_format_dispatch(yaml_file, json_file)`. Do not use `session.run` as a feature pipeline.

### context

`make_target` binds via `get_target_type().from_domain(get_domain_type()(**sample_data))`. The `data` argument is unused — context construction does not overlay request data. `assert_from_domain` constructs the domain object from each case's `data` and binds through the **target class** `from_domain`, not the registry. `assert_domain_type` checks own-namespace declaration (`'domain_type' in target_cls.__dict__`) versus omission. `assert_for_domain` asserts `BaseContext.for_domain(domain_cls) is context_cls`; `CONTEXT_NOT_FOUND` propagates.

## Overlay never writes sample_data

`given` / `invoke` update `session.data`. `run` builds `payload = {**sample, **self.data}` and passes that copy to `_exercise_target`. Event types use `sample_kwargs` as `sample`; others use `sample_data`. The bound tester's sample dict is not mutated.

## Error Handling

- Unknown `tester.type` in `build_tester_context` → `KeyError`.
- `run(target=...)` on a specialized type → `ValueError`.
- Assertion helpers raise `AssertionError` (or let `TiferetError` / `ModelError` surface on the event/aggregate paths).
- The tester blueprint does not raise `TiferetError` of its own.

## Testing

The harness tests its own blueprints in `tests/blueprints/test_tester.py` using the same `@use_tester` contour (`# *** testers` / `# ** tester:`). Production `tiferet/blueprints/tester.py` must not import pytest.

## Boundaries

**Inside this domain:** `@use_tester`, tester-scoped `build_cache`, `build_tester_context`, `build_test_session`, and the per-type exercise algorithms those functions dispatch.
**Outside this domain:** `TesterObject` field semantics ([docs/guides/domain/tester.md](../domain/tester.md)); `ContextMeta` registry rules ([docs/guides/contexts.md](../contexts.md)); leftover `tiferet.testing` bases ([docs/core/testing.md](../../core/testing.md)); core `build_app` five-handler wiring; feature E2E via tester sessions.

## Related Documentation

- [docs/guides/blueprints.md](../blueprints.md) — Blueprint strategies, including tester-scoped cache wrapping
- [docs/core/testing.md](../../core/testing.md) — Unit-test model index
- [docs/guides/domain/tester.md](../domain/tester.md) — `TesterObject` and `Verification`
- [docs/guides/contexts.md](../contexts.md) — Tester context registry and `TestSessionContext`
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments
