```markdown
# Contexts in Tiferet

Contexts are a core component of the Tiferet framework, encapsulating the runtime environment and interaction model for applications. They orchestrate user inputs, feature execution, error handling, and logging, aligning with Domain-Driven Design (DDD) principles to ensure modularity and separation of concerns. This document explains what Contexts are, their role in Tiferet, how to create or extend them, and how to test them, with examples from the calculator application.

## What is a Context?

A Context in Tiferet is a class that manages a specific aspect of the application’s runtime behavior, such as user interaction (e.g., CLI, web), feature orchestration, dependency injection, error handling, caching, or logging. Contexts are organized hierarchically, with high-level Contexts (e.g., `CliContext`) handling user-facing interactions and lower-level Contexts (e.g., `FeatureContext`, `ErrorContext`) supporting specific functions.

- **High-Level Contexts**: Extend `AppInterfaceContext` to manage user interactions, such as `CliContext` for command-line interfaces or `FlaskApiContext` for web APIs. They parse inputs, execute features, and handle responses/errors.
- **Low-Level Contexts**: Support specific operations, such as `FeatureContext` (feature execution), `ContainerContext` (dependency injection), `ErrorContext` (error handling), `CacheContext` (caching), `RequestContext` (request state), and `LoggingContext` (logging).

Contexts align with DDD’s bounded contexts, isolating interaction logic from domain logic (Commands) and infrastructure (Configurations), ensuring clarity and extensibility.

## Role in the Tiferet Framework

Contexts are one of four core components in Tiferet, alongside **Commands**, **Configurations**, and **Initializer Scripts**:
- **Commands**: Encapsulate domain logic (e.g., `AddNumber` for addition in the calculator).
- **Configurations**: Define behavior via YAML files (e.g., `app.yml`, `feature.yml`).
- **Initializer Scripts**: Bootstrap the application (e.g., `basic_calc.py`, `calc_cli.py`).
- **Contexts**: Manage runtime interactions and support services, orchestrated by `AppManagerContext` (aliased as `App`).

The `AppManagerContext` initializes the application, loading Configurations and creating high-level Contexts (e.g., `CliContext`) via `load_interface`. High-level Contexts, extending `AppInterfaceContext`, use lower-level Contexts to execute features, handle errors, and log events. This hierarchy ensures modularity, allowing new interfaces (e.g., web, TUI) to be added without altering core logic.

### Context Hierarchy
The following diagram illustrates the Context hierarchy and their interactions:

```mermaid
graph TD
    A[Initializer Scripts<br>basic_calc.py, calc_cli.py] --> B[AppManagerContext<br>(App)]
    B --> C[AppInterfaceContext<br>e.g., CliContext, FlaskApiContext]
    C --> D[FeatureContext]
    C --> E[ErrorContext]
    C --> F[LoggingContext]
    D --> G[ContainerContext]
    D --> H[RequestContext]
    D --> I[CacheContext]
    E --> I
    G --> I
    G --> J[Run Command<br>e.g., AddNumber]
    D --> J[Execute Feature]
    E --> K[Handle TiferetError]
    F --> L[Log Events]
    style B fill:#bbf,stroke:#333
    style C fill:#bbf,stroke:#333
    style D fill:#bbf,stroke:#333
    style E fill:#bbf,stroke:#333
    style F fill:#bbf,stroke:#333
    style G fill:#bbf,stroke:#333
    style H fill:#bbf,stroke:#333
    style I fill:#bbf,stroke:#333
```

- **AppManagerContext**: Initializes the application, loading Configurations and creating `AppInterfaceContext` instances.
- **AppInterfaceContext**: Base for user-facing Contexts (e.g., `CliContext`), managing feature execution, errors, and logging.
- **Lower-Level Contexts**: Support specific functions, integrated via dependency injection.

### Example: Calculator Application
In the calculator application ([app/commands/calc.py](https://github.com/greatstrength/tiferet/blob/main/app/commands/calc.py)), Contexts enable scripted (`basic_calc.py`) and CLI (`calc_cli.py`) interactions:
- **CliContext**: Parses CLI inputs (e.g., `python calc_cli.py calc add 1 2`), creates a `RequestContext`, and executes `calc.add` via `FeatureContext`.
- **FeatureContext**: Loads `AddNumber` from `ContainerContext` (using `container.yml`) and executes it, storing results in `RequestContext`.
- **ErrorContext**: Handles errors like `DIVISION_BY_ZERO` (from `error.yml`).
- **LoggingContext**: Logs events (e.g., “Executing feature: calc.add”).
- **CacheContext**: Caches features, injectors, and error maps for performance.
- **RequestContext**: Manages inputs (`{'a': 1, 'b': 2}`) and results (3).

## Creating and Extending Contexts

Contexts are designed for extensibility, using the template design pattern to allow new interfaces (e.g., web, TUI) to extend `AppInterfaceContext` without modifying core logic. Below are steps to create or extend Contexts, with examples.

### Creating a New Context
To add a new interface (e.g., a Flask API), follow these steps:
1. **Define the Context Class**:
   - Extend `AppInterfaceContext` to handle interface-specific logic (e.g., parsing HTTP requests for a web API).
   - Override methods like `parse_request`, `run`, or `handle_response` as needed.
   - Example: `FlaskApiContext` for a web interface ([app/contexts/flask.py](https://github.com/greatstrength/tiferet/blob/main/app/contexts/flask.py)):
     ```python
     from flask import Flask
     from tiferet.contexts.app import AppInterfaceContext
     from .request import FlaskRequestContext

     class FlaskApiContext(AppInterfaceContext):
         def __init__(self, interface_id, features, errors, logging, flask_api_handler):
             super().__init__(interface_id, features, errors, logging)
             self.flask_api_handler = flask_api_handler

         def parse_request(self, headers, data, feature_id, **kwargs) -> FlaskRequestContext:
             return FlaskRequestContext(headers=headers, data=data, feature_id=feature_id)

         def handle_response(self, request):
             response, status_code = super().handle_response(request), self.flask_api_handler.get_route(request.feature_id).status_code
             return response, status_code
     ```

2. **Configure in `app.yml`**:
   - Add the new interface to `app/configs/app.yml`, specifying the Context class and dependencies:
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

3. **Create an Initializer Script**:
   - Write a script (e.g., `calc_web.py`) to instantiate `AppManagerContext` and run the Context:
     ```python
     from tiferet import App
     app = App()
     web = app.load_interface('web_calc')
     if __name__ == '__main__':
         web.run()
     ```

4. **Implement Supporting Classes**:
   - Define a custom request Context (e.g., `FlaskRequestContext`) and handler (e.g., `FlaskApiHandler`) if needed, as shown in the `FlaskApiContext` example.

### Extending an Existing Context
To extend an existing Context (e.g., `CliContext` for custom CLI behavior):
1. **Subclass the Context**:
   - Extend `CliContext` or `AppInterfaceContext` to override specific methods.
   - Example: Add custom parsing logic to `CliContext`:
     ```python
     from tiferet.contexts.cli import CliContext

     class CustomCliContext(CliContext):
         def parse_request(self):
             request = super().parse_request()
             request.data['custom_key'] = 'custom_value'
             return request
     ```

2. **Update `app.yml`**:
   - Reference the new Context class:
     ```yaml
     interfaces:
       custom_cli:
         name: Custom CLI
         description: Custom CLI interface
         module_path: app.contexts
         class_name: CustomCliContext
         attrs:
           cli_service:
             module_path: tiferet.handlers.cli
             class_name: CliHandler
     ```

3. **Use in an Initializer Script**:
   - Update `calc_cli.py` or create a new script to use `custom_cli`.

### Best Practices
- Use the template design pattern to override only necessary methods (e.g., `parse_request`, `run`).
- Configure Contexts in `app.yml` to avoid code changes.
- Leverage lower-level Contexts (`FeatureContext`, `ErrorContext`, etc.) for modularity.
- Ensure type hints and docstrings for AI compatibility and developer clarity.

## Testing Contexts

Testing Contexts ensures they handle inputs, execute features, and manage errors/logging correctly. Tiferet uses `pytest` with `unittest.mock` for unit tests, as seen in tests for `AppInterfaceContext` and `FeatureContext` ([tests/app.py](https://github.com/greatstrength/tiferet/blob/main/tests/app.py), [tests/feature.py](https://github.com/greatstrength/tiferet/blob/main/tests/feature.py)).

### Testing Approach
- **Fixtures**: Mock dependencies (e.g., `FeatureContext`, `ErrorContext`, `CliService`) to isolate tests.
- **Scenarios**: Test success cases (e.g., feature execution), error cases (e.g., invalid inputs), and edge cases (e.g., `pass_on_error`).
- **Assertions**: Verify outputs, error codes, and logging calls.

### Example: Testing CliContext
To test `CliContext`:
1. **Create Fixtures**:
   ```python
   @pytest.fixture
   def cli_context(feature_context, error_context, logging_context):
       return CliContext(
           interface_id='calc_cli',
           features=feature_context,
           errors=error_context,
           logging=logging_context,
           cli_service=mock.Mock(spec=CliService)
       )
   ```

2. **Test Parsing**:
   ```python
   def test_cli_context_parse_request(cli_context):
       cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
       cli_context.cli_service.parse_arguments.return_value = {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
       request = cli_context.parse_request()
       assert isinstance(request, RequestContext)
       assert request.feature_id == 'calc.add'
       assert request.data == {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
   ```

3. **Test Execution**:
   ```python
   def test_cli_context_run(cli_context, logging_context):
       cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
       cli_context.cli_service.parse_arguments.return_value = {'group': 'calc', 'command': 'add', 'a': 1, 'b': 2}
       cli_context.features.execute_feature.return_value = None
       request = RequestContext(data={'a': 1, 'b': 2}, feature_id='calc.add')
       request.result = 3
       response = cli_context.run()
       assert response == 3
       logging_context.build_logger.assert_called_once()
   ```

4. **Test Error Handling**:
   ```python
   def test_cli_context_run_error(cli_context, logging_context):
       cli_context.cli_service.get_commands.return_value = {'calc.add': {'group': 'calc', 'key': 'add'}}
       cli_context.cli_service.parse_arguments.side_effect = Exception('Invalid args')
       with pytest.raises(SystemExit) as exc_info:
           cli_context.run()
       assert exc_info.value.code == 2
       logging_context.build_logger.assert_called_once()
       logging_context.build_logger.return_value.error.assert_called_with('Error parsing CLI request: Invalid args')
   ```

### Best Practices
- Mock dependencies to isolate Context logic.
- Test all overridden methods (e.g., `parse_request`, `run`).
- Verify logging (`LoggingContext`) and error handling (`ErrorContext`).
- Use `pytest` for parameterized tests to cover edge cases.

## Conclusion
Contexts are the backbone of Tiferet’s runtime behavior, enabling flexible, user-facing interfaces (e.g., `CliContext`) and supporting services (e.g., `FeatureContext`, `ErrorContext`). By extending `AppInterfaceContext` and configuring via `app.yml`, developers can create new interfaces like web APIs or TUIs with minimal code changes. Unit tests ensure robustness, covering parsing, execution, and error handling. Explore [app/contexts/](https://github.com/greatstrength/tiferet/tree/main/app/contexts/) for source code and [tests/](https://github.com/greatstrength/tiferet/tree/main/tests/) for test examples.
```