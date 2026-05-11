# Dependency Injection in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The `tiferet/di/` package provides the **app-level dependency injection** layer for the Tiferet framework. It defines the `ServiceProvider` abstract base class and its concrete implementation, `DynamicServiceProvider`, which backs `AppBuilder` during interface loading.

The `di/` package is distinct from the feature-level DI managed by `DIContext` (`contexts/di.py`):

- **`tiferet/di/`** — App-level DI. Manages the lifecycle of injected contexts and repositories for an interface (e.g., `FeatureContext`, `ErrorContext`, `LoggingContext`). Consumed by `AppBuilder`.
- **`tiferet/contexts/di.py` (`DIContext`)** — Feature-level DI. Loads `ServiceConfiguration` objects, resolves flagged dependencies, and builds per-flag providers for feature execution. Consumed by `FeatureContext`.

This document describes the structure, design principles, and best practices for writing and extending the DI layer, adhering to Tiferet's structured code style ([docs/core/code_style.md](code_style.md)).

## What is a ServiceProvider?

A `ServiceProvider` is an abstract class that manages a registry of service IDs and their corresponding types or values. It wraps the runtime dependency injector and exposes a simple, consistent API for registering and resolving services.

Key characteristics:
- Extends `ServiceProvider` (ABC) from `tiferet/di/settings.py`.
- Uses `RaiseError.execute()` for structured error handling.
- Returns fully resolved instances via `get_service()` — callers never interact with the container directly.

### Role in Runtime

`AppBuilder` holds a single `ServiceProvider` instance for the lifetime of an interface load:

1. `AppBuilder.__init__` creates a `DynamicServiceProvider` via `create_service_provider()`.
2. `load_interface` calls `app_interface.get_service_type_mapping()` to obtain a `Dict[str, type]`.
3. `load_app_instance` calls `service_provider.add_services(dependencies)` to register all interface dependencies.
4. `service_provider.get_service('app_context')` resolves and returns the fully constructed `AppInterfaceContext`.

## The ServiceProvider Abstract Base

`ServiceProvider` is defined in `tiferet/di/settings.py` and declares the contract all implementations must satisfy:

```python
# tiferet/di/settings.py

# *** classes

# ** class: service_provider
class ServiceProvider(ABC):
    '''
    Service provider for app context dependencies.
    '''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service_type: type): ...

    # * method: add_services
    @abstractmethod
    def add_services(self, services: Dict[str, type]): ...

    # * method: add_constants
    @abstractmethod
    def add_constants(self, constants: Dict[str, Any]): ...

    # * method: get_service
    @abstractmethod
    def get_service(self, service_id: str) -> Any: ...

    # * method: remove_service
    @abstractmethod
    def remove_service(self, service_id: str): ...
```

### Method Semantics

- **`add_service(service_id, service_type)`** — Registers a single service type under an ID as a `Factory` provider.
- **`add_services(services)`** — Bulk-registers a `Dict[str, type]` mapping. Class types are registered as `Factory` providers (new instance per resolution); non-type values (scalars, callables, etc.) are registered as `Object` providers (pass-through).
- **`add_constants(constants)`** — Registers scalar values (strings, numbers, booleans) as `Object` providers. Unlike the previous `dependencies` library backend, constants **can** be resolved directly via `get_service`.
- **`get_service(service_id)`** — Returns the fully resolved service instance. Raises `INVALID_DEPENDENCY_ERROR` if the service cannot be resolved.
- **`remove_service(service_id)`** — Deregisters a service. No-op if the ID is not present.

## The DynamicServiceProvider

`DynamicServiceProvider` is the concrete implementation in `tiferet/di/dynamic.py`. It satisfies the `ServiceProvider` contract using [`dependency-injector`](https://pypi.org/project/dependency-injector/)'s `DynamicContainer` as its backing resolver.

### Key Design Decisions

**DynamicContainer.** The `dependency-injector` library provides `DynamicContainer`, which supports runtime provider registration via `set_provider()`. Unlike the previous `dependencies` library (which required rebuilding an immutable `Injector` subclass on every mutation), providers can be added and removed incrementally.

**Provider types.** Two provider types are used:
- `Factory` — Wraps a class type. Each `get_service()` call creates a new instance with constructor kwargs wired to sibling providers.
- `Object` — Wraps a scalar value or callable. Each `get_service()` call returns the same value.

**Automatic constructor wiring.** `build_factory()` inspects the service class constructor via `inspect.signature()` and wires each parameter to a sibling provider if one exists. This enables cascading dependency resolution without explicit wiring configuration.

**No empty scope guard needed.** Unlike the `dependencies` library, `DynamicContainer` works correctly with zero providers. No special `None` guard is required.

```python
# tiferet/di/dynamic.py

# ** class: dynamic_service_provider
class DynamicServiceProvider(ServiceProvider):

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        self.container = containers.DynamicContainer()
        if services:
            self.add_services(services)

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        factory = self.build_factory(service_type)
        self.container.set_provider(service_id, factory)

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        for service_id, value in services.items():
            if isinstance(value, type):
                self.add_service(service_id, value)
            else:
                self.container.set_provider(service_id, providers.Object(value))

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        provider = self.container.providers.get(service_id)
        if provider is None:
            RaiseError.execute('INVALID_DEPENDENCY_ERROR', ...)
        return provider()

    # * method: build_factory
    def build_factory(self, service_type: type) -> providers.Factory:
        sig = inspect.signature(service_type.__init__)
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self' or param.kind in (VAR_POSITIONAL, VAR_KEYWORD):
                continue
            sibling = self.container.providers.get(param_name)
            if sibling is not None:
                kwargs[param_name] = sibling
        return providers.Factory(service_type, **kwargs)
```

## Structured Code Design

The `di/` package uses `# *** classes` / `# ** class:` artifact comments, consistent with other `settings.py` modules in the framework (e.g., `domain/settings.py`).

### Artifact Comments

- `# *** classes` — top-level section for the module.
- `# ** class: <snake_case_name>` — individual class definition.
- `# * attribute: <name>` — instance attributes (type hints only, no assignment).
- `# * init` — constructor.
- `# * method: <name>` — instance methods.
- `# * method: <name> (static)` — static methods.

**Spacing rules** follow `code_style.md`: one empty line between `# ***` and the first `# **`, one empty line between each `# *` section, one empty line after docstrings, and one empty line between code snippets.

**Example** — `settings.py` layout:
```python
# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Dict, Any


# *** classes

# ** class: service_provider
class ServiceProvider(ABC):
    '''...'''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service_type: type):
        ...
```

**Example** — `dynamic.py` layout:
```python
# *** imports

# ** core
from typing import Any, Dict
import inspect

# ** infra
from dependency_injector import containers, providers

# ** app
from ..events import RaiseError
from .settings import ServiceProvider


# *** classes

# ** class: dynamic_service_provider
class DynamicServiceProvider(ServiceProvider):
    '''...'''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        ...

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        ...
```

## Provider Types and Registration

### Factory Providers (Class Types)

When a class type is registered via `add_service()`, it is wrapped in a `providers.Factory`. Each resolution creates a new instance with constructor kwargs wired to sibling providers:

```python
provider.add_service('feature_service', FeatureYamlRepository)
provider.add_constants({'feature_yaml_file': 'app/configs/feature.yml'})

# FeatureYamlRepository(feature_yaml_file='app/configs/feature.yml') is resolved:
repo = provider.get_service('feature_service')  # ✓ new instance each time
```

### Object Providers (Scalars and Callables)

Non-type values registered via `add_services()` or `add_constants()` are wrapped in `providers.Object`. Each resolution returns the same value:

```python
provider.add_constants({'app_config_file': 'app/configs/app.yml'})

# Direct scalar resolution works (unlike the previous dependencies library):
path = provider.get_service('app_config_file')  # ✓ returns 'app/configs/app.yml'
```

## Creating a New ServiceProvider Implementation

To provide an alternative DI backend (e.g., for testing), extend `ServiceProvider` from `tiferet/di/settings.py` and implement all abstract methods.

**Example** — `SimpleServiceProvider` (dict-backed, for testing):
```python
# *** imports

# ** core
from typing import Any, Dict

# ** app
from ..events import RaiseError
from .settings import ServiceProvider


# *** classes

# ** class: simple_service_provider
class SimpleServiceProvider(ServiceProvider):
    '''
    A minimal dict-backed service provider for testing.
    '''

    # * attribute: registry
    registry: Dict[str, Any]

    # * init
    def __init__(self):
        '''Initialize with an empty registry.'''

        # Initialize the registry.
        self.registry = {}

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        '''Register a service type by ID.'''

        # Store the type in the registry.
        self.registry[service_id] = service_type

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        '''Bulk-register service types.'''

        # Merge the services into the registry.
        self.registry.update(services)

    # * method: add_constants
    def add_constants(self, constants: Dict[str, Any]):
        '''Register scalar constants.'''

        # Merge the constants into the registry.
        self.registry.update(constants)

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        '''Return the registered value for service_id.'''

        # Raise an error if the service is not registered.
        if service_id not in self.registry:
            RaiseError.execute(
                'INVALID_DEPENDENCY_ERROR',
                f'Dependency {service_id} could not be resolved.',
                dependency_name=service_id,
                exception='Service not registered.',
            )

        # Return the registered value.
        return self.registry[service_id]

    # * method: remove_service
    def remove_service(self, service_id: str):
        '''Deregister a service by ID.'''

        # Remove the service from the registry if present.
        self.registry.pop(service_id, None)
```

Inject a custom provider into `AppBuilder` via the `create_service_provider` static method or by subclassing.

## Testing ServiceProvider Implementations

Tests live in `tiferet/di/tests/` and follow the standard artifact comment structure.

### Key Patterns

- Test `init` with no services — assert container has no providers.
- Test `init` with services — assert types are registered and resolvable.
- Test `add_service` / `add_services` — assert services resolve to the correct types.
- Test `add_constants` — register a constant, resolve it directly, and register a service that depends on it to verify injection.
- Test `get_service` on an unregistered ID — assert `TiferetError` with `error_code == 'INVALID_DEPENDENCY_ERROR'`.
- Test `remove_service` — assert the service is gone and no longer resolvable.
- Test `remove_service` on an unknown ID — assert no exception is raised.

```python
# *** fixtures

# ** fixture: populated_provider
@pytest.fixture
def populated_provider() -> DynamicServiceProvider:
    '''Pre-populated provider for success-path tests.'''
    return DynamicServiceProvider(services={'my_service': MyService})


# *** tests

# ** test: get_service_success
def test_get_service_success(populated_provider: DynamicServiceProvider):
    '''Test that a registered service resolves to the correct type.'''

    # Resolve the service.
    service = populated_provider.get_service('my_service')

    # Assert it is the expected type.
    assert isinstance(service, MyService)


# ** test: get_service_not_found
def test_get_service_not_found():
    '''Test that an unregistered service raises INVALID_DEPENDENCY_ERROR.'''

    # Create an empty provider.
    provider = DynamicServiceProvider()

    # Attempt to resolve an unknown service.
    with pytest.raises(TiferetError) as exc_info:
        provider.get_service('missing')

    # Assert the correct error code.
    assert exc_info.value.error_code == 'INVALID_DEPENDENCY_ERROR'
```

## Backward Compatibility

A backward-compatible alias is provided in `tiferet/di/__init__.py`:

```python
DependenciesServiceProvider = DynamicServiceProvider
```

Downstream consumers importing `DependenciesServiceProvider` will receive `DynamicServiceProvider` transparently. The `ServiceProvider` ABC is unchanged.

## Package Layout

```
tiferet/di/
├── __init__.py          — Exports: ServiceProvider, DynamicServiceProvider (+ backward-compat alias)
├── settings.py          — ServiceProvider (ABC)
├── dynamic.py           — DynamicServiceProvider (dependency-injector-backed)
└── tests/
    ├── __init__.py
    └── test_dynamic.py
```

## Conclusion

The `tiferet/di/` package provides the app-level DI foundation for the Tiferet framework, abstracting the lifecycle of contexts and repositories behind the `ServiceProvider` contract. The `DynamicServiceProvider` satisfies this contract using the `dependency-injector` library's `DynamicContainer`, providing incremental provider registration, automatic constructor wiring, and direct scalar resolution.

New implementations extend `ServiceProvider` and override all abstract methods. Inject them into `AppBuilder` via the `create_service_provider` static method to swap backends without changing application code.

Explore source in `tiferet/di/`, runtime consumers in `tiferet/blueprints/main.py`, and tests in `tiferet/di/tests/`.
