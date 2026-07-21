# Interfaces in Tiferet

Interfaces are a core component of the Tiferet framework, defining service contracts that specify the anticipated structure and behavior of services used by commands and domain events, aligning with Domain-Driven Design (DDD) principles. In the current evolution of Tiferet, **Services** serve as the **unified vertical contracts** — abstract base classes that act as the primary interface for all domain-specific orchestration, data access, configuration management, middleware, and utility behavior.

This document focuses exclusively on **Services** as the vertical contracts.

## What is a Service?

A **Service** in Tiferet is an abstract class derived from `tiferet.interfaces.settings.Service` (a minimal `ABC`) that defines the expected behavior for vertical concerns in the application. Services act as the contracts that:

- Abstract data access (CRUD operations, existence checks, listing)
- Manage configuration persistence (loading/saving structured data from YAML/JSON/etc.)
- Provide middleware and utility behavior (file handling, context management, validation, caching)
- Coordinate domain logic while hiding infrastructure details

**Commands** and **domain events** depend on Service instances to perform persistence, retrieval, or orchestration (e.g., `error_service.save(error)`, `configuration_service.load(...)`). Services encapsulate the infrastructure details, allowing commands and events to remain pure domain logic.

### Role in Runtime
- **Commands** and **domain events** are the primary consumers of Services.
- Commands and events use Services to delegate vertical concerns (data access, configuration, file I/O, etc.).
- Concrete implementations (YAML-backed repositories, middleware classes) satisfy the Service interfaces while hiding implementation details.
- **Factories** (e.g., `ConfigurationFileRepository`) resolve the correct concrete Service at runtime based on context (file type, etc.).

### Key Characteristics of Services as Vertical Contracts
- **Vertical abstraction**: They cross the domain ↔ infrastructure boundary, hiding how data is stored, files are managed, or middleware is applied.
- **Unified interface**: All vertical concerns (previously handled by repositories, configuration loaders, middleware, utilities) converge under `Service`.
- **Swappable implementations**: Consumers depend only on the Service contract, so concrete implementations can be substituted without changing domain logic.
- **Extensibility**: New concerns (e.g., authentication, logging, rate limiting) can be added as new Service interfaces or layered inside existing ones.

In the error domain, `ErrorService` is the vertical contract that all error-related commands depend on. In configuration handling, `ConfigurationService` abstracts YAML/JSON loading and saving, with concrete middleware implementations satisfying the interface.

## Structured Code Design of Services

Services follow Tiferet's structured code style using artifact comments for organization and readability.

### Artifact Comments

Services are organized under the `# *** interfaces` top-level comment, with individual Services under `# ** interface: <snake_case_name>`. Within each Service:

- `# * attribute: <name>` — Declares expected instance attributes (type hints only).
- `# * method: <name>` — Defines abstract methods marked with `@abstractmethod`.

No `# * method: new` is used, as Services are interfaces.

**Example** – `tiferet/interfaces/error.py`:
```python
# *** interfaces

# ** interface: error_service
class ErrorService(Service):
    '''
    Vertical interface for managing error domain objects.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if an error exists.
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str) -> Error:
        '''
        Retrieve an error by ID.
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Error]:
        '''
        List all errors.
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, error: Error) -> None:
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

**Example** – `tiferet/interfaces/config.py` (configuration):
```python
# ** interface: configuration_service
class ConfigurationService(Service):
    '''
    Vertical interface for loading and saving structured configuration data.
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

**Example** – `tiferet/interfaces/file.py` (low-level middleware/utility):
```python
# ** interface: file_service
class FileService(Service):
    '''
    Vertical interface for low-level file stream management.
    '''

    # * method: open_file
    @abstractmethod
    def open_file(self):
        '''
        Open the configured file stream.
        '''
        raise NotImplementedError()

    # * method: close_file
    @abstractmethod
    def close_file(self):
        '''
        Close the file stream.
        '''
        raise NotImplementedError()
```

## Creating New and Extending Services

1. **Define a New Service Interface**
   - Place under `# *** interfaces` in a domain-specific module.
   - Extend `Service` from `tiferet.interfaces.settings`.
   - Define abstract methods with domain-appropriate signatures.

2. **Implement the Service**
   - Concrete classes implement the Service interface.
   - Middleware-style implementations often inherit from lower-level middleware while implementing the target Service.
   - Use factories (e.g., `ConfigurationFileRepository.open_config()`) to resolve concrete implementations dynamically.

3. **Use in Commands and Domain Events**
   - Declare the Service as a constructor dependency (e.g., `error_service: ErrorService`).
   - Depend only on the interface for all vertical operations.

## Best Practices
- Use artifact comments consistently (`# * method`, `# * attribute`).
- Define methods with clear RST docstrings, type hints, and domain intent.
- Use `@abstractmethod` to enforce implementation.
- Keep services focused but composable (layer via inheritance or decoration).
- Depend on Service contracts in commands and events — never hard-code concrete classes.
- Maintain one empty line between sections, comments, and code blocks.

## MiddlewareService

`MiddlewareService` (`tiferet/interfaces/middleware.py`) is the abstract contract for domain event middleware — a cross-cutting concern that wraps the execution of a domain event. Middleware is composed into an ordered chain, where each one may run logic before and after delegating to the next, letting concerns such as validation, logging, or timing layer around an event without changing the event itself.

```python
# *** interfaces

# ** interface: middleware_service
class MiddlewareService(Service):
    '''
    Abstract service interface for domain event middleware.
    '''

    # * method: __call__
    @abstractmethod
    def __call__(self,
            event: Any,
            kwargs: Dict[str, Any],
            next_fn: Callable[[], Any]) -> Any:
        '''
        Execute the middleware, calling next_fn() to continue the chain.

        In async execution contexts next_fn is a coroutine function
        and must be awaited.
        '''
        raise NotImplementedError()
```

For async middleware, implement `async def __call__` and `await next_fn()`. The interface is exported from `tiferet.interfaces` as `MiddlewareService`.

## Conclusion

Services are the unified vertical interfaces in Tiferet, serving as the primary interface for middleware, data access, configuration management, and utilities. Commands and domain events depend exclusively on these Service interfaces, achieving high decoupling, testability, and extensibility. Concrete implementations satisfy the Service interfaces while hiding infrastructure details.

Explore `tiferet/interfaces/` for base definitions and `tiferet/repos/` for implementation patterns.
