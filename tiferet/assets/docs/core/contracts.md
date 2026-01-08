# Contracts in Tiferet

Contracts are a core component of the Tiferet framework, defining interfaces that specify the anticipated structure and behavior of data used by Handlers, aligning with Domain-Driven Design (DDD) principles. Unlike Models, which represent the actual data and behavior, Contracts act as interfaces (akin to .NET or TypeScript interfaces) that ensure consistency when data is passed within or between components. Contracts are not directly accessible to Initializer Scripts but are used by Handlers to process Models that satisfy the contract specifications. This document explores the structured code design behind Contracts, how to write and extend them, and their role in the Tiferet framework, using the calculator application’s error handling as an example and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Contract?

A Contract in Tiferet is an abstract class that defines the structure and behavior of domain objects or data access operations, ensuring that Handlers and Contexts interact with data consistently. Contracts are implemented by Models (for data) or Handlers (for data access), providing a clear interface for domain operations. They align with DDD’s contract-based design, enforcing a ubiquitous language and modularity.

- **Horizontal Contracts**: Derived from `ModelContract` (from `tiferet.contracts.settings`), these define the structure of data passed within a Handler to repositories or between Contexts and Handlers. Examples include `Error` and `ErrorMessage` for error handling, or `FormatterContract` for logging configurations.
- **Vertical Contracts**: Derived from `Repository` (from `tiferet.contracts.settings`), these abstract data access operations, ensuring that data returned (e.g., Models) complies with `ModelContract` interfaces. Examples include `ErrorRepository` for error data access and `LoggingRepository` for logging configurations.
- **Role in Runtime**: Contracts are used by Handlers (e.g., `ErrorHandler`, `LoggingHandler`) to enforce consistent data structures and behaviors, configured via YAML files (e.g., `error.yml`). They ensure that Models (e.g., `Error`) satisfy the contract’s requirements when processed by Handlers or Contexts.
- **Accessibility**: Contracts are not directly accessible to Initializer Scripts but are implemented by Models and Handlers, which are used by Contexts (e.g., `ErrorContext.handle_error`).

In the calculator application, the `Error` contract ensures that error data (e.g., `DIVISION_BY_ZERO`) is structured consistently for `ErrorContext`, while `ErrorRepository` abstracts error data access from `error.yml`.

## Structured Code Design of Contracts

Tiferet enforces a structured code design for Contracts, using artifact comments to organize code and ensure consistency, as detailed in [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md). This structure makes Contracts readable, extensible, and AI-parsable, allowing developers to define domain-specific interfaces.

### Artifact Comments

Contracts are organized under the `# *** contracts` top-level comment, with individual Contracts under `# ** contract: <name>` in snake_case. Within each Contract, artifact types are defined under low-level comments:

- `# * attribute: <name>`: Declares abstract attributes (e.g., `id`, `message`), typically with type hints but no Schematics validation, as Contracts are interfaces.
- `# * method: <name>`: Identifies abstract methods (e.g., `format_message`, `get`) marked with `@abstractmethod`, defining required behavior for implementers.

Contracts do not include a `# * method: new`, as they are abstract and not instantiated directly. One empty line separates `# *** contracts` and `# ** contract: <name>`, subcomponents (`# *`), and after docstrings. For example, in `tiferet/contracts/error.py`:

```python
# *** imports

# ** core
from typing import List, Any
from abc import abstractmethod

# ** app
from .settings import ModelContract, Repository

# *** contracts

# ** contract: error_message
class ErrorMessage(ModelContract):
    '''
    Contract for an error message translation.
    '''

    # * attribute: lang
    lang: str

    # * attribute: text
    text: str

    # * method: format
    @abstractmethod
    def format(self, *args) -> str:
        '''
        Format the error message text with provided arguments.
        '''
        
        raise NotImplementedError('The format method must be implemented by the error message.')

# ** contract: error_repository
class ErrorRepository(Repository):
    '''
    Contract for an error repository to manage error objects.
    '''

    # * method: get
    @abstractmethod
    def get(self, id: str) -> Error:
        '''
        Get an error object by its ID.
        '''
        
        raise NotImplementedError('The get method must be implemented by the error repository.')
```

### Extensible Attributes and Methods

Attributes and methods in Contracts define the expected structure and behavior for implementers (Models or Handlers), used by Contexts and Handlers. Key considerations:

- **Attributes**: Specify the expected state (e.g., `name`, `message` in `Error`) with type hints, ensuring implementers (e.g., `Error` Model) provide these fields.
- **Methods**: Define abstract methods (e.g., `Error.format_response`, `ErrorRepository.get`) with `@abstractmethod`, specifying required behavior without implementation.
- **Extensibility**: Contracts are extended by creating new interfaces or implementing existing ones in Models (e.g., `Error` implements `Error` contract) or Handlers (e.g., `ErrorHandler` implements `ErrorRepository`).

Example: In the calculator application, the `Error` contract ensures `ErrorContext` receives consistent error data, while `ErrorRepository` ensures `ErrorHandler` retrieves `Error` Models from `error.yml`.

## Creating New and Extending Existing Contracts

To create new functionality or extend existing behavior, developers can define new Contract classes, following Tiferet’s structured code guidelines. Below are examples of creating a new `ModelContract` and `Repository` contract, focusing solely on the contract class definitions.

1. **Create a ModelContract Class**:

   - Place under `# *** contracts` and `# ** contract: <name>` in a module (e.g., `app/contracts/calculator.py`).
   - Extend `ModelContract` from `tiferet.contracts.settings` for horizontal contracts.
   - Define attributes and abstract methods under `# * attribute` and `# * method`.

     ```python
     # *** imports

     # ** core
     from typing import Any
     from abc import abstractmethod

     # ** app
     from tiferet.contracts.settings import ModelContract

     # *** contracts

     # ** contract: calculator_result
     class CalculatorResultContract(ModelContract):
         '''
         Contract for a calculator computation result.
         '''

         # * attribute: value
         value: float

         # * attribute: operation
         operation: str

         # * method: format_result
         @abstractmethod
         def format_result(self, precision: int = 2) -> str:
             '''
             Format the computation result as a string.
             '''
             
             raise NotImplementedError('The format_result method must be implemented by the calculator result.')
     ```

2. **Create a Repository Contract Class**:

   - Place under `# *** contracts` and `# ** contract: <name>` in the same module.
   - Extend `Repository` from `tiferet.contracts.settings` for vertical contracts.
   - Define abstract methods under `# * method` for data access operations.

     ```python
     # *** imports

     # ** core
     from typing import List
     from abc import abstractmethod

     # ** app
     from tiferet.contracts.settings import Repository
     from .calculator import CalculatorResultContract

     # *** contracts

     # ** contract: calculator_result
     class CalculatorResultContract(ModelContract):
         ...

     # ** contract: calculator_repository
     class CalculatorRepository(Repository):
         '''
         Contract for a repository to manage calculator results.
         '''

         # * method: save_result
         @abstractmethod
         def save_result(self, result: CalculatorResultContract) -> None:
             '''
             Save a calculator result.
             
             :param result: The calculator result to save.
             :type result: CalculatorResultContract
             '''
             
             raise NotImplementedError('The save_result method must be implemented by the calculator repository.')

         # * method: get_result
         @abstractmethod
         def get_result(self, operation: str) -> CalculatorResultContract:
             '''
             Get a calculator result by operation.
             
             :param operation: The operation to retrieve.
             :type operation: str
             :return: The calculator result.
             :rtype: CalculatorResultContract
             '''
             
             raise NotImplementedError('The get_result method must be implemented by the calculator repository.')

         # * method: list_results
         @abstractmethod
         def list_results(self) -> List[CalculatorResultContract]:
             '''
             List all calculator results.
             
             :return: The list of calculator results.
             :rtype: List[CalculatorResultContract]
             '''
             
             raise NotImplementedError('The list_results method must be implemented by the calculator repository.')
     ```

3. **Best Practices**:

   - Use artifact comments (`# * attribute`, `# * method`) consistently, with one empty line between subcomponents.
   - Define attributes with type hints for clarity, avoiding Schematics validation in Contracts.
   - Use `@abstractmethod` for methods to enforce implementation by Models or Handlers.
   - Maintain one empty line between `# *** contracts` and `# ** contract: <name>` and after docstrings.
   - Align contract methods with domain needs (e.g., `format_result` for calculator results, `save_result` for data access).

## Conclusion

Contracts are the interface core of Tiferet applications, defining the structure and behavior expected by Handlers for domain objects and data access. Their structured code design, using artifact comments (`# *** contracts`, `# ** contract: <name>`, `# * attribute`, `# * method`) and consistent formatting (docstrings, type hints, spacing), ensures consistency and extensibility. Developers can create new Contracts (e.g., `CalculatorResultContract`, `CalculatorRepository`) by following the structured guidelines. Contracts enforce modularity and domain integrity, supporting the calculator application’s error handling and logging. Explore [tiferet/contracts/](https://github.com/greatstrength/tiferet/tree/main/tiferet/contracts/) for source code.
