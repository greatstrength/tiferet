# Interfaces in Tiferet

Interfaces are a core component of the Tiferet framework, defining service contracts that specify the anticipated structure and behavior of services used by commands and domain events, aligning with Domain-Driven Design (DDD) principles. In the current evolution of Tiferet, **Services** serve as the **unified vertical contracts** — abstract base classes that act as the primary interface for all domain-specific orchestration, data access, configuration management, middleware, and utility behavior.

This document focuses exclusively on **Services** as the vertical contracts.

## What is a Service?

A **Service** in Tiferet is an abstract class derived from `tiferet.interfaces.settings.Service` (a minimal `ABC`) that defines the expected behavior for vertical concerns in the application. Services act as injectable interfaces that:

- Abstract data access (CRUD operations, existence checks, listing)
- Manage configuration persistence (loading/saving structured data from YAML/JSON/etc.)
- Provide middleware and utility behavior (file handling, context management, validation, caching)
- Coordinate domain logic while hiding infrastructure details

**Commands** and **domain events** depend on injected Service instances to perform persistence, retrieval, or orchestration (e.g., `error_service.save(error)`, `configuration_service.load(...)`). Services encapsulate the infrastructure details, allowing commands and events to remain pure domain logic.

### Role in Runtime
- **Commands** and **domain events** are the primary consumers of Services, receiving them via dependency injection (constructor).
- Commands and events use Services to delegate vertical concerns (data access, configuration, file I/O, etc.).
- Concrete implementations (YAML-backed repositories, middleware classes) satisfy the Service interfaces while hiding implementation details.
- **Factories** (e.g., `ConfigurationFileRepository`) resolve the correct concrete Service at runtime based on context (file type, etc.).

### Key Characteristics of Services as Vertical Contracts
- **Vertical abstraction**: They cross the domain ↔ infrastructure boundary, hiding how data is stored, files are managed, or middleware is applied.
- **Unified interface**: All vertical concerns (previously handled by repositories, configuration loaders, middleware, utilities) converge under `Service`.
- **Dependency injection**: Services are injected into commands and events via containers or initializers, making implementations swappable.
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
   - Inject the Service via constructor (e.g., `error_service: ErrorService`).
   - Depend only on the interface for all vertical operations.

## Migration from Contracts

The `tiferet.interfaces` package is the successor to `tiferet.contracts` and represents the canonical location for service interfaces going forward.

### Package Rename Rationale
The rename from `contracts` to `interfaces` better reflects the purpose of these components as abstract service interfaces, aligning with widely understood software engineering terminology and the v2.0 architectural direction.

### Artifact Comment Changes
When migrating service files from `tiferet.contracts` to `tiferet.interfaces`, update the artifact comments as follows:

- `# *** contracts` → `# *** interfaces`
- `# ** contract: <name>` → `# ** interface: <name>`

All other artifact comments (`# * method:`, `# * attribute:`, etc.) remain unchanged.

### Incremental Migration Path
Migration of concrete service interfaces (e.g., `ErrorService`, `FeatureService`, `ContainerService`) from `tiferet.contracts` to `tiferet.interfaces` will proceed incrementally:

1. **Phase 1 (current)**: Only the base `Service` class is ported to `tiferet.interfaces.settings`. All domain-specific interfaces remain in `tiferet.contracts`.
2. **Phase 2 (future)**: Individual service interfaces will be migrated as their dependent aggregates, mappers, and domain events become available in the v2.0 architecture.
3. **Backward compatibility**: During migration, `tiferet.contracts` will continue to function. No existing imports will break until an explicit deprecation cycle is initiated.

New service interfaces should be created in `tiferet.interfaces` from the start.

## Best Practices
- Use artifact comments consistently (`# * method`, `# * attribute`).
- Define methods with clear RST docstrings, type hints, and domain intent.
- Use `@abstractmethod` to enforce implementation.
- Keep services focused but composable (layer via inheritance or decoration).
- Inject Services into commands and events — never hard-code concrete classes.
- Maintain one empty line between sections, comments, and code blocks.

## Conclusion

Services are the unified vertical interfaces in Tiferet, serving as the primary interface for middleware, data access, configuration management, and utilities. Commands and domain events depend exclusively on these Service interfaces, achieving high decoupling, testability, and extensibility. Concrete implementations satisfy the Service interfaces while hiding infrastructure details.

Explore `tiferet/interfaces/` for base definitions, `tiferet/contracts/` for current domain-specific Service interfaces, and `tiferet/middleware/` and `tiferet/repos/` for implementation patterns.
