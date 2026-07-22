---
name: tiferet-code-di
description: Apply DI layer conventions when adding or modifying ServiceContainer, ServiceResolver, or pure DI helper functions in a Tiferet-family repo. Covers the event-free/asset-free design constraint, ABC inheritance requirements, Factory vs Singleton scope, and the injectable_parameter_names helper.
---

# Dependency Injection Code Style – Tiferet

## When to use
- When adding or modifying classes in `tiferet/di/` (container, resolver, or base ABCs).
- When adding a pure DI helper function (`injectable_parameter_names`, `normalize_flags`).
- Do NOT use for domain events or assets — the DI layer is deliberately event-free and asset-free.

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; pure, stateless DI helpers
# *** di                 ← DI containers and resolvers
# *** exports            ← __init__.py only
```

DI-specific labels:
```
# *** functions                         ← artifact section: pure, stateless DI helpers
# ** function: <snake_case_name>        ← artifact

# *** di                                ← artifact section: containers and resolvers
# ** di: <snake_case_name>             ← artifact
# * attribute: <name>                   ← artifact member: instance attributes
# * init                                ← artifact member: constructor
# * method: <name>                      ← artifact member: instance methods
# * method: <name> (static)            ← artifact member: static methods
# * method: <name> (class)             ← artifact member: classmethods
```

## Key conventions

- **Layer boundary — valid `# ** app` imports:** `domain` (`ServiceDependency`), `interfaces.di` (`DIService`). Never import from `events`, `assets`, `mappers`, `repos`, `utils`, `contexts`, or `blueprints`.
- The DI layer is **event-free and asset-free**: imports only stdlib, `dependency_injector`, `..domain`, and (in `dependency_injector.py`) `..interfaces.di`. Never import `RaiseError`, `TiferetError`, `a.error`, or any other event/asset.
- Raw exceptions surface from DI classes; callers with event access convert them to structured errors.
- **All new DI components must extend either `ServiceContainer` or `ServiceResolver`** — there is no valid DI class that does not inherit from one of these two ABCs.
- **DI inverts the domain event principle:** Domain events expose a minimal interface (`execute`) to serve unlimited domain use cases. DI components expose a richer interface to solve one highly specific concern — dependency resolution. Both are injection targets, but in opposite directions of interface breadth vs. domain breadth.
- **`injectable_parameter_names(service_type)`** — returns constructor parameter names eligible for automatic wiring (excludes `self`, `*args`, `**kwargs`). Uninspectable types are treated as no-arg.
- **`normalize_flags(*flags)`** — flattens mixed string/list/tuple input into a flat string list. Key for cache-key consistency.
- **`ServiceContainer`** (ABC engine): abstract contract for registering and resolving dependencies. Methods: `add_service`, `add_constant`, `get_dependency`, `has_dependency`, `remove_dependency`, `load_container`.
- **`ServiceResolver`** (ABC provider): owns a per-flag `ServiceContainer` cache. Provides `add_container`, `get_container`, `get_dependency` (template method); leaves `build_container(flags)` abstract for subclasses.
- **App-level:** `DIAppServiceContainer` uses `Singleton` scope — one shared instance per app. Created via `from_dependencies(services, constants)` classmethod.
- **Feature-level:** `DIDynamicServiceResolver` uses `Factory` scope — a new instance per resolution. Built per flag set by `build_container`.
- Use `# *** di` as the construct group for all DI component classes. Use `# * method: <name> (class)` for `@classmethod` entries.

## Example

```python
# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import inspect

# ** app
from ..domain.core import ServiceDependency

# *** functions

# ** function: injectable_parameter_names
def injectable_parameter_names(service_type: type) -> List[str]:
    '''
    Return the injectable constructor parameter names of a service type.

    Excludes self, *args, and **kwargs. Types whose constructor cannot be
    inspected are treated as no-arg.

    :param service_type: The service class to inspect.
    :type service_type: type
    :return: A list of injectable parameter names.
    :rtype: List[str]
    '''

    # Inspect the constructor signature; treat uninspectable types as no-arg.
    try:
        sig = inspect.signature(service_type.__init__)
    except (ValueError, TypeError):
        return []

    # Collect injectable parameter names, skipping self and variadic params.
    return [
        name for name, param in sig.parameters.items()
        if name != 'self'
        and param.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )
    ]

# *** di

# ** di: service_container
class ServiceContainer(ABC):
    '''
    Abstract DI container contract for the framework.

    Defines core operations for registering service dependencies and constants,
    resolving them, and removing them. All new DI containers must extend this ABC.

    Event-free: raw exceptions surface; callers convert to structured errors.
    '''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency in the container.

        :param service_id: The service identifier.
        :type service_id: str
        :param service: The core service dependency.
        :type service: ServiceDependency
        '''
        raise NotImplementedError()

    # * method: add_constant
    @abstractmethod
    def add_constant(self, constant_id: str, value: Any):
        '''
        Register a constant value in the container.

        :param constant_id: The constant identifier.
        :type constant_id: str
        :param value: The constant value.
        :type value: Any
        '''
        raise NotImplementedError()

    # * method: get_dependency
    @abstractmethod
    def get_dependency(self, dependency_id: str) -> Any:
        '''
        Resolve a registered dependency by identifier.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: The resolved instance or value.
        :rtype: Any
        '''
        raise NotImplementedError()

    # * method: has_dependency
    @abstractmethod
    def has_dependency(self, dependency_id: str) -> bool:
        '''
        Return True when a dependency is registered under the given identifier.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: True when registered, False otherwise.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: remove_dependency
    @abstractmethod
    def remove_dependency(self, dependency_id: str):
        '''
        Remove a registered dependency from the container. Idempotent.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        '''
        raise NotImplementedError()

    # * method: load_container
    @abstractmethod
    def load_container(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Bulk-load the container from service dependencies and constants.

        :param services: A mapping of service id to core service dependency.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        '''
        raise NotImplementedError()
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md
