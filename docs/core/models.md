# Models in Tiferet

Models are a core component of the Tiferet framework, representing domain objects that encapsulate the core concepts and behaviors of the application’s domain, aligning with Domain-Driven Design (DDD) principles. In Tiferet, Models define the data and behavior that embody the domain’s business logic. Models are not directly accessible to Initializer Scripts, but their behavior is invoked through Contexts, ensuring robust domain modeling. This document explores the structured code design behind Models, how to write and extend them, and how to test them, using the calculator application’s error handling as an example and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Model?

A Model in Tiferet is a class that defines a domain object (e.g., `Error` for error handling, `ErrorMessage` for error translations) using Schematics for validation and structure. Models extend `ModelObject` (from `tiferet.models.settings`) and encapsulate the state (attributes) and behavior (methods) of domain concepts, ensuring domain integrity through validation and standardized instantiation via `ModelObject.new()` or a custom `# * method: new`. They align with DDD’s ubiquitous language, providing a clear, consistent representation of domain concepts.

- **Domain Objects**: Models represent entities or value objects with attributes (e.g., `id`, `name`) and behaviors (e.g., formatting errors), used for domain logic (e.g., error handling in the calculator).
- **Role in Runtime**: Models are instantiated and used by Contexts (e.g., `ErrorContext`) and Handlers (e.g., `ErrorHandler`), configured via YAML files (e.g., `error.yml`). Their attributes and methods define domain behavior, such as formatting error messages or logging configurations.
- **Instantiation**: By default, Models use `ModelObject.new()` for instantiation, but a custom `# * method: new` can be defined for domain-specific logic (e.g., `Error.new` sets default `id`).
- **Accessibility**: Models are not directly accessible to Initializer Scripts, but their behavior is exposed through Contexts (e.g., `ErrorContext.handle_error`).

In the calculator application, the `Error` model handles errors like `DIVISION_BY_ZERO` (e.g., `python calc_cli.py calc divide 8 0`), while `ErrorMessage` supports multilingual error messages.

## Structured Code Design of Models

Tiferet enforces a structured code design for Models, using artifact comments to organize code and ensure consistency, as detailed in [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md). This structure makes Models readable, extensible, and AI-parsable, allowing developers to define domain-specific state and behavior.

### Artifact Comments

Models are organized under the `# *** models` top-level comment, with individual Models under `# ** model: <name>` in snake_case. Within each Model, artifact types are defined under low-level comments:

- `# * attribute: <name>`: Declares instance attributes (e.g., `name`, `message`), typically using Schematics types (e.g., `StringType`, `ListType`) for validation.
- `# * method: <name>`: Identifies methods (e.g., `format_message`, `format_response`) that implement domain-specific behavior.
- `# * method: new`: Marks an optional custom factory method for instantiation, encapsulating domain-specific logic (e.g., setting defaults in `Error.new`). If absent, `ModelObject.new` is used.

These comments provide a clear structure, with one empty line between `# *** models` and `# ** model: <name>`, between subcomponents (`# *`), between code snippets, and after docstrings. For example, in `tiferet/models/error.py`:

```python
# *** imports

# ** core
from typing import List, Any

# ** app
from .settings import ModelObject

# *** models

# ** model: error_message
class ErrorMessage(ModelObject):
    '''
    An error message object.
    '''

    # * attribute: lang
    lang = StringType(
        required=True,
        metadata=dict(
            description='The language of the error message text.'
        )
    )

    # * attribute: text
    text = StringType(
        required=True,
        metadata=dict(
            description='The error message text.'
        )
    )

    # * method: format
    def format(self, *args) -> str:
        '''
        Formats the error message text.
        '''
        
        # If there are no arguments, return the error message text.
        if not args:
            return self.text
        
        # Format the error message text and return it.
        return self.text.format(*args)

# ** model: error
class Error(ModelObject):
    '''
    An error object.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the error.'
        )
    )

    # * method: new
    @staticmethod
    def new(name: str, id: str = None, error_code: str = None, message: List[ErrorMessage | Any] = [], **kwargs) -> 'Error':
        '''
        Initializes a new Error object.
        '''
        
        # Set Id as the name lower cased if not provided.
        if not id:
            id = name.lower().replace(' ', '_')
        
        # Set the error code as the id upper cased if not provided.
        if not error_code:
            error_code = id.upper().replace(' ', '_')
        
        # Convert any error message dicts to ErrorMessage objects.
        message_objs = []
        for msg in message:
            if isinstance(msg, ErrorMessage):
                message_objs.append(msg)
            elif isinstance(msg, dict):
                message_objs.append(ModelObject.new(ErrorMessage, **msg))
        
        # Create and return a new Error object.
        return ModelObject.new(
            Error,
            id=id,
            name=name,
            error_code=error_code,
            message=message_objs,
            **kwargs
        )
```

### Extensible Attributes and Methods

Attributes and methods in Models are designed to encapsulate domain state and behavior, used by Contexts and Handlers rather than Initializer Scripts directly. Key considerations:

- **Attributes**: Define the Model’s state (e.g., `name`, `message` in `Error`) using Schematics types for validation (e.g., `required=True`). Metadata provides self-documentation.
- **Methods**: Implement domain-specific behavior (e.g., `Error.format_message` for formatting errors, `Logger.format_config` for logging setup). They are flexible, often accepting `*args` or `**kwargs` for extensibility.
- **Factory Method (`new`)**: The optional `# * method: new` provides custom instantiation logic (e.g., `Error.new` sets default `id` and converts messages). By default, `ModelObject.new` is used for instantiation, ensuring consistency.

Example: In the calculator application, `Error.format_response` formats `DIVISION_BY_ZERO` errors for output via `ErrorContext`.

## Creating New and Extending Existing Models

To create new functionality or extend existing behavior, developers can add or modify Model classes, following Tiferet’s structured code guidelines. Below are steps to create a new Model or extend an existing one, using a hypothetical `CalculatorResult` Model as an example.

1. **Define the Model Class**:

   - Place under `# *** models` and `# ** model: <name>` in a module (e.g., `app/models/calculator.py`).
   - Extend `ModelObject` from `tiferet.models.settings` for domain objects.
   - Add attributes and methods under `# * attribute` and `# * method`, using `ModelObject.new` for instantiation unless custom logic is needed.
   - Example: `CalculatorResult` for storing computation results:

     ```python
     # *** imports

     # ** core
     from typing import Any

     # ** app
     from tiferet.models.settings import ModelObject, StringType, FloatType

     # *** models

     # ** model: calculator_result
     class CalculatorResult(ModelObject):
         '''
         A model object for storing calculator computation results.
         '''

         # * attribute: value
         value = FloatType(
             required=True,
             metadata=dict(
                 description='The result of the computation.'
             )
         )

         # * attribute: operation
         operation = StringType(
             required=True,
             metadata=dict(
                 description='The operation performed (e.g., add, divide).'
             )
         )

         # * method: format_result
         def format_result(self, precision: int = 2) -> str:
             '''
             Formats the computation result as a string.
             
             :param precision: The number of decimal places.
             :type precision: int
             :return: The formatted result.
             :rtype: str
             '''
             
             # Format the value to the specified precision.
             formatted_value = f'{self.value:.{precision}f}'
             
             # Return the formatted result with operation.
             return f'{self.operation}: {formatted_value}'
     ```

2. **Configure in YAML** (if applicable):

   - Update relevant configuration files (e.g., `app/configs/feature.yml`) to reference the Model in features, if used by Contexts or Handlers.

     ```yaml
     features:

       calc.add:
         name: 'Add Number'
         description: 'Adds one number to another'
         commands:

           - attribute_id: add_number_cmd
             name: Add `a` and `b`
             result_model: calculator_result
     ```

3. **Use in a Context or Handler**:

   - Integrate the Model in a Context (e.g., `FeatureContext`) or Handler to process results, not directly in Initializer Scripts.

     ```python
     # *** imports

     # ** app
     from tiferet.contexts.feature import FeatureContext
     from app.models.calculator import CalculatorResult

     # *** contexts

     # ** context: feature_context
     class FeatureContext:
         
         # * method: execute_feature
         def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
             '''
             Execute a feature by its ID with the provided request.
             '''
             
             # Load the feature and execute commands (existing logic).
             ...
             
             # Store result in CalculatorResult.
             result = ModelObject.new(
                 CalculatorResult,
                 value=request.result,
                 operation=feature_id.split('.')[1]
             )
             request.set_result(result.format_result())
     ```

4. **Define Methods and Attributes**:

   - Add attributes under `# * attribute` with Schematics types for validation.
   - Define methods under `# * method` for domain behavior, with one empty line between snippets and after docstrings.
   - Use `ModelObject.new` for instantiation unless a custom `# * method: new` is required for domain-specific logic.

5. **Leverage Other Components**:

   - Use Models in Contexts (e.g., `FeatureContext`, `ErrorContext`) or Handlers to process domain data, ensuring integration with Configurations and Commands.

### Best Practices

- Use artifact comments (`# * attribute`, `# * method`, `# * method: new`) consistently, with one empty line between subcomponents.
- Define attributes with Schematics types and metadata for validation and documentation.
- Prefer `ModelObject.new` for instantiation, using `# * method: new` only for custom logic.
- Use RST-formatted docstrings with one empty line before snippets.
- Maintain one empty line between `# *** models` and `# ** model: <name>`.

## Testing Models

Testing ensures Models adhere to Tiferet’s structured code style and maintain domain integrity. Test modules use `pytest` with `unittest.mock` to isolate dependencies and cover success, error, and edge cases, organized under `# *** fixtures` and `# *** tests` with `# ** fixture` and `# ** test` comments, as seen in `tiferet/models/tests/test_error.py` and `tiferet/models/tests/test_logging.py`.

### Testing Approach

- **Fixtures**: Create domain model fixtures under `# ** fixture: <name>` to provide test instances (e.g., `Error`, `Formatter`) using `ModelObject.new` or custom `new` methods.
- **Scenarios**: Test factory methods (`new` or `ModelObject.new`) for instantiation, method behavior (e.g., `format_message`) for success and error cases, and edge cases (e.g., unsupported languages).
- **Assertions**: Verify attribute values, method outputs, and error handling.

### Example: Testing Error Model

Below is an example test suite for `Error` ([tiferet/models/error.py](https://github.com/greatstrength/tiferet/blob/main/tiferet/models/error.py)):

```python
# *** imports

# ** infra
import pytest

# ** app
from tiferet.models.error import Error, ErrorMessage
from tiferet.models.settings import ModelObject

# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    '''
    Fixture to create a basic error message object.
    '''
    
    # Create an ErrorMessage instance.
    return ModelObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred.'
    )

# ** fixture: error
@pytest.fixture
def error(error_message) -> Error:
    '''
    Fixture to create a basic error object.
    '''
    
    # Create an Error instance.
    return Error.new(
        name='Test Error',
        error_code='TEST_ERROR',
        message=[error_message]
    )

# *** tests

# ** test: error_new_success
def test_error_new_success(error_message):
    '''
    Test successful instantiation of an Error object.
    '''
    
    # Create an Error instance.
    error = Error.new(
        id='test_error',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[error_message]
    )
    
    # Verify attributes.
    assert error.id == 'test_error'
    assert error.name == 'Test Error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message

# ** test: error_format_response
def test_error_format_response(error):
    '''
    Test formatting the error response.
    '''
    
    # Format the response.
    response = error.format_response('en_US')
    
    # Verify response.
    assert response['error_code'] == 'TEST_ERROR'
    assert response['message'] == 'An error occurred.'
```

### Best Practices

- Use `# *** fixtures`, `# ** fixture`, `# *** tests`, `# ** test` for test organization, with one empty line between sections and comments.
- Create fixtures for each Model and its dependencies (e.g., `ErrorMessage` for `Error`).
- Test `# * method: new` (or `ModelObject.new`) and other methods for success, error, and edge cases.
- Include RST-formatted docstrings with one empty line after docstrings.
- Maintain one empty line between snippets within tests.

## Conclusion

Models are the behavioral core of Tiferet applications, encapsulating domain objects with robust validation and behavior. Their structured code design, using artifact comments (`# *** models`, `# ** model: <name>`, `# * attribute`, `# * method`, `# * method: new`) and consistent formatting (docstrings, indentation, snippets, spacing), ensures consistency and extensibility. Developers can create new Models (e.g., `CalculatorResult`) or extend existing ones (e.g., `Error`) by following the structured guidelines, using `ModelObject.new` for instantiation unless custom logic is needed. Unit tests validate domain integrity, covering instantiation and behavior. Explore [tiferet/models/](https://github.com/greatstrength/tiferet/tree/main/tiferet/models/) for source code and [tiferet/models/tests/](https://github.com/greatstrength/tiferet/tree/main/tiferet/models/tests/) for test examples.
