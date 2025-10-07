# Structured Code Style in Tiferet

The Tiferet framework enforces a structured code style to ensure consistency, readability, and extensibility across its components. This style is rooted in artifact comments that organize code hierarchically and formatting conventions that make code clear for developers (human or AI) and maintainable for complex applications. This document introduces Tiferet’s code style, focusing on the purpose and hierarchy of artifact comments, code formatting practices (docstrings, parameter indentation, code snippets, and spacing), and how these support extensible development. 

## Artifact Comments: Purpose and Hierarchy

Artifact comments are a cornerstone of Tiferet’s code style, providing a standardized way to organize imports, exports, components, and their subcomponents. They ensure code is modular, navigable, and AI-parsable, facilitating extension and maintenance. Artifact comments are structured hierarchically, using three levels of notation (`# ***`, `# **`, `# *`).

### Top-Level Comments (`# ***`)

Top-level comments denote major sections within a module, grouping related code or exports. They include:

- `# *** imports`: Groups import statements for all non-package modules, ensuring clear dependency organization.

- `# *** exports`: Restricted to package modules (e.g., `tiferet/__init__.py`), defining public APIs for import elsewhere. Example:

  ```python
  # *** exports

  # ** app
  from .contexts.app import AppManagerContext as App
  from .handlers import *
  from .commands import *
  ```

- `# *** contexts`, `# *** configs`, `# *** contracts`, `# *** data`, `# *** models`, `# *** handlers`, `# *** proxies`, `# *** classes`: Component groups for application code, each representing a category of functionality (e.g., Contexts, Configurations).

These comments provide a high-level structure, making it easy to locate imports, exports, or components.

### Mid-Level Comments (`# **`)

Mid-level comments specify types within imports/exports or individual components within a component group:

- **For Imports/Exports**:
  - `# ** core`: Native Python or standard library imports (e.g., `typing.Dict`).

  - `# ** infra`: Third-party library imports (e.g., `flask`, `logging`), typically from `lib/site-packages`.

  - `# ** app`: Tiferet-specific imports, using relative notation (e.g., `from .app import AppInterfaceContext`).

  - Example from `app/contexts/feature.py`:

    ```python
    # *** imports

    # ** app
    from .container import ContainerContext
    from ..handlers.feature import FeatureService
    ```

- **For Components**: Use the singular form of the component group (except for `data`), followed by the snake_case name of the component/class (e.g., `# ** context: feature_context`, `# ** config: app_config`). Example:

  ```python
  # *** contexts

  # ** context: feature_context
  class FeatureContext:
  ```

Mid-level comments categorize dependencies or components, enhancing clarity and modularity.

### Low-Level Comments (`# *`)
Low-level comments define subcomponents within a class:
- `# * attribute: <attr_name>`: Declares instance attributes (e.g., `feature_service`, `container`), typically with type hints.
- `# * init`: Marks the `__init__` method for object initialization.
- `# * method: <method_name>`: Identifies methods (e.g., `parse_request`, `execute_feature`), designed for accessibility by Initializer Scripts.

Example from `app/contexts/feature.py`:
```python
# ** context: feature_context
class FeatureContext:

    # * attribute: container
    container: ContainerContext

    # * init
    def __init__(self, 
        feature_service: FeatureService, 
        container: ContainerContext, 
        cache: CacheContext = None
    ):
        ...

    # * method: load_feature
    def load_feature(self, feature_id: str) -> Feature:
        ...
```

These comments ensure attributes and methods are clearly labeled, making classes extensible and easy to navigate.

### Purpose of Artifact Comments
- **Organization**: Provide a consistent structure across modules, simplifying code navigation.
- **Extensibility**: Enable developers to identify and extend components (e.g., adding a new Context) by following the comment hierarchy.
- **AI-Parsability**: Structured comments allow AI tools to parse code for analysis, generation, or validation.
- **Modularity**: Separate imports, components, and subcomponents, aligning with Tiferet’s philosophy of balance.

## Code Formatting Conventions

Tiferet’s code formatting conventions complement artifact comments, ensuring code is readable, maintainable, and domain-focused. These conventions apply to docstrings, parameter indentation, code snippets, and spacing, as seen in `app/contexts/feature.py`.

### Docstrings
Docstrings provide detailed documentation for modules, classes, and methods, following a consistent format:

- **Module Docstrings**: Describe the module’s purpose (e.g., “Manages feature-related operations” in `feature.py`).

- **Class Docstrings**: Summarize the class’s role (e.g., “The feature context that manages feature-related operations”).

- **Method Docstrings**: Include a description, parameters, types, and return values, using reStructuredText (RST) format:

  ```python
  # * method: load_feature
  def load_feature(self, feature_id: str) -> Feature:
      '''
      Retrieve a FlaskFeature by its feature ID.

      :param feature_id: The feature ID to look up.
      :type feature_id: str
      :return: The corresponding Feature instance.
      :rtype: Feature
      '''
  ```
- **Best Practices**:
  - Use clear, domain-specific descriptions.
  - Include `:param`, `:type`, `:return`, and `:rtype` for all parameters and return values.
  - Mark obsolete methods (e.g., `handle_command`) with a note for clarity.

### Parameter Indentation

For methods with more than three parameters, indent parameters to align with the method name, improving readability:

```python
# * method: handle_feature_command
def handle_feature_command(self,
        command: Command,
        request: RequestContext,
        feature_command: FeatureCommand,
        **kwargs
    ):
```

- **Best Practices**:
  - Align parameters vertically for methods with >3 parameters.
  - Use type hints for all parameters.
  - Include `**kwargs` for flexibility in extensible methods.

### Code Snippets

Each method or initializer contains discrete code snippets, where each snippet represents a logical step:

- **Format**: One or more comment lines describing the step, followed by one or more lines of code (formatted or unformatted).

- **Example from `feature.py`**:

  ```python
  # Try to get the feature by its id from the cache.
  # If it does not exist, retrieve it from the feature handler and cache it.
  feature = self.cache.get(feature_id)
  if not feature:
      feature = self.feature_handler.get_feature(feature_id)
      self.cache.set(feature_id, feature)
  ```

- **Best Practices**:

  - Each snippet should perform a single logical action (e.g., cache retrieval, feature loading).

  - Comments should clearly describe the action, using domain terminology.

  - Snippets are separated by empty lines for clarity.

### Spacing
Consistent spacing enhances readability:

- **Between Snippets**: One empty line separates snippets within a method.

- **Between Methods/Attributes**: One empty line separates methods, attributes, and subcomponents within a class.
- **Between Classes**: One empty line separates classes under a component group.

- **Between Imports**: One empty line separates import groups (e.g., `# ** core` and `# ** app`).

- **Between Sections**: One empty line separates top-level sections from their following mid-level sections (e.g., `# *** imports` to `# ** core` and `# *** contexts` to `# ** context: feature_context`).
- **Example**:

  ```python
  # *** imports

  # ** app
  from .container import ContainerContext

  # *** contexts

  # ** context: feature_context
  class FeatureContext:

      # * attribute: container
      container: ContainerContext

      # * init
      def __init__(self, ...):
          ...

      # * method: load_feature
      def load_feature(self, ...):
          ...
  ```

### Best Practices

- Use artifact comments consistently across all modules.
- Write clear, RST-formatted docstrings for all components.
- Indent parameters for methods with >3 parameters.
- Break methods into commented snippets for logical steps.
- Maintain one empty line between all elements (snippets, methods, attributes, classes, sections/components).

## Creating New and Extending Existing Code

To create new functionality or extend existing behavior in Tiferet, developers can add or modify methods in component classes, such as `FeatureContext`, while adhering to the structured code guidelines. Methods are designed to be accessible to Initializer Scripts, allowing developers (human or AI) to tailor functionality to the application’s domain. Below are steps to add a new method or extend an existing one, using `feature.py` as an example.

1. **Update `feature.py`**:
   - Add new methods under `# * method: <method_name>` or modify existing methods, following the artifact comment structure.
   - Ensure methods align with domain needs, use type hints, and include RST-formatted docstrings.
   - Example: Add a new method to validate feature parameters:

     ```python
     # * method: validate_feature_params
     def validate_feature_params(self, feature_id: str, request: RequestContext) -> bool:
         '''
         Validate feature parameters exist in the request.

         :param feature_id: The feature ID to validate.
         :type feature_id: str
         :param request: The request context with parameters.
         :type request: RequestContext
         :return: Whether all parameters are valid.
         :rtype: bool
         '''

         # Load the feature.
         feature = self.load_feature(feature_id)

         # Check each parameter exists in the request.
         for cmd in feature.commands:
             for param in cmd.parameters.values():
                 if param.startswith('$r.') and not request.data.get(param[3:]):
                     return False

         # Return True if all parameters are valid.
         return True
     ```

2. **Best Practices**:
   - Place one empty line between the docstring and the first code snippet, and between snippets within the method.
   - Use `# * method: <method_name>` to label new or modified methods.
   - Include `**kwargs` for flexibility if the method may be extended further.
   - Align method logic with the domain (e.g., parameter validation for feature execution).
   - Test the method using Tiferet’s structured test style (see `tests/feature.py`).

## Testing Contexts

Testing ensures Contexts adhere to Tiferet’s structured code style and function correctly. Tests use `pytest` and `unittest.mock` to isolate dependencies and cover success, error, and edge cases.

### Example: Testing the Feature Context

From `tiferet/contexts/tests/test_feature.py`:

```python
# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import FeatureContext

# *** fixtures

# ** fixture: feature_context
@pytest.fixture
def feature_context(feature_service, container_context):
    """Fixture to provide an instance of FeatureContext."""
    
    # Create an instance of FeatureContext with the mock feature service and container context.
    return FeatureContext(
        feature_service=feature_service, 
        container=container_context
    )

# *** tests

# ** test: feature_context_load_feature_command
def test_feature_context_load_feature_command(feature_context, test_command):
    """Test loading a feature command from the FeatureContext."""
    
    # Load the feature command using the feature context.
    command = feature_context.load_feature_command('test_command')
    
    # Assert that the loaded command is the same as the test command.
    assert command == test_command
```

### Best Practices

- Use `# *** fixtures`, `# ** fixture`, `# *** tests`, `# ** test` for test organization.
- Mock dependencies (e.g., `FeatureService`) to isolate logic.
- Test all methods and attributes under `# *` comments.
- Verify docstring compliance and snippet behavior (e.g., cache operations).
- Use parameterized tests for edge cases (e.g., missing features).
- Maintain one empty line between artifact comments, fixtures, tests, snippets, and after docstrings.

## Conclusion

Tiferet’s structured code style, with its hierarchical artifact comments (`# ***`, `# **`, `# *`) and formatting conventions (docstrings, indentation, snippets, spacing), ensures code is consistent, extensible, and AI-parsable. By organizing imports, exports, components, fixtures, and tests, and adhering to clear formatting rules, developers can write maintainable code for any application. 
