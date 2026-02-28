# Utilities in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

Utilities are a core component of the Tiferet framework, providing concrete infrastructure implementations that satisfy the **Services** (unified vertical contracts) defined in `tiferet/interfaces/`. They form the infrastructure layer that bridges abstract Service contracts — consumed by domain events and contexts — with underlying repeatable processes, whether those processes involve file system I/O, database access, computational algorithms, or external system integrations.

The utility pattern encapsulates **any reusable infrastructure concern** behind a consistent, injectable, and testable Service contract. While the current `tiferet/utils/` package contains file and data access utilities (YAML, JSON, CSV, SQLite), the architectural role extends to computational infrastructure as well — sorting algorithms, heuristics, AI model invocations, embedding pipelines, or any other repeatable process that domain events should consume without coupling to implementation details.

This document describes the structure, design principles, and best practices for writing and extending utilities, adhering to Tiferet’s structured code style ([docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/v1.9.x-maintenance/docs/core/code_style.md)).

## What is a Utility?

A **Utility** in Tiferet is a concrete class that implements one or more Services from `tiferet/interfaces/` and encapsulates a repeatable infrastructure process. Key characteristics:

- Implements a Service contract (e.g., `FileLoader` implements `FileService`, `SqliteClient` implements `SqliteService`).
- Encapsulates infrastructure concerns — both **physical** (file I/O, database connections, network calls) and **computational** (algorithms, heuristics, model inference, data transformation pipelines).
- Uses `RaiseError.execute()` from `tiferet/commands/settings.py` for structured error handling with framework-defined error codes.
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

### Key Characteristics

- **Service contract alignment** — every utility implements one or more Services.
- **Context manager lifecycle** for utilities that manage external resources.
- **Structured error handling** via `RaiseError.execute()`.
- **Inheritance hierarchy** — format-specific loaders extend `FileLoader`.
- **Static convenience methods** for common one-shot operations.
- **Caching for write operations** in `YamlLoader` and `JsonLoader`.

## The FileLoader Base Class

`FileLoader` implements `FileService` and provides the foundation for all file-based utilities.

## Current Utility Classes

### YamlLoader

Extends `FileLoader` for YAML file operations using PyYAML's `safe_load` and `safe_dump`.

- Overrides `verify_file` to enforce `.yaml`/`.yml` extension.
- `load(start_node, data_factory)` with node navigation and transformation.
- `save(data, data_path)` with path-based partial updates using cached content.
- Caches existing content in write mode on `__enter__`.

### JsonLoader

Extends `FileLoader` for JSON operations using the built-in `json` module.

- Enforces `.json` extension.
- Same `load` / `save` pattern as `YamlLoader`.
- Supports JSON path notation for partial updates.
- Write-mode caching.

### CsvLoader

Extends `FileLoader` for list-based CSV rows using `csv` module.

- CSV-compatible modes: `'r'`, `'w'`, `'a'`, `'r+'`, `'w+'`, `'a+'`.
- Lazy `csv.reader` / `csv.writer` initialization.
- Instance methods: `read_row()`, `read_all()`, `write_row()`, `write_all()`.
- Static helpers: `load_rows()`, `save_rows()`, `append_row()`, etc.
- Generator: `yield_rows()` with line-range filtering.

### CsvDictLoader

Extends `CsvLoader` for dict-based rows (`DictReader` / `DictWriter`).

- Requires explicit `fieldnames` for writing.
- Header control via `include_header`.

### SqliteClient

Extends `FileLoader` and implements `SqliteService`.

- Manages `sqlite3.Connection` and `Cursor`.
- Supports URI modes (`'ro'`, `'rw'`, `'rwc'`) and `':memory:'`.
- Auto commit/rollback on `__exit__`.
- Methods: `execute()`, `executemany()`, `executescript()`, `fetch_one()`, `fetch_all()`, `backup()`, etc.

## Structured Code Design of Utilities

Utilities follow Tiferet’s artifact comment structure:

```markdown
# *** utils
# ** util: file_loader
class FileLoader(FileService):
    # * attribute: path
    # * init
    # * method: open_file
    # * method: verify_file (static)
```

**Spacing rules** match `code_style.md`: one empty line between major sections, after docstrings, and between snippets.

## Creating New and Extending Utilities

### 1. Define a New Utility

```python
# *** imports
from ..events import RaiseError, a
from ..interfaces import FileService
from .file import FileLoader

# *** utils

# ** util: toml_loader
class TomlLoader(FileLoader):
    '''
    Utility for loading TOML files.
    '''

    # * method: verify_file
    def verify_file(self, path: str):
        if not path.endswith('.toml'):
            RaiseError.execute(a.const.INVALID_TOML_FILE_ID, ...)
        super().verify_file(path)

    # * method: load
    def load(self, start_node=lambda x: x, data_factory=lambda x: x):
        ...
```

### 2. Use in Domain Events / Repositories / Contexts

```python
with Yaml(path='feature.yml') as y:
    data = y.load(lambda d: d['features'], list)

rows = Csv.load_rows('data.csv', is_dict=True)
```

## Best Practices

- Use artifact comments consistently.
- Raise errors only via `RaiseError.execute()`.
- Implement context manager protocol for resource-owning utilities.
- Provide static one-shot helpers.
- Keep utilities focused on infrastructure — domain logic belongs in domain events / contexts.

## Testing Utilities

Use `pytest` + `tmp_path` fixture.

```python
# ** test: file_loader_invalid_mode
def test_file_loader_invalid_mode(temp_text_file):
    with pytest.raises(TiferetError) as exc:
        FileLoader(temp_text_file, mode='x')
    assert exc.value.error_code == a.const.INVALID_FILE_MODE_ID
```

## Package Layout

- `file.py` — `FileLoader` (alias: `File`)
- `yaml.py` — `YamlLoader` (alias: `Yaml`)
- `json.py` — `JsonLoader` (alias: `Json`)
- `csv.py` — `CsvLoader`, `CsvDictLoader`
- `sqlite.py` — `SqliteClient` (alias: `Sqlite`)
- `__init__.py` — exports + aliases
- Tests: `tiferet/utils/tests/`

## Relationship to Service Interfaces

Utilities implement Services from `tiferet/interfaces/`:

- `FileLoader` → `FileService`
- `SqliteClient` → `SqliteService`
- `YamlLoader` / `JsonLoader` / `CsvLoader` satisfy `ConfigurationService` pattern via repositories.

Future utilities (e.g., `EmbeddingClient`) follow the same pattern: define Service in `interfaces/`, implement in `utils/`.

## Conclusion

Utilities provide the infrastructure backbone of Tiferet, encapsulating repeatable processes behind injectable Services. Their consistent pattern — Service implementation, `RaiseError` handling, context-manager lifecycle, and artifact organization — ensures reliability and alignment with the framework.

Explore source in `tiferet/utils/`, contracts in `tiferet/interfaces/`, and tests in `tiferet/utils/tests/`.