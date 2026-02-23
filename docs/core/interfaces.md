# Interfaces in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Interfaces are a core component of the Tiferet framework, defining abstract service contracts that specify the anticipated structure and behavior of services used by commands and domain events, aligning with Domain-Driven Design (DDD) principles. In the current evolution of Tiferet, **Services** serve as the **unified vertical contracts** — abstract base classes that act as the primary interface for all domain-specific orchestration, data access, configuration management, middleware, and utility behavior.

This document focuses exclusively on **Services** as the vertical interface definitions.

## What is a Service?

A **Service** in Tiferet is an abstract class derived from `tiferet.interfaces.settings.Service` (a minimal `ABC`) that defines the expected behavior for vertical concerns in the application. Services act as injectable interfaces that:

- Abstract data access (CRUD operations, existence checks, listing)
- Manage configuration persistence (loading/saving structured data from YAML/JSON/etc.)
- Provide middleware and utility behavior (file handling, context management, validation, caching)
- Coordinate domain logic while hiding infrastructure details

**Commands and domain events** depend on injected Service instances to perform persistence, retrieval, or orchestration (e.g., `error_service.save(error)`, `configuration_service.load(...)`). Services encapsulate the infrastructure details, allowing commands to remain pure domain logic.

### Role in Runtime
- **Commands and domain events** are the primary consumers of Services, receiving them via dependency injection (constructor).
- They use Services to delegate vertical concerns (data access, configuration, file I/O, etc.).
- Concrete implementations (YAML-backed repositories, middleware classes) satisfy the Service interfaces while hiding implementation details.
- **Factories** (e.g., `ConfigurationFileRepository`) resolve the correct concrete Service at runtime based on context (file type, etc.).

### Key Characteristics of Services as Vertical Interfaces
- **Vertical abstraction**: They cross the domain ↔ infrastructure boundary, hiding how data is stored, files are managed, or middleware is applied.
- **Unified interface**: All vertical concerns (previously handled by repositories, configuration loaders, middleware, utilities) converge under `Service`.
- **Dependency injection**: Services are injected into commands via containers or initializers, making implementations swappable.
- **Extensibility**: New concerns (e.g., authentication, logging, rate limiting) can be added as new Service interfaces or layered inside existing ones.

In the error domain, `ErrorService` is the vertical interface that all error-related commands depend on. In configuration handling, `ConfigurationService` abstracts YAML/JSON loading and saving, with concrete middleware implementations satisfying the interface.

## The Service Base Class

`Service` extends `abc.ABC` and serves as the minimal abstract base for all service interfaces:

```python
# tiferet/interfaces/settings.py

from abc import ABC

class Service(ABC):
    '''
    The service interface as an abstract base class.
    '''

    pass
```

All domain-specific service interfaces extend `Service`.

## Structured Code Design of Interfaces

Interfaces follow Tiferet's structured code style using artifact comments for organization and readability.

### Artifact Comments

Interfaces are organized under the `# *** interfaces` top-level comment, with individual interfaces under `# ** interface: <snake_case_name>`. Within each interface:

- `# * attribute: <name>` — Declares expected instance attributes (type hints only).
- `# * method: <name>` — Defines abstract methods marked with `@abstractmethod`.

No `# * method: new` is used, as interfaces are abstract definitions.

**Spacing rules:**
- One empty line between `# *** interfaces` and first `# ** interface`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

**Example** — `ErrorService`:
```python
# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from .settings import Service

# *** interfaces

# ** interface: error_service
class ErrorService(Service):
    '''
    Service interface for managing error objects.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if an error exists by ID.
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve an error by ID.
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List:
        '''
        List all errors.
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, error) -> None:
        '''
        Persist an error.
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an error by ID.
        '''
        raise NotImplementedError()
```

**Example** — `ConfigurationService`:
```python
# ** interface: configuration_service
class ConfigurationService(Service):
    '''
    Interface for loading and saving structured configuration data.
    '''

    # * method: load
    @abstractmethod
    def load(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Any:
        '''
        Load configuration data.
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, data: Any, data_path: str = None, **kwargs):
        '''
        Save configuration data.
        '''
        raise NotImplementedError()
```

## Creating New and Extending Interfaces

### 1. Define a New Service Interface
- Place under `# *** interfaces` and `# ** interface: <name>` in a domain-specific module (e.g., `tiferet/interfaces/calculator.py`).
- Extend `Service` from `tiferet.interfaces.settings`.
- Define abstract methods with domain-appropriate signatures.
- Mark all methods with `@abstractmethod`.

**Example** — `CalculatorService`:
```python
# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from tiferet.interfaces.settings import Service

# *** interfaces

# ** interface: calculator_service
class CalculatorService(Service):
    '''
    Service interface for calculator operations.
    '''

    # * method: compute
    @abstractmethod
    def compute(self, operation: str, a: float, b: float) -> float:
        '''
        Perform a computation.
        '''
        raise NotImplementedError()

    # * method: history
    @abstractmethod
    def history(self) -> List:
        '''
        Retrieve computation history.
        '''
        raise NotImplementedError()
```

### 2. Implement the Interface
- Concrete classes implement the Service interface.
- Middleware-style implementations often inherit from lower-level middleware while implementing the target Service.
- Use factories to resolve concrete implementations dynamically.

### 3. Use in Commands / Domain Events
- Inject the Service via constructor (e.g., `error_service: ErrorService`).
- Depend only on the interface for all vertical operations.

### Best Practices
- Use artifact comments (`# * method`, `# * attribute`) consistently.
- Define methods with clear RST docstrings, type hints, and domain intent.
- Use `@abstractmethod` to enforce implementation.
- Keep services focused but composable (layer via inheritance or decoration).
- Inject Services into commands — never hard-code concrete classes.
- Maintain one empty line between sections, comments, and code blocks.

## Migration from Contracts

In v2.0, the `tiferet/contracts/` package was renamed to `tiferet/interfaces/`. The artifact comments were updated from `# *** contracts` / `# ** contract:` to `# *** interfaces` / `# ** interface:`. The `Service` base class and all service interface APIs remain identical — only the package name and artifact comment labels have changed.

The `tiferet/contracts/` package remains available for backward compatibility. New code should define service interfaces in `tiferet/interfaces/`.

## Package Layout

Interfaces are defined in `tiferet/interfaces/`:

- `settings.py` — `Service(ABC)` base class.
- `app.py` — `AppService`.
- `cache.py` — `CacheService`.
- `cli.py` — `CliService`.
- `config.py` — `ConfigurationService`.
- `container.py` — `ContainerService`.
- `error.py` — `ErrorService`.
- `feature.py` — `FeatureService`.
- `file.py` — `FileService`.
- `logging.py` — `LoggingService`.
- `sqlite.py` — `SqliteService`.
- `__init__.py` — Public exports for all service interfaces.

## Conclusion

Services are the unified vertical interfaces in Tiferet, serving as the primary abstract definitions for middleware, data access, configuration management, and utilities. Commands and domain events depend exclusively on these Service interfaces, achieving high decoupling, testability, and extensibility. Concrete implementations satisfy the Service interfaces while hiding infrastructure details.

Explore `tiferet/interfaces/` for current service definitions and `tiferet/repos/` for implementation patterns.
