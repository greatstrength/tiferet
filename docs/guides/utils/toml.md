# Utilities – TomlLoader (alias: Toml)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 22, 2026  
**Version:** 2.0.0

<a id="tomlloader"></a>
## Overview

`TomlLoader` is a format-specific utility for loading TOML files in Tiferet.  
It extends `FileLoader` (`tiferet/utils/file.py`), inheriting full context-manager lifecycle and file validation, while adding TOML parsing via Python's built-in `tomllib` module (Python 3.11+) with a `tomli` fallback for earlier versions.

Use `TomlLoader` (or its alias `Toml`) directly when you need to read TOML files inside domain events, scripts, or tests. For domain-model persistence (features, errors, containers, etc.) use the corresponding repositories and injected services.

**TOML is read-only in this utility** — the `tomllib` / `tomli` library only provides parsing, so there is no `save()` method. Use a third-party library (e.g., `tomlkit`) if you need to write TOML files.

`TomlLoader` implements no configuration contract — it declares only `FileLoader`. This is an intentional v2.0 design choice that keeps the utility as a pure infrastructure layer; format dispatch is owned by `ConfigurationRepository` instead.

## Ubiquitous Language

- **Read-only loader** — `TomlLoader`'s defining constraint: no `save()` method, since `tomllib`/`tomli` only parse.
- **`start_node`/`data_factory`** — the same two-stage transformation pattern shared with `YamlLoader`/`JsonLoader`.

## When to Use TomlLoader vs. Injected Service

| Scenario                                        | Recommended Approach                | Reason                                                                 |
|-------------------------------------------------|-------------------------------------|------------------------------------------------------------------------|
| One-shot TOML read in an event or script        | `Toml(path).load()`                | Simple, no dependency injection required                               |
| Domain object CRUD (features, errors, etc.)     | Inject corresponding `*Service`     | Keeps domain events decoupled from concrete file paths & formats       |
| Pre-flight TOML file validation                 | `TomlLoader.verify_toml_file()`     | Static check for extension + existence before opening                  |

## Basic Usage

```python
from tiferet.utils import Toml, TomlLoader    # both names are exported

# Load a TOML file (returns a dict)
loader = Toml('pyproject.toml')
data = loader.load()

# Load with transformations
loader = TomlLoader(path='pyproject.toml')
tool_config = loader.load(
    start_node=lambda d: d['tool']['tiferet'],    # navigate to a sub-key
    data_factory=lambda items: dict(items),        # transform result
)
```

## Constructor Parameters

| Parameter   | Type               | Default    | Description                                                                 |
|-------------|--------------------|------------|-----------------------------------------------------------------------------|
| `path`      | `str \| pathlib.Path` | required | Path to the TOML file (automatically converted to `Path`)                   |
| `mode`      | `str`              | `'rb'`     | File open mode (must be binary; `tomllib` requires binary streams)          |

Note: `encoding` is always `None` (binary mode). Additional kwargs are passed through to `FileLoader`.

## Methods

### `load(start_node, data_factory, **kwargs) -> Any`

Opens the file via the inherited context manager, parses TOML with `tomllib.load`, and applies two optional transformation functions in sequence:

1. **`start_node`** — first transformation on the raw parsed dict (e.g., navigate to a sub-key).
2. **`data_factory`** — final transformation on the result of `start_node` (e.g., cast to a list, build domain objects).

### `verify_toml_file(loader, default_path=None)` (static)

Pre-flight validation that checks:
1. The file has a `.toml` extension. If not, falls back to `default_path` if provided and valid; otherwise raises `INVALID_TOML_FILE_ID`.
2. The resolved file exists on disk; otherwise raises `TOML_FILE_NOT_FOUND_ID`.

## Error Handling

`TomlLoader` follows a layered error strategy:

- **`ServiceError` from `FileLoader`** (e.g., `FILE_NOT_FOUND_ID`, `INVALID_FILE_MODE_ID`) — re-raised as-is, preserving the original error code. This is why a missing file is never relabelled a parse failure.
- **`tomllib.TOMLDecodeError`** and other exceptions — caught and wrapped as `TOML_FILE_LOAD_ERROR_ID` with `error` and `path` kwargs.

Every failure is a `ServiceError` (`tiferet.interfaces.core`), which is deliberately
**not** a `TiferetError`: an infrastructural failure is not a domain outcome, so it
is never resolved through the error catalog or formatted into an API response. A
wrapped driver exception is preserved as `__cause__`, and each error carries the
provenance of the failing service (`module_path`, `class_name`, `target_method`).

Codes are hosted by the module that raises them (`tiferet.utils.toml`, with the
file-level codes in `tiferet.utils.file`), not by the error catalog:

```python
from tiferet.interfaces.core import ServiceError
from tiferet.utils.toml import (
    TOML_FILE_NOT_FOUND_ID,
    TOML_FILE_LOAD_ERROR_ID,
    INVALID_TOML_FILE_ID,    # extension mismatch in verify_toml_file
)
```

Inherited from `FileLoader` (`tiferet.utils.file`):
- `FILE_NOT_FOUND_ID`
- `INVALID_FILE_MODE_ID`
- `INVALID_ENCODING_ID`
- `FILE_ALREADY_OPEN_ID`

## Example – Domain Event with Direct Usage

```python
from tiferet.events import DomainEvent, a
from tiferet.utils import Toml

class LoadProjectConfig(DomainEvent):
    '''
    Load project configuration from a TOML file.
    '''

    @DomainEvent.parameters_required(['config_path'])
    def execute(self, config_path: str, **kwargs) -> dict:
        '''
        :param config_path: Path to the TOML configuration file.
        :type config_path: str
        :return: The parsed configuration dict.
        :rtype: dict
        '''

        loader = Toml(config_path)
        return loader.load()
```

## Example – Pre-Flight Validation with Fallback

```python
from pathlib import Path
from tiferet.utils import Toml, TomlLoader

# Validate a path before opening — with fallback
loader = TomlLoader(path='configs/app.conf')
default = Path('configs/app.toml')

TomlLoader.verify_toml_file(loader, default_path=default)
# If 'app.conf' has an invalid extension but 'app.toml' exists, validation passes.
```

## Example – Navigating Nested TOML Structures

```python
from tiferet.utils import Toml

# Load pyproject.toml and extract a specific section
deps = Toml('pyproject.toml').load(
    start_node=lambda d: d.get('project', {}).get('dependencies', []),
)
# deps == ['pydantic>=2.6', 'dependency-injector>=4.49.0', ...]
```

## Testing Pattern

```python
# *** tests

# ** test: load_project_config_success
def test_load_project_config_success(tmp_path):
    config_file = tmp_path / 'app.toml'
    config_file.write_text('[app]\nname = "TestApp"\nversion = "1.0"\n', encoding='utf-8')

    result = DomainEvent.handle(
        LoadProjectConfig,
        config_path=str(config_file),
    )

    assert result == {'app': {'name': 'TestApp', 'version': '1.0'}}

# ** test: load_project_config_file_not_found
def test_load_project_config_file_not_found(tmp_path):
    with pytest.raises(ServiceError) as exc_info:
        DomainEvent.handle(
            LoadProjectConfig,
            config_path=str(tmp_path / 'missing.toml'),
        )

    assert exc_info.value.error_code == FILE_NOT_FOUND_ID
```

## Deviations from YamlLoader / JsonLoader

- **Read-only**: `TomlLoader` has no `save()` method because `tomllib` / `tomli` only supports parsing. YAML and JSON loaders support both reading and writing.
- **Binary mode default**: The constructor defaults to `mode='rb'` and forces `encoding=None`, since `tomllib` requires binary streams. YAML and JSON default to text mode (`'r'`) with `encoding='utf-8'`.
- **Python version compatibility**: Uses `tomllib` (stdlib, Python 3.11+) with a `tomli` fallback for Python 3.10. YAML and JSON use `PyYAML` and `json` (stdlib) respectively, with no version-conditional imports.

## Boundaries

**Inside this domain:** read-only TOML parsing.
**Outside this domain:** the inherited file lifecycle and path/mode/encoding validation ([docs/guides/utils/file.md](file.md)); TOML writing (not supported by this utility — use a third-party library); TOML-file-to-domain-object mapping and format dispatch (`ConfigurationRepository` — [docs/guides/repos.md](../repos.md)).

## Related Documentation

- [docs/guides/utils/file.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/file.md) — FileLoader guide (parent class)
- [docs/guides/utils/yaml.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/yaml.md) — YamlLoader guide (sibling utility)
- [docs/guides/utils/json.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/json.md) — JsonLoader guide (sibling utility)
- [docs/guides/utils.md](../utils.md) — Utils layer strategy guide
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) — Full utilities architecture and style guide
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
