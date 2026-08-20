---
name: tiferet-code-interfaces
description: Apply service interface conventions when adding or modifying Service interfaces in a Tiferet-family repo. Covers the Service ABC, abstractmethod usage, MiddlewareService, and vertical contract design.
---

# Interfaces (Services) Code Style – Tiferet

## When to use
- When adding a new Service interface or modifying an existing one in `tiferet/interfaces/`.
- When defining the abstract contract for a new domain concern (data access, middleware, computation).
- Do NOT use for concrete implementations — those are repositories (`tiferet-code-repos`) or utilities (`tiferet-code-utils`).

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** interfaces         ← construct group for this skill
# *** exports            ← __init__.py only
```

Interface-specific labels:
```
# *** interfaces                        ← artifact section
# ** interface: <snake_case_name>       ← artifact
# * attribute: <name>                   ← artifact member: type-hinted instance attribute (rare; no assignment)
# * method: <name>                      ← artifact member: abstract method
```

## Key conventions

- **Layer boundary — valid `# ** app` imports:** `mappers` (aggregates for output types); sibling `interfaces` modules. Prefer the aggregate over the domain model when an aggregate exists. Never import from `events`, `repos`, `utils`, `contexts`, or `blueprints`.
- Extend `Service` from `tiferet.interfaces.core` (a minimal `ABC`).
- Mark every method `@abstractmethod` and raise `NotImplementedError()` in the body.
- Use RST docstrings with `:param`/`:type`/`:return`/`:rtype` on every method.
- No `# * init` — services are abstract definitions, not instantiated directly.
- Keep methods focused on a single vertical concern (data access, file I/O, configuration, middleware).
- Services are **unified vertical contracts**: data repositories, utility wrappers, and middleware all satisfy this same base.
- **`MiddlewareService`** (`tiferet/interfaces/middleware.py`) is the special abstract contract for domain event middleware — implement `__call__(self, event, kwargs, next_fn)` (sync) or `async def __call__` (async); label with `# * method: __call__`.
- Domain events and contexts depend exclusively on these Service interfaces; never depend on concrete classes.
- **Exported interfaces:** `Service`, `AppService`, `CliService`, `ConfigurationService`, `DIService`, `ErrorService`, `FeatureService`, `FileService`, `LoggingService`, `SqliteService`, `MiddlewareService`.

## Example

```python
# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from .core import Service
from ..mappers import ErrorAggregate

# *** interfaces

# ** interface: error_service
class ErrorService(Service):
    '''
    Vertical interface for managing Error domain objects.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check whether an error with the given ID exists.

        :param id: The error identifier.
        :type id: str
        :return: True if the error exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str) -> Optional[ErrorAggregate]:
        '''
        Retrieve an Error by its ID.

        :param id: The error identifier.
        :type id: str
        :return: The ErrorAggregate, or None if not found.
        :rtype: Optional[ErrorAggregate]
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[ErrorAggregate]:
        '''
        List all Error domain objects.

        :return: All stored errors.
        :rtype: List[ErrorAggregate]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, error: ErrorAggregate) -> None:
        '''
        Persist an Error domain object.

        :param error: The error aggregate to persist.
        :type error: ErrorAggregate
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an Error by ID (idempotent).

        :param id: The error identifier.
        :type id: str
        '''
        raise NotImplementedError()
```

## Docstrings & guides

- **Docstrings & guides:** Interface class docstrings open with a 1–2 sentence vision-tier value statement, linked via `# >> see: @guides/interfaces.md#<anchor>` to `docs/guides/interfaces.md`, which carries the full distillation-tier detail. See `tiferet-guide-docs` for the complete convention.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md
