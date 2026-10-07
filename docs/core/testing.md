# Tester Subdomain

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** October 7, 2026
**Version:** 2.2.0b1

## Overview

A unit test has two faces. In Python, `@use_tester` binds a `TesterObject` and injects `test_ctx` and `session`. In YAML, a test module under `tiferet_tests/` is a document whose only roots are `fixtures`, `tests`, and `testers`. A test, at the root or inside a tester, is a `Test`: a feature in purpose and a test in name. The model fields are `conditions`, `execute`, and `asserts`. The YAML phase key is `assert`.

`TestSessionContext` sees a `TestContext`, not a `FeatureContext`. This page states that. The constructor switch off `TesterContext` is performed by RFP-030, not here, so `@use_tester` is unchanged.

There is no `variables:` root. There is no separate tester vision file. Vision stays the class docstrings.

## The test module

A test module is one YAML document. It has three roots, in this order, and no others:

1. `fixtures` — named samples the tests and testers draw on.
2. `tests` — module-level tests.
3. `testers` — the attribution level. A tester holds `attributes` and `fixtures` and contains `tests`. It is not a fourth root and not a fourth phase.

Each root is a mapping. The key is the grammar snake name (`error_message`, `test_error`), not `Test*`. Omit an empty root. Do not write `{}` for an omitted root. No preamble keys.

A contained test is still the three YAML phases `conditions`, `execute`, `assert`. The model field for the third phase is `asserts`. Naming a root test from a tester does not move that test under the tester. A tester-local fixture is not promoted into the root `fixtures` mapping.

### File root

`tests/<rel>.py` maps to `tiferet_tests/<rel>.yml`, and only for `tests/**/test_*.py`. The extension is `.yml` only. `tests/domain/test_error.py` maps to `tiferet_tests/domain/test_error.yml`.

`conftest.py`, `__init__.py`, and `tests_int/` have no counterpart. Do not write the YAML under `tests/`. Do not delete the Python tests. This page names the tree; it does not create it. On this tip `tests/domain/test_error.py` has only testers, so its counterpart may omit `fixtures` and `tests` until a later RFP writes them.

### The three phases

`Test` (`tiferet/domain/test.py`) extends `Feature`. The model fields are three, in this order: `conditions`, `execute`, `asserts`. There is no fourth phase field and no field named `assert`. `asserts` carries no alias. The YAML phase key stays `assert`. Mapping `assert` onto `asserts` belongs to the transfer object, which this RFP does not add. The tester blueprint compiles those fields into `Feature.steps`; the handlers for those steps are registered by that blueprint. They are not added to the default feature catalog, and they do not decorate `core.build_cache`. RFP-028 names what a phase may contain. This page names the three fields and forbids a fourth.

`TestContext` (`tiferet/contexts/test.py`) extends `FeatureContext` and declares `domain_type = Test` in its own namespace. `Feature` stays mapped to `FeatureContext`: `BaseContext.for_domain(Feature)` is `FeatureContext`.

## Anchors, aliases, and merge

Anchors are load-time. `$r.` and `$fixture.` are runtime.

`&name`, `*name`, and `<<:` are part of the document. `yaml.safe_load` resolves them before a `Test` is built. The blueprint copies an aliased mapping when it builds a fixture or a test, so two tests do not share one sample dict. `$fixture.<name>` names a built fixture. `$r.<key>` names session data, including an `as` result. An anchor cannot do either, because those values do not exist at load time.

A management write preserves anchors. A `safe_dump` round-trip is not compliance: `safe_load` resolves anchors, and `safe_dump` does not emit them.

## Normative document

This is the document law, not a suggestion. `*plain` is the expected string. `$fixture.error_message` is the built instance. It is the law for a file that has all three roots. It is not a claim that proto's Python file already has all three.

```yaml
fixtures:
  error_message: &error_message
    module_path: &error_module tiferet.domain.error
    class_name: ErrorMessage
    attributes: &plain_message
      lang: &lang en_US
      text: &plain An error occurred.
  formatted_error_message:
    <<: *error_message
    attributes:
      lang: *lang
      text: &formatted 'An error occurred: {error}'

tests:
  error_message_format:
    conditions:
      fixtures: [error_message, formatted_error_message]
    execute:
      - target: error_message
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: *plain

testers:
  test_error:
    module_path: *error_module
    class_name: Error
    attributes:
      id: &error_id TEST_ERROR
      name: Test Error
      message: [$fixture.error_message]
    fixtures:
      error_message: *error_message
    tests:
      construction_derives_error_code:
        conditions:
          fixtures: [error_message]
        execute:
          - target: self
            method: new
            as: built
        assert:
          - outcome: built
            fields:
              id: *error_id
              error_code: *error_id
```

The snippet carries one anchor (`&error_message`), one alias (`*error_module`), one merge (`<<: *error_message`), one `$fixture.` reference (`$fixture.error_message`), and one `*alias` used as an expected value (`equals: *plain`).

## What stays absent

These stay absent. Do not restore them:

- `TesterService`
- `TesterConfigRepository`
- `TesterConfigObject`
- `TesterAggregate`
- `resolve_tester`
- tester events
- `Tester()`
- `test_case`

`testers:` is legal only as a root of a `tiferet_tests/**/*.yml` file. It is illegal in application `config.yml`. A `tiferet_tests/` file is not that forbidden section.

There is no AdminApp tester domain. A unit test is not dispatched through `AppSessionContext`. There is no stored callable, no `predicate` key, no `field_normalizers` key, and no YAML Python object tag.

## The Python grammar

The Python comment grammar is unchanged and stays beside the YAML roots. After preamble, a test module declares `# *** fixtures`, `# *** tests`, and `# *** testers`, in that order, and omits an empty group. Testers compose fixtures and tests; they do not replace them.

Under a tester class, members are `# * fixture:` and `# * test:`. `# * test:` is the only place a class member is a test rather than `# * method:`.

`@use_tester` (`tiferet.blueprints.tester`, exported from `tiferet`) injects `test_ctx` and `session` by parameter name and strips those names from the pytest signature. Types: `domain` | `aggregate` | `transfer_object` | `domain_event` | `service_event` | `generic` | `repo` | `context`.

```python
"""Tiferet Error Domain Tests"""

# *** imports

# ** app
from tiferet import use_tester
from tiferet.domain.error import ErrorMessage

# *** testers

# ** tester: test_error_message
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

    # * test: new_and_format
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

Pytest is an optional extra (`pip install tiferet[test]`) and the runner for `tests/` (`testpaths = ["tests", "tests_int"]` in `pyproject.toml`). The `tiferet/` package does not import pytest. `tiferet/testing/` is absent. Do not recreate it.

## Related Documentation

- [code_style.md](code_style.md) — artifact comments, including the test-module grammar
- [contexts.md](contexts.md) — `FeatureContext`, which `TestContext` extends
- [domain.md](domain.md) — `Feature`, which `Test` extends
