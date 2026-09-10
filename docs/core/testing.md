# Tester Subdomain

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** September 10, 2026
**Version:** 2.1.0

## Overview

Tester is a **core subdomain contour**, not an eleventh package. One `TesterObject` describes a constructible framework component and the assertions used to verify it. Variant contexts bind that object and expose ordinary assertion methods. Two public surfaces stay distinct:

- **Component testers:** `build_tester_context` / `@use_tester` inject a bound variant context as `test_ctx`.
- **Fluent session:** `Tester()` / `@test_case` compose a `TestSessionContext` (`given` / `invoke` / `verify` / `run`).

The former `tiferet/testing/` package was retired. There is no `tiferet/tester/` package, no empty `utils/tester.py` or `di/tester.py`, and pytest is not a Tiferet package.

## Contour

`tester.py` exists only in packages that actually have it:

- `tiferet/assets/tester.py` — default tester ids, data, sessions, and catalogs
- `tiferet/domain/tester.py` — `TesterObject`, `Verification`
- `tiferet/mappers/tester.py` — `TesterAggregate`, one `TesterConfigObject`
- `tiferet/interfaces/tester.py` — `TesterService`
- `tiferet/repos/tester.py` — `TesterConfigRepository`
- `tiferet/events/tester.py` — `TesterEvent` plus add/get/list/update/remove
- `tiferet/contexts/tester.py` — `TesterContext` and omitting-`domain_type` variants; `TestSessionContext`
- `tiferet/blueprints/tester.py` — `Tester` / `build_tester_context` / `@use_tester` / `@test_case`

Do not invent modules in `utils` or `di`.

## One TesterObject

`TesterObject` (`tiferet/domain/tester.py`) is the only tester domain model. `type` is the component discriminator:

- `domain`
- `aggregate`
- `transfer_object`
- `domain_event`
- `service_event`

Shared fields: `id`, `module_path`, `class_name`, `sample_data`, `expected_data` (defaults to `sample_data` when omitted), `equality_fields`, `field_normalizers`.

Variant fields live on the same model:

- **domain** — `description_cases`
- **aggregate** — `set_attribute_params`
- **transfer_object** — `aggregate_module_path`, `aggregate_class_name`, `aggregate_sample_data`, `map_kwargs`
- **domain_event / service_event** — `dependencies`, `sample_kwargs`, `required_params`
- **service_event** — also `service_attr`, `not_found_error_code`, `not_found_kwargs`

There is one configuration transfer object: `TesterConfigObject`. Configuration is a flat `testers:` map keyed by tester id.

### Event `dependencies` shape

Event testers declare constructor mocks as `ServiceDependency` dicts (`module_path`, `class_name`, optional `parameters`):

```yaml
testers:
  service_event.GetError:
    type: service_event
    module_path: tiferet.events.error
    class_name: GetError
    dependencies:
      error_service:
        module_path: tiferet.interfaces
        class_name: ErrorService
    sample_kwargs:
      id: TEST_ERROR
    required_params: []
    service_attr: error_service
    not_found_error_code: ERROR_NOT_FOUND
```

`@use_tester(..., dependencies={...})` uses the same dict shape. `DomainEventTesterContext.mock_dependencies()` builds `unittest.mock.Mock(spec=dependency.get_service_type())` for each entry.

## Import Law

Cite `tiferet-code-architecture`. Every `*/tester.py` follows its package's `# ** app` import rule:

- **assets / domain** — no framework package.
- **mappers** — `domain` only.
- **contexts** — `assets`, `domain`, sibling contexts, and `events` only.
- **blueprints** — reach domain objects via `contexts` (for example `TesterObject` re-exported from `contexts.tester`).

`contexts/tester.py` does not import pytest, does not generate test classes, and is not a `pytest11` plugin. `unittest.mock` is stdlib and is used only to build declared event-dependency specs.

## Two Public Surfaces

Do not collapse these APIs. `@use_tester` injects `test_ctx`. `@test_case` injects `tester_ctx`.

### Component testers — `build_tester_context` / `@use_tester`

`TesterContext` registers `domain_type = TesterObject`. Variant subclasses **omit** `domain_type` (the `CliSessionContext` analog) so `ContextMeta` keeps mapping `TesterObject` to `TesterContext`:

- `domain` → `DomainTesterContext` — `assert_new`, `assert_description`
- `aggregate` → `AggregateTesterContext` — `assert_new`, `assert_set_attribute`
- `transfer_object` → `TransferObjectTesterContext` — `assert_map`, `assert_from_model`, `assert_round_trip`
- `domain_event` → `DomainEventTesterContext` — `handle`, `assert_missing_required_params`
- `service_event` → `ServiceEventTesterContext` — `handle`, `assert_missing_required_params`, `assert_not_found`

Those methods are ordinary `# * method:` members on the context, not generated `test_*` methods. Tests call them on the injected `test_ctx`.

`build_tester_context(tester)` selects the variant from `tester.type` and returns `context_cls.from_domain(tester)`.

`@use_tester` constructs one `TesterObject` at decoration time (`target_cls` supplies `module_path` / `class_name`; `aggregate_cls` supplies aggregate coordinates; `id` defaults to `{type}.{class_name}`) and injects a fresh bound context as `test_ctx` into each `test_*` callable that declares that parameter. Wrapping is **test-method-only** today: member fixtures do not receive `test_ctx` unless they are `test_*` methods.

```python
from tiferet.blueprints.tester import use_tester
from tiferet.mappers.error import ErrorAggregate

@use_tester(
    type='aggregate',
    target_cls=ErrorAggregate,
    sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
    equality_fields=['id', 'name', 'error_code'],
    set_attribute_params=[
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', 'INVALID_MODEL_ATTRIBUTE'),
    ],
)
class ErrorAggregateTester:

    # * test: new
    def test_new(self, test_ctx):
        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        test_ctx.assert_set_attribute()
```

Event tests call `test_ctx.handle(mock_dependencies, **overrides)`, which delegates to `DomainEvent.handle` with `sample_kwargs` merged under caller overrides. A `# * fixture: mock_dependencies` may pre-configure the primary service; `assert_not_found` reconfigures `service.get.return_value = None` on its own mocks.

### Fluent session — `Tester()` / `@test_case`

`Tester` is the public alias of `tiferet.blueprints.tester.build_app`. It returns a `TestSessionContext`, which **still extends** `AppSessionContext`.

```python
from tiferet import Tester, test_case

result = (
    Tester()
    .given(value=1)
    .invoke(feature_id='test.empty')
    .verify(None)
    .run()
)

@test_case(value=1)
def test_empty_feature(tester_ctx):
    tester_ctx.invoke(feature_id='test.empty').verify(None).run()
```

- `given(preset_id=None, **data)` merges cache-seeded presets then literal state.
- `invoke(feature_id=..., event=...)` selects **exactly one** dispatch target.
- `verify(assertion, message=None)` queues a deferred predicate or literal.
- `run()` dispatches once, evaluates queued verifications, and clears the chain.

`@test_case(**given)` constructs `Tester()` (optional `interface_id`), seeds decoration-time given-state, and injects that session as `tester_ctx` without dispatching.

Fluent `run()` does **not** go through `AppSessionContext.run()`. Feature dispatch, event dispatch, and harness errors (`COMMAND_PARAMETER_REQUIRED`, `TEST_PRESET_NOT_FOUND`) raise raw `TiferetError`. Do not treat feature-path `TiferetAPIError` or `TestSessionContext` as a `RequestContext` as current API.

## Pytest

Pytest is an optional extra (`pip install tiferet[test]`) and the runner for `tests/` (`testpaths = ["tests", "tests_int"]` in `pyproject.toml`). Files under `tests/` may import pytest and use `@use_tester`. The `tiferet/` package does not import pytest.

Fixture wiring is pytest parameter-name injection. There is no Tiferet `use_fixture` decorator. A `# * test:` may list any `# *** fixtures` name, any same-class `# * fixture:` name, and `test_ctx` (`@use_tester` still injects `test_ctx` into test methods).

## Test-Module Artifact Grammar

After `# *** imports` / `# *** constants` / `# *** functions` / `# *** classes` (standalone helpers only — never a tester), test modules declare:

1. `# *** fixtures` — module-level pytest fixtures. Sections: `# ** fixture: <snake_name>` matching `def <snake_name>`.
2. `# *** tests` — module-level test **functions** only. Sections: `# ** test: <snake_name>` matching `def test_<snake_name>` (or `def <snake_name>` as shipped).
3. `# *** testers` — tester classes, last because they compose fixtures and tests. Sections: `# ** tester: <snake_name>` matching `class <Pascal>Tester` (suffix `Tester`, **not** prefix `Test`). Example: `# ** tester: error_aggregate_tester` → `class ErrorAggregateTester`.

Under a tester class, members are:

- `# * fixture: <name>` — a pytest fixture method; may request group-level fixtures by parameter name.
- `# * test: <name>` — a pytest test method. This is the **only** place a class member is a test rather than `# * method:`.

Bulk remediating the existing `tests/` tree to this grammar is not required of this documentation pass. Examples in this guide are written in the new shape; live files may still use `class TestFoo` / `# ** test:` classes until a later pass.

```python
"""Tiferet Error Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject
from tiferet.blueprints.tester import use_tester

# *** constants

# ** constant: error_sample_data
ERROR_SAMPLE_DATA = {
    'id': 'TEST_ERROR',
    'name': 'Test Error',
    'error_code': 'TEST_ERROR',
    'message': [{'lang': 'en_US', 'text': 'Test error message.'}],
}

# ** constant: equality_fields
EQUALITY_FIELDS = ['id', 'name', 'error_code']

# *** testers

# ** tester: error_aggregate_tester
@use_tester(
    type='aggregate',
    target_cls=ErrorAggregate,
    sample_data=ERROR_SAMPLE_DATA,
    equality_fields=EQUALITY_FIELDS,
    set_attribute_params=[
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
class ErrorAggregateTester:
    '''Bound aggregate tester for ErrorAggregate.'''

    # * test: new
    def test_new(self, test_ctx):
        '''Verify construction against declared expected data.'''

        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''Verify declared set_attribute cases.'''

        test_ctx.assert_set_attribute()

    # * test: rename
    def test_rename(self, test_ctx):
        '''Test the domain-specific rename mutation.'''

        aggregate = test_ctx.make_target()
        aggregate.rename('Renamed Error')
        assert aggregate.name == 'Renamed Error'


# ** tester: error_config_object_tester
@use_tester(
    type='transfer_object',
    target_cls=ErrorConfigObject,
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_SAMPLE_DATA,
    aggregate_sample_data=ERROR_SAMPLE_DATA,
    equality_fields=EQUALITY_FIELDS,
)
class ErrorConfigObjectTester:
    '''Bound transfer-object tester for ErrorConfigObject.'''

    # * test: map
    def test_map(self, test_ctx):
        test_ctx.assert_map()

    # * test: from_model
    def test_from_model(self, test_ctx):
        test_ctx.assert_from_model()

    # * test: round_trip
    def test_round_trip(self, test_ctx):
        test_ctx.assert_round_trip()
```

Event testers follow the same groups. Use `type='domain_event'` or `type='service_event'` and the YAML `dependencies` shape above. Call `test_ctx.handle(...)` / `test_ctx.assert_missing_required_params()` / `test_ctx.assert_not_found()`. Standalone `# ** test:` functions that call `DomainEvent.handle` directly remain valid for cases that do not need a bound tester.

## Related Documentation

- [code_style.md](code_style.md) — artifact comments, including test-module grammar
- [mappers.md](mappers.md) — Aggregate and TransferObject conventions
- [events.md](events.md) — domain event patterns
- [tiferet-code-architecture](../collab/agents/skills/tiferet-code-architecture/SKILL.md) — layer import law
- [tiferet-code-testing](../collab/agents/skills/tiferet-code-testing/SKILL.md) — skill distillation of this guide
