# Repositories in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Repositories are the concrete data-access layer in the Tiferet framework. Every repository implements a Service interface from `tiferet/interfaces/` and encapsulates the interaction between a data utility (e.g., `Yaml`) and the domain's transfer objects and aggregates.

Repositories are **never exported** from `tiferet/repos/__init__.py`. They are resolved at runtime through the DI service configuration (`container.yml` or equivalent), which specifies the `module_path` and `class_name` for each concrete implementation. Consuming code depends only on the abstract Service interface, never on a concrete repository class.

### Role in Runtime
- **Service implementations**: Repositories are the concrete classes that satisfy the Service interfaces injected into domain events and contexts.
- **Data-utility wiring**: Each repository composes a data utility (e.g., `Yaml`) with the domain's transfer objects to perform reads and writes against configuration files.
- **DI resolution**: Repositories are instantiated by the dependency injection container at runtime, not by direct import.

### Example: Error Domain

```python
class ErrorConfigRepository(ErrorService):
    # Implements ErrorService interface
    # Uses Yaml utility for file I/O
    # Uses ErrorYamlObject for serialization
    # Returns ErrorAggregate instances
```

## Structured Code Design

Repository classes follow the standard Tiferet artifact comment structure:

- `# *** repos` — top-level section for repository modules.
- `# ** repo: <name>` — individual repository (snake_case).
- `# * attribute: <name>` — instance attributes.
- `# * init` — constructor.
- `# * method: <name>` — methods implementing the Service interface.

**Spacing rules:**
- One empty line between `# *** repos` and first `# ** repo`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets within methods.

**Example** — `tiferet/repos/error.py`:
```python
"""Tiferet Error YAML Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import ErrorService
from ..mappers import (
    ErrorAggregate,
    ErrorYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: error_yaml_repository
class ErrorConfigRepository(ErrorService):
    '''
    The error YAML repository.
    '''

    # * attribute: yaml_file
    config_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, error_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the error YAML repository.

        :param error_config: The YAML configuration file path.
        :type error_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.config_file = error_config
        self.encoding = encoding
        self.default_role = 'to_data'

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if an error exists by ID.

        :param id: The error identifier.
        :type id: str
        :return: True if the error exists, otherwise False.
        :rtype: bool
        '''

        # Load the errors mapping from the configuration file.
        errors_data = Yaml(
            self.config_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('errors', {})
        )

        # Return whether the error id exists in the mapping.
        return id in errors_data
```

## The Three-Attribute Foundation

Every YAML-backed repository shares three instance attributes:

- **`yaml_file`** (`str`) — Path to the YAML configuration file.
- **`encoding`** (`str`) — File encoding, defaulting to `'utf-8'`.
- **`default_role`** (`str`) — The TransferObject serialization role used for writes, typically `'to_data'`.

The constructor parameter follows the convention `<domain>_yaml_file` (e.g., `error_config`, `feature_config`, `cli_config`). This domain-prefixed naming enables clean DI wiring in `container.yml`.

```python
# * init
def __init__(self, error_config: str, encoding: str = 'utf-8') -> None:
    self.config_file = error_config
    self.encoding = encoding
    self.default_role = 'to_data'
```

## Import Organization

Repositories follow the standard three-section import layout:

```python
# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import ErrorService           # Service interface
from ..mappers import (                          # Transfer objects and aggregates
    ErrorAggregate,
    ErrorYamlObject,
)
from ..utils import Yaml                         # Data utility
```

The `# ** app` section imports three categories:
1. The **Service interface** being implemented.
2. The **transfer objects and aggregates** used for mapping (concrete classes only; no base-class imports needed).
3. The **data utility** used for file I/O.

No `# ** infra` section is needed — repositories do not import third-party libraries directly; all external interaction flows through Tiferet utilities.

## Method Patterns

### Reading: `exists`, `get`, `list`

All read methods compose a `Yaml` utility instance with a `start_node` lambda to navigate the YAML structure:

```python
# Load a section.
errors_data = Yaml(self.config_file, encoding=self.encoding).load(
    start_node=lambda data: data.get('errors', {})
)

# Load a single entry by ID.
error_data = Yaml(self.config_file, encoding=self.encoding).load(
    start_node=lambda data: data.get('errors', {}).get(id)
)
```

Mapping from raw YAML data to domain aggregates uses `model_validate` on the concrete TransferObject class with the YAML dictionary key injected as the `id`:

```python
return ErrorYamlObject.model_validate(
    {**error_data, 'id': id}
).map()
```

### Writing: `save`

Save methods follow a three-step sequence:
1. **Serialize** the aggregate via the TransferObject's `from_model()` classmethod.
2. **Load the full file** to preserve sibling sections.
3. **Update** the target section with `setdefault` and persist via `to_primitive(role)`.

```python
# Convert the error model to configuration data.
error_data = ErrorYamlObject.from_model(error)

# Load the full configuration file.
full_data = Yaml(self.config_file, encoding=self.encoding).load()

# Update or insert the error entry.
full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)

# Persist the updated configuration file.
Yaml(self.config_file, mode='w', encoding=self.encoding).save(data=full_data)
```

### Deleting: `delete`

Delete operations are always **idempotent** — deleting a non-existent entry must not raise an error:

```python
# Load the full configuration file.
full_data = Yaml(self.config_file, encoding=self.encoding).load()

# Remove the entry if it exists (idempotent).
full_data.get('errors', {}).pop(id, None)

# Persist the updated configuration file.
Yaml(self.config_file, mode='w', encoding=self.encoding).save(data=full_data)
```

## Naming Convention

Repository classes follow the pattern `<Domain>ConfigRepository`:

- `AppConfigRepository` implements `AppService`
- `CliConfigRepository` implements `CliService`
- `DIConfigRepository` implements `DIService`
- `ErrorConfigRepository` implements `ErrorService`
- `FeatureConfigRepository` implements `FeatureService`
- `LoggingConfigRepository` implements `LoggingService`

The `Yaml` suffix identifies the backing utility. Other utility-backed implementations (e.g., JSON, SQLite) would follow the same interface with a different suffix (e.g., `ErrorJsonRepository`, `ErrorSqliteRepository`).

## Creating and Extending Repositories

### 1. Define the Repository

- Place under `# *** repos` and `# ** repo: <name>` in a domain-specific module.
- Extend the corresponding Service interface from `tiferet/interfaces/`.
- Set the three-attribute foundation in `__init__`.
- Implement each Service method using the read/write patterns described above.

**Example** — `CalculatorConfigRepository`:
```python
"""Tiferet Calculator YAML Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces.calculator import CalculatorService
from ..mappers.calculator import (
    CalculatorResultAggregate,
    CalculatorResultYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: calculator_yaml_repository
class CalculatorConfigRepository(CalculatorService):
    '''
    The calculator YAML repository.
    '''

    # * attribute: yaml_file
    config_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, calculator_config_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the calculator YAML repository.

        :param calculator_yaml_file: The YAML configuration file path.
        :type calculator_config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.config_file = calculator_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data'

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a calculator result exists by ID.

        :param id: The result identifier.
        :type id: str
        :return: True if the result exists, otherwise False.
        :rtype: bool
        '''

        # Load the results mapping from the configuration file.
        results_data = Yaml(
            self.config_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('results', {})
        )

        # Return whether the result id exists in the mapping.
        return id in results_data
```

### 2. Register via DI

Add the repository to the DI configuration file (`container.yml` or equivalent) with `module_path` and `class_name`. No `__init__.py` export is needed:

```yaml
services:
  calculator_service:
    module_path: tiferet.repos.calculator
    class_name: CalculatorConfigRepository
    params:
      calculator_yaml_file: app/configs/calculator.yml
```

### 3. Write Tests

Create tests in `tiferet/repos/tests/test_<domain>.py` using `tmp_path` fixtures with real temporary YAML files.

### Best Practices
- Use artifact comments consistently (`# *** repos`, `# ** repo:`, `# *`).
- Follow the three-attribute foundation for all YAML-backed repos.
- Use `YamlObject.model_validate({**data, 'id': id}).map()` for reads.
- Use `YamlObject.from_model(aggregate)` classmethod for writes, then `to_primitive(self.default_role)` to serialize.
- Make delete operations idempotent.
- Use `setdefault` for safe section updates on save.
- Use `start_node` lambdas for all read operations.
- Include RST docstrings with `:param`, `:type`, `:return`, `:rtype`.

## Testing Repositories

Repository tests are **integration tests** that operate against real temporary YAML files, not mocks. This is because the repository's value lies in the specific interaction between the utility and the transfer objects.

**Structure:**
- `# *** constants` — sample data dictionaries.
- `# *** fixtures` / `# ** fixture: <name>` — `tmp_path`-based YAML file and repository instance.
- `# *** tests` / `# ** test_int: <name>` — integration test cases.

**Example** — Error repository test fixture:
```python
# ** fixture: error_config
@pytest.fixture
def error_config(tmp_path) -> str:
    file_path = tmp_path / 'test_error.yaml'
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(ERROR_DATA, yaml_file)
    return str(file_path)

# ** fixture: error_config_repo
@pytest.fixture
def error_config_repo(error_config: str) -> ErrorConfigRepository:
    return ErrorConfigRepository(error_config)
```

Standard test cases cover:
- **exists** — positive and negative lookups.
- **get** — retrieval by ID; `None` for missing entries.
- **list** — full enumeration with count and field assertions.
- **save** — round-trip: save then retrieve and verify fields.
- **delete** — delete then confirm `exists` returns `False`; idempotent delete of non-existent IDs.

## Package Layout

Repositories are defined in `tiferet/repos/`:

- `__init__.py` — Empty exports (repositories are never exported).
- `app.py` — `AppConfigRepository`.
- `cli.py` — `CliConfigRepository`.
- `container.py` — `DIConfigRepository` (legacy).
- `di.py` — `DIConfigRepository`.
- `error.py` — `ErrorConfigRepository`.
- `feature.py` — `FeatureConfigRepository`.
- `logging.py` — `LoggingConfigRepository`.

Tests live in `tiferet/repos/tests/`.

## Migration from Proxies and Schematics

Repositories are the v2.0 successor to Proxies (`tiferet/proxies/`). Key changes:

- **Package rename**: `tiferet/proxies/yaml/<domain>.py` → `tiferet/repos/<domain>.py`. The nested middleware-specific directory structure is flattened into a single `repos/` package.
- **Base class**: Proxies extended `YamlConfigurationProxy` (a middleware base class). Repositories extend the Service interface directly and compose the `Yaml` utility internally.
- **Artifact comments**: `# *** proxies` / `# ** proxy:` → `# *** repos` / `# ** repo:`.
- **Data mapping**: Proxies used `DataObject.from_data()` and `DataObject.map()`. Repositories use `model_validate()` for reads and `from_model()` classmethod + `to_primitive(role)` for writes.
- **Contract alignment**: Proxies implemented `Repository` contracts. Repositories implement `Service` interfaces — the unified v2.0 contract type.
- **Pydantic v2 migration**: `TransferObject.from_data(Type, **kwargs)` → `Type.model_validate(data_dict)`; `Aggregate.new(Type, **kwargs)` → direct Pydantic constructor.

## Conclusion

Repositories provide the concrete data-access layer for the Tiferet framework, implementing Service interfaces with utility-backed persistence. Their structured design ensures consistency, testability, and clean DI resolution. Repositories are never exported directly — consuming code depends only on the abstract Service interface.

Explore source in `tiferet/repos/` and tests in `tiferet/repos/tests/` for implementation details.
