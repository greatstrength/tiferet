# Utilities in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Utilities are a core component of the Tiferet framework, providing concrete infrastructure implementations that satisfy the **Services** (unified vertical contracts) defined in `tiferet/interfaces/`. They form the infrastructure layer that bridges abstract Service contracts — consumed by domain events and contexts — with underlying repeatable processes, whether those processes involve file system I/O, database access, computational algorithms, or external system integrations.

The utility pattern encapsulates **any reusable infrastructure concern** behind a consistent, injectable, and testable Service contract. While the current `tiferet/utils/` package contains file and data access utilities (YAML, JSON, CSV, SQLite), the architectural role extends to computational infrastructure as well — sorting algorithms, heuristics, AI model invocations, embedding pipelines, or any other repeatable process that domain events should consume without coupling to implementation details.

This document describes the structure, design principles, and best practices for writing and extending utilities, adhering to Tiferet's structured code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## What is a Utility?

A **Utility** in Tiferet is a concrete class that implements one or more Services from `tiferet/interfaces/` and encapsulates a repeatable infrastructure process. Key characteristics:

- Implements a Service contract (e.g., `FileLoader` implements `FileService`, `SqliteClient` implements `SqliteService`).
- Encapsulates infrastructure concerns — both **physical** (file I/O, database connections, network calls) and **computational** (algorithms, heuristics, model inference, data transformation pipelines).
- Uses `RaiseError.execute()` from `tiferet/events/static.py` for structured error handling with framework-defined error codes.
- Provides both instance methods (for stateful or lifecycle-managed operations) and static convenience methods (for one-shot operations).
- Is exported from `tiferet/utils/__init__.py` with both full names and shorthand aliases (e.g., `FileLoader` / `File`, `YamlLoader` / `Yaml`).

### Physical vs. Computational Infrastructure

Utilities serve two complementary infrastructure roles:

- **Physical infrastructure**: File system access, database connections, network clients, external API wrappers. These utilities manage resource lifecycle (open/close, connect/disconnect) and typically use the context manager protocol.
- **Computational infrastructure**: Sorting algorithms, search heuristics, AI/ML model invocations, embedding generation, data transformation pipelines. These utilities encapsulate repeatable computational processes that domain events consume via injected Services, keeping domain logic decoupled from algorithmic implementation.

In both cases, the pattern is identical: a utility provides a concrete, reusable implementation behind a Service contract, making it injectable, testable, and swappable.

### Role in Runtime

- **Repositories and proxies** are the primary consumers of physical infrastructure utilities (e.g., `FeatureYamlRepository` uses `YamlLoader`).
- **Domain events** consume utilities indirectly through injected Services, keeping domain logic decoupled from infrastructure.
- **Contexts** may use utilities directly for low-level operations when a full repository is unnecessary.
- **Application code** (scripts, CLI handlers) may use utilities directly for quick operations outside the DDD layer.

## The FileLoader Base Class

`FileLoader` implements `FileService` and provides the foundation for all file-based utilities:

- **Path management** — accepts `str` or `pathlib.Path`, stores as `Path`.
- **Mode and encoding validation** — `verify_mode()` and `verify_encoding()` with structured error handling.
- **File existence checks** — `verify_file()` (static) adapts behavior to read vs. write modes.
- **Context manager protocol** — `__enter__` opens the file stream, `__exit__` closes it.
- **Already-open guard** — prevents double-open via `open_file()`.

Format-specific loaders (`YamlLoader`, `JsonLoader`, `CsvLoader`, `SqliteClient`) extend `FileLoader` and override or add methods as needed.

## Current Utility Classes

### FileLoader (alias: File)

Base utility implementing `FileService`. Manages file stream lifecycle with validation and context-manager support.

- `open_file()` / `close_file()` — stream lifecycle.
- `verify_file(path, mode)` (static) — existence checks adapted to mode.
- `verify_mode()` / `verify_encoding()` — validation.

### YamlLoader (alias: Yaml)

Extends `FileLoader` for YAML file operations using PyYAML's `safe_load` and `safe_dump`.

- Overrides `verify_file` to enforce `.yaml`/`.yml` extension.
- `load(start_node, data_factory)` with node navigation and transformation.
- `save(data, data_path)` with path-based partial updates using cached content.
- Caches existing content in write mode on `__enter__`.

### JsonLoader (alias: Json)

Extends `FileLoader` for JSON operations using the built-in `json` module.

- `verify_json_file()` (static) — enforces `.json` extension with optional fallback path.
- `load(start_node, data_factory)` — parse, transform, return.
- `save(data, data_path)` — serialize with indent=2.
- `parse_json_path(data, path)` (static) — dot-notation navigation with array index support.

### CsvLoader (alias: Csv)

Extends `FileLoader` for list-based CSV rows using the `csv` module.

- CSV-compatible modes: `'r'`, `'w'`, `'a'`, `'r+'`, `'w+'`, `'a+'`.
- Lazy `csv.reader` / `csv.writer` initialization.
- Instance methods: `read_row()`, `read_all()`, `write_row()`, `write_all()`.
- Static helpers: `load_rows()`, `save_rows()`, `append_row()`, `append_rows()`.
- Generator: `yield_rows()` with line-range filtering.

### CsvDictLoader (alias: CsvDict)

Extends `CsvLoader` for dict-based rows (`DictReader` / `DictWriter`).

- Requires explicit `fieldnames` for writing.
- Header control via `include_header`.
- Inherits all static helpers from `CsvLoader` with `is_dict=True` support.

### SqliteClient (alias: Sqlite)

Extends `FileLoader` and implements `SqliteService`.

- Manages `sqlite3.Connection` and `Cursor` internally.
- Supports URI modes (`'ro'`, `'rw'`, `'rwc'`) and `':memory:'`.
- Auto-commit on successful `__exit__`, auto-rollback on exception.
- Methods: `execute()`, `executemany()`, `executescript()`, `fetch_one()`, `fetch_all()`, `commit()`, `rollback()`, `backup()`.
- `__enter__` returns `self` (not a file stream).

## Structured Code Design of Utilities

Utilities follow Tiferet's artifact comment structure:

- `# *** utils` — top-level section.
- `# ** util: <snake_case_name>` — individual utility class.
- `# * attribute: <name>` — instance attributes.
- `# * init` — constructor.
- `# * method: <name>` — instance methods.
- `# * method: <name> (static)` — static methods.

**Spacing rules** match `code_style.md`: one empty line between major sections, after docstrings, and between code snippets.

**Example** — artifact structure for `FileLoader`:
```python
# *** utils

# ** util: file_loader
class FileLoader(FileService):
    '''
    Base utility for low-level file stream operations.
    '''

    # * attribute: path
    path: Path

    # * attribute: mode
    mode: str

    # * init
    def __init__(self, path, mode='r', encoding=None, newline=None, **kwargs):
        ...

    # * method: verify_file (static)
    @staticmethod
    def verify_file(path, mode='r'):
        ...

    # * method: verify_mode
    def verify_mode(self):
        ...

    # * method: open_file
    def open_file(self):
        ...

    # * method: close_file
    def close_file(self):
        ...

    # * method: __enter__
    def __enter__(self):
        ...

    # * method: __exit__
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...
```

## Creating New and Extending Utilities

### Physical Infrastructure Example — TomlLoader

```python
# *** imports

# ** core
import tomllib

# ** app
from .file import FileLoader
from ..events import RaiseError, a

# *** utils

# ** util: toml_loader
class TomlLoader(FileLoader):
    '''
    Utility for loading TOML files.
    '''

    # * init
    def __init__(self, path, mode='rb', **kwargs):
        super().__init__(path=path, mode=mode, **kwargs)

    # * method: load
    def load(self, start_node=lambda x: x, data_factory=lambda x: x):
        '''
        Load and parse TOML content.
        '''
        try:
            with self:
                data = tomllib.load(self.file)
                return data_factory(start_node(data))
        except tomllib.TOMLDecodeError as e:
            RaiseError.execute(
                error_code=a.const.INVALID_TOML_FILE_ID,
                error=str(e),
                path=str(self.path),
            )
```

### Computational Infrastructure Example — EmbeddingClient

```python
# *** imports

# ** app
from ..interfaces.embedding import EmbeddingService
from ..events import RaiseError, a

# *** utils

# ** util: embedding_client
class EmbeddingClient(EmbeddingService):
    '''
    Utility for generating text embeddings via an external model API.
    '''

    # * init
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

    # * method: embed
    def embed(self, text: str) -> list[float]:
        '''
        Generate an embedding vector for the given text.
        '''
        # Call external API and return vector.
        ...
```

## Best Practices

- Use artifact comments (`# *** utils` / `# ** util:` / `# * method:`) consistently.
- Raise errors only via `RaiseError.execute()` — never raise raw exceptions from utilities.
- Implement context manager protocol (`__enter__` / `__exit__`) for resource-owning utilities.
- Provide static one-shot helpers for common operations (e.g., `CsvLoader.load_rows()`).
- Keep utilities focused on infrastructure — domain logic belongs in domain events and contexts.
- Align every utility with a Service contract from `tiferet/interfaces/`.
- Stateless computational utilities need not implement context managers.

## Testing Utilities

Use `pytest` with `tmp_path` fixture for file-based utilities. Test structure follows artifact comments:

```python
# *** fixtures

# ** fixture: temp_file
@pytest.fixture
def temp_file(tmp_path) -> Path:
    '''
    Create a temporary file for testing.
    '''
    file_path = tmp_path / 'test.txt'
    file_path.write_text('hello', encoding='utf-8')
    return file_path

# *** tests

# ** test: file_loader_open_close
def test_file_loader_open_close(temp_file):
    '''
    Test opening and closing a file stream.
    '''
    loader = FileLoader(path=temp_file, mode='r', encoding='utf-8')
    loader.open_file()
    assert loader.file is not None
    loader.close_file()
    assert loader.file is None

# ** test: file_loader_invalid_mode
def test_file_loader_invalid_mode(temp_file):
    '''
    Test that an invalid mode raises INVALID_FILE_MODE.
    '''
    loader = FileLoader(path=temp_file, mode='z')
    with pytest.raises(TiferetError) as exc_info:
        loader.open_file()
    assert exc_info.value.error_code == a.const.INVALID_FILE_MODE_ID
```

**Key testing patterns:**
- Test success paths, error paths, and edge cases.
- Use in-memory databases for `SqliteClient` tests.
- Mock computational utilities when testing domain events that consume them.
- Verify structured error codes, not just exception types.

## Package Layout

```
tiferet/utils/
├── __init__.py          — Exports + aliases (File, Yaml, Json, Csv, CsvDict, Sqlite)
├── file.py              — FileLoader (alias: File) — implements FileService
├── yaml.py              — YamlLoader (alias: Yaml) — YAML read/write via PyYAML
├── json.py              — JsonLoader (alias: Json) — JSON read/write with path support
├── csv.py               — CsvLoader (alias: Csv), CsvDictLoader (alias: CsvDict)
├── sqlite.py            — SqliteClient (alias: Sqlite) — implements SqliteService + FileService
└── tests/
    ├── __init__.py
    ├── test_file.py
    ├── test_yaml.py
    ├── test_json.py
    ├── test_csv.py
    └── test_sqlite.py
```

## Relationship to Service Interfaces

Utilities implement Services from `tiferet/interfaces/`:

- `FileLoader` → `FileService` (`interfaces/file.py`)
- `SqliteClient` → `SqliteService` (`interfaces/sqlite.py`) + `FileService` (via `FileLoader`)
- `YamlLoader` / `JsonLoader` / `CsvLoader` satisfy the `ConfigurationService` pattern indirectly via repositories that consume them.

Future utilities follow the same pattern: define a Service interface in `tiferet/interfaces/`, implement the concrete utility in `tiferet/utils/`, and export with an alias.

## Conclusion

Utilities provide the infrastructure backbone of Tiferet, encapsulating repeatable processes — both physical and computational — behind injectable Service contracts. Their consistent pattern — Service implementation, `RaiseError` handling, context-manager lifecycle, and artifact organization — ensures reliability, testability, and alignment with the framework's DDD architecture.

Explore source in `tiferet/utils/`, contracts in `tiferet/interfaces/`, and tests in `tiferet/utils/tests/`.

For user-facing guides on consuming utilities directly, see:
- [docs/guides/utils/file.md](../guides/utils/file.md)
- [docs/guides/utils/yaml.md](../guides/utils/yaml.md)
- [docs/guides/utils/json.md](../guides/utils/json.md)
- [docs/guides/utils/csv.md](../guides/utils/csv.md)
- [docs/guides/utils/sqlite.md](../guides/utils/sqlite.md)
