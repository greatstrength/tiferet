# Domain Events in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Domain events are the operational core of the Tiferet framework. Every focused domain action — validation, service interaction, computation, or orchestration — is expressed as a class extending `DomainEvent` from `tiferet/events/core.py`.

`DomainEvent` provides:
- Core orchestration (`execute`, `handle`)
- Structured validation (`verify`)
- Error raising (`raise_error`)
- A declarative parameter validator via the static `@parameters_required` decorator

This class serves as the base for all domain event implementations. It centralizes execution patterns, validation, and error handling into a single, testable abstraction.

## The DomainEvent Base Class

`DomainEvent` extends `object` and provides the foundational methods for all domain operations:

```python
# tiferet/events/core.py

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
    def handle(event_cls: type, dependencies: Dict[str, Any] = {}, **kwargs) -> Any:
        '''Instantiate → execute pattern.'''
        event_handler = event_cls(**dependencies)
        result = event_handler.execute(**kwargs)
        return result
```

Key characteristics:
- **`execute(**kwargs)`** is the abstract entry point; subclasses must override it.
- **`raise_error`** is static — usable from both instance and class context.
- **`verify`** wraps `assert` with structured error raising for domain rule validation.
- **`handle(EventClass, dependencies, **kwargs)`** is the standard invocation pattern in tests and contexts.
- **`@parameters_required`** provides declarative, aggregated parameter validation.

## Per-Module Base Events

Each event module that shares a single injected service defines a **base event** that owns that service's dependency injection. Concrete events extend the base event and drop the `# * attribute` / `# * init` boilerplate, declaring only their `execute` method.

```python
# tiferet/events/error.py

# *** events

# ** event: error_event
class ErrorEvent(DomainEvent):
    '''
    Base event providing the shared ErrorService dependency for error domain events.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the error event with its shared service dependency.
        '''

        # Set the error service dependency.
        self.error_service = error_service

# ** event: get_error
class GetError(ErrorEvent):
    '''
    Event to retrieve an Error domain object by its ID.
    '''

    # * method: execute
    def execute(self, id: str, **kwargs) -> Error:
        '''
        Retrieve an Error by its ID.
        '''

        # Retrieve the error via the inherited service.
        return self.error_service.get(id)
```

The framework defines nine base events, one per single-service event module:

- `ErrorEvent` (`error_service`) — `tiferet/events/error.py`
- `FeatureEvent` (`feature_service`) — `tiferet/events/feature.py`
- `AppEvent` (`app_service`) — `tiferet/events/app.py`
- `CliEvent` (`cli_service`) — `tiferet/events/cli.py`
- `DIEvent` (`di_service`) — `tiferet/events/di.py`
- `LoggingEvent` (`logging_service`) — `tiferet/events/logging.py`
- `SqliteEvent` (`sqlite_service`) — `tiferet/events/sqlite.py`
- `YamlEvent` (`yaml_service`) — `tiferet/events/yaml.py`
- `CheckEvent` (`check_service`) — `tiferet/events/tester_phase.py`

`TestModuleEvent` (`tiferet/events/tester_module.py`) is also a shared base, but it holds no service; it supplies the `verify_defect` helper to the test-module events.

An event that takes no injected service extends `DomainEvent` (or `AsyncDomainEvent`) directly and uses no base event. The former static events (`ParseParameter`, `ImportDependency`) are gone; parameter parsing is `tiferet/blueprints/core.py::parse_parameter`.

> **Naming note:** The `FeatureEvent` base event reuses the name freed by the `FeatureEvent` → `EventFeatureStep` domain-object rename. The former `FeatureEvent` domain object (a feature workflow step) is now `EventFeatureStep`; the name `FeatureEvent` now denotes the feature module's base event.

## Structured Code Design

Domain events follow the standard Tiferet artifact comment structure:

- `# *** events` – top-level section (use `# *** classes` in `core.py`).
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
- Extend the module's base event (e.g., `ErrorEvent`) to inherit the shared service, or `DomainEvent` directly for events with no shared service.
- Implement `execute`; the base event supplies the `# * attribute` dependency and `# * init` (see [Per-Module Base Events](#per-module-base-events)).
- Use `@DomainEvent.parameters_required` for declarative parameter validation.

**Example** – `AddError` (extends the `ErrorEvent` base event):
```python
# *** imports

# ** app
from .core import DomainEvent, a
from ..domain import Error
from ..mappers import ErrorAggregate

# *** events

# ** event: add_error
class AddError(ErrorEvent):
    '''
    Event to add a new Error domain object to the repository.

    Extends the ErrorEvent base event (see "Per-Module Base Events"),
    which injects the shared error_service; only execute is defined here.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'message'])
    def execute(self, id: str, name: str, message: str, **kwargs) -> Error:
        '''
        Add a new Error.
        '''

        # Check existence via the inherited service.
        self.verify(
            not self.error_service.exists(id),
            a.const.ERROR_ALREADY_EXISTS_ID,
            message=f'An error with ID {id} already exists.',
            id=id,
        )

        # Create and save the error aggregate.
        new_error = ErrorAggregate(
            id=id,
            name=name,
            message=[{'lang': 'en_US', 'text': message}],
        )
        self.error_service.save(new_error)

        # Return the new error.
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

Event tests use the `@use_tester` harness ([testing.md](testing.md)). Two tester types cover events:

- **`domain_event`** binds a `DomainEventTesterContext`. Declare `target_cls`, `dependencies` (dependency name → `module_path` / `class_name`, auto-mocked), `sample_kwargs`, and `required_params`. The context provides `mock_dependencies()`, `handle(dependencies=None, **kwargs)` (merges `sample_kwargs` with overrides and invokes `DomainEvent.handle`), and `assert_missing_required_params()`.
- **`service_event`** binds a `ServiceEventTesterContext` for retrieve → verify → mutate → save events on one service. It adds `service_attr`, `not_found_error_code`, `not_found_kwargs`, `get_service_mock(dependencies=None)`, and `assert_not_found()`.

Parametrized cases are fields on the tester object, not conftest hooks. Override `mock_dependencies` as a `# * fixture:` member when a test needs a pre-configured service mock.

```python
# *** imports

# ** core
from unittest import mock

# ** infra
import pytest

# ** app
from tiferet.events.error import AddError
from tiferet.interfaces import ErrorService
from tiferet.blueprints.tester import use_tester

# *** testers

# ** tester: test_add_error
@use_tester(
    type='domain_event',
    target_cls=AddError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs={
        'id': 'NEW_ERROR',
        'name': 'New Error',
        'message': 'This is a new error message.',
        'lang': 'en_US',
        'additional_messages': {},
    },
    required_params=['id', 'name', 'message'],
)
class TestAddError:
    '''
    Tests for AddError using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Override to pre-configure exists to return False.
        '''

        # Create the mock error service.
        service = mock.Mock(spec=ErrorService)
        service.exists.return_value = False
        return {'error_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies):
        '''
        Test adding a new error successfully.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the service was called correctly.
        mock_dependencies['error_service'].save.assert_called_once_with(result)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Assert each required parameter raises COMMAND_PARAMETER_REQUIRED.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()
```

The full module is `tests/events/test_error.py`. Module-level `# *** tests` functions that call `DomainEvent.handle` directly remain valid for edge cases.

### Best Practices
- Use `@use_tester` with `type='domain_event'` or `type='service_event'` for event component tests; keep module-level pytest tests for cases no tester type fits.
- Mock injected services; avoid real I/O in unit tests.
- Test success, validation failures, and not-found cases.
- Verify service calls and return values.

## Middleware Support

`DomainEvent.handle()` and `DomainEvent.handle_async()` accept an optional `middleware` list that wraps event execution with cross-cutting concerns (logging, timing, tracing, retries) without modifying the event itself.

Each middleware is a callable following the `(event, kwargs, next_fn)` convention:
- `event` — the instantiated domain event.
- `kwargs` — the merged execution keyword arguments.
- `next_fn` — a zero-argument callable that invokes the remainder of the chain (the next middleware, or the event's `execute` when none remain).

Middleware is composed **outermost-first**: the first entry in the list is the outermost wrapper (first to run on entry, last to run on exit).

**Sync example** — compose the chain programmatically via `handle`:
```python
result = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    middleware=[LoggingMiddleware('root'), TimingMiddleware('root')],
    id='ERR_001',
)
```

A synchronous middleware calls `next_fn()` directly and returns its result:
```python
class LoggingMiddleware(MiddlewareService):

    # * method: __call__
    def __call__(self, event, kwargs, next_fn):
        result = next_fn()
        return result
```

**Async example** — `handle_async` composes the same chain for `AsyncDomainEvent` subclasses; async middleware must `await next_fn()`:
```python
class AsyncAuditMiddleware(MiddlewareService):

    # * method: __call__
    async def __call__(self, event, kwargs, next_fn):
        result = await next_fn()
        return result
```

**Configuration-driven middleware.** Beyond programmatic use, middleware can be declared in `config.yml` and resolved from the DI container by `FeatureContext` during `execute_feature` / `execute_feature_async`. Feature-level middleware wraps every step in the feature; step-level middleware applies to a single command.

For built-in middleware, the `MiddlewareService` interface, ordering, `config.yml` registration, and testing, see the [Utils strategy guide](../guides/utils.md#the-middlewareservice-pattern) and the [utils/core cookbook](../guides/utils/core.md).

## Package Layout

Domain events are defined in `tiferet/events/`:

- `core.py` – `DomainEvent` and `AsyncDomainEvent` base classes and the `@parameters_required` decorator.
- `app.py` – `AppEvent` base + app interface management events.
- `cli.py` – `CliEvent` base + CLI command management events.
- `di.py` – `DIEvent` base + DI service registration events.
- `error.py` – `ErrorEvent` base + error management events.
- `feature.py` – `FeatureEvent` base + feature workflow management events.
- `logging.py` – `LoggingEvent` base + logging configuration events.
- `sqlite.py` – `SqliteEvent` base + SQLite management events.
- `yaml.py` – `YamlEvent` base + YAML load/save and anchor events.
- `tester_module.py`, `tester_phase.py` – test-module document and tester-phase events (see [testing.md](testing.md)).
- `__init__.py` – Public exports (`DomainEvent`, `AsyncDomainEvent`, `TiferetError`, `a`).

Per-module test suites live in `tests/events/` (e.g., `test_app.py`, `test_cli.py`) and use `@use_tester`.

## Conclusion

Domain events are the operational core of Tiferet applications, providing validated, injectable domain operations. Their structured design ensures consistency, testability, and extensibility. The `@use_tester` `domain_event` / `service_event` testers eliminate boilerplate while enforcing consistent coverage of required-parameter validation and not-found error paths. Developers can create new events by following the artifact pattern and new tests with `@use_tester`. Explore `tiferet/events/` for source and `tests/events/` for test examples.
