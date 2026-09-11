---
name: tiferet-code-testing
description: Apply Tiferet test harness conventions when writing or extending tests in a Tiferet-family repo. Covers @use_tester, TesterObject types, test_ctx+session injection, and the leftover tiferet.testing bases.
---

# Testing Harness Code Style – Tiferet

## When to use
- When adding or modifying unit tests for a named Tiferet component.
- Pair with the component skill for the production artifact (`tiferet-code-domain`, `tiferet-code-events`, …).
- Do **not** migrate leftover `tests/events` or `tests/mappers` harness subclasses in this cycle.

## Artifact comment structure

```
# *** testers
# ** tester: TestClassName          ← PascalCase; class name stays Test*
# * method: test_<name>
```

Standalone functions (not a decorated harness) may still use `# *** tests` / `# ** test:`. Preamble: `# *** imports`, `# *** constants`.

## Key conventions

**v2.1.0 model:** one `TesterObject`; `TesterContext` (`domain_type=TesterObject`) plus omitting-`domain_type` variants; `TestSessionContext` is a `RequestContext`. Overlay given-state onto `session.data`, never `sample_data`.

**`@use_tester`** (`from tiferet import use_tester`):
- Wrap-all by parameter name (`test_ctx`, `session`). Signature strip so pytest does not treat them as fixtures.
- `type` defaults to `'generic'`. Types: `domain` | `aggregate` | `transfer_object` | `domain_event` | `service_event` | `generic` | `repo` | `context`.
- `target_cls` fills `module_path` / `class_name`. `aggregate_cls` / `domain_cls` fill matching import coordinates.
- Do not import pytest from `tiferet/`. Do not use `test_case`, `Tester()`, `resolve_tester`, `tester_config`, or a `testers:` YAML section.
- Tester-scoped `build_cache` wraps `core.build_cache`. Do not stack testers on `core.py`.

**Per type (summary):** specialized `assert_*` / `handle`; generic `get_target` + `assert_contract` + `session.run(target=fn)`; repo `make_target(config_file=)` CRUD (not `session.run`); context `from_domain` / own-namespace `domain_type` / `for_domain`.

**Leftover:** `tiferet.testing` (`AggregateTestBase`, `DomainEventTestBase`, …) still exists until a later freeze. Leave it. Do not delete `tiferet/testing/`.

## Example

```python
"""Tiferet Error Domain Tests"""

# *** imports

# ** app
from tiferet import use_tester
from tiferet.domain.error import ErrorMessage

# *** testers

# ** tester: TestErrorMessage
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
    equality_fields=['lang', 'text'],
    description_cases=[('format', (), 'An error occurred.')],
)
class TestErrorMessage:
    '''
    Tests for ErrorMessage.
    '''

    # * method: test_new_and_format
    def test_new_and_format(self, test_ctx, session):
        '''
        Construct from sample data and assert description cases.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Assert construction and description methods.
        test_ctx.assert_new()
        test_ctx.assert_description()
```

## Docstrings & guides

- Distillation: `docs/core/testing.md`, `docs/guides/domain/tester.md`, `docs/guides/blueprints/tester.md`.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/testing.md
