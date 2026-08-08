# Utilities – YamlLoader (alias: Yaml)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 01, 2026  
**Version:** 2.0.0

## Overview

`YamlLoader` is a format-specific utility for loading and saving YAML files in Tiferet.  
It extends `FileLoader` (`tiferet/utils/file.py`), inheriting full context-manager lifecycle and file validation, while adding YAML parsing via PyYAML's `safe_load` and serialization via `safe_dump`.

Use `YamlLoader` (or its alias `Yaml`) directly when you need to read or write YAML files inside domain events, scripts, or tests. For domain-model persistence (features, errors, containers, etc.) use the corresponding repositories and injected services.

`YamlLoader` implements no configuration contract — it declares only `FileLoader`. This is an intentional v2.0 design choice that keeps the utility as a pure infrastructure layer; format dispatch is owned by `ConfigurationRepository` instead.

## When to Use YamlLoader vs. Injected Service

| Scenario                                        | Recommended Approach                | Reason                                                                 |
|-------------------------------------------------|-------------------------------------|------------------------------------------------------------------------|
| One-shot YAML read/write in an event or script  | `Yaml(path, mode='r').load()`       | Simple, no dependency injection required                               |
| Domain object CRUD (features, errors, etc.)     | Inject corresponding `*Service`     | Keeps domain events decoupled from concrete file paths & formats       |
| Pre-flight YAML file validation                 | `YamlLoader.verify_yaml_file()`     | Static check for extension + existence before opening                  |

## Basic Usage

```python
from tiferet.utils import Yaml, YamlLoader    # both names are exported

# Load a YAML file (returns a dict)
loader = Yaml('app/configs/feature.yml', mode='r')
data = loader.load()

# Load with transformations
loader = YamlLoader(path='app/configs/feature.yml', mode='r')
features = loader.load(
    start_node=lambda d: d['features'],        # navigate to a sub-key
    data_factory=lambda items: list(items),     # transform result
)

# Save data to YAML
saver = Yaml('output/result.yaml', mode='w')
saver.save({'status': 'complete', 'items': [1, 2, 3]})
```

## Constructor Parameters

| Parameter   | Type               | Default    | Description                                                                 |
|-------------|--------------------|------------|-----------------------------------------------------------------------------|
| `path`      | `str \| pathlib.Path` | required | Path to the YAML file (automatically converted to `Path`)                   |
| `mode`      | `str`              | `'r'`      | File open mode (typically `'r'` for loading, `'w'` for saving)              |
| `encoding`  | `str`              | `'utf-8'`  | Text encoding (defaults to utf-8; YAML is always text-mode)                 |

## Methods

### `load(start_node, data_factory, **kwargs) -> Any`

Opens the file via the inherited context manager, parses YAML with `safe_load`, and applies two optional transformation functions in sequence:

1. **`start_node`** — first transformation on the raw parsed dict (e.g., navigate to a sub-key).
2. **`data_factory`** — final transformation on the result of `start_node` (e.g., cast to a list, build domain objects).

Empty files return `{}` (not `None`).

### `save(data, data_path=None, **kwargs) -> None`

Serializes `data` with `safe_dump` (sort_keys=False, allow_unicode=True) and writes the result to the file via the inherited context manager. The `data_path` parameter is reserved for future partial-update support and is currently ignored.

### `verify_yaml_file(loader, default_path=None)` (static)

Pre-flight validation that checks:
1. The file has a `.yaml` or `.yml` extension. If not, falls back to `default_path` if provided and valid; otherwise raises `INVALID_FILE_ID`.
2. The resolved file exists on disk; otherwise raises `YAML_FILE_NOT_FOUND_ID`.

## Error Handling

`YamlLoader` follows a layered error strategy. Every failure is a `ServiceError`
(`tiferet.interfaces.core`), which is deliberately **not** a `TiferetError`: an
infrastructural failure is not a domain outcome, so it is never resolved through
the error catalog or formatted into an API response.

- **`ServiceError` from `FileLoader`** (e.g., `FILE_NOT_FOUND_ID`, `INVALID_FILE_MODE_ID`) — re-raised as-is, preserving the original error code. This is why a missing file is never relabelled a parse failure.
- **`yaml.YAMLError`** — caught and wrapped as `YAML_FILE_LOAD_ERROR_ID`, with the parser exception preserved as `__cause__` so its line and column marks survive.
- **All other exceptions** during load/save — caught and wrapped as `YAML_FILE_LOAD_ERROR_ID` or `YAML_FILE_SAVE_ERROR_ID` respectively.

Codes are hosted by the module that raises them, not by the error catalog. Import
them from the utility module:

```python
from tiferet.interfaces.core import ServiceError
from tiferet.utils.yaml import (
    YAML_FILE_NOT_FOUND_ID,
    YAML_FILE_LOAD_ERROR_ID,
    YAML_FILE_SAVE_ERROR_ID,
)
from tiferet.utils.file import INVALID_FILE_ID    # extension mismatch in verify_yaml_file
```

Inherited from `FileLoader` (`tiferet.utils.file`):
- `FILE_NOT_FOUND_ID`
- `INVALID_FILE_MODE_ID`
- `INVALID_ENCODING_ID`
- `FILE_ALREADY_OPEN_ID`

Each error also carries the provenance of the failing service — `module_path`,
`class_name`, and `target_method` — naming the instance and the method that
failed.

## Example – Domain Event with Direct Usage

```python
from tiferet.events import DomainEvent, a
from tiferet.utils import Yaml

class LoadAppConfig(DomainEvent):
    '''
    Load application configuration from a YAML file.
    '''

    @DomainEvent.parameters_required(['config_path'])
    def execute(self, config_path: str, **kwargs) -> dict:
        '''
        :param config_path: Path to the YAML configuration file.
        :type config_path: str
        :return: The parsed configuration dict.
        :rtype: dict
        '''

        loader = Yaml(config_path, mode='r')
        return loader.load()
```

## Example – Pre-Flight Validation with Fallback

```python
from pathlib import Path
from tiferet.utils import Yaml, YamlLoader

# Validate a path before opening — with fallback
loader = YamlLoader(path='configs/app.conf', mode='r')
default = Path('configs/app.yaml')

YamlLoader.verify_yaml_file(loader, default_path=default)
# If 'app.conf' has an invalid extension but 'app.yaml' exists, validation passes.
```

## Example – Round-Trip Save and Reload

```python
from tiferet.utils import Yaml

# Save structured data
data = {'features': {'calc.add': {'name': 'Add Number'}}}
Yaml('output/features.yaml', mode='w').save(data)

# Reload and extract a sub-key
result = Yaml('output/features.yaml', mode='r').load(
    start_node=lambda d: d['features'],
)
assert 'calc.add' in result
```

## Testing Pattern

```python
# *** tests

# ** test: load_app_config_success
def test_load_app_config_success(tmp_path):
    config_file = tmp_path / 'app.yaml'
    config_file.write_text('name: TestApp\nversion: 1.0\n', encoding='utf-8')

    result = DomainEvent.handle(
        LoadAppConfig,
        config_path=str(config_file),
    )

    assert result == {'name': 'TestApp', 'version': 1.0}

# ** test: load_app_config_file_not_found
def test_load_app_config_file_not_found(tmp_path):
    with pytest.raises(ServiceError) as exc_info:
        DomainEvent.handle(
            LoadAppConfig,
            config_path=str(tmp_path / 'missing.yaml'),
        )

    assert exc_info.value.error_code == FILE_NOT_FOUND_ID
```

Note that a `ServiceError` is **not** skippable via a feature step's
`pass_on_error`, which passes on domain errors only. An event that wants to treat
a missing file as a no-op must catch the `ServiceError` and return `None` itself.

## Related Documentation

- [docs/guides/utils/file.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/file.md) — FileLoader guide (parent class)
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) — Full utilities architecture and style guide
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
