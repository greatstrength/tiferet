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

```
# *** events                      ← top-level (use # *** classes in settings.py)
# ** event: <snake_case_name>     ← individual event
# * attribute: <name>             ← injected dependency (on base event only)
# * init                          ← constructor (on base event only)
# * method: execute               ← main execution method
```

Side-effect-free module-level helpers go in a `# *** functions` section above `# *** events`.

## Key conventions

- Extend `DomainEvent` from `tiferet.events.settings` — either directly (new base or service-less event) or via the **per-module base event** (most common).
- **Per-module base events:** Each single-service module defines one base event (e.g. `ErrorEvent`, `FeatureEvent`, `AppEvent`, `CliEvent`, `DIEvent`, `LoggingEvent`, `SqliteEvent`) that holds the shared service. Concrete events extend the base and declare only `execute`.
- `@DomainEvent.parameters_required(['param1', 'param2'])` — declarative required-input validator placed as a decorator on `execute`. A parameter is invalid if absent, `None`, or an empty string after `.strip()`; falsy-but-valid values (`0`, `False`, `[]`) pass.
- `self.verify(expression, error_code, message=None, **kwargs)` — domain rule assertions inside `execute`.
- `self.raise_error(error_code, message=None, **kwargs)` — direct error raising when `verify` is not appropriate.
- Access error constants via `a.const.ERROR_CODE_ID` (import `a` from `tiferet.events.settings`).
- Return a domain object or identifier; never return `None` on success.
- `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)` — standard invocation pattern in tests and contexts.

## Example

```python
# *** imports

# ** app
from .settings import DomainEvent, a
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
