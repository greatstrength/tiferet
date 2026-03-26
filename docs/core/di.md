# Dependency Injection in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The `tiferet/di/` package provides the **app-level dependency injection** layer for the Tiferet framework. It defines the `ServiceProvider` abstract base class and its concrete implementation, `DependenciesServiceProvider`, which backs the `AppManagerContext` during interface loading.

The `di/` package is distinct from the feature-level DI managed by `DIContext` (`contexts/di.py`):

- **`tiferet/di/`** — App-level DI. Manages the lifecycle of injected contexts and repositories for an interface (e.g., `FeatureContext`, `ErrorContext`, `LoggingContext`). Consumed by `AppManagerContext`.
- **`tiferet/contexts/di.py` (`DIContext`)** — Feature-level DI. Loads `ServiceConfiguration` objects, resolves flagged dependencies, and builds per-flag injectors for feature execution. Consumed by `FeatureContext`.

This document describes the structure, design principles, and best practices for writing and extending the DI layer, adhering to Tiferet's structured code style ([docs/core/code_style.md](code_style.md)).

## What is a ServiceProvider?

A `ServiceProvider` is an abstract class that manages a registry of service IDs and their corresponding types or values. It wraps the runtime dependency injector and exposes a simple, consistent API for registering and resolving services.

Key characteristics:
- Extends `ServiceProvider` (ABC) from `tiferet/di/settings.py`.
- Maintains a `services` dictionary mapping service IDs to types or scalar values.
- Rebuilds its internal injector every time the registry is mutated.
- Uses `RaiseError.execute()` for structured error handling.
- Returns fully resolved instances via `get_service()` — callers never interact with the injector directly.

### Role in Runtime

`AppManagerContext` holds a single `ServiceProvider` instance for the lifetime of an interface load:

1. `AppManagerContext.__init__` creates a `DependenciesServiceProvider` (or accepts an injected one).
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

- **`add_service(service_id, service_type)`** — Registers a single service type under an ID.
- **`add_services(services)`** — Bulk-registers a `Dict[str, type]` mapping. Equivalent to calling `add_service` for each entry. Prefer this for registering multiple services at once (e.g., all interface dependencies from `get_service_type_mapping()`).
- **`add_constants(constants)`** — Registers scalar values (strings, integers, etc.) as constructor injection parameters. **Important:** scalars registered this way are injected into other services at construction time; they cannot be resolved directly via `get_service`. See [Scalar Constants vs. Service Types](#scalar-constants-vs-service-types) below.
- **`get_service(service_id)`** — Returns the fully resolved service instance. Raises `INVALID_DEPENDENCY_ERROR` if the service cannot be resolved.
- **`remove_service(service_id)`** — Deregisters a service. No-op if the ID is not present.

## The DependenciesServiceProvider

`DependenciesServiceProvider` is the concrete implementation in `tiferet/di/dependencies.py`. It satisfies the `ServiceProvider` contract using the [`dependencies`](https://pypi.org/project/dependencies/) library's `Injector` as its backing resolver.

### Key Design Decisions

**Injector rebuild on every mutation.** Each call to `add_service`, `add_services`, `add_constants`, or `remove_service` triggers `build_injector()`, which creates a new `Injector` subclass type from the current `services` dict. This is intentional — injectors in the `dependencies` library are immutable class definitions, so they must be recreated to reflect changes.

**Empty scope guard.** The `dependencies` library raises `DependencyError: Extension scope can not be empty` when an `Injector` is created with no attributes. `build_injector` guards against this by setting `self.injector = None` when `services` is empty. `get_service` checks for `None` and raises `INVALID_DEPENDENCY_ERROR` immediately rather than letting the library raise.

**Named injector.** The `_name` attribute is stored at construction time and used as the class name for every rebuilt `Injector` type. The default is `'TiferetInjector'`. Pass a custom `name` via `__init__` or `new()` when you need distinguishable repr output (e.g., in tests or logging).

```python
# tiferet/di/dependencies.py

# ** class: dependencies_service_provider
class DependenciesServiceProvider(ServiceProvider):

    # * attribute: services
    services: Dict[str, type]

    # * attribute: injector
    injector: type          # Injector subclass type, or None if empty

    # * attribute: _name
    _name: str

    # * init
    def __init__(self, services: Dict[str, type] = None, name: str = 'TiferetInjector'):
        self._name = name
        self.services = services or {}
        self.build_injector()

    # * method: new (static)
    @staticmethod
    def new(name: str, dependencies: Dict[str, type]) -> 'DependenciesServiceProvider':
        return DependenciesServiceProvider(services=dependencies, name=name)

    # * method: build_injector
    def build_injector(self):
        if self.services:
            self.injector = type(self._name, (Injector,), self.services)
        else:
            self.injector = None
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

**Example** — `dependencies.py` layout:
```python
# *** imports

# ** core
from typing import Any, Dict

# ** infra
from dependencies import Injector
from dependencies.exceptions import DependencyError

# ** app
from ..events import RaiseError
from .settings import ServiceProvider


# *** classes

# ** class: dependencies_service_provider
class DependenciesServiceProvider(ServiceProvider):
    '''...'''

    # * attribute: services
    services: Dict[str, type]

    # * init
    def __init__(self, services: Dict[str, type] = None, name: str = 'TiferetInjector'):
        ...

    # * method: new (static)
    @staticmethod
    def new(name: str, dependencies: Dict[str, type]) -> 'DependenciesServiceProvider':
        ...
```

## Scalar Constants vs. Service Types

The `add_constants` method accepts plain scalar values (strings, numbers, booleans) alongside class types. These behave differently inside the injector:

- **Service types** (classes): Resolved by the `dependencies` library through instantiation. Accessed via `get_service(service_id)`.
- **Scalar constants**: Injected as constructor parameters into other services that declare them as `__init__` arguments. They **cannot** be accessed directly via `get_service` — the library raises `DependencyError: Scalar dependencies could only be used to instantiate classes`.

```python
# Correct use of add_constants — injectable into a service constructor.
provider.add_services({'configurable_repo': MyYamlRepository})
provider.add_constants({'my_yaml_file': 'app/configs/my.yml'})

# MyYamlRepository(my_yaml_file) is resolved correctly:
repo = provider.get_service('configurable_repo')  # ✓

# Accessing the scalar directly raises INVALID_DEPENDENCY_ERROR:
path = provider.get_service('my_yaml_file')  # ✗
```

## Creating a New ServiceProvider Implementation

To provide an alternative DI backend (e.g., backed by a different IoC library or a simple dict for testing), extend `ServiceProvider` from `tiferet/di/settings.py` and implement all abstract methods.

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

Inject a custom provider into `AppManagerContext` via the `service_provider` parameter:

```python
app = AppManagerContext(service_provider=SimpleServiceProvider())
```

## Testing ServiceProvider Implementations

Tests live in `tiferet/di/tests/` and follow the standard artifact comment structure.

### Key Patterns

- Test `init` with no services — assert `injector is None` (empty scope guard).
- Test `init` with services — assert types are registered and resolvable.
- Test `add_service` / `add_services` — assert services resolve to the correct types.
- Test `add_constants` — register a service that depends on the constant, resolve the service, and assert the value was injected.
- Test `get_service` on an unregistered ID — assert `TiferetError` with `error_code == 'INVALID_DEPENDENCY_ERROR'`.
- Test `remove_service` — assert the service is gone and no longer resolvable.
- Test `remove_service` on an unknown ID — assert no exception is raised.
- Test injector rebuild — assert `injector` reference changes after mutation.

```python
# *** fixtures

# ** fixture: populated_provider
@pytest.fixture
def populated_provider() -> DependenciesServiceProvider:
    '''Pre-populated provider for success-path tests.'''
    return DependenciesServiceProvider(services={'my_service': MyService})


# *** tests

# ** test: get_service_success
def test_get_service_success(populated_provider: DependenciesServiceProvider):
    '''Test that a registered service resolves to the correct type.'''

    # Resolve the service.
    service = populated_provider.get_service('my_service')

    # Assert it is the expected type.
    assert isinstance(service, MyService)


# ** test: get_service_not_found
def test_get_service_not_found():
    '''Test that an unregistered service raises INVALID_DEPENDENCY_ERROR.'''

    # Create an empty provider.
    provider = DependenciesServiceProvider()

    # Attempt to resolve an unknown service.
    with pytest.raises(TiferetError) as exc_info:
        provider.get_service('missing')

    # Assert the correct error code.
    assert exc_info.value.error_code == 'INVALID_DEPENDENCY_ERROR'
```

## Package Layout

```
tiferet/di/
├── __init__.py          — Exports: ServiceProvider, DependenciesServiceProvider
├── settings.py          — ServiceProvider (ABC)
├── dependencies.py      — DependenciesServiceProvider (dependencies-library-backed)
└── tests/
    ├── __init__.py
    └── test_dependencies.py
```

## Conclusion

The `tiferet/di/` package provides the app-level DI foundation for the Tiferet framework, abstracting the lifecycle of contexts and repositories behind the `ServiceProvider` contract. The `DependenciesServiceProvider` satisfies this contract using the `dependencies` library while handling the library's constraints (empty scope guard, scalar injection limitations) transparently.

New implementations extend `ServiceProvider` and override all abstract methods. Inject them into `AppManagerContext` via the `service_provider` constructor parameter to swap backends without changing application code.

Explore source in `tiferet/di/`, runtime consumers in `tiferet/contexts/app.py`, and tests in `tiferet/di/tests/`.
