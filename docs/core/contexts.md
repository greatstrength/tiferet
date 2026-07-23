# Contexts in Tiferet

Contexts are a core component of the Tiferet framework, representing the structural "body" of an application in runtime "graph space." While blueprints (`tiferet/blueprints/`) control the timing, execution, and procedure of the app, Contexts define its shape and behavior, encapsulating user interactions, internal orchestration, and supporting services. In Tiferet, Contexts are the primary runtime components safely accessible to blueprints, making their methods and attributes extensible for developers (human or AI). This document explores the structured code design behind Contexts, how to write and extend them, and how to test them, using the calculator application as an example and adhering to Tiferet's code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Context?

A Context in Tiferet is a class that encapsulates a specific aspect of an application’s runtime behavior, such as user-facing interactions (e.g., CLI, web), feature execution, dependency injection, error handling, caching, or logging. Contexts form a graph-like structure during execution, defining how the application processes inputs, executes domain logic, and returns outputs. They align with Domain-Driven Design (DDD) principles, isolating concerns to ensure modularity and extensibility.

### Types of Contexts
All contexts extend `BaseContext` (`tiferet/contexts/core.py`), which provides a `ContextMeta` registry mapping a domain object type (`domain_type`) to its context class. `BaseContext.for_domain(DomainType)` resolves the registered class, and `BaseContext.from_domain(domain_obj, **kwargs)` constructs a context bound to a loaded domain object (exposed as `ctx.domain`). Caching is not part of the base; contexts that need a `CacheContext` (e.g., `AppSessionContext`, `FeatureContext`) declare and wire it themselves.

Tiferet recognizes two broad categories:

- **High-Level Contexts**: Handle user interactions (e.g., `CliContext` for command-line interfaces, `FlaskApiContext` for web APIs). They extend `AppSessionContext`, the minimal hub built declaratively from the loaded `AppSession`. CLI interfaces point at `CliContext`, which owns argparse parsing; the `build_cli` blueprint is a thin entrypoint that delegates to `CliContext.run_cli`.
- **Low-Level Contexts**: Support specific functions (e.g., `FeatureContext`, `AsyncFeatureContext`, `ErrorContext`, `CacheContext`, `RequestContext`, `LoggingContext`).

In the calculator application, `AppSessionContext` handles feature execution, while low-level contexts manage dependency injection, error handling, and logging.

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

**Example** – `tiferet/contexts/app.py` (minimal hub):
```python
# *** imports

# ** app
from .core import BaseContext
from .cache import CacheContext
from .feature import FeatureContext
from .error import ErrorContext
from .logging import LoggingContext
from ..domain import AppSession

# *** contexts

# ** context: app_session_context
class AppSessionContext(BaseContext):

    # * attribute: domain_type
    domain_type = AppSession

    # * init
    def __init__(self,
                 get_dependency,
                 logging_context=None,
                 cache=None,
                 execute_feature_handler=None,
                 create_request_handler=None,
                 raise_error_handler=None,
                 response_handler=None):
        '''
        Initialize the hub. The loaded AppSession is bound via from_domain as
        self.domain, supplying the session id and logger id on demand.
        '''
        super().__init__()
        self.cache = cache if cache is not None else CacheContext()
        self.get_dependency = get_dependency
        # ... store the injected handler callables and logging context;
        # sub-contexts are built on demand via BaseContext.for_domain ...

    # * method: run
    def run(self, feature_id, headers=None, data=None, **kwargs):
        '''
        Execute a feature and return the response.
        '''
        # Build the logger from the lazily-created logging context.
        logger = self.load_logging_context().build_logger()

        # Parse request into a RequestContext (interface id from self.domain.id).
        request = self.parse_request(headers or {}, data or {}, feature_id)

        # Execute the feature.
        try:
            self.execute_feature(feature_id=feature_id, request=request, logger=logger, **kwargs)
        except TiferetError as e:
            return self.handle_error(e)

        # Return the response via the request context.
        return request.handle_response()
```

The hub builds the `FeatureContext` and `ErrorContext` on demand (via `BaseContext.for_domain`) inside `execute_feature` / `handle_error`, lazily caches the `LoggingContext` (`load_logging_context`), and loads domain objects via `load_feature_domain` / `get_error`. The hub owns a `CacheContext` — used by `load_feature_domain` and `get_error` (which resolves an error from the cache, pre-seeded with the framework defaults under `error_`-prefixed keys by `build_cache`, before falling back to the get-error event and caching the result) and shared with the `FeatureContext` it builds; the error and logging contexts no longer take a cache. Feature-step services are resolved through the injected `get_dependency` handler (provided by the `ServiceResolver`), which the hub forwards to each `FeatureContext` it builds.

When a loaded `Feature` has `is_async` set to `True`, `execute_feature` selects the `AsyncFeatureContext` subclass — which extends `FeatureContext` with awaiting (`handle_feature_step_async` / `execute_feature_async`) step execution while inheriting the shared step-resolution, parameter-parsing, condition, and middleware helpers — and drives its `execute_feature_async` coroutine to completion via a `_run_coroutine` helper. The helper uses `asyncio.run` when no event loop is running and falls back to a dedicated worker thread when one is, keeping `run()` synchronous. `AsyncFeatureContext` deliberately does not declare its own `domain_type`, so the `Feature → FeatureContext` registry entry is preserved.

### Cache Context and Default Catalogs

The `CacheContext` (`tiferet/contexts/cache.py`) exposes `get`, `set`, `delete`, `clear`, and `get_by_prefix(prefix)` — the last returns all entries whose keys start with the given prefix as a `Dict[str, Any]`. This backs enumeration of the framework catalogs that `build_cache` seeds under namespaced key prefixes.

The app-context module (`tiferet/contexts/app.py`) provides paired seeders and getters for the bootstrap catalogs:

- `add_default_app_services` / `add_default_app_constants` seed the cache under the `app_service_` and `app_constant_` key prefixes (stacked as decorators on `build_cache`).
- `get_default_app_services(cache)` returns the seeded `AppServiceDependency` domain objects (the values behind the `app_service_` prefix).
- `get_default_app_constants(cache)` returns the seeded bootstrap constants keyed by name, stripping the `app_constant_` prefix.

These getters let the `build_app_service_container` blueprint pull the framework defaults back off the shared cache when composing the app-level service container.

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
        # Forward the resolved hub collaborators/defaults to AppSessionContext.
        # The blueprint imports this class from the interface's module_path/
        # class_name and constructs it via from_domain.
        super().__init__(**kwargs)
        self.flask_handler = flask_handler

    # * method: parse_request
    def parse_request(self, flask_request) -> FlaskRequestContext:
        '''
        Parse Flask request into RequestContext.
        '''
        # Extract headers, data, feature_id
        ...
```

### Extending Existing Contexts
- Override methods under `# * method` to customize behavior.
- Use `super()` for template pattern compliance.

## Testing Contexts

Tests use `pytest` with `unittest.mock`, organized under `# *** fixtures` and `# *** tests`.

**Example** – `AppSessionContext` test:
```python
# *** fixtures

# ** fixture: app_session_context
@pytest.fixture
def app_session_context(app_session, logging_context):
    # Build the hub declaratively from a loaded app session via from_domain.
    context = AppSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        logging_context=logging_context,
    )
    return context

# *** tests

# ** test: app_session_context_run_success
def test_app_session_context_run_success(app_session_context, logging_context):
    # Arrange the logger.
    logging_context.build_logger.return_value = mock.Mock()

    # Act.
    result = app_session_context.run('calc.add', data={'a': 1, 'b': 2})

    # The feature context is built on demand inside execute_feature; assert the
    # run completed and produced a response.
    assert result is not None
```

### Best Practices
- Use `# ** fixture` and `# ** test` comments.
- Mock dependencies.
- Test all `# * method` behaviors.
- Include RST docstrings.

## Conclusion

Contexts define the runtime shape of Tiferet applications, orchestrating user interaction and internal services. Their structured design ensures consistency and extensibility. Developers can create new Contexts or extend existing ones by following artifact patterns and conventions. Explore `tiferet/contexts/` for source and `tests/contexts/` for test examples.
