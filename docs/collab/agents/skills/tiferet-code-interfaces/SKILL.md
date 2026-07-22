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

- **Layer boundary — valid `# ** app` imports:** `domain` (for type hints in abstract method signatures); sibling `interfaces` modules. Never import from `events`, `mappers`, `repos`, `utils`, `contexts`, or `blueprints`.
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
from ..domain.error import Error

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
    def get(self, id: str) -> Optional[Error]:
        '''
        Retrieve an Error by its ID.

        :param id: The error identifier.
        :type id: str
        :return: The Error domain object, or None if not found.
        :rtype: Optional[Error]
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Error]:
        '''
        List all Error domain objects.

        :return: All stored errors.
        :rtype: List[Error]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, error: Error) -> None:
        '''
        Persist an Error domain object.

        :param error: The error to persist.
        :type error: Error
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

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md
