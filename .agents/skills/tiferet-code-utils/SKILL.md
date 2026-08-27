---
name: tiferet-code-utils
description: Apply utility conventions when adding or modifying infrastructure utilities in a Tiferet-family repo. Covers the FileLoader base, context manager protocol, static one-shot helpers, exported aliases, and computational vs physical infrastructure.
---

# Utilities Code Style – Tiferet

## When to use
- When adding a new utility class or modifying an existing one in `tiferet/utils/`.
- When implementing physical infrastructure (file I/O, database, network) or domain-specific computational infrastructure (algorithms, ML inference, transformations) as a cohesive mechanism, whether Service-backed or called directly.
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

- **Layer boundary — valid `# ** app` imports:** `interfaces` (to implement a Service contract; also the source of `ServiceError`); `mappers` (aggregates and transfer types); sibling utility modules (e.g. `.file` for `FileLoader`). Error codes are declared as local module constants (e.g. `tiferet/utils/toml.py::INVALID_TOML_FILE_ID`), not imported from `assets`. Never import from `domain`, `repos`, `di`, `contexts`, `blueprints`, or `events`.
- Implementing a **Service** contract from `tiferet/interfaces/` is **optional**. Add one when the capability is genuinely extensible and must be reachable through a declared feature step; a raw utility called directly by an event does not need a Service interface.
- A side-effect-free algorithm that does not provide a domain-specific cohesive mechanism belongs in `# *** functions`, not `utils`.
- A utility may supply a `Callable` to a mapper method as a valid semantic boundary. Mappers never import utilities, and repositories never supply operational callbacks to mappers or utilities.
- Use `ServiceError.raise_for(self, error_code, ...)` from `tiferet/interfaces/core.py` for all error paths — never raise raw exceptions from utilities. `ServiceError` derives its `module_path`/`class_name`/`target_method` provenance from the failing service instance and the calling frame.
- **Resource-owning utilities** implement the context manager protocol: `__enter__` (open/connect) and `__exit__` (close/disconnect; commit or rollback on error).
- **Static one-shot helpers** on utilities (e.g. `CsvLoader.load_rows(path)`) provide a convenience API that opens, reads, closes in a single call.
- Export from `tiferet/utils/__init__.py` with both the full class name and a short alias (e.g. `FileLoader` / `File`, `YamlLoader` / `Yaml`).
- Stateless computational utilities (algorithms, inference) do NOT need context managers.

**Current utility aliases:**

| Full name | Alias | Service contract |
|---|---|---|
| `FileLoader` | `File` | `FileService` |
| `YamlLoader` | `Yaml` | (via `FileLoader`) |
| `JsonLoader` | `Json` | (via `FileLoader`) |
| `TomlLoader` | `Toml` | (via `FileLoader`) |
| `CsvLoader` | `Csv` | (via `FileLoader`) |
| `CsvDictLoader` | `CsvDict` | (via `FileLoader`) |
| `SqliteClient` | `Sqlite` | `SqliteService`, `FileService` |
| `LoggingMiddleware` | — | `MiddlewareService` |
| `TimingMiddleware` | — | `MiddlewareService` |
| `CacheMiddleware` | — | `MiddlewareService` |

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
        '''

        # Open, parse, transform, and return the TOML data.
        with self:
            try:
                data = tomllib.load(self.file)
            except tomllib.TOMLDecodeError as e:
                ServiceError.raise_for(
                    self,
                    INVALID_TOML_FILE_ID,
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

## Docstrings & guides

- **Docstrings & guides:** Utility class docstrings open with a 1–2 sentence vision-tier value statement, linked via `# >> see: @guides/utils.md#<anchor>` (strategy) or `@guides/utils/<module>.md#<anchor>` (cookbook detail) to the corresponding guide. See `tiferet-guide-docs` for the complete convention.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md
