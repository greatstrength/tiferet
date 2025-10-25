# Contexts in Tiferet

Contexts are a core component of the Tiferet framework, representing the structural "body" of an application in runtime "graph space." While Initializer Scripts control the timing, execution, and procedure of the app, Contexts define its shape and behavior, encapsulating user interactions, internal orchestration, and supporting services. In Tiferet, Contexts and Handlers are the only components safely accessible to Initializer Scripts at runtime, making their methods and attributes extensible for developers (human or AI). This document explores the structured code design behind Contexts, how to write and extend them, and how to test them, using the calculator application as an example and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Context?

A Context in Tiferet is a class that encapsulates a specific aspect of an application’s runtime behavior, such as user-facing interactions (e.g., CLI, web), feature execution, dependency injection, error handling, caching, or logging. Contexts form a graph-like structure during execution, defining how the application processes inputs, executes domain logic, and returns outputs. They align with Domain-Driven Design (DDD) principles, isolating concerns (e.g., interaction logic from domain logic) to ensure modularity and extensibility.

## Types of Contexts

Tiferet loosely understands three context types:

- **High-Level Contexts**: Handle user interactions, such as `CliContext` for command-line interfaces or `FlaskApiContext` for web APIs. They extend `AppInterfaceContext` to parse inputs and manage execution.
- **Low-Level Contexts**: Support specific functions, such as `FeatureContext` (feature execution), `ContainerContext` (dependency injection), `ErrorContext` (error handling), `CacheContext` (caching), `RequestContext` (request state), and `LoggingContext` (logging).
- **Role in Runtime**: Contexts are instantiated by `AppManagerContext` (aliased as `App`) via Initializer Scripts (e.g., `calc_cli.py`) and configured via YAML files (e.g., `app.yml`). Their methods and attributes are designed to be safely exposed for extension.

In the calculator application, `CliContext` handles CLI inputs (e.g., `python calc_cli.py calc add 1 2`), while low-level Contexts like `FeatureContext` and `ErrorContext` manage feature execution and errors.

## Structured Code Design of Contexts

Tiferet enforces a structured code design for Contexts, using artifact comments to organize code and ensure consistency, as detailed in [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md). This structure makes Contexts readable, extensible, and AI-parsable, allowing developers to tailor methods and attributes to the application’s domain.

### Artifact Comments

Contexts are organized under the `# *** contexts` top-level comment, with individual Contexts under `# ** context: <context_name>` in snake_case. Within each Context, three artifact types are defined under low-level comments:

- `# * attribute: <attribute_name>`: Declares instance attributes (e.g., `cli_service`, `features`), typically with type hints.
- `# * init`: Marks the initializer method (`__init__`).
- `# * method: <method_name>`: Identifies methods (e.g., `parse_request`, `run`), designed for accessibility by Initializer Scripts.

These comments provide a clear, consistent structure, with one empty line between the top-level `# *** contexts` and the first mid-level `# ** context: <context_name>`, and between subcomponents (`# *`). For example, in `app/contexts/cli.py`:

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
        Initialize the CLI context with a CLI service.
        '''
        
        # Initialize the base class with the interface ID, features, and errors.
        super().__init__(interface_id, features, errors, logging)
        
        # Set the CLI service.
        self.cli_service = cli_service

    # * method: parse_request
    def parse_request(self):
        '''
        Parse the command line arguments and return a Request object.
        '''
        
        # Retrieve the command map from the CLI service.
        cli_commands = self.cli_service.get_commands()
        
        # Parse the command line arguments for the CLI command.
        data = self.cli_service.parse_arguments(cli_commands)
```

### Extensible Methods and Attributes

Methods and attributes in Contexts are designed to be accessible to Initializer Scripts, allowing safe extension by developers. There are no strict rules for their design, as they depend on the application’s domain and runtime needs. Key considerations:

- **Attributes**: Store dependencies (e.g., cli_service, features) or state (e.g., interface_id). Use type hints for clarity and AI compatibility.
- **Methods**: Handle domain-specific tasks (e.g., parse_request for input processing, run for execution). They should be flexible, accepting **kwargs where appropriate, and align with the Context’s purpose.
- **Extensibility**: High-level Contexts (e.g., CliContext) use the template design pattern, overriding methods like parse_request or run from AppInterfaceContext to customize behavior while reusing core logic.

Example: In the calculator application, CliContext.parse_request parses CLI inputs (e.g., calc add 1 2) into a RequestContext, while run executes features via FeatureContext.

## Writing Contexts
To write a Context, follow Tiferet’s structured code design and tailor methods/attributes to the domain. Below are steps to create a new Context, using FlaskApiContext as an example for a web interface.

## Creating New and Extending Existing Contexts

To create new functionality or extend existing behavior, developers can add or modify Context classes, following Tiferet’s structured code guidelines. Below are steps to create a new Context or extend an existing one, using `FlaskApiContext` as an example for a web interface.

1. **Define the Context Class**:

   - Place under `# *** contexts` and `# ** context: <context_name>` in a module (e.g., `app/contexts/flask.py`).
   - Extend `AppInterfaceContext` for user-facing Contexts or create a standalone class for low-level Contexts.
   - Add attributes and methods under `# * attribute` and `# * method`, with one empty line between subcomponents and snippets.
   - Example: `FlaskApiContext` for a web API:

     ```python
     # *** imports

     # ** core
     from typing import Any

     # ** infra
     from flask import Flask

     # ** app
     from tiferet.contexts.app import AppInterfaceContext
     from .request import FlaskRequestContext

     # *** contexts

     # ** context: flask_api_context
     class FlaskApiContext(AppInterfaceContext):

         # * attribute: flask_api_handler
         flask_api_handler: FlaskApiHandler

         # * init
         def __init__(self,
                 interface_id,
                 features,
                 errors,
                 logging,
                 flask_api_handler
             ):
             '''
             Initialize the application interface context.
             '''
             
             # Call the parent constructor.
             super().__init__(interface_id, features, errors, logging)
             
             # Set the attributes.
             self.flask_api_handler = flask_api_handler

         # * method: parse_request
         def parse_request(self, headers, data, feature_id, **kwargs) -> FlaskRequestContext:
             '''
             Parse the incoming request and return a FlaskRequestContext instance.
             '''
             
             # Return a FlaskRequestContext instance.
             return FlaskRequestContext(headers=headers, data=data, feature_id=feature_id)

         # * method: handle_response
         def handle_response(self, request):
             '''
             Handle the response from the request context.
             '''
             
             # Handle the response from the parent context.
             response = super().handle_response(request)
             
             # Retrieve the route by the request feature id.
             route = self.flask_api_handler.get_route(request.feature_id)
             
             # Return the result as JSON with the specified status code.
             return response, route.status_code
     ```

2. **Configure in `app.yml`**:

   - Add the Context to `app/configs/app.yml`, specifying its module and class, with one empty line between sections:

     ```yaml
     interfaces:

       web_calc:
         name: Web Calculator
         description: Calculator via HTTP API
         module_path: app.contexts
         class_name: FlaskApiContext
         attrs:

           flask_api_handler:
             module_path: app.handlers
             class_name: FlaskApiHandler
     ```

3. **Use in an Initializer Script**:

   - Create a script (e.g., `calc_web.py`) to instantiate and run the Context, following the structured code style:

     ```python
     # *** imports

     # ** app
     from tiferet import App

     # *** script

     app = App()
     web = app.load_interface('web_calc')
     if __name__ == '__main__':
         web.run()
     ```

4. **Define Methods and Attributes**:

   - Add attributes under `# * attribute` to store dependencies or state, with type hints.
   - Define methods under `# * method`, ensuring they align with the domain (e.g., HTTP request parsing for web), with one empty line between snippets and after docstrings.
   - Use `**kwargs` for flexibility and RST-formatted docstrings.

5. **Leverage Lower-Level Contexts**:

   - Inject `FeatureContext`, `ErrorContext`, `LoggingContext`, etc., to reuse core functionality (e.g., feature execution, error handling).

### Best Practices

- Use artifact comments (`# * attribute`, `# * init`, `# * method`) consistently, with one empty line between subcomponents.
- Design methods to be accessible to Initializer Scripts, focusing on domain-specific tasks.
- Ensure attributes are typed and documented for AI compatibility.
- Follow the template design pattern for high-level Contexts, overriding only necessary methods.
- Maintain one empty line between `# ***` and `# **`, and between snippets within methods.

### Best Practices

- Use artifact comments (# * attribute, # * init, # * method) for consistency.
- Design methods to be accessible to Initializer Scripts, focusing on domain-specific tasks.
- Ensure attributes are typed and documented for AI compatibility.
- Follow the template design pattern for high-level Contexts, overriding only necessary methods.

## Testing Contexts

Testing ensures Contexts adhere to Tiferet’s structured code style and function correctly. Test modules use `pytest` with `unittest.mock` to isolate dependencies and cover success, error, and edge cases, organized under `# *** fixtures` and `# *** tests` with `# ** fixture` and `# ** test` comments, as seen in `tiferet/contexts/tests/test_app.py` and `tiferet/context/tests/test_feature.py`.

### Testing Approach

- **Fixtures**: Mock dependencies (e.g., `CliService`, `FeatureContext`) under `# ** fixture: <fixture_name>`.
- **Scenarios**: Test success cases (e.g., parsing inputs, executing features), error cases (e.g., invalid inputs), and edge cases (e.g., `pass_on_error`).
- **Assertions**: Verify outputs, error codes, logging calls, and state changes in `RequestContext`.

### Example: Testing CliContext

Below is an example test suite for `CliContext` ([tiferet/contexts/cli.py](https://github.com/greatstrength/tiferet/blob/main/tiferet/contexts/cli.py)):

```python
# *** imports

# ** core
import pytest
from unittest import mock

# ** app
from tiferet.contexts.cli import CliContext
from tiferet.contexts.app import RequestContext

# *** fixtures

# ** fixture: cli_context
@pytest.fixture
def cli_context(feature_context, error_context, logging_context):
    '''
    Fixture to create a CliContext instance.
    '''
    
    # Create a CliContext with mocked dependencies.
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
    '''
    Test parsing CLI arguments in CliContext.
    '''
    
    # Mock CLI service responses.
    cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
    cli_context.cli_service.parse_arguments.return_value = {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
    
    # Parse the request.
    request = cli_context.parse_request()
    
    # Assert request properties.
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'calc.add'
    assert request.data == {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}

# ** test: cli_context_run_success
def test_cli_context_run_success(cli_context, logging_context):
    '''
    Test successful CLI execution in CliContext.
    '''
    
    # Mock CLI service and feature execution.
    cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
    cli_context.cli_service.parse_arguments.return_value = {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
    cli_context.features.execute_feature.return_value = None
    request = RequestContext(data={'a': 1, 'b': 2}, feature_id='calc.add')
    request.result = 3
    
    # Run the CLI context and verify output.
    with mock.patch('builtins.print') as mocked_print:
        cli_context.run()
        mocked_print.assert_called_with(3)
    
    # Verify logging.
    logging_context.build_logger.assert_called_once()

# ** test: cli_context_run_error
def test_cli_context_run_error(cli_context, logging_context):
    '''
    Test error handling in CliContext.
    '''
    
    # Mock CLI service to raise an error.
    cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
    cli_context.cli_service.parse_arguments.side_effect = Exception('Invalid args')
    
    # Verify error handling and exit code.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run()
    assert exc_info.value.code == 2
    
    # Verify logging.
    logging_context.build_logger.assert_called_once()
    logging_context.build_logger.return_value.error.assert_called_with('Error parsing CLI request: Invalid args')
```

### Best Practices

- Use `# *** fixtures`, `# ** fixture`, `# *** tests`, `# ** test` for test organization, with one empty line between sections and comments.
- Mock dependencies to isolate Context logic (e.g., `CliService`, `FeatureContext`).
- Test all methods and attributes under `# *` comments, verifying outputs and state changes.
- Include RST-formatted docstrings for fixtures and tests, with one empty line after docstrings.
- Use parameterized tests for edge cases (e.g., invalid inputs, missing features).
- Maintain one empty line between snippets within tests.


## Conclusion

Contexts are the structural core of Tiferet applications, defining their shape in runtime graph space. Their structured code design, using artifact comments (`# * attribute`, `# * init`, `# * method`) and consistent formatting (docstrings, indentation, snippets, spacing), ensures consistency and extensibility. Developers can create new Contexts (e.g., `FlaskApiContext`) or extend existing ones (e.g., `CliContext`) by following the template design pattern and configuring via `app.yml`. Unit tests validate robustness, covering parsing, execution, and error handling. Explore [app/contexts/](https://github.com/greatstrength/tiferet/tree/main/app/contexts/) for source code and [tests/](https://github.com/greatstrength/tiferet/tree/main/tests/) for test examples.
