# Interfaces in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Endurance is the promise that outlasts any one store. Interfaces are `Service` ABCs: vertical contracts for persistence, files, middleware, and DI. That position is **Netzach**. A service does not run a feature and does not open a file. It names what any implementor — a repo, a util, a test double — must be able to do. See [architecture.md](architecture.md).

Legal `# ** app` imports: `mappers` (aggregates) to type domain-related outputs, especially when the implementor will be a repository. Prefer the aggregate over the domain model when an aggregate exists. Sibling interface modules are legal. `contexts` and `blueprints` do not import this package. Service instances reach a blueprint only through `di`.

## Life in the system

`Service` (`tiferet/interfaces/core.py`) is a minimal ABC. Everything vertical converges on it: error catalogs, feature workflows, files, SQLite, configuration, cache, middleware, DI registrations. Commands and domain events depend on the contract (`error_service.save(error)`). They never name `ErrorConfigRepository`. Chesed expands the registration into an instance. Malkuth or Yesod satisfies it.

That is why interfaces may import aggregates. `ErrorService.get` returns `ErrorAggregate` because the implementor is a repo that maps a transfer object into mutable form. Typing the method as `Error` would lie about what the caller can do next, or force the event to re-wrap the noun before it can mutate. Six interface modules already import `*Aggregate`. That is correct. The old skill line “never mappers” was inverted on purpose.

Binah does not import Netzach. The hub asks `get_dependency`. Chochmah does not import Netzach. The factory asks Chesed. If a context grows an `AppService` parameter, the contract has leaked into the client — the `AppSessionContext.load` violation, in other words.

`MiddlewareService` is the same endurance applied to the event chain. It is callable: `__call__(self, event, kwargs, next_fn)`. Async middleware awaits `next_fn()`. The event does not know it is wrapped. The contract endures around the heart without becoming the heart.

## A vertical contract

```python
# tiferet/interfaces/error.py

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
    def get(self, id: str) -> ErrorAggregate:
        '''
        Retrieve an error by ID.
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, error: ErrorAggregate) -> None:
        '''
        Persist an error.
        '''
        raise NotImplementedError()
```

What the reader just saw: every method is abstract. The return type is the aggregate, not the noun. `save` accepts the aggregate because mutation already happened in Hod. The repo will turn that into a transfer object. The event never sees the file.

`ConfigurationService` and `FileService` follow the same shape for loaders. `DIService` is the contract Chesed reads when it builds a container. `ServiceError` is the miss that Chesed raises — an interface error, not an asset catalog entry — so `di` can fail without importing `TiferetError`.

## Structured code design

Use `# *** interfaces` / `# ** interface:` / `# * method` with `@abstractmethod`. No `# * method: new`. Implementors live in `repos/` or `utils/`, never in this package. Full grammar: [code_style.md](code_style.md). Pattern notes live in [docs/guides/interfaces.md](../guides/interfaces.md).

## In short

- Interfaces are enduring Service ABCs. That contract is Netzach.
- Import aggregates from `mappers` to type outputs. Do not type a domain model when an aggregate exists.
- Used by events, di, utils (when injectable), and repos. Not imported by contexts or blueprints.
- Depend on the contract in events. Never name the concrete repository.
- `MiddlewareService` wraps `execute` without becoming an event.
