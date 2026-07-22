---
name: tiferet-code-events
description: Apply domain event conventions when adding or modifying domain events in a Tiferet-family repo. Covers per-module base events, the parameters_required decorator, verify/raise_error patterns, and the DomainEventTestBase harness.
---

# Domain Events Code Style – Tiferet

## When to use
- When adding a new domain event class or modifying an existing one in `tiferet/events/`.
- When implementing event-driven domain logic: validation, service interaction, orchestration.
- When writing event tests using `DomainEventTestBase` or `ServiceEventTestBase`.
- Pair with `tiferet-code-testing` for the full testing harness reference.

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** events             ← construct group for this skill
# *** exports            ← __init__.py only
```

Event-specific labels:
```
# *** events                      ← artifact section
# ** event: <snake_case_name>     ← artifact
# * attribute: <name>             ← artifact member: injected dependency (base event only)
# * init                          ← artifact member: constructor (base event only)
# * method: execute               ← artifact member: main execution method
```

## Key conventions

- **Layer boundary — valid `# ** app` imports:** `assets`, `domain`, `interfaces`, `mappers`, `di`. Never import from `repos`, `utils`, `contexts`, or `blueprints`.
- Extend `DomainEvent` from `tiferet.events.core` — either directly (new base or service-less event) or via the **per-module base event** (most common).
- **Per-module base events:** Each single-service module defines one base event (e.g. `ErrorEvent`, `FeatureEvent`, `AppEvent`, `CliEvent`, `DIEvent`, `LoggingEvent`, `SqliteEvent`) that holds the shared service. Concrete events extend the base and declare only `execute`.
- `@DomainEvent.parameters_required(['param1', 'param2'])` — declarative required-input validator placed as a decorator on `execute`. A parameter is invalid if absent, `None`, or an empty string after `.strip()`; falsy-but-valid values (`0`, `False`, `[]`) pass.
- `self.verify(expression, error_code, message=None, **kwargs)` — domain rule assertions inside `execute`.
- `self.raise_error(error_code, message=None, **kwargs)` — direct error raising when `verify` is not appropriate.
- Access error constants via `a.<submodule>.ERROR_CODE_ID` (e.g. `a.error.COMMAND_PARAMETER_REQUIRED_ID`). `a` is imported as `from .. import assets as a`; constants are namespaced by sub-module: `a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`.
- Return a domain object or identifier; never return `None` on success.
- `DomainEvent.handle(EventClass, dependencies={...}, middleware=None, **kwargs)` — standard invocation pattern in tests and contexts. `middleware` is an optional outermost-first list of `(event, kwargs, next_fn)` callables.
- `DomainEvent.handle_async(...)` — async equivalent; use when driving `AsyncDomainEvent` subclasses.
- **`AsyncDomainEvent`** — extend this instead of `DomainEvent` when `execute` is a coroutine (`async def execute`). Inherits `verify`, `raise_error`, and `parameters_required` unchanged.

## Example

```python
# *** imports

# ** app
from .core import DomainEvent, a
from ..domain import Error
from ..mappers import ErrorAggregate
from .error import ErrorEvent     # per-module base event

# *** events

# ** event: add_error
class AddError(ErrorEvent):
    '''
    Event to add a new Error domain object to the repository.

    Extends ErrorEvent (the per-module base), which injects error_service;
    only execute is defined here.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'message'])
    def execute(self,
            id: str,
            name: str,
            message: str,
            **kwargs,
        ) -> Error:
        '''
        Add a new Error.

        :param id: The unique error identifier.
        :type id: str
        :param name: The human-readable error name.
        :type name: str
        :param message: The default English error message.
        :type message: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Error domain object.
        :rtype: Error
        '''

        # Verify the error does not already exist.
        self.verify(
            not self.error_service.exists(id),
            a.error.ERROR_ALREADY_EXISTS_ID,
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

        # Return the newly created error.
        return new_error
```

The corresponding per-module base event (already defined in `tiferet/events/error.py`) is:

```python
# ** event: error_event
class ErrorEvent(DomainEvent):
    '''
    Base event providing the shared ErrorService dependency.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize with the shared error service.

        :param error_service: The error service dependency.
        :type error_service: ErrorService
        '''

        # Set the error service dependency.
        self.error_service = error_service
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md
