# Domain Events in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Domain events are the operational core of the Tiferet framework. Every focused domain action — validation, service interaction, computation, or orchestration — is expressed as a class extending `DomainEvent` from `tiferet.events.settings`.

`DomainEvent` provides:
- Core orchestration (`execute`, `handle`)
- Structured validation (`verify`)
- Error raising (`raise_error`)
- A declarative parameter validator via the static `@parameters_required` decorator

This class serves as the base for all domain event implementations. It centralizes execution patterns, validation, and error handling into a single, testable abstraction.

## The DomainEvent Base Class

`DomainEvent` extends `object` and provides the foundational methods for all domain operations:

```python
# tiferet/events/settings.py

class DomainEvent(object):
    '''
    A base class for a domain event object.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Any:
        '''Abstract execution entry point.'''
        raise NotImplementedError()

    # * method: raise_error (static)
    @staticmethod
    def raise_error(error_code: str, message: str = None, **kwargs):
        '''Raise a structured TiferetError.'''
        raise TiferetError(error_code, message, **kwargs)

    # * method: verify
    def verify(self, expression: bool, error_code: str, message: str = None, **kwargs):
        '''Assert expression; raise on failure.'''
        try:
            assert expression
        except AssertionError:
            self.raise_error(error_code, message, **kwargs)

    # * method: parameters_required (static)
    @staticmethod
    def parameters_required(param_names: list):
        '''Declarative parameter validator – raises aggregated error.'''
        ...

    # * method: handle (static)
    @staticmethod
    def handle(command: type, dependencies: Dict[str, Any] = {}, **kwargs) -> Any:
        '''Instantiate → execute pattern.'''
        command_handler = command(**dependencies)
        result = command_handler.execute(**kwargs)
        return result
```

Key characteristics:
- **`execute(**kwargs)`** is the abstract entry point; subclasses must override it.
- **`raise_error`** is static — usable from both instance and class context.
- **`verify`** wraps `assert` with structured error raising for domain rule validation.
- **`handle(EventClass, dependencies, **kwargs)`** is the standard invocation pattern in tests and contexts.
- **`@parameters_required`** provides declarative, aggregated parameter validation.

## Structured Code Design

Domain events follow the standard Tiferet artifact comment structure:

- `# *** events` – top-level section (use `# *** classes` in `settings.py`).
- `# ** event: <name>` – individual domain event (snake_case).
- `# * attribute: <name>` – injected dependencies.
- `# * init` – constructor.
- `# * method: execute` – main execution method.

**Spacing rules:**
- One empty line between `# *** events` and first `# ** event`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

## Creating Domain Events

### 1. Define the Event Class
- Extend `DomainEvent`.
- Declare dependencies under `# * attribute`.
- Implement `__init__` and `execute`.
- Use `@DomainEvent.parameters_required` for declarative parameter validation.

**Example** – `AddError`:
```python
# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from tiferet.events import DomainEvent, a
from tiferet.contracts import ErrorService
from tiferet.domain.error import Error

# *** events

# ** event: add_error
class AddError(DomainEvent):
    '''
    Event to add a new Error domain object to the repository.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the AddError event.
        '''
        self.error_service = error_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'message'])
    def execute(self, **kwargs) -> Error:
        '''
        Add a new Error.
        '''

        # Unpack parameters.
        id = kwargs['id']
        name = kwargs['name']
        message = kwargs['message']

        # Check existence.
        self.verify(
            not self.error_service.exists(id),
            a.const.ERROR_ALREADY_EXISTS_ID,
            message=f'An error with ID {id} already exists.',
            id=id
        )

        # Create and save.
        new_error = Error.new(id=id, name=name, message=message)
        self.error_service.save(new_error)

        return new_error
```

### 2. Use in Context or Integration
- Inject event instance into contexts.
- Call via `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)`.

## The `@parameters_required` Decorator

The `@parameters_required` decorator provides declarative, aggregated parameter validation:

```python
@DomainEvent.parameters_required(['id', 'name'])
def execute(self, **kwargs) -> Any:
    ...
```

### Validation Rules
- Inspects `**kwargs` keys (compatible with `handle` which calls `execute(**kwargs)`).
- A parameter is **missing/invalid** if:
  - Not present in `kwargs`
  - Value is `None`
  - Value is `str` and `.strip() == ""`
- **Falsy-but-valid** cases (pass validation):
  - `0`, `0.0`, `False`, `[]`, `{}`, `set()`, etc.
- Collects **all** violations → raises **single** `TiferetError`.
- Error uses constant `a.const.COMMAND_PARAMETER_REQUIRED_ID`.
- Error `kwargs`: `{'parameters': ['id', 'name'], 'command': 'ClassName'}`.

### Comparison: `@parameters_required` vs `verify` vs `raise_error`

- **`@parameters_required`**: Declarative, applied as a decorator. Best for validating that required kwargs are present and non-empty before execution begins. Aggregates all violations into one error.
- **`verify`**: Imperative, called within `execute`. Best for domain rule assertions (e.g., "entity must not already exist").
- **`raise_error`**: Low-level, raises a single `TiferetError`. Use directly when custom error logic is needed.

## Testing Domain Events

Tests validate input validation, service interactions, and error handling using `pytest`.

### Test Harness

The domain event test harness (`tiferet/events/tests/settings.py`) provides two base classes that eliminate boilerplate and enforce consistency across all event test modules.

#### DomainEventTestBase

Base class for testing any `DomainEvent` subclass. Subclasses declare four class attributes:

- **`event_cls`** — the `DomainEvent` class under test.
- **`dependencies`** — dict mapping dependency name → type (auto-mocked via the `mock_dependencies` fixture).
- **`sample_kwargs`** — default kwargs for a successful `execute()` call.
- **`required_params`** — list of required parameter names (auto-parametrized validation tests).

Provides:
- **`mock_dependencies`** fixture — creates `mock.Mock(spec=Type)` for each declared dependency.
- **`handle(mock_dependencies, **overrides)`** — merges `sample_kwargs` with overrides and invokes `DomainEvent.handle`.
- **`test_missing_required_params`** — auto-parametrized test that sets each required param to `None` and asserts `COMMAND_PARAMETER_REQUIRED` is raised.

```python
class TestAddError(DomainEventTestBase):
    event_cls = AddError
    dependencies = {'error_service': ErrorService}
    sample_kwargs = dict(id='ERR_001', name='Test Error', message='A test error.')
    required_params = ['id', 'name', 'message']

    def test_success(self, mock_dependencies):
        mock_dependencies['error_service'].exists.return_value = False
        result = self.handle(mock_dependencies)
        assert result is not None
        mock_dependencies['error_service'].save.assert_called_once()
```

#### ServiceEventTestBase

Extends `DomainEventTestBase` for events that follow the retrieve → verify → mutate → save pattern with a single service. Adds three class attributes:

- **`service_attr`** — the dependency name (e.g., `'error_service'`).
- **`not_found_error_code`** — error code raised when the service returns `None`.
- **`not_found_kwargs`** — kwargs that trigger the not-found path (defaults to `sample_kwargs`).

Provides:
- **`get_service_mock(mock_dependencies)`** — retrieves the primary service mock by `service_attr`.
- **`test_not_found`** — auto test that configures `service.get()` to return `None` and asserts the configured error code is raised.

```python
class TestGetError(ServiceEventTestBase):
    event_cls = GetError
    dependencies = {'error_service': ErrorService}
    service_attr = 'error_service'
    sample_kwargs = dict(id='ERR_001')
    required_params = ['id']
    not_found_error_code = a.const.ERROR_NOT_FOUND_ID
    not_found_kwargs = dict(id='missing_error')

    def test_success(self, mock_dependencies):
        mock_dependencies['error_service'].get.return_value = sample_error
        result = self.handle(mock_dependencies)
        assert result is sample_error
```

#### Conftest Hook

The `pytest_generate_tests` hook in `tiferet/events/tests/conftest.py` dynamically parametrizes `test_missing_required_params` over the `required_params` list for any `DomainEventTestBase` subclass:

```python
def pytest_generate_tests(metafunc):
    cls = metafunc.cls
    if cls and issubclass(cls, DomainEventTestBase) and metafunc.function.__name__ == 'test_missing_required_params':
        params = getattr(cls, 'required_params', [])
        metafunc.parametrize('required_param', params)
```

#### Overriding `mock_dependencies`

For events that need a pre-configured service mock (e.g., `service.get()` returns a real aggregate), override the `mock_dependencies` fixture:

```python
class TestUpdateError(ServiceEventTestBase):
    event_cls = UpdateError
    dependencies = {'error_service': ErrorService}
    service_attr = 'error_service'
    # ...

    @pytest.fixture
    def mock_dependencies(self, sample_error):
        service = mock.Mock(spec=ErrorService)
        service.get.return_value = sample_error
        return {'error_service': service}
```

The `test_not_found` auto-test reconfigures `service.get.return_value = None` before executing, so the override is safe for both paths.

### Standalone Tests

For simple events or edge cases that don't fit the harness, standalone test functions with module-level fixtures remain valid:

```python
# ** fixture: mock_error_service
@pytest.fixture
def mock_error_service():
    return mock.Mock(spec=ErrorService)

# ** test: add_error_success
def test_add_error_success(mock_error_service):
    mock_error_service.exists.return_value = False
    result = DomainEvent.handle(
        AddError,
        dependencies={'error_service': mock_error_service},
        id='TEST_001',
        name='Test Error',
        message='A test error.'
    )
    assert result is not None
    mock_error_service.save.assert_called_once()
```

### Best Practices
- Prefer the harness for all new event tests.
- Mock injected services; avoid real I/O in unit tests.
- Test success, validation failures, and not-found cases.
- Verify service calls and return values.
- Use `DomainEvent.handle` for consistent instantiation and execution.
- Override `mock_dependencies` when tests need a pre-configured aggregate.

## Package Layout

Domain events are defined in `tiferet/events/`:

- `settings.py` – `DomainEvent` base class, `@parameters_required` decorator.
- `static.py` – Static utility events (`ParseParameter`, `ImportDependency`, `RaiseError`).
- `app.py` – App interface management events.
- `cli.py` – CLI command management events.
- `container.py` – Container attribute management events.
- `dependencies.py` – DI service configuration events.
- `error.py` – Error management events.
- `feature.py` – Feature workflow management events.
- `logging.py` – Logging configuration events.
- `sqlite.py` – SQLite management events.
- `__init__.py` – Public exports (`DomainEvent`, `TiferetError`, `a`).

Tests live in `tiferet/events/tests/`:

- `settings.py` – Test harness (`DomainEventTestBase`, `ServiceEventTestBase`).
- `conftest.py` – `pytest_generate_tests` hook for auto-parametrization.
- `test_app.py`, `test_cli.py`, `test_container.py`, etc. – Per-module test suites.

## Conclusion

Domain events are the operational core of Tiferet applications, providing validated, injectable domain operations. Their structured design ensures consistency, testability, and extensibility. The test harness (`DomainEventTestBase` / `ServiceEventTestBase`) eliminates boilerplate while enforcing consistent coverage of required-parameter validation and not-found error paths. Developers can create new events by following the artifact pattern and new tests by extending the harness. Explore `tiferet/events/` for source and `tiferet/events/tests/` for test examples.
