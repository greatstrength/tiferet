---
name: tiferet-code-utils
description: Apply utility conventions when adding or modifying infrastructure utilities in a Tiferet-family repo. Covers the FileLoader base, context manager protocol, static one-shot helpers, exported aliases, and computational vs physical infrastructure.
---

# Utilities Code Style – Tiferet

## When to use
- When adding a new utility class or modifying an existing one in `tiferet/utils/`.
- When implementing physical infrastructure (file I/O, database, network) or computational infrastructure (algorithms, ML inference, transformations) behind a Service contract.
- When extending `FileLoader` for a new file format (e.g. TOML, XML).

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** utils              ← construct group for this skill
# *** exports            ← __init__.py only
```

Util-specific labels:
```
# *** utils                             ← artifact section
# ** util: <snake_case_name>            ← artifact
# * attribute: <name>                   ← artifact member: instance attributes
# * init                                ← artifact member: constructor
# * method: <name>                      ← artifact member: instance methods
# * method: <name> (static)             ← artifact member: static one-shot helpers
```

## Key conventions

- **Layer boundary — valid `# ** app` imports:** `interfaces` (the Service contract to implement, plus `interfaces.core` for `ServiceError`), `mappers`. Never import from `events`, `domain`, `repos`, `di`, `contexts`, or `blueprints`. The `events` prohibition is real: reaching into `events` for an error vocabulary was the violation the service error protocol removed.
- Implementing a **Service** contract from `tiferet/interfaces/` is **optional** — required only when the utility needs to be DI-injectable (resolved from the container). Utilities called statically or directly do not need a Service interface. The config loaders (`YamlLoader`, `JsonLoader`, `TomlLoader`) deliberately declare only `FileLoader`.
- Raise every failure as a `ServiceError` via `ServiceError.raise_for(self, error_code, message, ...)` from `tiferet/interfaces/core.py`. Never let a raw driver exception escape a utility, and never use `RaiseError` / `TiferetError` — an infrastructural failure is not a domain outcome.
- Host each error code as an `_ID` constant in a `# *** constants` section of the module that raises it. Infrastructure codes are **not** catalogued in `assets/error.py`. When a code is raised from two modules, host it in the one they both already import (e.g. `INVALID_FILE_ID` lives in `utils/file.py`).
- Supply the message inline as an f-string, since a service error is never localized. When a placeholder-free message repeats across raise sites, hoist it to a module-level message constant in a `# *** constants (messages)` sub-group.
- Pass `cause=e` when converting an underlying exception so its detail survives as `__cause__`.
- At a static raise site with no instance available, pass the class in place of `self`.
- **Resource-owning utilities** implement the context manager protocol: `__enter__` (open/connect) and `__exit__` (close/disconnect; commit or rollback on error).
- **Static one-shot helpers** on utilities (e.g. `CsvLoader.load_rows(path)`) provide a convenience API that opens, reads, closes in a single call.
- Export from `tiferet/utils/__init__.py` with both the full class name and a short alias (e.g. `FileLoader` / `File`, `YamlLoader` / `Yaml`).
- Stateless computational utilities (algorithms, inference) do NOT need context managers.

**Current utility aliases:**

| Full name | Alias | Service contract | Hosted error codes |
|---|---|---|---|
| `FileLoader` | `File` | `FileService` | `FILE_NOT_FOUND`, `FILE_ALREADY_OPEN`, `INVALID_FILE`, `INVALID_FILE_MODE`, `INVALID_ENCODING` |
| `YamlLoader` | `Yaml` | `FileService` (inherited) | `YAML_FILE_NOT_FOUND`, `YAML_FILE_LOAD_ERROR`, `YAML_FILE_SAVE_ERROR` |
| `JsonLoader` | `Json` | `FileService` (inherited) | `JSON_FILE_NOT_FOUND`, `JSON_FILE_LOAD_ERROR`, `JSON_FILE_SAVE_ERROR`, `INVALID_JSON_PATH` |
| `TomlLoader` | `Toml` | `FileService` (inherited) | `TOML_FILE_NOT_FOUND`, `TOML_FILE_LOAD_ERROR`, `INVALID_TOML_FILE` |
| `CsvLoader` | `Csv` | `FileService` (inherited) | `CSV_FIELDNAMES_REQUIRED`, `CSV_INVALID_READ_MODE`, `CSV_INVALID_WRITE_MODE` |
| `CsvDictLoader` | `CsvDict` | `FileService` (inherited) | (shares the `CsvLoader` codes) |
| `SqliteClient` | `Sqlite` | `SqliteService`, `FileService` | `SQLITE_CONN_FAILED`, `SQLITE_CONN_ALREADY_OPEN`, `SQLITE_CONN_NOT_INITIALIZED`, `SQLITE_INVALID_MODE`, `SQLITE_STATEMENT_FAILED`, `SQLITE_QUERY_FAILED`, `SQLITE_TRANSACTION_FAILED`, `SQLITE_BACKUP_FAILED` |
| `LoggingMiddleware` | — | `MiddlewareService` | — |
| `TimingMiddleware` | — | `MiddlewareService` | — |
| `CacheMiddleware` | — | `MiddlewareService` | — |

The config loaders declare only `FileLoader`; they implement no configuration
contract, since no consumer or implementer needs one.

## Example

```python
# *** imports

# ** core
import tomllib
from pathlib import Path

# ** app
from .file import FileLoader
from ..interfaces.core import ServiceError

# *** constants

# ** constant: invalid_toml_file_id
INVALID_TOML_FILE_ID = 'INVALID_TOML_FILE'

# *** utils

# ** util: toml_loader
class TomlLoader(FileLoader):
    '''
    Utility for loading TOML configuration files.

    Implements FileService via FileLoader. Context manager opens the
    file stream; load() parses and transforms the content.
    '''

    # * init
    def __init__(self, path, mode: str = 'rb', **kwargs):
        '''
        Initialize the TOML loader.

        :param path: Path to the TOML file.
        :type path: str | Path
        :param mode: File open mode (default 'rb' for TOML).
        :type mode: str
        :param kwargs: Additional kwargs forwarded to FileLoader.
        :type kwargs: dict
        '''

        # Initialize the file loader base.
        super().__init__(path=path, mode=mode, **kwargs)

    # * method: load
    def load(self,
            start_node=lambda x: x,
            data_factory=lambda x: x):
        '''
        Load and parse the TOML file content.

        :param start_node: Function to navigate to a sub-node of the parsed data.
        :type start_node: Callable
        :param data_factory: Function to transform the navigated data.
        :type data_factory: Callable
        :return: The loaded and transformed data.
        :rtype: Any
        :raises ServiceError: If the file cannot be parsed.
        '''

        # Open, parse, transform, and return the TOML data.
        with self:
            try:
                data = tomllib.load(self.file)
            except tomllib.TOMLDecodeError as e:
                ServiceError.raise_for(
                    self,
                    INVALID_TOML_FILE_ID,
                    f'File is not a valid TOML file: {self.path}.',
                    cause=e,
                    error=str(e),
                    path=str(self.path),
                )

        # Apply the start_node navigation and data_factory transform.
        return data_factory(start_node(data))

    # * method: load_toml (static)
    @staticmethod
    def load_toml(path, start_node=lambda x: x, data_factory=lambda x: x):
        '''
        One-shot static helper: open, parse, close, and return.

        :param path: Path to the TOML file.
        :type path: str | Path
        :param start_node: Sub-node navigation function.
        :type start_node: Callable
        :param data_factory: Data transformation function.
        :type data_factory: Callable
        :return: The loaded and transformed data.
        :rtype: Any
        '''

        # Delegate to an instance with managed lifecycle.
        return TomlLoader(path).load(start_node=start_node, data_factory=data_factory)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md
