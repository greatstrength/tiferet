```markdown
# Utilities in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Utilities are a core component of the Tiferet framework, providing concrete infrastructure implementations that satisfy the **Services** (unified vertical contracts) defined in `tiferet/contracts/`. They form the infrastructure layer that bridges abstract Service contracts — consumed by commands and contexts — with underlying repeatable processes, whether those processes involve file system I/O, database access, computational algorithms, or external system integrations.

The utility pattern encapsulates **any reusable infrastructure concern** behind a consistent, injectable, and testable Service contract. While the current `tiferet/utils/` package contains file and data access utilities (YAML, JSON, CSV, SQLite), the architectural role extends to computational infrastructure as well — sorting algorithms, heuristics, AI model invocations, embedding pipelines, or any other repeatable process that commands should consume without coupling to implementation details.

This document describes the structure, design principles, and best practices for writing and extending utilities, adhering to Tiferet’s structured code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/v1.x-proto/tiferet/assets/docs/core/code_style.md)).

## What is a Utility?

A **Utility** in Tiferet is a concrete class that implements one or more Services from `tiferet/contracts/` and encapsulates a repeatable infrastructure process. Key characteristics:

- Implements a Service contract (e.g., `FileLoader` implements `FileService`, `SqliteClient` implements `SqliteService`).
- Encapsulates infrastructure concerns — both **physical** (file I/O, database connections, network calls) and **computational** (algorithms, heuristics, model inference, data transformation pipelines).
- Uses `RaiseError.execute()` from `tiferet/commands/settings.py` for structured error handling with framework-defined error codes.
- Provides both instance methods (for stateful or lifecycle-managed operations) and static convenience methods (for one-shot operations).
- Is exported from `tiferet/utils/__init__.py` with both full names and shorthand aliases (e.g., `FileLoader` / `File`, `YamlLoader` / `Yaml`).

### Physical vs. Computational Infrastructure

Utilities serve two complementary infrastructure roles:

- **Physical infrastructure**: File system access, database connections, network clients, external API wrappers. These utilities manage resource lifecycle (open/close, connect/disconnect) and typically use the context manager protocol.
- **Computational infrastructure**: Sorting algorithms, search heuristics, AI/ML model invocations, embedding generation, data transformation pipelines. These utilities encapsulate repeatable computational processes that commands consume via injected Services, keeping domain logic decoupled from algorithmic implementation.

In both cases, the pattern is identical: a utility provides a concrete, reusable implementation behind a Service contract, making it injectable, testable, and swappable. A `FileLoader` abstracts disk I/O; a hypothetical `EmbeddingClient` or `HeuristicSolver` would abstract computational infrastructure in exactly the same way.

### Role in Runtime

- **Repositories and proxies** are the primary consumers of physical infrastructure utilities. For example, `FeatureYamlRepository` uses `YamlLoader` to load and save feature configurations from YAML files.
- **Commands** consume utilities indirectly through injected Services, keeping domain logic decoupled from infrastructure. A command performing similarity search would depend on an injected `EmbeddingService`, not a concrete embedding client.
- **Contexts** may use utilities directly for low-level operations when a full repository is unnecessary.
- **Application code** (scripts, CLI handlers) may use utilities directly for quick operations outside the DDD layer.

### Key Characteristics

- **Service contract alignment**: Every utility implements one or more Services, ensuring it can be injected into commands and contexts without tight coupling.
- **Context manager lifecycle**: Utilities that manage external resources (files, connections) support `with` statements for safe acquisition and release. Files are opened on `__enter__` and closed on `__exit__`; connections are committed or rolled back automatically.
- **Structured error handling**: All validation and runtime errors are raised via `RaiseError.execute()` with specific error codes from the framework constants.
- **Inheritance hierarchy**: Format-specific loaders extend `FileLoader`, inheriting context management, mode/encoding validation, and file verification. `SqliteClient` further extends `FileLoader` while also implementing `SqliteService`.
- **Static convenience methods**: Several utilities offer static methods for common one-shot operations (e.g., `CsvLoader.load_rows()`, `CsvLoader.save_rows()`, `CsvLoader.append_row()`), reducing boilerplate for simple use cases.
- **Caching for write operations**: `YamlLoader` and `JsonLoader` cache existing file content when opened in write mode, enabling path-based partial updates without losing existing data.

## The FileLoader Base Class

`FileLoader` implements `FileService` and provides the foundation for all file-based utilities.

## Current Utility Classes

### YamlLoader

Extends `FileLoader` for YAML file operations using PyYAML's `safe_load` and `safe_dump`.

- **Verification**: Overrides `verify_file` to ensure the file has a `.yaml` or `.yml` extension. Provides a static `verify_yaml_file()` method for pre-validation with optional default path resolution.
- **Loading**: `load(start_node, data_factory)` reads YAML content, navigates to a specified node via `start_node`, and transforms data via `data_factory`.
- **Saving**: `save(data, data_path)` writes YAML data. When `data_path` is provided, performs a path-based partial update using cached content from the original file.
- **Caching**: On `__enter__` in write mode, reads and caches existing file content to support partial updates.

### JsonLoader

Extends `FileLoader` for JSON file operations using Python's built-in `json` module.

- **Verification**: Overrides `verify_file` to ensure the file has a `.json` extension.
- **Loading**: `load(start_node, data_factory)` reads JSON content with the same navigation and factory pattern as `YamlLoader`.
- **Saving**: `save(data, data_path, indent)` writes JSON data with configurable indentation. Supports JSON path notation (e.g., `"key1.key2[0].key3"`) for partial updates via `parse_json_path()`.
- **Caching**: Same write-mode caching pattern as `YamlLoader`.

### CsvLoader

Extends `FileLoader` for CSV file operations using Python's `csv` module with list-based rows.

- **Mode validation**: Overrides `verify_mode` with CSV-compatible modes: `'r'`, `'w'`, `'a'`, `'r+'`, `'w+'`, `'a+'`.
- **Reader/Writer management**: `build_reader()` and `build_writer()` lazily initialize `csv.reader` and `csv.writer` on demand, with mode validation.
- **Instance methods**: `read_row()`, `read_all()`, `write_row()`, `write_all()` for use within a context manager.
- **Static convenience methods**: `load_rows()`, `save_rows()`, `append_row()`, `append_dict_row()`, `save_dict_rows()` for one-shot operations that handle context management internally.
- **Row iteration**: `yield_rows()` provides a generator for memory-efficient row-by-row reading with line number range filtering.
- **Line number helpers**: `get_start_line_num()` and `get_end_line_num()` compute line numbers accounting for header presence.

### CsvDictLoader

Extends `CsvLoader` for dict-based CSV rows using `csv.DictReader` and `csv.DictWriter`.

- Overrides `build_reader()` to use `csv.DictReader`.
- Overrides `build_writer(fieldnames)` to use `csv.DictWriter`, requiring explicit fieldnames.
- Overrides `write_row()` and `write_all()` with `include_header` support for header row management.

### SqliteClient

Extends `FileLoader` and implements `SqliteService` for SQLite database operations using Python's `sqlite3` module.

- **Connection management**: Overrides `open_file()` and `close_file()` to manage `sqlite3.Connection` and `sqlite3.Cursor` instead of text file streams. Supports URI syntax for flexible mode control (`'ro'`, `'rw'`, `'rwc'`).
- **Transaction control**: `__exit__` automatically commits on success or rolls back on exception. Manual `commit()` and `rollback()` are also available.
- **Query execution**: `execute()`, `executemany()`, `executescript()` for parameterized and batch SQL operations.
- **Data fetching**: `fetch_one()` and `fetch_all()` for query results, with optional `sqlite3.Row` factory for dict-like access.
- **Backup**: `backup(target_path, pages, progress)` for online database backup.
- **Custom functions**: Supports registering custom SQL functions via `custom_functions` parameter.
- **In-memory databases**: Supports `':memory:'` path for in-memory databases.

## Structured Code Design of Utilities

Utilities follow Tiferet’s structured code style using artifact comments for organization and readability.

### Artifact Comments

Utilities are organized under the `# *** utils` top-level comment, with individual utilities under `# ** util: <snake_case_name>`. Within each utility:

- `# * attribute: <name>` — Declares instance attributes.
- `# * init` — Constructor.
- `# * method: <name>` — Instance methods.
- `# * method: <name> (static)` — Static methods.

**Spacing rules:**
- One empty line between `# *** utils` and first `# ** util`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

**Example** — `tiferet/utils/file.py`:
```python
# *** imports

# ** core
import os
from typing import Any

# ** app
from ..commands import RaiseError, a
from ..contracts import FileService

# *** utils

# ** util: file_loader
class FileLoader(FileService):
    '''
    Utility for loading files into the application.
    '''

    # * attribute: path
    path: str

    # * attribute: mode
    mode: str

    # * attribute: encoding
    encoding: str

    # * attribute: newline
    newline: str

    # * attribute: file
    file: Any

    # * init
    def __init__(self, path: str, mode: str = 'r', encoding: str = 'utf-8', newline: str = None):
        '''
        Initialize the FileLoader.

        :param path: The path to the file to load.
        :type path: str
        :param mode: The mode in which to open the file.
        :type mode: str
        :param encoding: The encoding to use when reading the file.
        :type encoding: str
        :param newline: The newline parameter for file operations.
        :type newline: str
        '''

        # Verify the file mode.
        self.verify_mode(mode)

        # Validate the encoding.
        self.verify_encoding(encoding)

        # Set the path, mode, and encoding.
        self.mode = mode
        self.path = path
        self.encoding = encoding
        self.newline = newline

        # Set the file stream to None initially.
        self.file = None

    # * method: open_file
    def open_file(self):
        '''
        Open the file with the specified path, mode, and encoding.
        '''

        # Verify the file before opening.
        self.verify_file(self.path)

        # Raise an error if the file is already open.
        if self.file is not None:
            RaiseError.execute(
                a.const.FILE_ALREADY_OPEN_ID,
                f'File is already open: {self.path}.',
                path=self.path
            )

        # Open the file with the specified parameters.
        self.file = open(
            self.path,
            mode=self.mode,
            encoding=self.encoding,
            newline=self.newline
        )
```

All format-specific loaders inherit this lifecycle. Subclasses override `verify_file` to add format-specific validation (e.g., `.yaml`/`.yml` extension check) and `verify_mode` for format-specific mode constraints.

## Creating New and Extending Utilities

### 1. Define a New Utility

- Place under `# *** utils` and `# ** util: <name>` in `tiferet/utils/`.
- Extend `FileLoader` for file-based utilities, or implement a Service contract directly for computational utilities.
- Implement or override format-specific verification, loading, and saving.
- Use `RaiseError.execute()` with appropriate error codes for all error conditions.

**Example — Physical Infrastructure** (`TomlLoader`):
```python
# *** imports

# ** core
from typing import Any, Dict, Callable

# ** infra
import tomllib

# ** app
from .file import FileLoader
from ..commands import RaiseError, a
from ..contracts import FileService

# *** utils

# ** util: toml_loader
class TomlLoader(FileLoader):
    '''
    Utility for loading TOML files into the application.
    '''

    # * method: verify_file
    def verify_file(self, path: str):
        '''
        Verify that the file is a valid TOML file.

        :param path: The path to the TOML file.
        :type path: str
        '''

        # Verify the TOML file extension.
        if not path or not path.endswith('.toml'):
            RaiseError.execute(
                a.const.INVALID_TOML_FILE_ID,
                f'File {path} is not a valid TOML file.',
                path=path
            )

        # Call the parent class verification.
        super().verify_file(path)

    # * method: load
    def load(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Dict[str, Any]:
        '''
        Load the TOML file and return its contents.

        :param start_node: A callable to navigate to a starting node.
        :type start_node: Callable
        :param data_factory: A callable to transform the loaded data.
        :type data_factory: Callable
        :return: The contents of the TOML file.
        :rtype: Dict[str, Any]
        '''

        # Load and parse the TOML content.
        toml_content = tomllib.loads(self.file.read())

        # Navigate to the start node.
        toml_content = start_node(toml_content)

        # Return the processed content.
        return data_factory(toml_content)
```

**Example — Computational Infrastructure** (`EmbeddingClient`):
```python
# *** imports

# ** core
from typing import List

# ** app
from ..commands import RaiseError, a
from ..contracts import EmbeddingService

# *** utils

# ** util: embedding_client
class EmbeddingClient(EmbeddingService):
    '''
    Utility for generating vector embeddings from text inputs.
    Encapsulates model loading, inference, and result normalization
    behind the EmbeddingService contract.
    '''

    # * attribute: model
    model: Any

    # * attribute: model_name
    model_name: str

    # * init
    def __init__(self, model_name: str, **kwargs):
        '''
        Initialize the embedding client with a model name.

        :param model_name: The name or path of the embedding model to load.
        :type model_name: str
        '''

        # Store the model name.
        self.model_name = model_name

        # Load the model.
        self.model = self._load_model(model_name, **kwargs)

    # * method: embed
    def embed(self, texts: List[str]) -> List[List[float]]:
        '''
        Generate embeddings for a list of text inputs.

        :param texts: The text inputs to embed.
        :type texts: List[str]
        :return: A list of embedding vectors.
        :rtype: List[List[float]]
        '''

        # Validate the input texts.
        if not texts:
            RaiseError.execute(
                a.const.EMBEDDING_INPUT_EMPTY_ID,
                'Cannot generate embeddings for empty input.',
            )

        # Generate and return the embeddings.
        return self.model.encode(texts).tolist()
```

### 2. Extend an Existing Utility

- Override `verify_file` for additional format validation.
- Override `verify_mode` for format-specific mode constraints.
- Override `__enter__` / `__exit__` for additional lifecycle behavior (e.g., caching).
- Add static convenience methods for common one-shot operations.

### 3. Use in Commands / Repositories / Contexts

- Commands should depend on the **Service contract**, not the concrete utility class.
- Repositories and proxies import utilities directly (e.g., `from tiferet.utils import Yaml`).
- Use within a `with` block for safe resource management when the utility manages external resources.
- For one-shot operations, use static methods when available.

```python
# Loading YAML with context manager
with Yaml(path='app/configs/feature.yml') as yaml_r:
    features = yaml_r.load(
        start_node=lambda data: data.get('features', {}),
        data_factory=lambda data: [Feature.from_data(f) for f in data]
    )

# One-shot CSV loading
rows = Csv.load_rows(
    csv_file='data/records.csv',
    is_dict=True,
    data_factory=lambda row: Record.from_data(row)
)
```

## Best Practices

- Use artifact comments (`# * attribute`, `# * method`, `# * method: <name> (static)`) consistently.
- Always use `RaiseError.execute()` with framework error codes — never raise raw exceptions.
- Implement the context manager protocol (`__enter__` / `__exit__`) for all utilities that manage external resources.
- Override `verify_file` and `verify_mode` in subclasses for format-specific validation.
- Provide static convenience methods for common single-operation use cases.
- Cache existing file content in write mode when supporting partial updates.
- Keep utilities focused on infrastructure operations — domain logic belongs in commands and contexts.
- Computational utilities should be stateless where possible, or manage state explicitly through clear initialization.
- Maintain one empty line between sections, comments, and code blocks.

## Testing Utilities

Tests validate initialization, verification, lifecycle management, loading, saving, and error handling using `pytest`.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Pattern**: Use `pytest`'s `tmp_path` fixture to create temporary files for test isolation. Test both success paths and error conditions (invalid paths, modes, encodings, formats). For computational utilities, mock external dependencies (models, APIs) and verify input validation and output shape.

**Example** — `FileLoader` tests:
```python
# *** imports

# ** infra
import pytest

# ** app
from ..file import FileLoader
from ...commands import TiferetError, a

# *** fixtures

# ** fixture: temp_text_file
@pytest.fixture
def temp_text_file(tmp_path):
    '''
    Fixture to create a temporary text file with sample content.
    '''

    # Create a temporary text file.
    file_path = tmp_path / 'test.txt'
    with open(file_path, 'w', encoding='utf-8') as fmw:
        fmw.write('Sample content')

    # Return the file path.
    return str(file_path)

# *** tests

# ** test: file_loader_instantiation
def test_file_loader_instantiation(temp_text_file: str):
    '''
    Test successful instantiation of a FileLoader object.
    '''

    # Open the file and verify attributes.
    with FileLoader(path=temp_text_file) as fl:
        assert isinstance(fl, FileLoader)
        assert fl.mode == 'r'
        assert fl.encoding == 'utf-8'
        assert fl.file is not None

# ** test: file_loader_instantiation_invalid_mode
def test_file_loader_instantiation_invalid_mode(temp_text_file: str):
    '''
    Test that an invalid mode raises a TiferetError.
    '''

    # Attempt to create with invalid mode.
    with pytest.raises(TiferetError) as exc_info:
        FileLoader(path=temp_text_file, mode='x')

    # Verify the error code.
    assert exc_info.value.error_code == a.const.INVALID_FILE_MODE_ID
```

### Best Practices

- Use `tmp_path` for file isolation in physical infrastructure tests.
- Test context manager open/close lifecycle.
- Test all validation paths (invalid modes, encodings, paths, file formats).
- Test loading and saving with various data shapes.
- Verify error codes from `TiferetError` on failure cases.
- For `SqliteClient`, test with `':memory:'` for fast, isolated database tests.
- For computational utilities, mock external models or APIs and verify input validation, output structure, and error handling.

## Package Layout

Utilities are defined in `tiferet/utils/`:

- `file.py` — `FileLoader` (alias: `File`). Base utility implementing `FileService`. Context manager for generic file I/O with mode, encoding, and path validation.
- `yaml.py` — `YamlLoader` (alias: `Yaml`). YAML file loading and saving via PyYAML. Supports path-based partial updates.
- `json.py` — `JsonLoader` (alias: `Json`). JSON file loading and saving. Supports JSON path navigation and partial updates.
- `csv.py` — `CsvLoader` (alias: `Csv`), `CsvDictLoader` (alias: `CsvDict`). CSV file reading and writing for both list-based and dict-based rows. Includes static convenience methods for common operations.
- `sqlite.py` — `SqliteClient` (alias: `Sqlite`). SQLite database client implementing both `FileService` and `SqliteService`. Manages connections, transactions, queries, and backups.
- `__init__.py` — Public exports with full names and shorthand aliases.

Tests live in `tiferet/utils/tests/`.

## Relationship to Service Contracts

Utilities are the **concrete implementations** of the Services (vertical contracts) defined in `tiferet/contracts/`:

- `FileLoader` implements `FileService` (`contracts/file.py`) — `open_file()`, `close_file()`.
- `SqliteClient` implements `SqliteService` (`contracts/sqlite.py`) — `execute()`, `executemany()`, `executescript()`, `fetch_one()`, `fetch_all()`, `commit()`, `rollback()`, `backup()`.

While `YamlLoader`, `JsonLoader`, and `CsvLoader` do not directly implement a dedicated Service, they satisfy the `ConfigurationService` contract pattern through their `load()` and `save()` methods, and are consumed by repositories that implement `ConfigurationService`.

Future computational utilities follow the same pattern: define a Service in `tiferet/contracts/` (e.g., `EmbeddingService`), then implement the concrete utility in `tiferet/utils/`.

## Conclusion

Utilities are the infrastructure backbone of the Tiferet framework, encapsulating repeatable processes — both physical and computational — behind injectable Services. They bridge the abstract contracts consumed by commands and contexts with concrete implementations, whether those implementations involve file system access, database queries, sorting algorithms, AI model inference, or any other infrastructure concern.

Their consistent design pattern — Service contract implementation, structured error handling via `RaiseError`, context manager lifecycle for resource management, and artifact comment organization — ensures that utilities are reliable, testable, and aligned with the framework's design philosophy. The current file and data access utilities establish the pattern; future computational utilities extend the same architecture into new domains.

Explore source in `tiferet/utils/` for current utilities, `tiferet/contracts/` for the contracts they implement, and `tiferet/utils/tests/` for test examples.
```