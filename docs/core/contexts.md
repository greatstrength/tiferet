# Contexts in Tiferet

Contexts are the runtime graph. A context binds a domain object (`from_domain`) and exposes operational behavior. The hub must be able to run without knowing how it was assembled. That position is **Binah**.

Legal `# ** app` imports: `assets` (one way); `domain`; sibling contexts; `events` as the client surface. Illegal: `blueprints`, `interfaces`, `di`, `mappers`, `utils`, `repos`. Blueprints are the factory; contexts are the client. Prefer handler injection over constructing sibling contexts. See [architecture.md](architecture.md).

This document explores the structured code design behind Contexts, how to write and extend them, and how to test them, adhering to Tiferet's code style ([code_style.md](code_style.md)).

## What is a Context?

A Context in Tiferet is a class that encapsulates a specific aspect of an application's runtime behavior, such as user-facing interactions (e.g., CLI, web), feature execution, dependency injection, error handling, caching, or logging. Contexts form a graph-like structure during execution, defining how the application processes inputs, executes domain logic, and returns outputs. They align with Domain-Driven Design (DDD) principles, isolating concerns to ensure modularity and extensibility.

### Types of Contexts
All contexts extend `BaseContext` (`tiferet/contexts/core.py`), which provides a `ContextMeta` registry mapping a domain object type (`domain_type`) to its context class. `BaseContext.for_domain(DomainType)` resolves the registered class, and `BaseContext.from_domain(domain_obj, **kwargs)` constructs a context bound to a loaded domain object (exposed as `ctx.domain`). Caching is not part of the base; contexts that need a `CacheContext` (e.g., `AppSessionContext`, `FeatureContext`) declare and wire it themselves.

Tiferet recognizes two broad categories:

- **High-Level Contexts**: Handle user interactions (e.g., `CliSessionContext` for command-line interfaces, `FlaskApiContext` for web APIs). They extend `AppSessionContext`, the minimal hub built declaratively from the loaded `AppSession`. CLI interfaces point at `CliSessionContext`, which owns argparse parsing via an injected `parse_cli_args` closure; the `build_cli` blueprint is a thin entrypoint that wires the five-handler contract and delegates to `CliSessionContext.run`.
- **Low-Level Contexts**: Support specific functions (e.g., `FeatureContext`, `ErrorContext`, `CacheContext`, `RequestContext`, `LoggingContext`).

In the calculator application, `AppSessionContext` handles feature execution through its five required template-method handlers, while low-level contexts manage feature step execution, error formatting, caching, and logger assembly.

**Note on Method Design**: The nature of methods in Contexts is not restrictive regarding inputs and outputs. Methods must be defined according to the domain requirements of the context containing them, allowing flexibility for domain-specific tasks while maintaining clear, documented signatures.

## Structured Code Design of Contexts

Tiferet enforces a structured code design for Contexts using **artifact comments** to organize code and ensure consistency.

### Artifact Comments

Contexts are organized under the `# *** contexts` top-level comment, with individual Contexts under `# ** context: <snake_case_name>`. Within each Context:

- `# * attribute: <name>` — instance attributes (with type hints).
- `# * init` — constructor.
- `# * method: <name>` — methods.

**Spacing**:
- One empty line between `# *** contexts` and first `# ** context`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

**Example** – `tiferet/contexts/app.py` (minimal hub with the five-handler contract):
```python
# *** imports

# ** app
from .core import BaseContext
from .cache import CacheContext
from .request import RequestContext
from ..domain import AppSession

# *** contexts

# ** context: app_session_context
class AppSessionContext(BaseContext):

    # * attribute: domain_type
    domain_type = AppSession

    # * init
    def __init__(self,
                 get_dependency,
                 cache=None,
                 build_logger_handler=None,
                 execute_feature_handler=None,
                 create_request_handler=None,
                 raise_error_handler=None,
                 response_handler=None):
        """
        Initialize the hub. The loaded AppSession is bound via from_domain as
        self.domain, supplying the session id and logger id on demand.
        """
        super().__init__()
        self.cache = cache if cache is not None else CacheContext()
        self.get_dependency = get_dependency
        # Store the five template-method handlers (validated lazily on first use).
        self._build_logger = build_logger_handler
        self._execute_feature = execute_feature_handler
        self._create_request = create_request_handler
        self._raise_error = raise_error_handler
        self._build_response = response_handler

    # * method: run
    def run(self, feature_id, headers=None, data=None, **kwargs):
        """
        Execute a feature and return the response.
        """
        # Build the logger via the required build_logger template method.
        logger = self.build_logger()

        # Build the request context (interface id from self.domain.id).
        request = self.build_request(feature_id, headers or {}, data or {})

        # Execute the feature.
        try:
            self.execute_feature(feature_id, request, logger=logger, **kwargs)
        except TiferetError as e:
            return self.handle_error(e)

        # Return the response via the response template method.
        return self.build_response(request)
```

### The Five Required Handlers

`AppSessionContext` (and subclasses such as `CliSessionContext`) implements a **required five-handler template-method contract**. Each public template method is backed by an injected handler slot:

| Template method | Handler slot | Role |
| --- | --- | --- |
| `build_logger` | `build_logger_handler` | Construct (and typically cache) the session logger by `logger_id` |
| `build_request` | `create_request_handler` | Construct a `RequestContext` for the feature run |
| `execute_feature` | `execute_feature_handler` | Resolve and drive the bound `FeatureContext` against the request |
| `handle_error` | `raise_error_handler` | Format a domain error into a structured API error response |
| `build_response` | `response_handler` | Extract the final response from the completed request |

Handlers are **required**, not optional fallbacks. An unwired slot raises `APP_ERROR` via the module helper `raise_unwired_handler_error(handler_name, interface_id, ...)` on first use. There is no inline fallback implementation on the hub.

`handle_error` also re-raises an incoming `TiferetAPIError` verbatim before consulting `raise_error_handler`, so already-formatted API errors are never double-wrapped.

`build_logger_handler` replaces the former separately-loaded `LoggingContext` on the hub. The hub no longer accepts a `logging_context` constructor keyword constructor keyword, does not cache a `_logging` attribute, and does not call `load_logging_context`. Logger construction is a first-class template method; the blueprint wires a cache-backed closure (`blueprints/core.py::build_logger_handler`) that lists logging configs, merges them over cache-seeded defaults via `merge_logging_settings`, builds a one-shot `LoggingContext.from_domain(settings, logger_id=...)`, and caches the resulting logger under `LOGGER_CACHE_PREFIX`.

Blueprint wiring lives in `build_app_session_context` / `build_cli_session_context` / `build_admin_app_session_context` / `build_admin_cli_session_context`. `RESERVED_CONTEXT_PARAMETERS` in `blueprints/core.py` includes `build_logger_handler` (and the other four handler names) so generic collaborator resolution does not attempt to DI-resolve them.

### Domain-Bound FeatureContext

`FeatureContext` is constructed via `BaseContext.from_domain(feature, get_dependency=..., cache=...)`. The bound `Feature` is available as `self.domain`. Its public execution surface takes **no** `feature` parameter:

```python
def execute_feature(self, request, *flags, **kwargs):
    feature = self.domain
    ...

def resolve_feature_steps(self, request, *execution_flags):
    feature = self.domain
    ...
```

`create_feature_context` in `blueprints/core.py` returns a `FeatureContext` (not a `(Feature, FeatureContext)` tuple). The hub's `execute_feature_handler` therefore calls:

```python
feature_context = create_feature_context(get_dependency, cache, feature_id)
feature_context.execute_feature(request, *flags, **kwargs)
```

Async dispatch is owned by `FeatureContext` itself via `Feature.is_async` and `EventFeatureStep.is_async` (see the Feature domain guide). There is no separate `AsyncFeatureContext` class and no `handle_feature_step` / `get_feature_handler` public surface on the hub.

### Cache Context and Default Catalogs

The `CacheContext` (`tiferet/contexts/cache.py`) exposes `get`, `set`, `delete`, `clear`, and `get_by_prefix(prefix)` — the last returns all entries whose keys start with the given prefix as a `Dict[str, Any]`. This backs enumeration of the framework catalogs that `build_cache` seeds under namespaced key prefixes.

The app-context module (`tiferet/contexts/app.py`) provides paired seeders and getters for the bootstrap catalogs:

- `add_default_app_services` / `add_default_app_constants` seed the cache under the `app_service_` and `app_constant_` key prefixes (stacked as decorators on `build_cache`).
- `get_default_app_services(cache)` returns the seeded `AppServiceDependency` domain objects (the values behind the `app_service_` prefix).
- `get_default_app_constants(cache)` returns the seeded bootstrap constants keyed by name, stripping the `app_constant_` prefix.

These getters let the `build_app_service_container` blueprint pull the framework defaults back off the shared cache when composing the app-level service container. Admin blueprints stack additional seeders (`add_default_admin_services`, `add_default_admin_constants`, `add_default_features(ADMIN_DEFAULT_FEATURES)`, `add_default_errors(ADMIN_DEFAULT_ERRORS)`, and for the admin CLI `add_default_cli_commands(ADMIN_DEFAULT_COMMANDS)`).

## Writing Contexts

### Creating a New Context
1. Place under `# *** contexts` in appropriate module.
2. Extend `AppSessionContext` for high-level contexts or base class for low-level.
3. Use `# * attribute`, `# * init`, `# * method` comments.
4. Follow spacing and docstring conventions.

**Example** – High-level `FlaskApiContext`:
```python
# ** context: flask_api_context
class FlaskApiContext(AppSessionContext):

    # * attribute: flask_handler
    flask_handler: FlaskApiHandler

    # * init
    def __init__(self, flask_handler, **kwargs):
        # Forward the resolved hub collaborators/handlers to AppSessionContext.
        # The blueprint imports this class from the interface's module_path/
        # class_name and constructs it via from_domain with the five handlers.
        super().__init__(**kwargs)
        self.flask_handler = flask_handler

    # * method: parse_request
    def parse_request(self, flask_request) -> FlaskRequestContext:
        """
        Parse Flask request into RequestContext.
        """
        # Extract headers, data, feature_id
        ...
```

### Extending Existing Contexts
- Override methods under `# * method` to customize behavior.
- Use `super()` for template pattern compliance so unwired-handler guards remain intact.
- Do not reintroduce truthiness-guarded fallbacks for any of the five required handlers.

## Testing Contexts

Tests use `pytest` with `unittest.mock`, organized under `# *** fixtures` and `# *** tests`.

**Example** – `AppSessionContext` test:
```python
# *** fixtures

# ** fixture: app_session_context
@pytest.fixture
def app_session_context(app_session):
    # Build the hub declaratively from a loaded app session via from_domain.
    context = AppSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        build_logger_handler=mock.Mock(return_value=mock.Mock()),
        execute_feature_handler=mock.Mock(),
        create_request_handler=mock.Mock(),
        raise_error_handler=mock.Mock(),
        response_handler=mock.Mock(return_value={'ok': True}),
    )
    return context

# *** tests

# ** test: app_session_context_run_success
def test_app_session_context_run_success(app_session_context):
    # Act.
    result = app_session_context.run('calc.add', data={'a': 1, 'b': 2})

    # Assert the five handlers were consulted and a response was produced.
    app_session_context._build_logger.assert_called()
    app_session_context._execute_feature.assert_called()
    assert result is not None
```

### Best Practices
- Use `# ** fixture` and `# ** test` comments.
- Mock all five handler slots explicitly; leave a slot `None` only when testing the unwired-handler error path.
- Test all `# * method` behaviors, including `raise_unwired_handler_error` when a handler is missing.
- Include RST docstrings.

## Conclusion

Contexts define the runtime shape of Tiferet applications, orchestrating user interaction and internal services through a required five-handler template-method contract. Their structured design ensures consistency and extensibility. Developers can create new Contexts or extend existing ones by following artifact patterns and conventions. Explore `tiferet/contexts/` for source and `tests/contexts/` for test examples.

## Related Documentation

- [architecture.md](architecture.md) — Package import law
- [docs/guides/contexts.md](../guides/contexts.md) — Context strategies and runtime patterns
- [docs/core/blueprints.md](blueprints.md) — Blueprint composition and handler wiring
- [docs/guides/blueprints.md](../guides/blueprints.md) — Blueprint strategies, including admin entry points
- [docs/guides/admin.md](../guides/admin.md) — Admin application and CLI catalog
- [docs/core/code_style.md](code_style.md) — Artifact comments and formatting rules
