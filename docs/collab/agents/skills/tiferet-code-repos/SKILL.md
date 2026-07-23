---
name: tiferet-code-repos
description: Apply repository conventions when adding or modifying configuration repositories in a Tiferet-family repo. Covers ConfigurationRepository base, naming, read/write patterns, DI registration, and integration testing.
---

# Repositories Code Style – Tiferet

## When to use
- When adding a new repository or modifying an existing one in `tiferet/repos/`.
- When implementing persistence for a domain concept backed by YAML or JSON config files.
- Do NOT export repositories from `__init__.py` — they are DI-resolved at runtime.

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** repos              ← construct group for this skill
# *** exports            ← __init__.py only
```

Repo-specific labels:
```
# *** repos                            ← artifact section
# ** repo: <snake_case_name>           ← artifact
# * attribute: <name>                  ← artifact member: instance attributes (inherited; rarely redeclared)
# * init                               ← artifact member: constructor
# * method: <name>                     ← artifact member: Service interface implementation
```

## Key conventions

**Layer boundary — valid `# ** app` imports:** `interfaces` (the Service to implement), `mappers` (transfer objects and aggregates), `utils` (loader utilities), `events` (`RaiseError`, `a`). Never import from `domain` directly (use `mappers` instead), `di`, `contexts`, or `blueprints`.

**Naming:**
- `<Domain>ConfigRepository` — for YAML/JSON config-backed repos (e.g. `ErrorConfigRepository`, `FeatureConfigRepository`). Both formats are handled by `ConfigurationRepository`.
- `<Domain>SqliteRepository` — for SQLite-backed repos (e.g. `OrderSqliteRepository`). The suffix reflects the backing connector (`SqliteClient`) rather than the file format.

**Class declaration:** Extend the Service interface **and** `ConfigurationRepository`:
```python
class ErrorConfigRepository(ErrorService, ConfigurationRepository):
```

**Constructor:** Accept `<domain>_config: str` and forward to the base:
```python
def __init__(self, error_config: str, encoding: str = 'utf-8') -> None:
    ConfigurationRepository.__init__(self, config_file=error_config, encoding=encoding)
```

**`ConfigurationRepository` base** (inherited from `tiferet/repos/core.py`):
- `config_file`, `encoding`, `default_role` (fixed to `'to_data'`)
- `_load(start_node=..., data_factory=...)` — format-dispatched read (YAML or JSON based on file extension)
- `_save(data)` — format-dispatched write

**Read pattern** (`exists`, `get`, `list`): use `_load` with a `start_node` lambda:
```python
data = self._load(start_node=lambda d: d.get('errors', {}))
return ErrorConfigObject.model_validate({**data[id], 'id': id}).map()
```

**Write pattern** (`save`): serialize → load full file → update section → save:
```python
error_data = ErrorConfigObject.from_model(error)
full_data = self._load()
full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)
self._save(full_data)
```

**Delete pattern**: always idempotent — use `.pop(id, None)`:
```python
full_data.get('errors', {}).pop(id, None)
self._save(full_data)
```

**Testing:** Integration tests only — use `tmp_path` fixtures with real temp YAML/JSON files. Use `# ** test_int: <name>` labels for integration test cases.

## Example

```python
"""Tiferet Error Configuration Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from ..interfaces import ErrorService
from ..mappers import ErrorAggregate, ErrorConfigObject
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

        :param error_config: Path to the configuration file.
        :type error_config: str
        :param encoding: File encoding.
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

        # Load the errors mapping.
        errors_data = self._load(start_node=lambda data: data.get('errors', {}))

        # Return whether the id is present.
        return id in errors_data

    # * method: get
    def get(self, id: str) -> Optional[ErrorAggregate]:
        '''
        Retrieve an Error by ID.

        :param id: The error identifier.
        :type id: str
        :return: The ErrorAggregate, or None if not found.
        :rtype: Optional[ErrorAggregate]
        '''

        # Load the specific error entry.
        error_data = self._load(
            start_node=lambda data: data.get('errors', {}).get(id)
        )

        # Return None if not found.
        if not error_data:
            return None

        # Map to an aggregate and return.
        return ErrorConfigObject.model_validate({**error_data, 'id': id}).map()

    # * method: save
    def save(self, error: ErrorAggregate) -> None:
        '''
        Persist an Error aggregate to the configuration file.

        :param error: The error aggregate to persist.
        :type error: ErrorAggregate
        '''

        # Convert the aggregate to configuration data.
        error_data = ErrorConfigObject.from_model(error)

        # Load the full configuration file.
        full_data = self._load()

        # Insert or update the error entry.
        full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)

        # Persist the updated configuration.
        self._save(full_data)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/repos.md
