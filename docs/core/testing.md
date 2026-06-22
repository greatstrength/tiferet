# Testing Harness

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 22, 2026  
**Version:** 2.0.0

## Overview

The `tiferet.testing` package provides reusable base classes and hooks for testing Tiferet components. Instead of writing boilerplate for each Aggregate, TransferObject, or DomainEvent test, subclass the appropriate base and declare class attributes — the harness handles instantiation, assertion, parametrization, and common test patterns automatically.

**Module:** `tiferet/testing/`

### Exports

- `MapperAssertions` — Mixin with shared assertion helpers for comparing domain objects.
- `AggregateTestBase` — Base class for Aggregate tests (instantiation, `set_attribute` validation).
- `TransferObjectTestBase` — Base class for TransferObject tests (`map`, `from_model`, round-trip).
- `DomainEventTestBase` — Base class for DomainEvent tests (auto-mocked dependencies, required param validation).
- `ServiceEventTestBase` — Extended base for events with service get/save/delete patterns.
- `register_mapper_hooks` — Conftest hook for parametrizing `AggregateTestBase.test_set_attribute`.
- `register_event_hooks` — Conftest hook for parametrizing `DomainEventTestBase.test_missing_required_params`.

## Mapper Test Harness

### MapperAssertions

Internal mixin providing two assertion helpers. Both `AggregateTestBase` and `TransferObjectTestBase` inherit from it.

**`assert_model_matches(model, sample, equality_fields, field_normalizers)`**

Compares model attributes against a sample dict field-by-field. Per-field normalizers allow custom comparison logic for complex types (e.g., sorting nested lists into tuples for order-independent comparison).

```python
# Normalizer example: compare nested service lists as sorted tuples
FIELD_NORMALIZERS = {
    'services': lambda svcs: tuple(sorted(
        (s.service_id, s.module_path) for s in (svcs or [])
    )),
}
```

**`assert_nested_list_matches(actual_list, expected_list, key_field, compare_fields)`**

Compares lists of domain objects by a key field (e.g., `service_id`, `flag`). Useful for verifying nested collections through round-trips.

### AggregateTestBase

Base class for testing Aggregate components. Declare class attributes; the harness provides `test_new` and `test_set_attribute` automatically.

**Required class attributes:**

- `aggregate_cls` — The Aggregate class under test.
- `sample_data` — Dict of aggregate-format sample data.
- `equality_fields` — List of field names to compare.
- `set_attribute_params` — List of `(attr, value, expect_error_code | None)` tuples.

**Optional class attributes:**

- `field_normalizers` — Dict mapping field names to normalizer callables.

**Inherited tests:**

- `test_new` — Verifies direct constructor instantiation and field values against `sample_data`.
- `test_set_attribute` — Parametrized test for valid and invalid attribute mutations. Parametrization is driven by `register_mapper_hooks` in `conftest.py`.

**Override hook:**

- `make_aggregate(data=None)` — Override when the aggregate has a custom constructor signature.

**Example:**

```python
from tiferet.events import a
from tiferet.mappers.error import ErrorAggregate
from tiferet.testing import AggregateTestBase

ERROR_SAMPLE_DATA = {
    'id': 'TEST_ERROR',
    'name': 'TEST_ERROR',
    'error_code': 'TEST_ERROR',
    'message': [{'lang': 'en', 'text': 'Test error message.'}],
}

class TestErrorAggregate(AggregateTestBase):
    aggregate_cls = ErrorAggregate
    sample_data = ERROR_SAMPLE_DATA
    equality_fields = ['id', 'name', 'error_code']

    set_attribute_params = [
        ('name', 'Updated Error', None),                                  # valid
        ('invalid_attribute', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),  # invalid
    ]

    # Domain-specific tests beyond the harness:
    def test_rename(self, aggregate):
        aggregate.rename('Renamed Error')
        assert aggregate.name == 'Renamed Error'
```

### TransferObjectTestBase

Base class for testing TransferObject components. Provides `test_map`, `test_from_model`, and `test_round_trip` automatically.

**Required class attributes:**

- `transfer_cls` — The TransferObject class under test.
- `aggregate_cls` — The target Aggregate class.
- `sample_data` — YAML-format sample data (as it appears in configuration).
- `aggregate_sample_data` — Aggregate-format expected data (with defaults filled in).
- `equality_fields` — List of field names to compare.

**Optional class attributes:**

- `field_normalizers` — Per-field normalizer callables.
- `map_kwargs` — Extra kwargs to pass to `.map()`.

**Inherited tests:**

- `test_map` — Verifies `model_validate()` → `map()` produces a valid aggregate matching `aggregate_sample_data`.
- `test_from_model` — Verifies aggregate → TransferObject conversion via `from_model()`.
- `test_round_trip` — Verifies aggregate → TransferObject → aggregate preserves data.

**Override hook:**

- `make_aggregate(data=None)` — Same purpose as `AggregateTestBase`.

**Example:**

```python
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject
from tiferet.testing import TransferObjectTestBase

class TestErrorConfigObject(TransferObjectTestBase):
    transfer_cls = ErrorConfigObject
    aggregate_cls = ErrorAggregate
    sample_data = ERROR_SAMPLE_DATA
    aggregate_sample_data = ERROR_SAMPLE_DATA
    equality_fields = ['id', 'name', 'error_code']

    # Domain-specific tests beyond the harness:
    def test_map_messages(self):
        yaml_obj = ErrorConfigObject.model_validate(self.sample_data)
        mapped = yaml_obj.map()
        assert len(mapped.message) == 1
```

## Domain Event Test Harness

### DomainEventTestBase

Base class for testing DomainEvent components. Auto-mocks dependencies and provides parametrized required-parameter validation.

**Required class attributes:**

- `event_cls` — The DomainEvent class under test.
- `dependencies` — Dict mapping dependency name to its type (for auto-mocking via `mock.Mock(spec=...)`).
- `sample_kwargs` — Default kwargs for a successful `execute()` call.
- `required_params` — List of required parameter names (for auto-parametrized validation tests).

**Inherited fixture:**

- `mock_dependencies` — Auto-creates `mock.Mock(spec=dep_type)` for each entry in `dependencies`. Override this fixture when you need pre-configured mock behavior (e.g., `service.exists.return_value = False`).

**Inherited method:**

- `handle(mock_dependencies, **kwargs)` — Invokes the event via `DomainEvent.handle` with `sample_kwargs` merged with any overrides.

**Inherited test:**

- `test_missing_required_params` — Parametrized test that sets each `required_params` entry to `None` and asserts `COMMAND_PARAMETER_REQUIRED` is raised. Parametrization is driven by `register_event_hooks` in `conftest.py`.

**Example:**

```python
from unittest import mock
import pytest
from tiferet.events.error import AddError
from tiferet.interfaces import ErrorService
from tiferet.testing import DomainEventTestBase

class TestAddError(DomainEventTestBase):
    event_cls = AddError
    dependencies = {'error_service': ErrorService}
    sample_kwargs = dict(
        id='NEW_ERROR',
        name='New Error',
        message='This is a new error message.',
        lang='en_US',
        additional_messages=[],
    )
    required_params = ['id', 'name', 'message']

    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''Override to pre-configure exists to return False.'''
        service = mock.Mock(spec=ErrorService)
        service.exists.return_value = False
        return {'error_service': service}

    def test_success(self, mock_dependencies):
        result = self.handle(mock_dependencies)
        assert result.id == 'NEW_ERROR'
        mock_dependencies['error_service'].save.assert_called_once()
```

### ServiceEventTestBase

Extended base for events that depend on a single service with get/save/delete patterns. Inherits everything from `DomainEventTestBase` and adds a `test_not_found` test.

**Additional class attributes:**

- `service_attr` — The dependency name (e.g., `'error_service'`).
- `not_found_error_code` — Error code raised when the service returns `None`.
- `not_found_kwargs` — Kwargs that trigger the not-found path (defaults to `sample_kwargs`).

**Additional method:**

- `get_service_mock(mock_dependencies)` — Returns the mock for the primary service by `service_attr` name.

**Additional test:**

- `test_not_found` — Configures `service.get.return_value = None` and asserts the correct not-found error code is raised.

## Conftest Hooks

The testing harness uses pytest's `pytest_generate_tests` hook to dynamically parametrize certain tests. Two hook registration functions are provided — call them from your test suite's `conftest.py`.

### register_mapper_hooks

Parametrizes `test_set_attribute` for all `AggregateTestBase` subclasses using their `set_attribute_params` class attribute.

**Usage in `conftest.py`:**

```python
from tiferet.testing.hooks import register_mapper_hooks

def pytest_generate_tests(metafunc):
    register_mapper_hooks(metafunc)
```

### register_event_hooks

Parametrizes `test_missing_required_params` for all `DomainEventTestBase` subclasses using their `required_params` class attribute.

**Usage in `conftest.py`:**

```python
from tiferet.testing.hooks import register_event_hooks

def pytest_generate_tests(metafunc):
    register_event_hooks(metafunc)
```

Both hooks can be combined in a single `conftest.py` if your test directory contains both mapper and event tests:

```python
from tiferet.testing.hooks import register_mapper_hooks, register_event_hooks

def pytest_generate_tests(metafunc):
    register_mapper_hooks(metafunc)
    register_event_hooks(metafunc)
```

## Test File Structure

Harness-based test files follow this general structure:

```python
"""Tiferet <Domain> <Component> Tests"""

# *** imports
from tiferet.testing import AggregateTestBase, TransferObjectTestBase  # or DomainEventTestBase

# *** constants
SAMPLE_DATA = { ... }
EQUALITY_FIELDS = [ ... ]

# *** classes

# ** class: TestSomeAggregate
class TestSomeAggregate(AggregateTestBase):
    aggregate_cls = SomeAggregate
    sample_data = SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS
    set_attribute_params = [
        ('name', 'Updated', None),
        ('invalid', 'value', 'INVALID_MODEL_ATTRIBUTE'),
    ]

    # Domain-specific mutation tests go here.

# ** class: TestSomeConfigObject
class TestSomeConfigObject(TransferObjectTestBase):
    transfer_cls = SomeConfigObject
    aggregate_cls = SomeAggregate
    sample_data = { ... }  # YAML-format
    aggregate_sample_data = SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS

    # Domain-specific serialization tests go here.
```

## Package Layout

```
tiferet/testing/
├── __init__.py    — Public exports
├── mappers.py     — MapperAssertions, AggregateTestBase, TransferObjectTestBase
├── domain.py      — DomainEventTestBase, ServiceEventTestBase
└── hooks.py       — register_mapper_hooks, register_event_hooks
```

## Related Documentation

- [docs/core/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md) — Aggregate and TransferObject conventions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and testing
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment and formatting rules
