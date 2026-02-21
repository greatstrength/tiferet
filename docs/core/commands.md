# Commands in Tiferet

Commands are the primary operational units in the Tiferet framework. They encapsulate focused domain actions, validation, and service interactions in a consistent, injectable, and testable way.

This document describes the structure, design principles, and best practices for writing Commands, using the error command suite as an example.

## What is a Command?

A Command is a class that performs a single, well-defined domain operation (e.g., `AddError`, `GetFeature`, `SetAppConstants`). Key characteristics:
- Extends the base `Command` class (`tiferet/commands/settings.py`).
- Receives dependencies via constructor injection (usually a service or repository).
- Exposes an `execute(**kwargs)` method as the entry point.
- Uses `verify_parameter` and `verify` for input and domain validation.
- Raises structured `TiferetError` instances via `raise_error` or `RaiseError.execute`.
- Is invoked in production and tests via the static `Command.handle` method.

Commands are called by Contexts (often through injected handler callables) and return domain models, identifiers, or results.

### Role in Runtime
- **Execution**: Contexts use commands to perform business logic (e.g., `FeatureContext` loads and executes feature commands).
- **Validation**: Centralized checks prevent invalid operations.
- **Error Handling**: Consistent structured errors.
- **Dependency Injection**: Commands are wired via `Command.handle` or container.

In the calculator application, commands like `AddNumber` execute arithmetic operations, while configuration commands (e.g., `AddError`, `UpdateFeatureCommand`) manage domain metadata.

## Structured Code Design of Commands

Commands follow a strict artifact comment structure:

- `# *** commands` – top-level section.
- `# ** command: <name>` – individual command (snake_case).
- `# * attribute: <name>` – injected dependencies.
- `# * init` – constructor.
- `# * method: execute` – main execution method.

**Spacing rules:**
- One empty line between `# *** commands` and first `# ** command`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

**Example** – `tiferet/commands/error.py`:
```python
# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import Command, const
from ..models import Error
from ..contracts import ErrorService

# *** commands

# ** command: add_error
class AddError(Command):
    '''
    Command to add a new Error domain object to the repository.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the AddError command.
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self,
            id: str,
            name: str,
            message: str,
            lang: str = 'en_US',
            additional_messages: List[Dict[str, Any]] = []
        ) -> Error:
        '''
        Add a new Error.
        '''
        # Validation
        self.verify_parameter(id, 'id', 'AddError')
        self.verify_parameter(name, 'name', 'AddError')
        self.verify_parameter(message, 'message', 'AddError')

        # Check existence
        self.verify(
            not self.error_service.exists(id),
            const.ERROR_ALREADY_EXISTS_ID,
            message=f'An error with ID {id} already exists.',
            id=id
        )

        # Create and save
        new_error = Error.new(id=id, name=name, message=[{'lang': lang, 'text': message}] + additional_messages)
        self.error_service.save(new_error)

        return new_error
```

## Creating New and Extending Existing Commands

### 1. Define the Command Class
- Place under `# *** commands` in a domain-specific module (e.g., `tiferet/commands/app.py`).
- Extend `Command`.
- Declare dependencies under `# * attribute`.
- Implement `__init__` and `execute`.

**Example** – `SetAppConstants`:
```python
# *** imports

# ** core
from typing import Dict, Any

# ** app
from .settings import Command
from ..contracts.app import AppService
from ..models.app import AppInterface

# *** commands

# ** command: set_app_constants
class SetAppConstants(Command):
    '''
    Command to set or clear constants on an app interface.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    # * method: execute
    def execute(self, id: str, constants: Dict[str, Any] | None = None, **kwargs) -> str:
        '''
        Set constants on app interface.
        '''
        # Validation
        self.verify_parameter(id, 'id', self.__class__.__name__)

        # Retrieve interface
        interface = self.app_service.get(id)
        self.verify(
            interface is not None,
            'APP_INTERFACE_NOT_FOUND',
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Update constants
        interface.set_constants(constants)

        # Persist
        self.app_service.save(interface)

        return id
```

### 2. Use in Context or Integration
- Inject command instance into contexts.
- Call via `command.execute(...)` or `Command.handle` in tests.

### Best Practices
- Use `# * attribute`, `# * init`, `# * method: execute` consistently.
- Validate required parameters with `verify_parameter`.
- Use `verify` for domain rules.
- Raise structured errors via `raise_error` or `RaiseError.execute`.
- Return domain models or identifiers.
- Keep commands focused on one operation.

## Testing Commands

Tests validate input validation, service interactions, and error handling.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Invocation**: Always use `Command.handle` in tests.

**Example** – `SetAppConstants` test:
```python
def test_set_app_constants_success(mock_app_service):
    interface = mock_app_service.get.return_value
    result = Command.handle(
        SetAppConstants,
        dependencies={'app_service': mock_app_service},
        id='test_app',
        constants={'KEY': 'VALUE'}
    )
    assert result == 'test_app'
    mock_app_service.get.assert_called_once_with('test_app')
    mock_app_service.save.assert_called_once_with(interface)
    assert interface.set_constants.called_with({'KEY': 'VALUE'})
```

### Best Practices
- Mock injected services.
- Test success, validation failures, and not-found cases.
- Verify service calls and return values.

## Conclusion

Commands are the operational core of Tiferet applications, providing validated, injectable domain operations. Their structured design ensures consistency, testability, and extensibility. Developers can create new commands by following the artifact pattern and using `Command.handle` for invocation. Explore `tiferet/commands/` for source and `tiferet/commands/tests/` for test examples.