# Handlers in Tiferet

Handlers, or Service Handlers, are a core component of the Tiferet framework, encapsulating domain-specific service methods that manage events and implement core business logic for Commands and Contexts, aligning with Domain-Driven Design (DDD) principles. Handlers deal exclusively with Contracts (`ModelContract` and `Repository`), assuming that the data they process adheres to these interfaces, and never interact directly with Models. Handlers are accessible to Initializer Scripts, making their methods and attributes extensible for developers (human or AI). This document explores the structured code design behind Handlers, how to write and extend them, and how to test them, using the calculator application’s logging functionality as an example and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Handler?

A Handler in Tiferet is a class that provides domain-specific service methods to handle events, such as retrieving configurations, formatting data, or creating resources (e.g., loggers). Handlers implement `Repository` or other Contracts, ensuring consistent data access and processing, and are used by Commands and Contexts to execute business logic. They align with DDD’s application services, orchestrating domain operations while relying on Contracts for data structure and behavior.

- **Role in Runtime**: Handlers are instantiated by Contexts (e.g., `LoggingContext`) or Commands and configured via YAML files (e.g., `logging.yml`). They process data compliant with Contracts, such as `FormatterContract` or `LoggingRepository`, to perform tasks like logger creation or error handling.
- **Contract-Based**: Handlers interact only with Contracts, not Models, assuming the data satisfies the contract’s interface (e.g., `ErrorRepository` for error data access).
- **Accessibility**: Handlers are accessible to Initializer Scripts via Contexts, allowing developers to extend their functionality (e.g., custom logging in `calc_cli.py`).
- **Examples**: In the calculator application, `LoggingHandler` creates loggers for `LoggingContext` to log events (e.g., “Executing feature: calc.add”), while `ErrorHandler` retrieves errors compliant with `ErrorRepository` for `ErrorContext`.

## Structured Code Design of Handlers

Tiferet enforces a structured code design for Handlers, using artifact comments to organize code and ensure consistency, as detailed in [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md). This structure makes Handlers readable, extensible, and AI-parsable, allowing developers to implement domain-specific services.

### Artifact Comments

Handlers are organized under the `# *** handlers` top-level comment, with individual Handlers under `# ** handler: <name>` in snake_case. Within each Handler, artifact types are defined under low-level comments:

- `# * attribute: <name>`: Declares instance attributes (e.g., `logging_repo`), typically repositories or configuration data, with type hints.
- `# * init`: Marks the initializer method for setting up dependencies.
- `# * method: <name>`: Identifies service methods (e.g., `list_all`, `create_logger`) that implement domain logic, often satisfying `Repository` Contracts.

One empty line separates `# *** handlers` and `# ** handler: <name>`, subcomponents (`# *`), between code snippets, and after docstrings. For example, in `tiferet/handlers/logging.py`:

```python
# *** imports

# ** core
import logging
import logging.config

# ** app
from ..commands import raise_error
from ..contracts.logging import LoggingRepository

# *** handlers

# ** handler: logging_handler
class LoggingHandler:
    '''
    Logging handler for managing logger configurations.
    '''

    # * attribute: logging_repo
    logging_repo: LoggingRepository

    # * init
    def __init__(self, logging_repo: LoggingRepository):
        '''
        Initialize the logging handler.
        '''
        
        # Set the logging repository.
        self.logging_repo = logging_repo

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all formatter, handler, and logger configurations.
        '''
        
        # Retrieve all logging configurations from the repository.
        return self.logging_repo.list_all()
```

### Extensible Attributes and Methods

Attributes and methods in Handlers are designed to be accessible to Initializer Scripts via Contexts, implementing domain-specific logic while adhering to Contracts. Key considerations:

- **Attributes**: Store dependencies (e.g., `logging_repo`) or state, using type hints to specify Contract types (e.g., `LoggingRepository`).
- **Methods**: Implement domain-specific services (e.g., `create_logger`, `format_config`), satisfying Contract methods (e.g., `LoggingRepository.list_all`) and handling errors via `raise_error`.
- **Extensibility**: Handlers can be extended by adding new methods or implementing additional Contracts, with `**kwargs` for flexibility.

Example: In the calculator application, `LoggingHandler.create_logger` generates a logger for `LoggingContext` to log events like “Error parsing CLI request.”

## Creating New and Extending Existing Handlers

To create new functionality or extend existing behavior, developers can define new Handler classes or add methods to existing ones, following Tiferet’s structured code guidelines. Below are examples of creating a new Handler and extending an existing one, focusing on the Handler class definitions.

1. **Create a New Handler Class**:

   - Place under `# *** handlers` and `# ** handler: <name>` in a module (e.g., `app/handlers/calculator.py`).

   - Extend `ServiceHandler` from `tiferet.handlers.settings` or implement a `Repository` Contract.

   - Define attributes and methods under `# * attribute` and `# * method`.

     ```python
     # *** imports
     
     # ** core
     from typing import List, Any
     from abc import abstractmethod
     
     # ** app
     from tiferet.handlers.settings import ServiceHandler
     from tiferet.contracts.calculator import CalculatorRepository
     
     # *** handlers
     
     # ** handler: calculator_handler
     class CalculatorHandler(ServiceHandler):
         '''
         Handler for managing calculator operations and results.
         '''
     
         # * attribute: calc_repo
         calc_repo: CalculatorRepository
     
         # * init
         def __init__(self, calc_repo: CalculatorRepository):
             '''
             Initialize the calculator handler.
             '''
             
             # Set the calculator repository.
             self.calc_repo = calc_repo
     
         # * method: save_result
         def save_result(self, result: CalculatorResultContract) -> None:
             '''
             Save a calculator result.
             
             :param result: The calculator result to save.
             :type result: CalculatorResultContract
             '''
             
             # Save the result using the repository.
             self.calc_repo.save_result(result)
     ```

2. **Extend an Existing Handler Class**:

   - Add a new method to an existing Handler (e.g., `LoggingHandler` in `tiferet/handlers/logging.py`) under `# * method`.

   - Ensure the method aligns with domain needs and uses Contracts.

     ```python
     # *** imports
     
     # ** core
     import logging
     import logging.config
     
     # ** app
     from ..commands import raise_error
     from ..contracts.logging import LoggingRepository
     
     # *** handlers
     
     # ** handler: logging_handler
     class LoggingHandler:
         '''
         Logging handler for managing logger configurations.
         '''
     
         # * attribute: logging_repo
         logging_repo: LoggingRepository
     
         # * init
         def __init__(self, logging_repo: LoggingRepository):
             '''
             Initialize the logging handler.
             '''
             
             # Set the logging repository.
             self.logging_repo = logging_repo
     
         # * method: clear_loggers
         def clear_loggers(self) -> None:
             '''
             Clear all existing logger configurations.
             '''
             
             # Reset the logging manager.
             logging.getLogger('').handlers = []
             
             # Log the clearing action.
             logging.getLogger('').info('All logger configurations cleared.')
     ```

3. **Best Practices**:

   - Use artifact comments (`# * attribute`, `# * method`, `# * init`) consistently, with one empty line between subcomponents.
   - Define attributes with type hints specifying Contract types (e.g., `CalculatorRepository`).
   - Implement methods to satisfy Contract requirements (e.g., `LoggingRepository.list_all`), using `raise_error` for error handling.
   - Maintain one empty line between `# *** handlers` and `# ** handler: <name>`, between snippets, and after docstrings.
   - Align methods with domain needs (e.g., `save_result` for calculator operations).

## Testing Handlers

Testing ensures Handlers adhere to Tiferet’s structured code style and correctly implement domain logic. Test modules use `pytest` with `unittest.mock` to isolate dependencies and cover success, error, and edge cases, organized under `# *** fixtures` and `# *** tests` with `# ** fixture` and `# ** test` comments, as seen in `tiferet/handlers/tests/test_logging.py`.

### Testing Approach

- **Fixtures**: Create Handler and dependency fixtures under `# ** fixture: <name>` to provide test instances (e.g., `LoggingHandler`, `LoggingRepository`), mocking Contracts.
- **Scenarios**: Test service methods (e.g., `list_all`, `create_logger`) for success, error cases (e.g., invalid configurations), and edge cases (e.g., empty data).
- **Assertions**: Verify method outputs, Contract compliance, and error handling via `raise_error`.

### Example: Testing LoggingHandler

Below is an example test suite for `LoggingHandler` (tiferet/handlers/logging.py):

```python
# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.handlers.logging import LoggingHandler
from tiferet.models.logging import Formatter, Handler, Logger
from tiferet.contracts.logging import LoggingRepository

# *** fixtures

# ** fixture: formatter
@pytest.fixture
def formatter():
    '''
    Fixture to create a Formatter instance.
    '''
    
    # Create a Formatter instance.
    return ModelObject.new(
        Formatter,
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# ** fixture: logging_handler
@pytest.fixture
def logging_handler(logging_repo):
    '''
    Fixture to create a LoggingHandler instance with mocked repository.
    '''
    
    # Create a LoggingHandler instance.
    return LoggingHandler(logging_repo=logging_repo)

# *** tests

# ** test: logging_handler_list_all_success
def test_logging_handler_list_all_success(logging_handler, formatter):
    '''
    Test successful listing of all logging configurations by LoggingHandler.
    '''
    
    # Mock repository response.
    logging_handler.logging_repo.list_all.return_value = ([formatter], [], [])
    
    # Call list_all to retrieve configurations.
    formatters, handlers, loggers = logging_handler.list_all()
    
    # Assert that the configurations are correctly retrieved.
    assert len(formatters) == 1
    assert formatters[0] == formatter
    assert handlers == []
    assert loggers == []

# ** test: logging_handler_format_config_no_root
def test_logging_handler_format_config_no_root(logging_handler, formatter):
    '''
    Test LoggingHandler format_config with no root logger.
    '''
    
    # Call format_config without a root logger, expecting an error.
    with pytest.raises(TiferetError) as exc_info:
        logging_handler.format_config(
            formatters=[formatter],
            handlers=[],
            loggers=[]
        )
    
    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'
    assert 'No root logger' in str(exc_info.value)
```

### Best Practices

- Use `# *** fixtures`, `# ** fixture`, `# *** tests`, `# ** test` for test organization, with one empty line between sections and comments.
- Mock Contract dependencies (e.g., `LoggingRepository`) to isolate Handler logic.
- Test all methods under `# * method` for success, error, and edge cases.
- Include RST-formatted docstrings with one empty line after docstrings.
- Maintain one empty line between snippets within tests.

## Conclusion

Handlers are the service core of Tiferet applications, implementing domain-specific logic for Commands and Contexts while interacting only with Contracts. Their structured code design, using artifact comments (`# *** handlers`, `# ** handler: <name>`, `# * attribute`, `# * method`, `# * init`) and consistent formatting (docstrings, indentation, snippets, spacing), ensures consistency and extensibility. Developers can create new Handlers (e.g., `CalculatorHandler`) or extend existing ones (e.g., `LoggingHandler`) by following the structured guidelines. Unit tests validate domain logic and Contract compliance, supporting the calculator application’s logging and error handling. Explore tiferet/handlers/ for source code and tiferet/handlers/tests/ for test examples.
