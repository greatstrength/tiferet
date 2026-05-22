# Contexts in Tiferet

Contexts are a core component of the Tiferet framework, representing the structural "body" of an application in runtime "graph space." While blueprints (`tiferet/blueprints/`) control the timing, execution, and procedure of the app, Contexts define its shape and behavior, encapsulating user interactions, internal orchestration, and supporting services. In Tiferet, Contexts are the primary runtime components safely accessible to blueprints, making their methods and attributes extensible for developers (human or AI). This document explores the structured code design behind Contexts, how to write and extend them, and how to test them, using the calculator application as an example and adhering to Tiferet's code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Context?

A Context in Tiferet is a class that encapsulates a specific aspect of an application’s runtime behavior, such as user-facing interactions (e.g., CLI, web), feature execution, dependency injection, error handling, caching, or logging. Contexts form a graph-like structure during execution, defining how the application processes inputs, executes domain logic, and returns outputs. They align with Domain-Driven Design (DDD) principles, isolating concerns to ensure modularity and extensibility.

### Types of Contexts
Tiferet recognizes two broad categories:

- **High-Level Contexts**: Handle user interactions (e.g., `FlaskApiContext` for web APIs). They typically extend `AppInterfaceContext`. CLI interfaces use `AppInterfaceContext` directly, with argparse wiring handled by the `build_cli` blueprint.
- **Low-Level Contexts**: Support specific functions (e.g., `FeatureContext`, `DIContext`, `ErrorContext`, `CacheContext`, `RequestContext`, `LoggingContext`).

In the calculator application, `AppInterfaceContext` handles feature execution, while low-level contexts manage dependency injection, error handling, and logging.

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

**Example** – `tiferet/contexts/app.py`:
```python
# *** imports

# ** app
from .feature import FeatureContext
from .error import ErrorContext
from .logging import LoggingContext

# *** contexts

# ** context: app_interface_context
class AppInterfaceContext:

    # * attribute: interface_id
    interface_id: str

    # * attribute: features
    features: FeatureContext

    # * attribute: errors
    errors: ErrorContext

    # * attribute: logging
    logging: LoggingContext

    # * init
    def __init__(self, interface_id, features, errors, logging):
        '''
        Initialize the application interface context.
        '''
        self.interface_id = interface_id
        self.features = features
        self.errors = errors
        self.logging = logging

    # * method: run
    def run(self, feature_id, headers=None, data=None, **kwargs):
        '''
        Execute a feature and return the response.
        '''
        # Build logger.
        logger = self.logging.build_logger()

        # Parse request into a RequestContext.
        request = self.parse_request(headers or {}, data or {}, feature_id)

        # Execute the feature.
        try:
            self.execute_feature(feature_id=feature_id, request=request, logger=logger, **kwargs)
        except TiferetError as e:
            return self.handle_error(e)

        # Return the response.
        return self.handle_response(request)
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

**Example** – `AppInterfaceContext` test:
```python
# *** fixtures

# ** fixture: app_interface_context
@pytest.fixture
def app_interface_context(feature_context, error_context, logging_context):
    return AppInterfaceContext(
        interface_id='basic_calc',
        features=feature_context,
        errors=error_context,
        logging=logging_context,
    )

# *** tests

# ** test: app_interface_context_run_success
def test_app_interface_context_run_success(app_interface_context):
    # Arrange the logger.
    app_interface_context.logging.build_logger.return_value = mock.Mock()

    # Act.
    result = app_interface_context.run('calc.add', data={'a': 1, 'b': 2})

    # Assert execution was invoked.
    app_interface_context.features.execute_feature.assert_called_once()
    assert result is not None
```

### Best Practices
- Use `# ** fixture` and `# ** test` comments.
- Mock dependencies.
- Test all `# * method` behaviors.
- Include RST docstrings.

## Conclusion

Contexts define the runtime shape of Tiferet applications, orchestrating user interaction and internal services. Their structured design ensures consistency and extensibility. Developers can create new Contexts or extend existing ones by following artifact patterns and conventions. Explore `tiferet/contexts/` for source and `tiferet/contexts/tests/` for test examples.