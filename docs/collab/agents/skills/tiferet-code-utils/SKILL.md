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

```
# *** utils                             ← top-level
# ** util: <snake_case_name>            ← individual utility class
# * attribute: <name>                   ← instance attributes
# * init                                ← constructor
# * method: <name>                      ← instance methods
# * method: <name> (static)             ← static one-shot helpers
```

## Key conventions

- Utilities implement a **Service** contract from `tiferet/interfaces/` (e.g. `FileLoader` implements `FileService`, `SqliteClient` implements `SqliteService`).
- Use `RaiseError.execute(error_code, ...)` from `tiferet/events/static.py` for all error paths — never raise raw exceptions from utilities.
- **Resource-owning utilities** implement the context manager protocol: `__enter__` (open/connect) and `__exit__` (close/disconnect; commit or rollback on error).
- **Static one-shot helpers** on utilities (e.g. `CsvLoader.load_rows(path)`) provide a convenience API that opens, reads, closes in a single call.
- Export from `tiferet/utils/__init__.py` with both the full class name and a short alias (e.g. `FileLoader` / `File`, `YamlLoader` / `Yaml`).
- Stateless computational utilities (algorithms, inference) do NOT need context managers.

**Current utility aliases:**

| Full name | Alias | Service |
|---|---|---|
| `FileLoader` | `File` | `FileService` |
| `YamlLoader` | `Yaml` | (via `FileLoader`) |
| `JsonLoader` | `Json` | (via `FileLoader`) |
| `CsvLoader` | `Csv` | (via `FileLoader`) |
| `CsvDictLoader` | `CsvDict` | (via `FileLoader`) |
| `SqliteClient` | `Sqlite` | `SqliteService`, `FileService` |

## Example

```python
# *** imports

# ** core
import tomllib
from pathlib import Path

# ** app
from .file import FileLoader
from ..events.static import RaiseError
from .. import assets as a

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
        '''

        # Open, parse, transform, and return the TOML data.
        with self:
            try:
                data = tomllib.load(self.file)
            except tomllib.TOMLDecodeError as e:
                RaiseError.execute(
                    error_code=a.const.INVALID_TOML_FILE_ID,
                    message=str(e),
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
