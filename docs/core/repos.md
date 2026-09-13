# Repositories in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Repositories are the concrete data-access layer in the Tiferet framework. Every repository implements a Service interface from `tiferet/interfaces/` and inherits the shared `ConfigurationRepository` base, which handles format-specific file I/O and TransferObject serialization for the domain's aggregates.

Repositories are **never exported** from `tiferet/repos/__init__.py`. They are resolved at runtime through the DI service registration (`config.yml` or equivalent), which specifies the `module_path` and `class_name` for each concrete implementation. Consuming code depends only on the abstract Service interface, never on a concrete repository class.

### Role in Runtime
- **Service implementations**: Repositories are the concrete classes that satisfy the Service interfaces injected into domain events and contexts.
- **Configuration-backed persistence**: Each repository inherits `ConfigurationRepository`, which dispatches reads and writes to a format-specific loader based on the configuration file extension.
- **DI resolution**: Repositories are instantiated by the dependency injection container at runtime, not by direct import.

### Example: Error Domain

```python
class ErrorConfigRepository(ErrorService, ConfigurationRepository):
    # Implements ErrorService interface
    # Inherits ConfigurationRepository for format-dispatched file I/O
    # Uses ErrorConfigObject for serialization
    # Returns ErrorAggregate instances
```

## The ConfigurationRepository Base

All concrete repositories inherit the shared `ConfigurationRepository` base (`tiferet/repos/core.py`), which makes persistence format-agnostic. The base dispatches to a format-specific loader by the configuration file extension:

- `.yaml` / `.yml` → `YamlLoader`
- `.json` → `JsonLoader`
- any other extension → raises `UNSUPPORTED_CONFIG_FILE_TYPE`

It supplies three inherited attributes — `config_file`, `encoding`, and `default_role` (fixed to `'to_data'`) — and the inherited `_load` / `_save` helpers that concrete repositories call instead of instantiating a loader directly:

```python
# tiferet/repos/core.py

# ** class: configuration_repository
class ConfigurationRepository:
    '''
    A format-agnostic base for configuration repositories.
    '''

    # * attribute: config_file
    config_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, config_file: str, encoding: str = 'utf-8') -> None:
        self.config_file = config_file
        self.encoding = encoding
        self.default_role = 'to_data'
```

Concrete repositories accept a domain-prefixed `<domain>_config` parameter and forward it to the base as `config_file`.

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
"""Tiferet Error Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import ErrorService
from ..mappers import (
    ErrorAggregate,
    ErrorConfigObject,
)
from .core import ConfigurationRepository

# *** repos

# ** repo: error_config_repository
class ErrorConfigRepository(ErrorService, ConfigurationRepository):
    '''
    The error configuration repository.
    '''

    # * init
    def __init__(self, error_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the error configuration repository.

        :param error_config: The configuration file path.
        :type error_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=error_config, encoding=encoding)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if an error exists by ID.

        :param id: The error identifier.
        :type id: str
        :return: True if the error exists, otherwise False.
        :rtype: bool
        '''

        # Load the errors mapping via the inherited loader.
        errors_data = self._load(
            start_node=lambda data: data.get('errors', {})
        )

        # Return whether the error id exists in the mapping.
        return id in errors_data
```

## The Inherited Configuration Foundation

Every repository inherits three instance attributes from `ConfigurationRepository`:

- **`config_file`** (`str`) — Path to the configuration file (`.yaml`/`.yml` or `.json`).
- **`encoding`** (`str`) — File encoding, defaulting to `'utf-8'`.
- **`default_role`** (`str`) — The TransferObject serialization role used for writes, fixed to `'to_data'`.

The constructor parameter follows the convention `<domain>_config` (e.g., `error_config`, `feature_config`, `cli_config`) and is forwarded to the base as `config_file`. This domain-prefixed naming enables clean DI wiring in `config.yml`.

```python
# * init
def __init__(self, error_config: str, encoding: str = 'utf-8') -> None:
    ConfigurationRepository.__init__(self, config_file=error_config, encoding=encoding)
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
    ErrorConfigObject,
)
from .core import ConfigurationRepository    # Shared configuration base
```

The `# ** app` section imports three categories:
1. The **Service interface** being implemented.
2. The **transfer objects and aggregates** used for mapping (concrete classes only; no base-class imports needed).
3. The **`ConfigurationRepository` base** that supplies format-dispatched file I/O.

No `# ** infra` section is needed — repositories do not import third-party libraries directly; all external interaction flows through the inherited base and Tiferet utilities.

## Method Patterns

### Reading: `exists`, `get`, `list`

All read methods call the inherited `_load` helper with a `start_node` lambda to navigate the configuration structure:

```python
# Load a section.
errors_data = self._load(
    start_node=lambda data: data.get('errors', {})
)

# Load a single entry by ID.
error_data = self._load(
    start_node=lambda data: data.get('errors', {}).get(id)
)
```

Mapping from raw configuration data to domain aggregates uses `model_validate` on the concrete TransferObject class with the dictionary key injected as the `id`:

```python
return ErrorConfigObject.model_validate(
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
error_data = ErrorConfigObject.from_model(error)

# Load the full configuration file.
full_data = self._load()

# Update or insert the error entry.
full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)

# Persist the updated configuration file.
self._save(full_data)
```

### Deleting: `delete`

Delete operations are always **idempotent** — deleting a non-existent entry must not raise an error:

```python
# Load the full configuration file.
full_data = self._load()

# Remove the entry if it exists (idempotent).
full_data.get('errors', {}).pop(id, None)

# Persist the updated configuration file.
self._save(full_data)
```

## Naming Convention

Repository classes follow the pattern `<Domain>ConfigRepository`:

- `AppConfigRepository` implements `AppService`
- `CliConfigRepository` implements `CliService`
- `DIConfigRepository` implements `DIService`
- `ErrorConfigRepository` implements `ErrorService`
- `FeatureConfigRepository` implements `FeatureService`
- `LoggingConfigRepository` implements `LoggingService`

The `Config` suffix identifies the shared `ConfigurationRepository` base, which resolves the backing loader (`YamlLoader` or `JsonLoader`) from the configuration file extension at runtime.

## Creating and Extending Repositories

### 1. Define the Repository

- Place under `# *** repos` and `# ** repo: <name>` in a domain-specific module.
- Extend the corresponding Service interface from `tiferet/interfaces/` together with `ConfigurationRepository`.
- Forward the `<domain>_config` path to the `ConfigurationRepository` base in `__init__`.
- Implement each Service method using the read/write patterns described above.

**Example** — `CalculatorConfigRepository`:
```python
"""Tiferet Calculator Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces.calculator import CalculatorService
from ..mappers.calculator import (
    CalculatorResultAggregate,
    CalculatorResultConfigObject,
)
from .core import ConfigurationRepository

# *** repos

# ** repo: calculator_config_repository
class CalculatorConfigRepository(CalculatorService, ConfigurationRepository):
    '''
    The calculator configuration repository.
    '''

    # * init
    def __init__(self, calculator_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the calculator configuration repository.

        :param calculator_config: The configuration file path.
        :type calculator_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=calculator_config, encoding=encoding)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a calculator result exists by ID.

        :param id: The result identifier.
        :type id: str
        :return: True if the result exists, otherwise False.
        :rtype: bool
        '''

        # Load the results mapping via the inherited loader.
        results_data = self._load(
            start_node=lambda data: data.get('results', {})
        )

        # Return whether the result id exists in the mapping.
        return id in results_data
```

### 2. Register via DI

Add the repository to the DI configuration file (`config.yml` or equivalent) with `module_path` and `class_name`. No `__init__.py` export is needed:

```yaml
services:
  calculator_service:
    module_path: tiferet.repos.calculator
    class_name: CalculatorConfigRepository
    params:
      calculator_config: app/configs/calculator.yml
```

### 3. Write Tests

Create tests in `tests/repos/test_<domain>.py`. Seed YAML/JSON with `tmp_path` fixtures, then bind a `@use_tester(type='repo')` class that constructs via `test_ctx.make_target(config_file=...)`.

### Best Practices
- Use artifact comments consistently (`# *** repos`, `# ** repo:`, `# *`).
- Extend `ConfigurationRepository` and forward `<domain>_config` to the base for all repos.
- Use `ConfigObject.model_validate({**data, 'id': id}).map()` for reads.
- Use `ConfigObject.from_model(aggregate)` classmethod for writes, then `to_primitive(self.default_role)` to serialize.
- Make delete operations idempotent.
- Use `self._load()` with `start_node` lambdas for reads, and `self._save()` for writes.
- Include RST docstrings with `:param`, `:type`, `:return`, `:rtype`.

## Testing Repositories

Repository tests in `tests/repos/` are **file-backed integration tests**. They write real YAML/JSON via `tmp_path`, then construct the repository with `test_ctx.make_target(config_file=...)`. They do not mock the loader, and they do not drive CRUD through `session.run()`.

**Structure** after preamble (`# *** imports` / `# *** constants`):
- `# *** fixtures` / `# ** fixture: <name>` — `tmp_path` seed fixtures that write sample constants to a temp file. Do not construct the repository in a module-level `*_config_repo` fixture.
- `# *** tests` / `# ** test: <name>` — leftover module-level functions only (omit if none). `tests/repos/test_core.py` keeps `pytest.raises(ServiceError)` for an unsupported extension here; `_get_loader` `isinstance` stays in `tests/` (contexts must not import `utils`).
- `# *** testers` / `# ** tester: test_<snake>` — `class Test*` with `@use_tester(type='repo', target_cls=<Repo>, config_parameter='<domain>_config', ...)`. Members are `# * test:` / `# * fixture:`.

CRUD cases live on the `TesterObject` (`exists_cases`, `get_cases`, `list_ids`, `delete_ids`, `aggregate_cls` / `aggregate_sample_data`). Methods call `test_ctx.assert_exists` / `assert_get` / `assert_list` / `assert_save` / `assert_delete` after `make_target`. Empty CRUD lists are no-ops (DI/logging binders). Domain-specific extras (feature `list(group_id=)`, CLI parent arguments) stay bespoke `# * test:` on the same class.

**Example** — Error repository tester:
```python
# ** fixture: error_yaml_file
@pytest.fixture
def error_yaml_file(tmp_path) -> str:
    file_path = tmp_path / 'test_error.yaml'
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(ERROR_DATA, f)
    return str(file_path)

# *** testers

# ** tester: test_error_config_repository
@use_tester(
    type='repo',
    target_cls=ErrorConfigRepository,
    config_parameter='error_config',
    sample_data={},
    equality_fields=['id', 'name'],
    aggregate_cls=ErrorAggregate,
    aggregate_sample_data={'id': 'NEW_ERROR_CODE', 'name': 'New Error'},
    exists_cases=[('TEST_ERROR_CODE', True), ('MISSING_ERROR_CODE', False)],
    get_cases=[('TEST_ERROR_CODE', {'id': 'TEST_ERROR_CODE', 'name': 'Test Error'}), ('MISSING_ERROR_CODE', None)],
    list_ids=['TEST_ERROR_CODE'],
    delete_ids=['TEST_FORMATTED_ERROR_CODE'],
)
class TestErrorConfigRepository:

    # * test: exists
    def test_exists(self, test_ctx, error_yaml_file: str) -> None:
        repo = test_ctx.make_target(config_file=error_yaml_file)
        test_ctx.assert_exists(repo)
```

Worked tree: `tests/repos/test_{error,feature,app,cli}.py` (five-method CRUD), `test_{di,logging}.py` (empty CRUD lists plus bespoke methods), `test_core.py` (unsupported extension).
See [docs/core/testing.md](testing.md) for `@use_tester` and [Test-Module Artifact Grammar](code_style.md#test-module-artifact-grammar).

## Package Layout

Repositories are defined in `tiferet/repos/`:

- `__init__.py` — Empty exports (repositories are never exported).
- `core.py` — `ConfigurationRepository` (shared format-dispatch base).
- `app.py` — `AppConfigRepository`.
- `cli.py` — `CliConfigRepository`.
- `di.py` — `DIConfigRepository`.
- `error.py` — `ErrorConfigRepository`.
- `feature.py` — `FeatureConfigRepository`.
- `logging.py` — `LoggingConfigRepository`.

Tests live in `tests/repos/`.

## Conclusion

Repositories provide the concrete data-access layer for the Tiferet framework, implementing Service interfaces with utility-backed persistence. Their structured design ensures consistency, testability, and clean DI resolution. Repositories are never exported directly — consuming code depends only on the abstract Service interface.

Explore source in `tiferet/repos/` and tests in `tests/repos/` for implementation details.
