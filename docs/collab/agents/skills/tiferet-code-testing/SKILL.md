---
name: tiferet-code-testing
description: >-
  Apply Tiferet tester-subdomain conventions when writing or extending tests
  in a Tiferet-family repo. Covers one TesterObject, @use_tester /
  build_tester_context, Tester() / TestSessionContext, omitting-domain_type
  variant contexts, and test-module artifact grammar.
---

# Tester Subdomain Code Style – Tiferet

## When to use
- When adding or modifying tests for domain objects, Aggregates, TransferObjects (ConfigObjects), or DomainEvents.
- When using `@use_tester` / `build_tester_context` or fluent `Tester()` / `@test_case`.
- Pair with the relevant component skill (`tiferet-code-events`, `tiferet-code-mappers`, etc.) for the production artifact conventions.

## Artifact comment structure

After preamble groups (`imports` / `constants` / `functions` / `classes` — standalone helpers only, never a tester), test modules declare:

```
# *** fixtures                          ← module-level pytest fixtures
# ** fixture: <snake_name>              ← matching def <snake_name>

# *** tests                             ← module-level test functions only
# ** test: <snake_name>                 ← matching def test_<snake_name>

# *** testers                           ← tester classes last
# ** tester: <snake_name>               ← class <Pascal>Tester (suffix Tester, not prefix Test)
```

Inside a tester class:

```
# * fixture: <name>                     ← pytest fixture method
# * test: <name>                        ← pytest test method (never # * method:)
```

Class-form `@use_tester` injects `test_ctx` into any member that lists it, including `# * fixture:` methods.

## Key conventions

**Contour.** Tester is `tester.py` in packages that have it (`assets`, `domain`, `mappers`, `interfaces`, `repos`, `events`, `contexts`, `blueprints`). One `TesterObject`; `type` is `domain` / `aggregate` / `transfer_object` / `domain_event` / `service_event`. One `TesterConfigObject`. The former `tiferet/testing/` package was retired. Do not invent `tiferet/tester/`, `utils/tester.py`, or `di/tester.py`.

**Import law** (cite `tiferet-code-architecture`): contexts import assets/domain/siblings/events only; mappers import domain only; blueprints reach domain via contexts; assets and domain import no framework package. No pytest class generation or `pytest11` in `contexts/tester.py`.

**Two surfaces, not collapsed:**
- `@use_tester` / `build_tester_context` → bound variant context as `test_ctx`. `TesterContext.domain_type = TesterObject`. Variants omit `domain_type`: `DomainTesterContext`, `AggregateTesterContext`, `TransferObjectTesterContext`, `DomainEventTesterContext`, `ServiceEventTesterContext`. Call ordinary methods (`assert_new`, `assert_set_attribute`, `assert_map`, `handle`, …).
- `Tester()` / `@test_case` → `TestSessionContext` (`given` / `invoke` / `verify` / `run`), still an `AppSessionContext` subclass. Feature, event, and harness errors are raw `TiferetError`. Do not document feature-path `TiferetAPIError` or session-as-request as current. `@test_case` injects `tester_ctx`.

**Event `dependencies`:** `ServiceDependency` dicts (`module_path`, `class_name`).

**Pytest** is an optional extra and the runner for `tests/`. Those files may import pytest and use `@use_tester`. Fixture injection is by parameter name; no Tiferet `use_fixture` decorator. Class-form `@use_tester` injects `test_ctx` into members that list it, including fixtures.

**General:**
- Keep docstrings RST-style and keep one blank line after docstrings.
- Use mocks for event/unit tests; use real temp files (`tmp_path`) for repository integration tests.
- **Docstrings & guides:** Tester has no `docs/guides/` entry of its own — when a test module's tester usage is worth distilling, add it to the guide of the component under test (per `tiferet-guide-docs`).

## Example

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
        '''
        Verify construction against declared expected data.

        :param test_ctx: Bound AggregateTesterContext.
        :type test_ctx: AggregateTesterContext
        '''

        test_ctx.assert_new()

    # * test: rename
    def test_rename(self, test_ctx):
        '''
        Test the domain-specific rename mutation.

        :param test_ctx: Bound AggregateTesterContext.
        :type test_ctx: AggregateTesterContext
        '''

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
```

Event testers use `type='domain_event'` or `type='service_event'` with:

```python
dependencies={
    'error_service': {
        'module_path': 'tiferet.interfaces',
        'class_name': 'ErrorService',
    },
}
```

Call `test_ctx.handle(mock_dependencies)` and `test_ctx.assert_missing_required_params()`. Service-event testers also set `service_attr` / `not_found_error_code` and may call `test_ctx.assert_not_found()`.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/testing.md
