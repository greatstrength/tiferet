# Builders in Tiferet

Builders are a core component of the Tiferet framework in v2.0+. They serve as the primary public entry point for applications, providing a clean, high-level API for loading services, preparing defaults, resolving interfaces, and executing features.

While Contexts define the runtime shape and behavior of an individual interface, Builders orchestrate the overall application lifecycle and wiring. They replace previous direct usage of lower-level contexts for application initialization.

## What is a Builder?

A Builder in Tiferet is a class that encapsulates the initialization and orchestration logic required to prepare and run an application interface. Builders are intentionally thin: they focus on service loading, default configuration injection, dependency wiring, and delegation to the appropriate `AppInterfaceContext`.

The canonical implementation is `AppBuilder` in `tiferet/builders/main.py`.

### Role in the Architecture

Builders sit at the highest level of the application graph:

- They load the application service (typically a repository)
- They prepare default services and constants from `assets.constants`
- They resolve interfaces via domain events (`GetAppInterface`)
- They wire the dependency injection container
- They delegate feature execution to the resolved `AppInterfaceContext`

This design keeps application code simple while maintaining full extensibility and testability.

## Types of Builders

Tiferet currently defines one primary builder:

- **High-Level Builder**: `AppBuilder` — used for general script, CLI, and custom interfaces.

Future specialized builders may include:
- `CliBuilder` — optimized for pure CLI applications with argument parsing
- `WebBuilder` — for web framework integration (Flask, FastAPI, etc.)
- `TestBuilder` — for integration and unit testing with mocked services

## Structured Code Design of Builders

Builders follow Tiferet’s standard artifact comment structure.

### Artifact Comments

Builders are organized under the `# *** builders` top-level comment, with individual builders under `# ** builder: <snake_case_name>`. Within each builder:

- `# * attribute: <name>` — instance attributes (with type hints)
- `# * init` — constructor
- `# * method: <name>` — methods (including static factory methods)

**Spacing rules:**
- One empty line between `# *** builders` and first `# ** builder`
- One empty line between each `# *` section
- One empty line after docstrings and between code snippets

**Example** — `tiferet/builders/main.py`:

```python
# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..contexts.app import AppInterfaceContext
from ..assets import TiferetError
from ..di import ServiceProvider, DependenciesServiceProvider
from .. import assets as a
from ..domain import DomainObject, AppInterface, AppServiceDependency
from ..events import DomainEvent, ImportDependency, RaiseError
from ..events.app import GetAppInterface

# *** constants

# ** constant: app_service_key
APP_SERVICE_KEY = 'app_service'

# *** builders

# ** builder: app_builder
class AppBuilder(object):
    '''
    The main application builder for Tiferet v2.0+.
    '''

    # * attribute: cache
    cache: Dict[str, Any]

    # * attribute: service_provider
    service_provider: ServiceProvider

    # * init
    def __init__(self):
        '''
        Initialize the AppBuilder with empty cache and default service provider.
        '''

        self.cache = {}
        self.service_provider = self.create_service_provider()
```

## Writing Builders

### Creating a New Builder

1. Place the class under `# *** builders` in an appropriate module (e.g., `tiferet/builders/main.py`).
2. Use `# ** builder: <snake_case_name>`.
3. Implement the standard lifecycle:
   - `__init__`
   - `create_service_provider` (static factory)
   - `load_app_service`
   - `load_default_services`
   - `load_app_instance`
   - `load_interface`
   - `run` (high-level entry point)

### Key Patterns

**Method Chaining**  
`load_app_service()` returns `self` to support fluent usage:

```python
builder = AppBuilder().load_app_service(...)
```

**Default Configuration Injection**  
Builders automatically inject `DEFAULT_SERVICES` and `DEFAULT_CONSTANTS` via `GetAppInterface`:

```python
app_interface = DomainEvent.handle(
    GetAppInterface,
    ...,
    default_services=default_services,
    default_constants=a.const.DEFAULT_CONSTANTS,
)
```

**Service Provider Registration**  
The builder’s static factory is registered so contexts can create scoped providers:

```python
dependencies['create_service_provider'] = self.create_service_provider
```

**Defensive Service Lookup**  
Always check the cache before using the app service:

```python
app_service = self.cache.get(APP_SERVICE_KEY)
if not app_service:
    RaiseError.execute(...)
```

## Testing Builders

Builder tests use `pytest` with `unittest.mock`. Focus on:

- Proper initialization of cache and service provider
- Correct loading of the app service
- Delegation to `GetAppInterface` with defaults injected
- Validation of the resolved `AppInterfaceContext`
- High-level `run()` behavior

**Example test structure:**

```python
# *** fixtures

# ** fixture: app_builder
@pytest.fixture
def app_builder():
    builder = AppBuilder()
    builder.load_app_service(...)
    return builder

# *** tests

# ** test: app_builder_load_interface_with_defaults
def test_app_builder_load_interface_with_defaults(app_builder):
    with mock.patch('tiferet.events.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = mock_app_interface

        result = app_builder.load_interface('test_calc')

        assert isinstance(result, AppInterfaceContext)
        assert mock_handle.call_args.kwargs['default_constants'] == a.const.DEFAULT_CONSTANTS
```

## Best Practices

- Keep builders **thin** — they should orchestrate, not implement domain logic.
- Always validate the resolved context type in `load_interface`.
- Use `RaiseError.execute()` for all error paths with proper constants.
- Support method chaining where it improves developer experience.
- Register `create_service_provider` so contexts remain decoupled from the builder.

## Conclusion

Builders provide a clean, high-level API for initializing and running Tiferet applications. They encapsulate service loading, default configuration, and interface resolution while delegating execution to `AppInterfaceContext`. Their structured design ensures consistency, forward-compatibility, and extensibility.

Explore source in `tiferet/builders/` and tests in `tiferet/builders/tests/` for implementation details.

## Related Documentation

- [docs/guides/builders.md](../guides/builders.md) — Builder strategies and patterns
- [docs/core/contexts.md](../core/contexts.md) — Context design and usage
- [docs/guides/events.md](../guides/events.md) — Domain event usage within builders
- [docs/core/code_style.md](../core/code_style.md) — Artifact comments and formatting