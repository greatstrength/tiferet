---
title: Contexts in Tiferet
framework: Tiferet
version: 1.0.0
repo: https://github.com/greatstrength/tiferet
keywords: [contexts, appinterfacecontext, clicontext, featurecontext, containercontext, errorcontext, cachecontext, requestcontext, loggingcontext, structured code]
---

# Contexts in Tiferet

Contexts are a core component of the Tiferet framework, representing the structural "body" of an application in runtime "graph space." While Initializer Scripts control the timing, execution, and procedure of the app, Contexts define its shape and behavior, encapsulating user interactions, feature orchestration, and supporting services. In Tiferet, Contexts and Handlers are the only components safely accessible to Initializer Scripts at runtime, making their methods and attributes extensible for developers (human or AI). This document explores the structured code design behind Contexts, how to write them, and how to test them, using the calculator application as an example.

## What is a Context?

A Context in Tiferet is a class that encapsulates a specific aspect of an application’s runtime behavior, such as user-facing interactions (e.g., CLI, web), feature execution, dependency injection, error handling, caching, or logging. Contexts form a graph-like structure during execution, defining how the application processes inputs, executes domain logic, and returns outputs. They align with Domain-Driven Design (DDD) principles, isolating concerns (e.g., interaction logic from domain logic) to ensure modularity and extensibility.

- **High-Level Contexts**: Handle user interactions, such as `CliContext` for command-line interfaces or `FlaskApiContext` for web APIs. They extend `AppInterfaceContext` to parse inputs and manage execution.
- **Low-Level Contexts**: Support specific functions, such as `FeatureContext` (feature execution), `ContainerContext` (dependency injection), `ErrorContext` (error handling), `CacheContext` (caching), `RequestContext` (request state), and `LoggingContext` (logging).
- **Role in Runtime**: Contexts are instantiated by `AppManagerContext` (aliased as `App`) via Initializer Scripts (e.g., `calc_cli.py`) and configured via YAML files (e.g., `app.yml`). Their methods and attributes are designed to be safely exposed for extension.

In the calculator application, `CliContext` handles CLI inputs (e.g., `python calc_cli.py calc add 1 2`), while low-level Contexts like `FeatureContext` and `ErrorContext` manage feature execution and errors.

## Structured Code Design of Contexts

Tiferet enforces a structured code design for Contexts, using artifact comments to organize code and ensure consistency. This structure makes Contexts readable, extensible, and AI-parsable, allowing developers to tailor methods and attributes to the application’s domain.

### Artifact Comments
Context classes are organized under specific artifact comments in Python modules:
- `# *** imports`: Groups import statements, categorized as:
  - `# ** core`: Standard Python or typing imports (e.g., `typing.Dict`).
  - `# ** infra`: Infrastructure dependencies (e.g., `flask`, `logging`).
  - `# ** app`: Tiferet-specific imports (e.g., `AppInterfaceContext`, `CliService`).
- `# *** contexts`: Marks the section containing Context classes.
- `# ** context: <context_name>`: Identifies individual Contexts (e.g., `cli_context`, `feature_context`).

Within each Context, three artifact types are defined:
- `# * attribute: <attribute_name>`: Declares instance attributes (e.g., `cli_service`, `features`).
- `# * init`: Marks the initializer method (`__init__`).
- `# * method: <method_name>`: Identifies methods (e.g., `parse_request`, `run`).

These comments provide a clear, consistent structure, making it easy to navigate and extend Contexts. For example, in `cli.py`:
```python
# *** imports
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
        super().__init__(interface_id, features, errors, logging)
        self.cli_service = cli_service

    # * method: parse_request
    def parse_request(self):
        # CLI-specific parsing logic
        ...

Extensible Methods and Attributes
Methods and attributes in Contexts are designed to be accessible to Initializer Scripts, allowing safe extension by developers. There are no strict rules for their design, as they depend on the application’s domain and runtime needs. Key considerations:

Attributes: Store dependencies (e.g., cli_service, features) or state (e.g., interface_id). Use type hints for clarity and AI compatibility.
Methods: Handle domain-specific tasks (e.g., parse_request for input processing, run for execution). They should be flexible, accepting **kwargs where appropriate, and align with the Context’s purpose.
Extensibility: High-level Contexts (e.g., CliContext) use the template design pattern, overriding methods like parse_request or run from AppInterfaceContext to customize behavior while reusing core logic.

Example: In the calculator application, CliContext.parse_request parses CLI inputs (e.g., calc add 1 2) into a RequestContext, while run executes features via FeatureContext.
Writing Contexts
To write a Context, follow Tiferet’s structured code design and tailor methods/attributes to the domain. Below are steps to create a new Context, using FlaskApiContext as an example for a web interface.
Steps to Write a Context

Define the Context Class:

Place under # *** contexts and # ** context: <context_name>.
Extend AppInterfaceContext for user-facing Contexts or create a standalone class for low-level Contexts (e.g., FeatureContext).
Example: FlaskApiContext for a web API (app/contexts/flask.py):# *** imports
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
    def __init__(self, interface_id, features, errors, logging, flask_api_handler):
        super().__init__(interface_id, features, errors, logging)
        self.flask_api_handler = flask_api_handler

    # * method: parse_request
    def parse_request(self, headers, data, feature_id, **kwargs) -> FlaskRequestContext:
        return FlaskRequestContext(headers=headers, data=data, feature_id=feature_id)

    # * method: handle_response
    def handle_response(self, request):
        response, status_code = super().handle_response(request), self.flask_api_handler.get_route(request.feature_id).status_code
        return response, status_code




Configure in app.yml:

Add the Context to app/configs/app.yml, specifying its module and class:interfaces:
  web_calc:
    name: Web Calculator
    description: Calculator via HTTP API
    module_path: app.contexts
    class_name: FlaskApiContext
    attrs:
      flask_api_handler:
        module_path: app.handlers
        class_name: FlaskApiHandler




Use in an Initializer Script:

Create a script (e.g., calc_web.py) to instantiate and run the Context:# *** imports
# ** app
from tiferet import App

# *** script
app = App()
web = app.load_interface('web_calc')
if __name__ == '__main__':
    web.run()




Define Methods and Attributes:

Add attributes (e.g., flask_api_handler) under # * attribute to store dependencies or state.
Define methods (e.g., parse_request, run) under # * method, ensuring they align with the domain (e.g., HTTP request parsing for web).
Use **kwargs for flexibility and type hints for clarity.


Leverage Lower-Level Contexts:

Inject FeatureContext, ErrorContext, LoggingContext, etc., to reuse core functionality (e.g., feature execution, error handling).



Best Practices

Use artifact comments (# * attribute, # * init, # * method) for consistency.
Design methods to be accessible to Initializer Scripts, focusing on domain-specific tasks.
Ensure attributes are typed and documented for AI compatibility.
Follow the template design pattern for high-level Contexts, overriding only necessary methods.

Testing Contexts
Testing Contexts ensures they correctly handle inputs, execute features, manage errors, and log events. Tiferet uses pytest with unittest.mock to isolate dependencies and test scenarios, as seen in tests for AppInterfaceContext and FeatureContext (tests/app.py, tests/feature.py).
Testing Approach

Fixtures: Mock dependencies (e.g., CliService, FeatureContext) to isolate Context logic.
Scenarios: Test success cases (e.g., parsing inputs, executing features), error cases (e.g., invalid inputs), and edge cases (e.g., pass_on_error).
Assertions: Verify outputs, error codes, logging calls, and state changes in RequestContext.

Example: Testing CliContext
Below is an example test suite for CliContext (app/contexts/cli.py):
# *** imports
# ** core
import pytest
from unittest import mock
# ** app
from tiferet.contexts.cli import CliContext
from tiferet.contexts.app import RequestContext

# *** fixtures
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
def test_cli_context_parse_request(cli_context):
    cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
    cli_context.cli_service.parse_arguments.return_value = {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
    request = cli_context.parse_request()
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'calc.add'
    assert request.data == {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}

def test_cli_context_run_success(cli_context, logging_context):
    cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
    cli_context.cli_service.parse_arguments.return_value = {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
    request = RequestContext(data={'a': 1, 'b': 2}, feature_id='calc.add')
    request.result = 3
    cli_context.features.execute_feature.return_value = None
    with mock.patch('builtins.print') as mocked_print:
        cli_context.run()
        mocked_print.assert_called_with(3)
    logging_context.build_logger.assert_called_once()

def test_cli_context_run_error(cli_context, logging_context):
    cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
    cli_context.cli_service.parse_arguments.side_effect = Exception('Invalid args')
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run()
    assert exc_info.value.code == 2
    logging_context.build_logger.assert_called_once()
    logging_context.build_logger.return_value.error.assert_called_with('Error parsing CLI request: Invalid args')

Best Practices

Mock dependencies to isolate Context logic (e.g., CliService, FeatureContext).
Test all methods (e.g., parse_request, run) and attributes accessed by Initializer Scripts.
Verify logging (LoggingContext) and error handling (ErrorContext) calls.
Use parameterized tests for edge cases (e.g., invalid inputs, missing features).

Contexts in Graph Space
Contexts form a graph-like structure during runtime, with AppManagerContext as the root, creating AppInterfaceContext instances (e.g., CliContext) that delegate to lower-level Contexts. The following diagram illustrates this structure in the calculator application:
graph TD
    A[Initializer Scripts<br>e.g., basic_calc.py, calc_cli.py] -->|Instantiate| B[AppManagerContext<br>(App)]
    B -->|Load| C[Configurations<br>e.g., app.yml, cli.yml]
    B -->|Create| D[CliContext<br>extends AppInterfaceContext]
    D -->|Execute| E[FeatureContext]
    D -->|Handle Errors| F[ErrorContext]
    D -->|Log| G[LoggingContext]
    E -->|Resolve| H[ContainerContext]
    E -->|Manage| I[RequestContext]
    E -->|Cache| J[CacheContext]
    F -->|Cache| J
    H -->|Cache| J
    H -->|Run| K[Commands<br>e.g., AddNumber]
    C -->|Define| D
    C -->|Define| E
    C -->|Define| F
    C -->|Define| K
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#dfd,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333
    style F fill:#bbf,stroke:#333
    style G fill:#bbf,stroke:#333
    style H fill:#bbf,stroke:#333
    style I fill:#bbf,stroke:#333
    style J fill:#bbf,stroke:#333
    style K fill:#ffb,stroke:#333,stroke-width:2px


Nodes: AppManagerContext (root), CliContext (user-facing), and lower-level Contexts (FeatureContext, etc.).
Edges: Show instantiation, configuration loading, feature execution, and Command resolution.
Graph Space: Contexts form a directed graph, with CliContext orchestrating interactions and lower-level Contexts handling specific tasks.

Conclusion
Contexts are the structural core of Tiferet applications, defining their shape in runtime graph space. Their structured code design, using artifact comments (# * attribute, # * init, # * method), ensures consistency and extensibility. Developers can create new Contexts (e.g., FlaskApiContext) or extend existing ones (e.g., CliContext) by following the template design pattern and configuring via app.yml. Unit tests validate robustness, covering parsing, execution, and error handling. Explore app/contexts/ for source code and tests/ for test examples.```