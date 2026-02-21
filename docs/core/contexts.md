# Contexts in Tiferet

Contexts are a core component of the Tiferet framework, representing the structural "body" of an application in runtime "graph space." While Initializer Scripts control the timing, execution, and procedure of the app, Contexts define its shape and behavior, encapsulating user interactions, internal orchestration, and supporting services. In Tiferet, Contexts are the primary runtime components safely accessible to Initializer Scripts, making their methods and attributes extensible for developers (human or AI). This document explores the structured code design behind Contexts, how to write and extend them, and how to test them, using the calculator application as an example and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/v1.x-proto/tiferet/assets/docs/core/code_style.md)).

## What is a Context?

A Context in Tiferet is a class that encapsulates a specific aspect of an application’s runtime behavior, such as user-facing interactions (e.g., CLI, web), feature execution, dependency injection, error handling, caching, or logging. Contexts form a graph-like structure during execution, defining how the application processes inputs, executes domain logic, and returns outputs. They align with Domain-Driven Design (DDD) principles, isolating concerns to ensure modularity and extensibility.

### Types of Contexts
Tiferet recognizes two broad categories:

- **High-Level Contexts**: Handle user interactions (e.g., `CliContext` for command-line, `FlaskApiContext` for web APIs). They typically extend `AppInterfaceContext`.
- **Low-Level Contexts**: Support specific functions (e.g., `FeatureContext`, `ContainerContext`, `ErrorContext`, `CacheContext`, `RequestContext`, `LoggingContext`).

In the calculator application, `CliContext` handles CLI inputs, while low-level contexts manage feature execution, error handling, and logging.

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

**Example** – `tiferet/contexts/cli.py`:
```python
# *** imports

# ** core
import sys

# ** app
from .app import AppInterfaceContext
from ..handlers.cli import CliService

# *** contexts

# ** context: cli_context
class CliContext(AppInterfaceContext):

    # * attribute: cli_service
    cli_service: CliService

    # * init
    def __init__(self, interface_id, features, errors, logging, cli_service):
        '''
        Initialize the CLI context.
        '''
        super().__init__(interface_id, features, errors, logging)
        self.cli_service = cli_service

    # * method: parse_request
    def parse_request(self):
        '''
        Parse CLI arguments and return RequestContext.
        '''
        # Retrieve commands and parse args
        cli_commands = self.cli_service.get_commands()
        data = self.cli_service.parse_arguments(cli_commands)
        # Build feature_id and return RequestContext
        ...
```

## Writing Contexts

### Creating a New Context
1. Place under `# *** contexts` in appropriate module.
2. Extend `AppInterfaceContext` for high-level contexts or base class for low-level.
3. Use `# * attribute`, `# * init`, `# * method` comments.
4. Follow spacing and docstring conventions.

**Example** – High-level `FlaskApiContext`:
```python
# ** context: flask_api_context
class FlaskApiContext(AppInterfaceContext):

    # * attribute: flask_handler
    flask_handler: FlaskApiHandler

    # * init
    def __init__(self, interface_id, features, errors, logging, flask_handler):
        super().__init__(interface_id, features, errors, logging)
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

**Example** – `CliContext` test:
```python
# *** fixtures

# ** fixture: cli_context
@pytest.fixture
def cli_context(feature_context, error_context, logging_context):
    return CliContext(
        interface_id='calc_cli',
        features=feature_context,
        errors=error_context,
        logging=logging_context,
        cli_service=mock.Mock(spec=CliService)
    )

# *** tests

# ** test: cli_context_parse_request
def test_cli_context_parse_request(cli_context):
    # Mock service responses
    cli_context.cli_service.get_commands.return_value = {...}
    cli_context.cli_service.parse_arguments.return_value = {...}
    request = cli_context.parse_request()
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'calc.add'
```

### Best Practices
- Use `# ** fixture` and `# ** test` comments.
- Mock dependencies.
- Test all `# * method` behaviors.
- Include RST docstrings.

## Conclusion

Contexts define the runtime shape of Tiferet applications, orchestrating user interaction and internal services. Their structured design ensures consistency and extensibility. Developers can create new Contexts or extend existing ones by following artifact patterns and conventions. Explore `tiferet/contexts/` for source and `tiferet/contexts/tests/` for test examples.