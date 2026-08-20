# Domain Events in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

An event is the heart of the running system: the only unit of work that must know the session and the store, that commands, executes, and returns a noun. That position is **Tiferet** — the name for a middle that holds both sides without becoming either. High is the request, the feature, the human intent. Low is the aggregate, the util, the service, the store. Nothing else in the framework is allowed to stand in both places at once.

Without events there is no feature to wire and nothing for a user to mean. Configs are the camp; events are the productions the camp is organized to serve. The basic calculator begins its story here for that reason. The first thing a consumer writes after configuration is an `execute`. See [architecture.md](architecture.md) for the map this chapter sits in the center of.

Inbound: `assets` (`a`), `blueprints` (bootstrap only), `contexts` (the client surface). Outbound: `domain`, `mappers`, `utils`, `interfaces`. `di` does not import events. `execute` should return a domain model when one exists. Otherwise it may return anything it can legally reach beneath it — an aggregate or transfer object, a util result, or an interface-shaped value. It does not return a context, a blueprint, or a repo. Error constants are `a.<submodule>.*`, never `a.const`.

## Life in the system

A domain event is a production. The left-hand side is the required input and the domain predicate. The right-hand side is the action and the returned noun. `parameters_required` is the guard. `verify` is the constraint. `execute` is the action. A feature step with a `condition` is a second, outer rule set around the same heart.

That is why the package may legally touch `domain`, `mappers`, `utils`, and `interfaces` in one class, and why it may not import `contexts`, `blueprints`, `di`, or `repos`. The event *uses* a service. It does not *be* the store, the factory, or the session. Mutation happens on an aggregate. Persistence happens behind an interface. The event commands both and returns the noun.

It is entered two ways, and the two ways must not be confused. A blueprint may call `DomainEvent.handle` — or import the event class directly — only as pre-DI bootstrap, before the container exists. After composition, the feature loop belongs to the context. The context is the client: it asks `get_dependency` for the event and calls `handle`. Tests use the same seam. Hand-constructing `EventClass(...).execute(...)` skips the seam the rest of the system is built on.

Every focused domain action — validation, service interaction, computation, orchestration — is a class extending `DomainEvent` from `tiferet/events/core.py`. When a module shares one injected service, that service lives on a per-module base event (`ErrorEvent`, `FeatureEvent`, `AppEvent`, and the rest). Concrete events extend the base and declare only `execute`. Service-less utilities (`ParseParameter`, `ImportDependency`) extend `DomainEvent` directly.

## The DomainEvent base

`DomainEvent` is a plain object. It is not a domain noun and not a context. It centralizes the four things every operation in this system must be able to do: run, require, verify, and raise.

```python
# tiferet/events/core.py

class DomainEvent(object):
    '''
    A base class for a domain event object.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Any:
        '''Abstract execution entry point.'''
        raise NotImplementedError()

    # * method: raise_error (static)
    @staticmethod
    def raise_error(error_code: str, message: str = None, **kwargs):
        '''Raise a structured TiferetError.'''
        TiferetError.raise_error(error_code, message, **kwargs)

    # * method: verify
    def verify(self, expression: bool, error_code: str, message: str = None, **kwargs):
        '''Assert expression; raise on failure.'''
        if not expression:
            self.raise_error(error_code, message, **kwargs)

    # * method: parameters_required (static)
    @staticmethod
    def parameters_required(param_names: list):
        '''Declarative parameter validator – raises aggregated error.'''
        ...

    # * method: handle (static)
    @staticmethod
    def handle(event_cls: type, dependencies: Dict[str, Any] = {}, middleware: list = None, **kwargs) -> Any:
        '''Instantiate → execute, optionally through middleware.'''
        event_handler = event_cls(**dependencies)
        ...
        return event_handler.execute(**kwargs)
```

What the reader just saw: `execute` is the only entry the rest of the system is allowed to mean by "do the work." `raise_error` is static so a class or an instance can fail the same way. `verify` is the predicate — if the expression is falsy, the named error is raised. `handle` is the seam: instantiate with injected dependencies, then execute, optionally through an outermost-first middleware chain. `handle_async` is the same seam for `AsyncDomainEvent`.

## A module base, then a concrete event

When every event in a file needs the same service, the service is not repeated on each class. The base event owns the injection. The concrete event owns the production.

```python
# tiferet/events/error.py

# *** events

# ** event: error_event
class ErrorEvent(DomainEvent):
    '''
    Base event providing the shared ErrorService dependency for error domain events.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the error event with its shared service dependency.
        '''

        # Set the error service dependency.
        self.error_service = error_service

# ** event: get_error
class GetError(ErrorEvent):
    '''
    Event to retrieve an Error domain object by its ID.
    '''

    # * method: execute
    def execute(self, id: str, **kwargs) -> Error:
        '''
        Retrieve an Error by its ID.
        '''

        # Retrieve the error via the inherited service.
        return self.error_service.get(id)
```

`GetError` returns the noun. It does not format a response — that is a context. It does not open a file — that is a repo behind `ErrorService`. The seven framework bases follow the same shape: `ErrorEvent`, `FeatureEvent`, `AppEvent`, `CliEvent`, `DIEvent`, `LoggingEvent`, `SqliteEvent`. The name `FeatureEvent` is the feature *module* base. The former domain object of that name is now `EventFeatureStep`.

## The production, written out

`AddError` is the scene this chapter exists to teach. Required inputs are declared. A domain predicate is verified. Mutation lives on the aggregate. The service persists. The noun comes back.

```python
# *** imports

# ** app
from .core import DomainEvent, a
from ..domain import Error
from ..mappers import ErrorAggregate

# *** events

# ** event: add_error
class AddError(ErrorEvent):
    '''
    Event to add a new Error domain object to the repository.

    Extends the ErrorEvent base event, which injects the shared
    error_service; only execute is defined here.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'message'])
    def execute(self, id: str, name: str, message: str, **kwargs) -> Error:
        '''
        Add a new Error.
        '''

        # Check existence via the inherited service.
        self.verify(
            not self.error_service.exists(id),
            a.error.ERROR_ALREADY_EXISTS_ID,
            message=f'An error with ID {id} already exists.',
            id=id,
        )

        # Create and save the error aggregate.
        new_error = ErrorAggregate(
            id=id,
            name=name,
            message=[{'lang': 'en_US', 'text': message}],
        )
        self.error_service.save(new_error)

        # Return the new error.
        return new_error
```

Read the block as a production. The decorator is the LHS guard: `id`, `name`, and `message` must be present and non-blank. `0`, `False`, and `[]` would pass; `None` and `""` would not. All violations raise one aggregated `TiferetError` with `a.error.COMMAND_PARAMETER_REQUIRED_ID`. `verify` is the domain predicate: the error must not already exist. `ErrorAggregate` is Hod doing the form-giving; the event does not put a `rename` on `Error`. `error_service.save` is Netzach, implemented somewhere in Malkuth the event is not allowed to import. The return is Gevurah — the noun, preferred.

The calculator tells the same story at a smaller scale. `AddNumber` verifies two operands and returns a number — a legal inferior, because there is no richer noun to give back. `DivideNumber` adds a predicate (`b != 0`). `SaveFormula` in the same example returns a `FormulaAggregate` when the noun *does* exist. Prefer the domain model; otherwise return what you can legally reach.

## How the three verbs differ

- **`@parameters_required`** — declarative, on `execute`. Presence and non-emptiness of kwargs before the body runs. Aggregates every miss into one error.
- **`verify`** — imperative, inside `execute`. A domain rule ("must not already exist," "denominator is not zero").
- **`raise_error`** — the direct failure when there is no predicate to wrap, or when a conversion cannot complete.

Error constants come from the namespaced catalogs: `a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`. There is no `a.const`.

## Calling the event

Contexts and tests use the same seam:

```python
result = DomainEvent.handle(
    AddError,
    dependencies={'error_service': error_service},
    id='TEST_001',
    name='Test Error',
    message='A test error.',
)
```

`handle` instantiates, then executes. An optional `middleware` list wraps the call outermost-first: each entry is `(event, kwargs, next_fn)`. Feature-level and step-level middleware in `config.yml` are the same contract, resolved by `FeatureContext`. Async events extend `AsyncDomainEvent` and are driven with `handle_async`; `verify` and `raise_error` stay synchronous on purpose.

The test harness (`DomainEventTestBase`, `ServiceEventTestBase` in `tiferet/testing/`) is built on that seam. Declare `event_cls`, `dependencies`, `sample_kwargs`, and `required_params`. The harness mocks the services, calls `handle`, and parametrizes the missing-parameter path. Prefer it for new event tests. Per-method CRUD walkthroughs belong in `docs/guides/events/`, not here.

## Structured code design

Events follow the standard artifact comment structure. Use `# *** events` (or `# *** classes` in `core.py`), `# ** event: <name>` in snake_case, `# * attribute` / `# * init` on the base event only, and `# * method: execute` on the concrete class. One empty line between `# ***` and the first `# **`, between each `# *`, after docstrings, and between snippets. Full grammar: [code_style.md](code_style.md).

## Package layout

- `core.py` — `DomainEvent`, `AsyncDomainEvent`, `@parameters_required`, `ParseParameter`, `ImportDependency`
- `app.py`, `cli.py`, `di.py`, `error.py`, `feature.py`, `logging.py`, `sqlite.py` — one base event and its productions each
- `__init__.py` — public exports (`DomainEvent`, `TiferetError`, `a`)
- Tests in `tests/events/`; harness in `tiferet/testing/`

## In short

- An event is the unit of work. It commands, executes, and prefers to return a noun. That middle is Tiferet.
- Enter it through `DomainEvent.handle` (bootstrap from a blueprint, client from a context, always from a test). Do not hand-construct.
- Required inputs are a decorator. Domain rules are `verify`. Immediate failure is `raise_error`. Constants are `a.<submodule>`.
- Legal imports: `assets`, `domain`, `mappers`, `utils`, `interfaces`. Not `di`, `repos`, `contexts`, `blueprints`.
- Put a shared service on the module base event. Put mutation on an aggregate. Persist behind an interface. Never return a context, a blueprint, or a repo.
