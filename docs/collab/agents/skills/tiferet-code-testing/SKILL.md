---
name: tiferet-code-testing
description: Apply Tiferet test harness conventions when writing or extending tests in a Tiferet-family repo. Covers MapperAssertions, AggregateTestBase, TransferObjectTestBase, DomainEventTestBase, ServiceEventTestBase, and conftest hook registration.
---

# Testing Harness Code Style – Tiferet

## When to use
- When adding or modifying tests for Aggregates, TransferObjects (ConfigObjects), or DomainEvents.
- When migrating standalone tests to the shared harnesses in `tiferet.testing`.
- When adding `conftest.py` hook registrations for mapper or event test parametrization.
- Pair with the relevant component skill (`tiferet-code-events`, `tiferet-code-mappers`, etc.) for the production artifact conventions.

## Artifact comment structure

Test modules introduce two testing-specific artifact sections as their primary additions:

```
# *** fixtures                          ← module-level pytest fixtures (testing-specific)
# ** fixture: <snake_case_name>         ← individual fixture

# *** tests                             ← test classes or standalone tests (testing-specific)
# ** test: TestClassName                ← harness test class (PascalCase)
# ** test: <snake_case_name>            ← standalone test function
```

Standard preamble groups follow general styling rules and appear before `fixtures` and `tests`:

```
# *** imports
# ** core / # ** infra / # ** app

# *** constants                         ← shared sample data and normalizers
# ** constant: <snake_case_name>
```

Inside harness test classes:

```
# * attribute: <name>                   ← artifact member: harness class configuration attrs
# * fixture: <name>                     ← artifact member: fixture overrides
# * method: <name>                      ← artifact member: custom test methods
```

Repository integration tests use `# ** test_int: <name>`.

## Key conventions

**Mapper harnesses** (`tiferet.testing`):
- `MapperAssertions` — shared comparison helpers.
- `AggregateTestBase` — required attrs: `aggregate_cls`, `sample_data`, `equality_fields`, `set_attribute_params`; optional `field_normalizers`.
- `TransferObjectTestBase` — required attrs: `transfer_cls`, `aggregate_cls`, `sample_data`, `aggregate_sample_data`, `equality_fields`; optional `field_normalizers`, `map_kwargs`.
- Put reusable dicts and normalizer functions under `# *** constants`.
- For nested collections, define normalizer functions that accept dicts or domain objects and return comparable tuples.

**Event harnesses** (`tiferet.testing`):
- `DomainEventTestBase` — required attrs: `event_cls`, `dependencies`, `sample_kwargs`, `required_params`.
- `ServiceEventTestBase` — adds `service_attr`, `not_found_error_code`, `not_found_kwargs`.
- Override `mock_dependencies` as a `# * fixture:` when service mocks need preconfigured behavior.
- Use `self.handle(mock_dependencies, **overrides)` to invoke `DomainEvent.handle`.

**Hook registration** in `conftest.py`:
- `register_mapper_hooks(metafunc)` — parametrizes `AggregateTestBase.test_set_attribute`.
- `register_event_hooks(metafunc)` — parametrizes `DomainEventTestBase.test_missing_required_params`.

**General:**
- Tests use `pytest`.
- Keep docstrings RST-style and keep one blank line after docstrings.
- Use mocks for event/unit tests; use real temp files (`tmp_path`) for repository integration tests.

## Example

```python
"""Tiferet Error Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.events import a
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject
from tiferet.testing import AggregateTestBase, TransferObjectTestBase

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

# ** constant: message_tuple
def MESSAGE_TUPLE(message):
    '''
    Normalize an error message dict or domain object into a comparable tuple.

    :param message: The message dict or domain object.
    :type message: dict | object
    :return: A comparable message tuple.
    :rtype: tuple
    '''

    # Normalize dict input.
    if isinstance(message, dict):
        return (message['lang'], message['text'])

    # Normalize domain object input.
    return (message.lang, message.text)

# ** constant: field_normalizers
FIELD_NORMALIZERS = {
    'message': lambda messages: tuple(
        sorted(MESSAGE_TUPLE(m) for m in (messages or []))
    ),
}

# *** tests

# ** test: TestErrorAggregate
class TestErrorAggregate(AggregateTestBase):
    '''
    Tests for ErrorAggregate using the mapper harness.
    '''

    # * attribute: aggregate_cls
    aggregate_cls = ErrorAggregate

    # * attribute: sample_data
    sample_data = ERROR_SAMPLE_DATA

    # * attribute: equality_fields
    equality_fields = EQUALITY_FIELDS

    # * attribute: field_normalizers
    field_normalizers = FIELD_NORMALIZERS

    # * attribute: set_attribute_params
    set_attribute_params = [
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: test_rename
    def test_rename(self, aggregate):
        '''
        Test the domain-specific rename mutation.

        :param aggregate: The harness-created ErrorAggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Rename the aggregate.
        aggregate.rename('Renamed Error')

        # Assert the mutation was applied.
        assert aggregate.name == 'Renamed Error'


# ** test: TestErrorConfigObject
class TestErrorConfigObject(TransferObjectTestBase):
    '''
    Tests for ErrorConfigObject using the transfer object harness.
    '''

    # * attribute: transfer_cls
    transfer_cls = ErrorConfigObject

    # * attribute: aggregate_cls
    aggregate_cls = ErrorAggregate

    # * attribute: sample_data
    sample_data = ERROR_SAMPLE_DATA

    # * attribute: aggregate_sample_data
    aggregate_sample_data = ERROR_SAMPLE_DATA

    # * attribute: equality_fields
    equality_fields = EQUALITY_FIELDS

    # * attribute: field_normalizers
    field_normalizers = FIELD_NORMALIZERS
```

`conftest.py` hook registration:

```python
# *** imports

# ** app
from tiferet.testing import register_mapper_hooks, register_event_hooks

# *** functions

# ** function: pytest_generate_tests
def pytest_generate_tests(metafunc):
    '''
    Register Tiferet harness parametrization hooks.

    :param metafunc: The pytest metafunc object.
    :type metafunc: object
    '''

    # Register mapper harness parametrization.
    register_mapper_hooks(metafunc)

    # Register domain event harness parametrization.
    register_event_hooks(metafunc)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/testing.md
