---
name: tiferet-code-di
description: Apply DI layer conventions when adding or modifying ServiceContainer, ServiceResolver, or pure DI helper functions in a Tiferet-family repo. Covers the event-free/asset-free design constraint, Factory vs Singleton scope, and the injectable_parameter_names helper.
---

# Dependency Injection Code Style – Tiferet

## When to use
- When adding or modifying classes in `tiferet/di/` (container, resolver, or base ABCs).
- When adding a pure DI helper function (`injectable_parameter_names`, `normalize_flags`, `create_cache_key`, `merge_settings`).
- Do NOT use for domain events or assets — the DI layer is deliberately event-free and asset-free.

## Artifact comment structure

```
# *** functions                         ← pure, stateless DI helpers
# ** function: <snake_case_name>        ← individual function

# *** classes                           ← base classes and concrete implementations
# ** class: <snake_case_name>           ← individual class (ABCs and implementations)
# * attribute: <name>                   ← instance attributes
# * init                                ← constructor
# * method: <name>                      ← instance methods
# * method: <name> (static)             ← static methods
# * method: <name> (class)              ← classmethods
```

## Key conventions

- The DI layer is **event-free and asset-free**: imports only stdlib, `dependency_injector`, `..domain`, and (in `dependency_injector.py`) `..interfaces.di`. Never import `RaiseError`, `TiferetError`, `a.const`, or any other event/asset.
- Raw exceptions surface from DI classes; callers with event access convert them to structured errors.
- **`injectable_parameter_names(service_type)`** — returns constructor parameter names eligible for automatic wiring (excludes `self`, `*args`, `**kwargs`). Use in `build_factory` / `build_singleton` to wire sibling providers automatically.
- **`normalize_flags(*flags)`** — flattens mixed string/list/tuple input into a flat string list. Key for cache-key consistency.
- **`ServiceContainer`** (engine): registers services as `Factory` providers (one new instance per resolution) or `Object` providers (scalars/callables). `add_service(id, dependency)` wires constructor kwargs to sibling providers.
- **`ServiceResolver`** (provider): owns a per-flag `ServiceContainer` cache. Template-method `get_dependency(service_id, *flags)` normalizes flags, looks up or builds a container, then delegates. Only `build_container(flags)` is abstract.
- **App-level:** `DIAppServiceContainer` uses `Singleton` scope — one shared instance per app. Created via `from_dependencies(services, constants)` classmethod.
- **Feature-level:** `DIDynamicServiceResolver` uses `Factory` scope — a new instance per resolution. Built per flag set by `build_container`.
- Use `# *** classes` in all DI modules (no `# *** di` group). Use `# * method: <name> (class)` for `@classmethod` entries.

## Example

```python
# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Any, Dict, List

# ** infra
from dependency_injector import containers, providers

# ** app
from ..domain.core import ServiceDependency

# *** functions

# ** function: injectable_parameter_names
def injectable_parameter_names(service_type: type) -> List[str]:
    '''
    Return the injectable constructor parameter names of a service type.

    Excludes self and variadic parameters (*args, **kwargs).

    :param service_type: The service class to inspect.
    :type service_type: type
    :return: A list of injectable parameter names.
    :rtype: List[str]
    '''

    import inspect

    # Inspect the constructor signature.
    sig = inspect.signature(service_type.__init__)

    # Collect injectable parameter names.
    return [
        name for name, param in sig.parameters.items()
        if name != 'self'
        and param.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )
    ]

# *** classes

# ** class: service_container
class ServiceContainer(object):
    '''
    Low-level dependency-injection engine backed by DynamicContainer.

    Event-free: missing or failing providers raise raw exceptions.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        '''
        Initialize the service container.

        :param services: Optional initial service type mapping.
        :type services: Dict[str, type]
        '''

        # Create the dynamic container.
        self.container = containers.DynamicContainer()

        # Bulk-load any initial services.
        if services:
            self.add_services(services)

    # * method: add_services
    def add_services(self, services: Dict[str, Any]):
        '''
        Bulk-register services: scalars as Object providers, types as Factories.

        :param services: Mapping of service ID to type or scalar value.
        :type services: Dict[str, Any]
        '''

        # Register scalars first so factories can wire to them.
        for service_id, value in services.items():
            if not isinstance(value, type):
                self.container.set_provider(service_id, providers.Object(value))

        # Register class types as Factory providers.
        for service_id, value in services.items():
            if isinstance(value, type):
                factory = self._build_factory(value)
                self.container.set_provider(service_id, factory)

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        '''
        Resolve and return a registered service instance.

        :param service_id: The service identifier.
        :type service_id: str
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Look up and invoke the provider; raises raw exception if missing.
        provider = self.container.providers.get(service_id)
        return provider()

    # * method: _build_factory (static)
    @staticmethod
    def _build_factory(service_type: type) -> providers.Factory:
        '''
        Build a Factory provider with constructor kwargs wired to sibling providers.

        :param service_type: The class to wrap in a Factory provider.
        :type service_type: type
        :return: The configured Factory provider.
        :rtype: providers.Factory
        '''

        # Wire each injectable parameter to a sibling provider.
        kwargs = {}
        for param_name in injectable_parameter_names(service_type):
            sibling = ServiceContainer.container.providers.get(param_name)
            if sibling is not None:
                kwargs[param_name] = sibling
        return providers.Factory(service_type, **kwargs)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md
