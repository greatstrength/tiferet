# Data Transfer Objects in Tiferet

Data Transfer Objects (DTOs) are a core component of the Tiferet framework, encapsulating data mappings between Models and response or persisted data, aligning with Domain-Driven Design (DDD) principles. Derived from `DataObject`, DTOs facilitate the transformation of configuration data (e.g., YAML) into Models or Contracts, ensuring consistent data exchange within the application. DTOs are accessible by use in Commands and Proxies, making their methods and attributes extensible for developers looking to map model data to context-specific response models and structured persistence data, respectively (human or AI). This document explores the structured code design behind DTOs, how to write and extend them, and how to test them, using the calculator application’s CLI and feature configurations as examples and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Data Transfer Object?

A Data Transfer Object in Tiferet is a class that maps data between Models (or Contracts) and external representations, such as YAML configurations or response data. Extending `DataObject` (from `tiferet.data.settings`), DTOs use methods like `map()`, `from_model()`, `from_data()`, `allow()`, and `deny()` to transform data, often producing `ModelContract`-compliant objects for use in Handlers or Proxies. DTOs align with DDD’s data transfer patterns, ensuring modularity and consistency in data handling.

- **Role in Runtime**: DTOs are used by Commands to format response models and by Proxies to map configuration data (e.g., `cli.yml`, `feature.yml`) into Models or Contracts for persistence. They bridge the gap between external data (e.g., YAML) and internal domain logic.
- **Mapping Methods**: `DataObject.map()` transforms DTO data into Models or Contracts, `allow()`/`deny()` control field inclusion/exclusion, and `to_primitive()` serializes data to dictionaries, often with role-based transformations (e.g., `to_data`, `to_model`).
- **Accessibility**: DTOs are accessible to Commands (for response formatting) and Proxies (for persistence), allowing developers to extend data mappings (e.g., custom CLI parsing in `calc_cli.py`).
- **Examples**: In the calculator application, `CliCommandYamlData` maps `cli.yml` configurations to `CliCommand` objects for Commands, while `FeatureData` maps `feature.yml` to `Feature` objects for persistence via Proxies.

## Structured Code Design of Data Transfer Objects

Tiferet enforces a structured code design for DTOs, using artifact comments to organize code and ensure consistency, as detailed in [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md). This structure makes DTOs readable, extensible, and AI-parsable, allowing developers to define domain-specific data mappings.

### Artifact Comments

DTOs are organized under the `# *** data` top-level comment, with individual DTOs under `# ** data: <name>` in snake_case. Within each DTO, artifact types are defined under low-level comments:

- `# * attribute: <name>`: Declares instance attributes (e.g., `id`, `arguments`), using the same Schematics types as Model Objects (e.g., `StringType`, `ListType`) for validation, but supporting `serialized_name` and `deserialize_from` for attribute aliasing, which is not permitted in Model Objects.
- `# * method: <name>`: Identifies methods (e.g., `map`, `to_primitive`) that implement data mapping logic, often overriding `DataObject` methods.

One empty line separates `# *** data` and `# ** data: <name>`, subcomponents (`# *`), between code snippets, and after docstrings. For example, in `tiferet/data/cli.py`:

```python
# *** imports

# ** app
from .settings import DataObject
from ..models.cli import CliCommand, CliArgument
from ..contracts.cli import CliCommand as CliCommandContract

# *** data

# ** data: cli_command_yaml_data
class CliCommandYamlData(CliCommand, DataObject):
    '''
    Represents the YAML data for a CLI command.
    '''

    class Options:
        '''
        Options for the data object.
        '''
        
        serialize_when_none = False
        roles = {
            'to_data': DataObject.deny('id', 'arguments'),
            'to_model': DataObject.deny('arguments')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier for the command.'
        )
    )

    # * attribute: arguments
    arguments = ListType(
        ModelType(CliArgument),
        serialized_name='args',
        deserialize_from=['args', 'arguments'],
        default=[],
        metadata=dict(
            description='A list of arguments for the command.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> CliCommandContract:
        '''
        Maps the YAML data to a CLI command object.
        '''
        
        # Map the data to a CLI command object.
        return ModelObject.new(
            CliCommand,
            **self.to_primitive('to_model')
        )
```

### Extensible Attributes and Methods

Attributes and methods in DTOs are designed to be accessible via Commands or Proxies, enabling flexible data mappings. Key considerations:

- **Attributes**: Define the DTO’s state (e.g., `id`, `arguments` in `CliCommandYamlData`) using Schematics types for validation, with `serialized_name` and `deserialize_from` for aliasing to support flexible data mapping, unlike Model Objects.
- **Methods**: Implement mapping logic (e.g., `map`, `to_primitive`), often overriding `DataObject` methods to customize transformations (e.g., role-based serialization with `to_data` or `to_model`). Overriding `to_primitive` is ideal when a DTO contains a nested object matching an existing Model schema, reducing the need for new DTOs.
- **Extensibility**: DTOs can be extended by adding new attributes or overriding methods like `map` or `to_primitive`, using `DataObject.allow()` or `deny()` for field control.

Example: In the calculator application, `CliCommandYamlData.map` converts `cli.yml` data (e.g., `calc.add`) into a `CliCommand` object for Commands, matching the YAML structure:

```yaml
cli:
  cmds:
    calc.add:
      group_key: calc
      key: add
      description: Adds two numbers.
      args:
        - name_or_flags: [a]
          description: The first number to add.
        - name_or_flags: [b]
          description: The second number to add.
      name: Add Number Command
```

## Creating New and Extending Existing Data Transfer Objects

To create new functionality or extend existing behavior, developers can define new DTO classes or add methods to existing ones, following Tiferet’s structured code guidelines. Below are examples of creating a new DTO and extending an existing one, focusing on the DTO class definitions.

1. **Create a New Data Transfer Object Class**:

   - Place under `# *** data` and `# ** data: <name>` in a module (e.g., `app/data/calculator.py`).
   - Extend `DataObject` from `tiferet.data.settings`, optionally inheriting a Model (e.g., `CalculatorResult`).
   - Define attributes and methods under `# * attribute` and `# * method`.

     ```python
     # *** imports

     # ** core
     from typing import Any

     # ** app
     from tiferet.data.settings import DataObject
     from tiferet.models.calculator import CalculatorResult
     from tiferet.contracts.calculator import CalculatorResultContract

     # *** data

     # ** data: calculator_result_yaml_data
     class CalculatorResultYamlData(CalculatorResult, DataObject):
         '''
         Represents YAML data for a calculator computation result.
         '''

         class Options:
             '''
             Options for the data object.
             '''
             
             serialize_when_none = False
             roles = {
                 'to_data': DataObject.deny('id'),
                 'to_model': DataObject.allow('value', 'operation')
             }

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

         # * method: map
         def map(self, **kwargs) -> CalculatorResultContract:
             '''
             Maps the YAML data to a calculator result object.
             '''
             
             # Map the data to a CalculatorResult object.
             return ModelObject.new(
                 CalculatorResult,
                 **self.to_primitive('to_model')
             )
     ```

2. **Extend an Existing Data Transfer Object Class**:

   - Add a new method to an existing DTO (e.g., `CliCommandYamlData` in `tiferet/data/cli.py`) under `# * method`.
   - Ensure the method aligns with domain needs and uses `DataObject` methods for mapping.

     ```python
     # *** imports

     # ** app
     from .settings import DataObject
     from ..models.cli import CliCommand, CliArgument
     from ..contracts.cli import CliCommand as CliCommandContract

     # *** data

     # ** data: cli_command_yaml_data
     class CliCommandYamlData(CliCommand, DataObject):
         '''
         Represents the YAML data for a CLI command.
         '''

         class Options:
             '''
             Options for the data object.
             '''
             
             serialize_when_none = False
             roles = {
                 'to_data': DataObject.deny('id', 'arguments'),
                 'to_model': DataObject.deny('arguments')
             }

         # * attribute: id
         id = StringType(
             metadata=dict(
                 description='The unique identifier for the command.'
             )
         )

         # * attribute: arguments
         arguments = ListType(
             ModelType(CliArgument),
             serialized_name='args',
             deserialize_from=['args', 'arguments'],
             default=[],
             metadata=dict(
                 description='A list of arguments for the command.'
             )
         )

         # * method: to_primitive
         def to_primitive(self, role: str = 'to_data', **kwargs) -> dict:
             '''
             Converts the data object to a primitive dictionary.
             '''
             
             # Convert the data object to a primitive dictionary.
             if role == 'to_data':
                 return dict(
                     **super().to_primitive(
                         role,
                         **kwargs
                     ),
                     args=[arg.to_primitive() for arg in self.arguments]
                 )
             
             # Convert the data object to a model dictionary.
             elif role == 'to_model':
                 return dict(
                     **super().to_primitive(
                         role,
                         **kwargs
                     ),
                     arguments=[arg.to_primitive() for arg in self.arguments]
                 )
     ```

3. **Best Practices**:

   - Use artifact comments (`# * attribute`, `# * method`) consistently, with one empty line between subcomponents.
   - Define attributes with Schematics types, using `serialized_name` and `deserialize_from` for aliasing where needed.
   - Override `DataObject` methods (e.g., `map`, `to_primitive`) with role-based transformations using `allow()` or `deny`, especially for nested objects matching Model schemas.
   - Maintain one empty line between `# *** data` and `# ** data: <name>`, between snippets, and after docstrings.
   - Align methods with domain needs (e.g., mapping CLI configurations for `calc.add`).

## Testing Data Transfer Objects

Testing ensures DTOs adhere to Tiferet’s structured code style and correctly map data. Test modules use `pytest` to cover initialization, mapping, and serialization, organized under `# *** fixtures` and `# *** tests` with `# ** fixture` and `# ** test` comments, as seen in `tiferet/data/tests/test_cli.py` and `tiferet/data/tests/test_feature.py`.

### Testing Approach

- **Fixtures**: Create DTO fixtures under `# ** fixture: <name>` to provide test instances (e.g., `CliCommandYamlData`), using `DataObject.from_data()`.
- **Scenarios**: Test initialization (`from_data`), mapping (`map`), and serialization (`to_primitive`) for success and edge cases.
- **Assertions**: Verify attribute values, mapped object types, and serialized data structures.

### Example: Testing CliCommandYamlData

Below is an example test suite for `CliCommandYamlData` ([tiferet/data/cli.py](https://github.com/greatstrength/tiferet/blob/main/tiferet/data/cli.py)):

```python
# *** imports

# ** infra
import pytest

# ** app
from tiferet.data.cli import CliCommandYamlData
from tiferet.models.cli import CliCommand

# *** fixtures

# ** fixture: cli_command_yaml_data
@pytest.fixture
def cli_command_yaml_data():
    '''
    Provides a fixture for CLI command YAML data.
    '''
    
    # Create a CliCommandYamlData instance.
    return DataObject.from_data(
        CliCommandYamlData,
        id='calc.add',
        name='Add Number Command',
        description='Adds two numbers.',
        group_key='calc',
        key='add',
        args=[
            dict(
                name_or_flags=['--a', '-a'],
                description='The first number to add.',
                required=True
            ),
            dict(
                name_or_flags=['--b', '-b'],
                description='The second number to add.',
                required=False
            )
        ]
    )

# *** tests

# ** test: cli_command_yaml_data_from_data
def test_cli_command_yaml_data_from_data(cli_command_yaml_data):
    '''
    Test the creation of CLI command YAML data from a dictionary.
    '''
    
    # Assert the DTO is an instance of CliCommandYamlData.
    assert isinstance(cli_command_yaml_data, CliCommandYamlData)
    
    # Assert the attributes are correctly set.
    assert cli_command_yaml_data.id == 'calc.add'
    assert cli_command_yaml_data.name == 'Add Number Command'
    assert cli_command_yaml_data.description == 'Adds two numbers.'
    assert cli_command_yaml_data.group_key == 'calc'
    assert cli_command_yaml_data.key == 'add'
    
    # Assert the arguments are correctly set.
    assert len(cli_command_yaml_data.arguments) == 2
    assert cli_command_yaml_data.arguments[0].name_or_flags == ['--a', '-a']
    assert cli_command_yaml_data.arguments[0].description == 'The first number to add.'
    assert cli_command_yaml_data.arguments[0].required is True

# ** test: cli_command_yaml_data_map
def test_cli_command_yaml_data_map(cli_command_yaml_data):
    '''
    Test the mapping of CLI command YAML data to a CLI command object.
    '''
    
    # Map the YAML data to a CLI command object.
    cli_command = cli_command_yaml_data.map()
    
    # Assert the mapped CLI command is valid.
    assert isinstance(cli_command, CliCommand)
    assert cli_command.id == 'calc.add'
    assert cli_command.name == 'Add Number Command'
    assert cli_command.description == 'Adds two numbers.'
    assert cli_command.group_key == 'calc'
    assert cli_command.key == 'add'
```

### Best Practices

- Use `# *** fixtures`, `# ** fixture`, `# *** tests`, `# ** test` for test organization, with one empty line between sections and comments.
- Create fixtures using `DataObject.from_data()` to initialize DTOs.
- Test initialization, mapping, and serialization methods for correctness.
- Include RST-formatted docstrings with one empty line after docstrings.
- Maintain one empty line between snippets within tests.

## Conclusion

Data Transfer Objects are the mapping core of Tiferet applications, facilitating data transformation between Models and response or persisted data. Their structured code design, using artifact comments (`# *** data`, `# ** data: <name>`, `# * attribute`, `# * method`) and consistent formatting (docstrings, indentation, snippets, spacing), ensures consistency and extensibility. Developers can create new DTOs (e.g., `CalculatorResultYamlData`) or extend existing ones (e.g., `CliCommandYamlData`) by following the structured guidelines, leveraging `to_primitive` for nested Model schemas. Unit tests validate mapping and serialization, supporting the calculator application’s CLI and feature configurations. Explore [tiferet/data/](https://github.com/greatstrength/tiferet/tree/main/tiferet/data/) for source code and [tiferet/data/tests/](https://github.com/greatstrength/tiferet/tree/main/tiferet/data/tests/) for test examples.
