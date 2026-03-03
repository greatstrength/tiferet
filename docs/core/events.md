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

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Invocation**: Always use `DomainEvent.handle` in tests.

**Example** – `AddError` test:
```python
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
- Mock injected services.
- Test success, validation failures, and not-found cases.
- Verify service calls and return values.
- Use `DomainEvent.handle` for consistent instantiation and execution.

## Package Layout

Domain events are defined in `tiferet/events/`:

- `settings.py` – `DomainEvent` base class, `@parameters_required` decorator.
- `__init__.py` – Public exports (`DomainEvent`, `TiferetError`, `a`).

Tests live in `tiferet/events/tests/`.

## Conclusion

Domain events are the operational core of Tiferet applications, providing validated, injectable domain operations. Their structured design ensures consistency, testability, and extensibility. Developers can create new events by following the artifact pattern and using `DomainEvent.handle` for invocation. Explore `tiferet/events/` for source and `tiferet/events/tests/` for test examples.
