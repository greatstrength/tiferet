# Contracts in Tiferet

Contracts are a core component of the Tiferet framework, defining interfaces that specify the anticipated structure and behavior of services used by commands, aligning with Domain-Driven Design (DDD) principles. In the current evolution of Tiferet, **Services** serve as the **unified vertical contracts** — abstract base classes that act as the primary interface for all domain-specific orchestration, data access, configuration management, middleware, and utility behavior.

This document focuses exclusively on **Services** as the vertical contracts.

## What is a Service?

A **Service** in Tiferet is an abstract class derived from `tiferet.contracts.settings.Service` (a minimal `ABC`) that defines the expected behavior for vertical concerns in the application. Services act as injectable interfaces that:

- Abstract data access (CRUD operations, existence checks, listing)
- Manage configuration persistence (loading/saving structured data from YAML/JSON/etc.)
- Provide middleware and utility behavior (file handling, context management, validation, caching)
- Coordinate domain logic while hiding infrastructure details

**Commands** depend on injected Service instances to perform persistence, retrieval, or orchestration (e.g., `error_service.save(error)`, `configuration_service.load(...)`). Services encapsulate the infrastructure details, allowing commands to remain pure domain logic.

### Role in Runtime
- **Commands** are the primary consumers of Services, receiving them via dependency injection (constructor).
- Commands use Services to delegate vertical concerns (data access, configuration, file I/O, etc.).
- Concrete implementations (YAML-backed repositories, middleware classes) satisfy the Service contracts while hiding implementation details.
- **Factories** (e.g., `ConfigurationFileRepository`) resolve the correct concrete Service at runtime based on context (file type, etc.).

### Key Characteristics of Services as Vertical Contracts
- **Vertical abstraction**: They cross the domain ↔ infrastructure boundary, hiding how data is stored, files are managed, or middleware is applied.
- **Unified interface**: All vertical concerns (previously handled by repositories, configuration loaders, middleware, utilities) converge under `Service`.
- **Dependency injection**: Services are injected into commands via containers or initializers, making implementations swappable.
- **Extensibility**: New concerns (e.g., authentication, logging, rate limiting) can be added as new Service contracts or layered inside existing ones.

In the error domain, `ErrorService` is the vertical contract that all error-related commands depend on. In configuration handling, `ConfigurationService` abstracts YAML/JSON loading and saving, with concrete middleware implementations satisfying the contract.

## Structured Code Design of Services

Services follow Tiferet’s structured code style using artifact comments for organization and readability.

### Artifact Comments

Services are organized under the `# *** contracts` top-level comment, with individual Services under `# ** contract: <snake_case_name>`. Within each Service:

- `# * attribute: <name>` — Declares expected instance attributes (type hints only).
- `# * method: <name>` — Defines abstract methods marked with `@abstractmethod`.

No `# * method: new` is used, as Services are interfaces.

**Example** – `tiferet/contracts/error.py`:
```python
# *** contracts

# ** contract: error_service
class ErrorService(Service):
    '''
    Vertical contract for managing error domain objects.
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

**Example** – `tiferet/contracts/config.py` (configuration):
```python
# ** contract: configuration_service
class ConfigurationService(Service):
    '''
    Vertical contract for loading and saving structured configuration data.
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

**Example** – `tiferet/contracts/file.py` (low-level middleware/utility):
```python
# ** contract: file_service
class FileService(Service):
    '''
    Vertical contract for low-level file stream management.
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

1. **Define a New Service Contract**
   - Place under `# *** contracts` in a domain-specific module.
   - Extend `Service` from `tiferet.contracts.settings`.
   - Define abstract methods with domain-appropriate signatures.

2. **Implement the Service**
   - Concrete classes implement the Service contract.
   - Middleware-style implementations often inherit from lower-level middleware while implementing the target Service.
   - Use factories (e.g., `ConfigurationFileRepository.open_config()`) to resolve concrete implementations dynamically.

3. **Use in Commands**
   - Inject the Service via constructor (e.g., `error_service: ErrorService`).
   - Depend only on the interface for all vertical operations.

## Best Practices
- Use artifact comments consistently (`# * method`, `# * attribute`).
- Define methods with clear RST docstrings, type hints, and domain intent.
- Use `@abstractmethod` to enforce implementation.
- Keep services focused but composable (layer via inheritance or decoration).
- Inject Services into commands — never hard-code concrete classes.
- Maintain one empty line between sections, comments, and code blocks.

## Conclusion

Services are the unified vertical contracts in Tiferet, serving as the primary interface for middleware, data access, configuration management, and utilities. Commands depend exclusively on these Service interfaces, achieving high decoupling, testability, and extensibility. Concrete implementations satisfy the Service contracts while hiding infrastructure details.

Explore `tiferet/contracts/` for current Service definitions and `tiferet/middleware/` and `tiferet/repos/` for implementation patterns.
