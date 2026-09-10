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

The framework defines seven base events, one per single-service event module:

- `ErrorEvent` (`error_service`) — `tiferet/events/error.py`
- `FeatureEvent` (`feature_service`) — `tiferet/events/feature.py`
- `AppEvent` (`app_service`) — `tiferet/events/app.py`
- `CliEvent` (`cli_service`) — `tiferet/events/cli.py`
- `DIEvent` (`di_service`) — `tiferet/events/di.py`
- `LoggingEvent` (`logging_service`) — `tiferet/events/logging.py`
- `SqliteEvent` (`sqlite_service`) — `tiferet/events/sqlite.py`

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

Tests validate input validation, service interactions, and error handling using pytest (optional extra; runner for `tests/`). Bind a variant tester context with `@use_tester`. Full conventions: [testing.md](testing.md).

**Test-module groups:** `# *** fixtures` → `# *** tests` (functions) → `# *** testers` (`*Tester` classes). Tester members are `# * fixture:` / `# * test:` only. Bulk remediating existing `tests/events/` files is not required of this documentation pass.

Event `type` values are `'domain_event'` (`DomainEventTesterContext`) and `'service_event'` (`ServiceEventTesterContext`). Both omit `domain_type`. Declare constructor mocks as `ServiceDependency` dicts:

```yaml
dependencies:
  error_service:
    module_path: tiferet.interfaces
    class_name: ErrorService
```

`DomainEventTesterContext` provides `mock_dependencies()`, `handle(dependencies=None, **kwargs)` (delegates to `DomainEvent.handle` with `sample_kwargs`), and `assert_missing_required_params()`. `ServiceEventTesterContext` adds `get_service_mock` and `assert_not_found()` (`service_attr` + `not_found_error_code`; unset is a no-op).

```python
@use_tester(
    type='domain_event',
    target_cls=AddError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(id='ERR_001', name='Test Error', message='A test error.'),
    required_params=['id', 'name', 'message'],
)
class AddErrorTester:

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        service = mock.Mock(spec=ErrorService)
        service.exists.return_value = False
        return {'error_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies):
        result = test_ctx.handle(mock_dependencies)
        assert result is not None
        mock_dependencies['error_service'].save.assert_called_once()

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        test_ctx.assert_missing_required_params()
```

```python
@use_tester(
    type='service_event',
    target_cls=GetError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(id='ERR_001'),
    required_params=['id'],
    service_attr='error_service',
    not_found_error_code=a.error.ERROR_NOT_FOUND_ID,
)
class GetErrorTester:

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_error) -> dict:
        service = mock.Mock(spec=ErrorService)
        service.get.return_value = sample_error
        return {'error_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies):
        result = test_ctx.handle(mock_dependencies)
        assert result is sample_error

    # * test: not_found
    def test_not_found(self, test_ctx):
        test_ctx.assert_not_found()
```

`assert_not_found` builds its own mocks and sets `service.get.return_value = None`, so a success-path `# * fixture: mock_dependencies` does not collide with it.

### Standalone Tests

For simple events or edge cases that do not need a bound tester, standalone `# ** test:` functions with module-level fixtures remain valid:

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
- Prefer `@use_tester` with `type='domain_event'` or `type='service_event'` for new event tests.
- Mock injected services; avoid real I/O in unit tests.
- Test success, validation failures, and not-found cases.
- Verify service calls and return values.
- Use `test_ctx.handle` (or `DomainEvent.handle` in standalone tests) for consistent instantiation and execution.
- Override `mock_dependencies` as a `# * fixture:` when tests need a pre-configured aggregate.

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

**Configuration-driven middleware.** Beyond programmatic use, middleware can be declared in `config.yml` and resolved from the DI container by `FeatureContext.execute_feature` (which drives sync and async step dispatch internally based on `is_async` flags — there is no separate async context class). Feature-level middleware wraps every step in the feature; step-level middleware applies to a single command.

For built-in middleware, the `MiddlewareService` interface, ordering, `config.yml` registration, and testing, see [docs/guides/utils.md](../guides/utils.md) (the middleware composition pattern lives alongside the utils strategy guide, not in a standalone middleware guide).

## Package Layout

Domain events are defined in `tiferet/events/`:

- `core.py` – `DomainEvent` base class, `@parameters_required` decorator.
- `app.py` – `AppEvent` base + app session management events.
- `cli.py` – `CliEvent` base + CLI command management events.
- `di.py` – `DIEvent` base + DI service registration events.
- `error.py` – `ErrorEvent` base + error management events.
- `feature.py` – `FeatureEvent` base + feature workflow management events.
- `logging.py` – `LoggingEvent` base + logging configuration events.
- `sqlite.py` – `SqliteEvent` base + SQLite management events.
- `tester.py` – `TesterEvent` base + tester configuration events.
- `__init__.py` – Public exports (`DomainEvent`, `TiferetError`, `a`).

Per-module test suites live in `tests/events/` (e.g., `test_app.py`, `test_cli.py`, etc.). The former test-harness package was retired; event tests bind `DomainEventTesterContext` / `ServiceEventTesterContext` via `@use_tester` (see [testing.md](testing.md)).

## Conclusion

Domain events are the operational core of Tiferet applications, providing validated, injectable domain operations. Their structured design ensures consistency, testability, and extensibility. Bound event testers cover required-parameter validation and not-found paths without a separate testing package. Developers can create new events by following the artifact pattern and new tests with `@use_tester`. Explore `tiferet/events/` for source and `tests/events/` for test examples.
