# Proxies in Tiferet

Proxies, or Domain Proxies, are a core component of the Tiferet framework, providing concrete implementations of `Repository` Contracts for domain-specific data access, bound to both their domain and the middleware service they encapsulate (e.g., YAML, JSON), aligning with Domain-Driven Design (DDD) principles. Proxies handle the retrieval and persistence of `ModelContract`-compliant objects, ensuring consistent data access for Handlers and Commands, and are organized in a file structure reflecting their domain and middleware (e.g., `tiferet/proxies/yaml/feature.py`). Proxies are not directly accessible to Initializer Scripts but are used implicitly by Handlers and Commands through their Repository interface to manage domain data. This document explores the structured code design behind Proxies, how to write and extend them, and how to test them, using the calculator application’s feature and error configurations as examples and adhering to Tiferet’s code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Proxy?

A Proxy in Tiferet is a class that implements a `Repository` Contract, providing domain-specific data access (e.g., retrieving or saving features, errors) using a specific middleware service (e.g., YAML, SQLite). Proxies are typically subclasses of a middleware-specific base class (e.g., `YamlConfigurationProxy`) and are organized in a file structure that reflects their domain and middleware (e.g., `tiferet/proxies/yaml/error.py`). They align with DDD’s repository pattern, abstracting data access while returning `ModelContract`-compliant objects.

- **Role in Runtime**: Proxies are used by Handlers (e.g., `FeatureHandler`, `ErrorHandler`) and Commands to load or save data from configuration files (e.g., `feature.yml`, `error.yml`) or other storage mediums, ensuring compliance with `Repository` Contracts.
- **Contract-Based**: Proxies implement `Repository` Contracts (e.g., `FeatureRepository`, `ErrorRepository`), returning `ModelContract` objects (e.g., `Feature`, `Error`) without directly interacting with Models.
- **File Structure**: Proxies are organized under `tiferet/proxies/<middleware>/<domain>.py` (e.g., `tiferet/proxies/yaml/feature.py`), reflecting their domain and middleware service.
- **Accessibility**: Proxies are not directly accessible to Initializer Scripts but are used implicitly by Handlers and Commands through their Repository interface, configured via YAML files (e.g., `app.yml`).
- **Examples**: In the calculator application, `FeatureYamlProxy` retrieves `Feature` objects from `feature.yml` for `FeatureHandler`, while `ErrorYamlProxy` manages `Error` objects for `ErrorHandler` (e.g., `DIVISION_BY_ZERO`).

## Structured Code Design of Proxies

Tiferet enforces a structured code design for Proxies, using artifact comments to organize code and ensure consistency, as detailed in [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md). This structure makes Proxies readable, extensible, and AI-parsable, allowing developers to implement domain-specific data access.

### Artifact Comments

Proxies are organized under the `# *** proxies` top-level comment, with individual Proxies under `# ** proxy: <name>` in snake_case. Within each Proxy, artifact types are defined under low-level comments:

- `# * attribute: <name>`: Declares instance attributes (e.g., `config_file`), typically configuration paths or middleware clients, with type hints.
- `# * init`: Marks the initializer method for setting up middleware dependencies.
- `# * method: <name>`: Identifies methods (e.g., `get`, `save`) that implement `Repository` Contract methods, handling data access.

One empty line separates `# *** proxies` and `# ** proxy: <name>`, subcomponents (`# *`), between code snippets, and after docstrings. For example, in `tiferet/proxies/yaml/error.py`:

```python
# *** imports

# ** core
from typing import Any, List

# ** app
from .core import YamlConfigurationProxy, raise_error
from ...contracts.error import Error as ErrorContract, ErrorRepository
from ...data.error import ErrorData

# *** proxies

# ** proxy: error_yaml_proxy
class ErrorYamlProxy(ErrorRepository, YamlConfigurationProxy):
    '''
    The YAML proxy for the error repository.
    '''

    # * init
    def __init__(self, error_config_file: str):
        '''
        Initialize the yaml proxy.
        '''
        
        # Set the base path.
        super().__init__(error_config_file)

    # * method: get
    def get(self, id: str) -> ErrorContract:
        '''
        Get the error.
        '''
        
        # Load the error data from the yaml configuration file.
        _data: ErrorData = self.load_yaml(
            create_data=lambda data: ErrorData.from_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))
        
        # Return the error object.
        return _data.map() if _data else None
```

### Extensible Attributes and Methods

Attributes and methods in Proxies are designed to implement `Repository` Contracts, enabling flexible data access for Handlers and Commands. Key considerations:

- **Attributes**: Define the Proxy’s state (e.g., `config_file` in `YamlConfigurationProxy`), typically specifying middleware resources (e.g., YAML file paths) with type hints.
- **Methods**: Implement `Repository` Contract methods (e.g., `get`, `list`, `save`), using middleware clients (e.g., `yaml_client`) and Data Transfer Objects (e.g., `ErrorData`) to manage data, with error handling via `raise_error`.
- **Extensibility**: Proxies can be extended by adding new methods or implementing additional `Repository` Contracts, with `**kwargs` for flexibility.

Example: In the calculator application, `ErrorYamlProxy.save` persists `Error` objects to `error.yml` for `ErrorHandler`, ensuring `DIVISION_BY_ZERO` errors are stored correctly.

## Creating New and Extending Existing Proxies

To create new functionality or extend existing behavior, developers can define new Proxy classes or add methods to existing ones, following Tiferet’s structured code guidelines. Below are examples of creating a new Proxy and extending an existing one, focusing on the Proxy class definitions.

1. **Create a New Proxy Class**:

   - Place under `# *** proxies` and `# ** proxy: <name>` in a domain-specific module (e.g., `app/proxies/yaml/calculator.py`).
   - Extend `YamlConfigurationProxy` (or another middleware base) and implement a `Repository` Contract (e.g., `CalculatorRepository`).
   - Define attributes and methods under `# * attribute` and `# * method`.

     ```python
     # *** imports

     # ** core
     from typing import Any, List

     # ** app
     from tiferet.proxies.yaml.core import YamlConfigurationProxy, raise_error
     from tiferet.contracts.calculator import CalculatorRepository, CalculatorResultContract
     from tiferet.data.calculator import CalculatorResultYamlData

     # *** proxies

     # ** proxy: calculator_yaml_proxy
     class CalculatorYamlProxy(CalculatorRepository, YamlConfigurationProxy):
         '''
         YAML proxy for the calculator repository.
         '''

         # * init
         def __init__(self, calc_config_file: str):
             '''
             Initialize the yaml proxy.
             '''
             
             # Set the base path.
             super().__init__(calc_config_file)

         # * method: save_result
         def save_result(self, result: CalculatorResultContract) -> None:
             '''
             Save a calculator result.
             '''
             
             # Create updated result data.
             result_data = CalculatorResultYamlData.from_model(CalculatorResultYamlData, result)
             
             # Save the result data.
             yaml_client.save(
                 yaml_file=self.config_file,
                 data=result_data.to_primitive(),
                 data_save_path=f'results/{result.operation}'
             )

         # * method: get_result
         def get_result(self, operation: str) -> CalculatorResultContract:
             '''
             Get a calculator result by operation.
             '''
             
             # Load the result data from the yaml configuration file.
             _data: CalculatorResultYamlData = self.load_yaml(
                 create_data=lambda data: CalculatorResultYamlData.from_data(
                     **data),
                 start_node=lambda data: data.get('results').get(operation))
             
             # Return the result object.
             return _data.map() if _data else None
     ```

2. **Extend an Existing Proxy Class**:

   - Add a new method to an existing Proxy (e.g., `FeatureYamlProxy` in `tiferet/proxies/yaml/feature.py`) under `# * method`.
   - Ensure the method aligns with the `Repository` Contract and domain needs.

     ```python
     # *** imports

     # ** core
     from typing import Any, List

     # ** app
     from tiferet.contracts.feature import Feature, FeatureRepository
     from tiferet.data.feature import FeatureYamlData
     from tiferet.proxies.yaml.core import YamlConfigurationProxy, raise_error

     # *** proxies

     # ** proxy: feature_yaml_proxy
     class FeatureYamlProxy(FeatureRepository, YamlConfigurationProxy):
         '''
         YAML repository for features.
         '''

         # * init
         def __init__(self, feature_config_file: str):
             '''
             Initialize the yaml repository.
             '''
             
             # Set the base path.
             super().__init__(feature_config_file)

         # * method: clear_features
         def clear_features(self) -> None:
             '''
             Clear all feature configurations from the YAML file.
             '''
             
             # Reset the feature configurations.
             yaml_client.save(
                 yaml_file=self.config_file,
                 data={},
                 data_save_path='features'
             )
     ```

3. **Best Practices**:

   - Use artifact comments (`# * attribute`, `# * method`, `# * init`) consistently, with one empty line between subcomponents.
   - Define attributes with type hints for middleware resources (e.g., `config_file`).
   - Implement `Repository` Contract methods, using middleware clients and DTOs for data access.
   - Maintain one empty line between `# *** proxies` and `# ** proxy: <name>`, between snippets, and after docstrings.
   - Use integration tests for replicable environments (e.g., YAML, SQLite) and mock for server environments (e.g., MySQL).

## Testing Proxies

Testing ensures Proxies adhere to Tiferet’s structured code style and correctly implement `Repository` Contracts. Test modules use `pytest` with `unittest.mock` for server environments or integration tests for replicable environments (e.g., file system, YAML, SQLite), organized under `# *** fixtures` and `# *** tests` with `# ** fixture` and `# ** test` comments, as seen in `tiferet/proxies/yaml/tests/test_error.py` and `tiferet/proxies/yaml/tests/test_feature.py`.

### Testing Approach

- **Fixtures**: Create Proxy and dependency fixtures under `# ** fixture: <name>` to provide test instances (e.g., `ErrorYamlProxy`), using configuration file paths or mocked data.
- **Scenarios**: Test `Repository` methods (e.g., `get`, `list`, `save`) for success, error cases (e.g., file not found), and edge cases (e.g., non-existent IDs), using integration tests for replicable environments.
- **Assertions**: Verify returned objects comply with `ModelContract`, error handling via `raise_error`, and data persistence.

### Example: Testing ErrorYamlProxy

Below is an example test suite for `ErrorYamlProxy` ([tiferet/proxies/yaml/error.py](https://github.com/greatstrength/tiferet/blob/main/tiferet/proxies/yaml/error.py)):

```python
# *** imports

# ** core
import yaml

# ** infra
import pytest

# ** app
from tiferet.proxies.yaml.error import ErrorYamlProxy
from tiferet.configs import TiferetError
from tiferet.models.error import Error, ErrorMessage

# *** fixtures

# ** fixture: error_config_file
@pytest.fixture
def error_config_file():
    '''
    Fixture to provide the path to the error configuration file.
    '''
    
    # Return the test configuration file path.
    return 'tiferet/configs/tests/test.yml'

# ** fixture: error_yaml_proxy
@pytest.fixture
def error_yaml_proxy(error_config_file):
    '''
    Fixture to create an instance of the ErrorYamlProxy.
    '''
    
    # Create an ErrorYamlProxy instance.
    return ErrorYamlProxy(error_config_file)

# *** tests

# ** test: error_yaml_proxy_load_yaml
def test_error_yaml_proxy_load_yaml(error_yaml_proxy):
    '''
    Test the error YAML proxy load YAML method.
    '''
    
    # Load the YAML file.
    data = error_yaml_proxy.load_yaml()
    
    # Check the loaded data.
    assert data
    assert data.get('errors')
    assert len(data['errors']) > 0

# ** test: error_yaml_proxy_get
def test_error_yaml_proxy_get(error_yaml_proxy):
    '''
    Test retrieving an error from the ErrorYamlProxy.
    '''
    
    # Get the error.
    test_error = error_yaml_proxy.get('test_error')
    
    # Check the error.
    assert test_error
    assert test_error.id == 'test_error'
    assert test_error.name == 'Test Error'
    assert test_error.error_code == 'TEST_ERROR'
```

### Best Practices

- Use `# *** fixtures`, `# ** fixture`, `# *** tests`, `# ** test` for test organization, with one empty line between sections and comments.
- Use integration tests for replicable environments (e.g., YAML, SQLite) and mock dependencies for server environments (e.g., MySQL).
- Test all `Repository` Contract methods (`get`, `list`, `save`) for correctness and error handling.
- Include RST-formatted docstrings with one empty line after docstrings.
- Maintain one empty line between snippets within tests.

## Conclusion

Proxies are the data access core of Tiferet applications, implementing `Repository` Contracts for domain-specific, middleware-bound data operations. Their structured code design, using artifact comments (`# *** proxies`, `# ** proxy: <name>`, `# * attribute`, `# * method`, `# * init`) and consistent formatting (docstrings, indentation, snippets, spacing), ensures consistency and extensibility. Developers can create new Proxies (e.g., `CalculatorYamlProxy`) or extend existing ones (e.g., `FeatureYamlProxy`) by following the structured guidelines. Integration tests validate data access in replicable environments, supporting the calculator application’s feature and error configurations. Explore [tiferet/proxies/](https://github.com/greatstrength/tiferet/tree/main/tiferet/proxies/) for source code and [tiferet/proxies/yaml/tests/](https://github.com/greatstrength/tiferet/tree/main/tiferet/proxies/yaml/tests/) for test examples.