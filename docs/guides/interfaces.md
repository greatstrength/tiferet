# Interfaces – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/interfaces/`  
**Version:** 2.0.0a4

## Overview

The interfaces layer defines abstract service contracts that domain events, contexts, and repositories depend on. Every interface extends `Service` (ABC) from `tiferet/interfaces/settings.py` and declares the expected behavior for a vertical concern — data access, configuration management, file I/O, or database operations — without prescribing how it is implemented.

There are two categories of service interfaces in Tiferet:

- **Infrastructure services** — abstract low-level I/O operations that are independent of any domain model (`FileService`, `ConfigurationService`, `SqliteService`). These are general-purpose contracts consumed by middleware, repositories, and utilities.
- **Domain services** — abstract persistence and query operations scoped to a specific domain aggregate (`AppService`, `CliService`, `DIService`, `ErrorService`, `FeatureService`, `LoggingService`). These are the primary contracts consumed by domain events.

This guide covers the cross-cutting strategies and design decisions that apply across all interface modules.

## The Standard CRUD Pattern

Most domain services follow a consistent five-method CRUD pattern:

| Method | Signature | Purpose |
|---|---|---|
| `exists` | `(id: str) -> bool` | Check presence before get or save |
| `get` | `(id: str) -> Aggregate` | Retrieve a single aggregate by ID |
| `list` | `(...) -> List[Aggregate]` | Retrieve all aggregates, optionally filtered |
| `save` | `(aggregate) -> None` | Persist a new or updated aggregate |
| `delete` | `(id: str) -> None` | Remove an aggregate by ID (idempotent) |

`exists` is used by domain events to enforce uniqueness before creation, or to confirm presence before retrieval. `delete` operations are always idempotent — calling delete on a non-existent ID must not raise an error.

### Example — ErrorService

```python
class ErrorService(Service):

    @abstractmethod
    def exists(self, id: str) -> bool: ...

    @abstractmethod
    def get(self, id: str) -> ErrorAggregate: ...

    @abstractmethod
    def list(self) -> List[ErrorAggregate]: ...

    @abstractmethod
    def save(self, error: ErrorAggregate) -> None: ...

    @abstractmethod
    def delete(self, id: str) -> None: ...
```

`AppService`, `CliService`, `ErrorService`, and `FeatureService` all follow this pattern exactly. Variations are introduced only where the domain genuinely requires them.

## Domain-Specific Variations

### FeatureService — Filtered List

`FeatureService.list` accepts an optional `group_id` parameter to filter results by feature group. This is the only standard CRUD method with a parameter, and its presence in the signature reflects the hierarchical `group.feature_key` ID structure of the Feature domain.

```python
def list(self, group_id: Optional[str] = None) -> List[FeatureAggregate]: ...
```

### CliService — Extra Query Method

`CliService` adds `get_parent_arguments()` beyond the standard five methods. This method returns all top-level `CliArgumentAggregate` objects — arguments that apply to the CLI root rather than to any specific command. It is not part of the CRUD contract but serves a specific runtime need of `CliContext`.

```python
def get_parent_arguments(self) -> List[CliArgumentAggregate]: ...
```

### DIService — Non-Standard Naming

`DIService` manages two distinct resources: service configurations and constants. Because both live in the same configuration file but require separate operations, the method names are domain-specific rather than generic CRUD:

| Standard | DIService equivalent |
|---|---|
| `exists` | `configuration_exists` |
| `get` | `get_configuration` |
| `list` | `list_all` (returns a tuple: configurations + constants dict) |
| `save` | `save_configuration` |
| `delete` | `delete_configuration` |
| *(none)* | `save_constants` |

The `list_all` return type is `Tuple[List[ServiceConfigurationAggregate], Dict[str, str]]` — a paired result that loads the full DI container state in one call. `save_constants` has no CRUD equivalent because constants are a flat key-value dict, not an aggregate.

### LoggingService — Split by Sub-Entity Type

`LoggingService` manages three distinct sub-entities (formatters, handlers, loggers) that are always loaded together but saved and deleted independently. This yields a `list_all` bulk-read pattern paired with entity-specific write methods:

```python
def list_all(self) -> Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]: ...
def save_formatter(self, formatter: FormatterAggregate) -> None: ...
def save_handler(self, handler: HandlerAggregate) -> None: ...
def save_logger(self, logger: LoggerAggregate) -> None: ...
def delete_formatter(self, formatter_id: str) -> None: ...
def delete_handler(self, handler_id: str) -> None: ...
def delete_logger(self, logger_id: str) -> None: ...
```

There are no `exists` or `get` methods on `LoggingService` because the standard usage is to load all logging configuration at once and configure the logging system in a single pass.

## The `NotImplementedError` Message Convention

Every abstract method body raises `NotImplementedError` with a descriptive string in the format `'<method> method is required for <ServiceClass>.'`. This makes errors from unimplemented concrete classes immediately actionable:

```python
raise NotImplementedError('get method is required for ErrorService.')
raise NotImplementedError('configuration_exists method is required for DIService.')
```

The message pattern is consistent across all interfaces. Deviating from it (e.g., using a generic `'Not implemented'` message) reduces debuggability when a concrete class forgets to implement a method.

## Aggregate Return Types

Domain service interfaces always declare return types as **Aggregates**, not plain `DomainObject` instances. Concrete repository implementations return aggregates so that callers — typically domain events — can invoke mutation methods without type-casting:

```python
# Domain event calls service, receives an aggregate, and mutates it directly.
feature = self.feature_service.get(id)           # returns FeatureAggregate
feature.add_step(attribute_id=attribute_id, ...)  # mutation method on aggregate
self.feature_service.save(feature)
```

If the interface declared a plain `Feature` return type, domain events would need to convert it to an aggregate before mutation, creating unnecessary overhead and reducing clarity.

Infrastructure services (`FileService`, `ConfigurationService`, `SqliteService`) are the exception — they have no domain aggregate concept and return raw I/O types (`IO[Any]`, `Any`).

## How Services Are Consumed by Domain Events

Services are injected into domain events via constructor parameters. The event depends only on the abstract interface — never on a concrete implementation:

```python
# ** event: get_feature
class GetFeature(DomainEvent):

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        self.feature_service = feature_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> FeatureAggregate:

        # Retrieve the feature from the service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Return the feature aggregate.
        return feature
```

The concrete implementation (`FeatureYamlRepository`, or a mock in tests) is wired at runtime by the dependency injection container. Tests always mock the service interface:

```python
mock_feature_service = mock.Mock(spec=FeatureService)
mock_feature_service.get.return_value = sample_feature

result = DomainEvent.handle(
    GetFeature,
    dependencies={'feature_service': mock_feature_service},
    id='group.sample_feature',
)
```

## When to Deviate from the Standard CRUD Pattern

Use the standard `exists / get / list / save / delete` names whenever possible. Deviate only when:

1. **The domain manages multiple sub-entities of different types** and a single generic name would be ambiguous (`LoggingService` splits by formatter/handler/logger).
2. **The resource is not an aggregate** — constants are a plain dict, not a model with an ID, so `save_constants` is appropriate and `save(constants)` would be misleading.
3. **A meaningful qualifier adds clarity** — `configuration_exists` is clearer than `exists` when a service manages both configurations and constants under the same contract.

Do not rename standard methods for stylistic reasons. If `get` and `exists` cover the use case, use them.

## Adding a New Service Interface

1. Create a new module in `tiferet/interfaces/` (e.g., `tiferet/interfaces/myservice.py`).
2. Extend `Service` from `.settings`.
3. Import the relevant aggregate type(s) from `..mappers`.
4. Define all methods with `@abstractmethod`, RST docstrings, and a descriptive `NotImplementedError` message.
5. Export the new service class from `tiferet/interfaces/__init__.py` under `# ** app`.

```python
# tiferet/interfaces/myservice.py
"""Tiferet Interfaces MyService"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from ..mappers import MyAggregate
from .settings import Service

# *** interfaces

# ** interface: my_service
class MyService(Service):
    '''
    Service interface for managing my domain objects.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a my domain object exists by ID.

        :param id: The identifier.
        :type id: str
        :return: True if it exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for MyService.')
```

## Related Documentation

- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service base class reference and artifact comment conventions
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and conventions
- [docs/core/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md) — Aggregate and TransferObject base class reference
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and dependency injection
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting rules
