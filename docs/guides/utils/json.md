**This conversation is part of the Tiferet Framework project.**  
**Repository:** https://github.com/greatstrength/tiferet – Tiferet Framework  

```markdown
# Utilities – JsonLoader (alias: Json)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 01, 2026  
**Version:** 2.0.0a1

## Overview

`JsonLoader` is a format-specific utility for loading and saving JSON files in Tiferet.  
It extends `FileLoader` (`tiferet/utils/file.py`), inheriting full context-manager lifecycle and file validation, while adding JSON parsing via Python's built-in `json` module.

Use `JsonLoader` (or its alias `Json`) directly when you need to read or write JSON files inside domain events, scripts, or tests. For domain-model persistence (features, errors, containers, etc.) use the corresponding repositories and injected services.

`JsonLoader` does **not** implement `ConfigurationService` — this is an intentional v2.0 design choice that keeps the utility as a pure infrastructure layer.

## When to Use JsonLoader vs. Injected Service

| Scenario                                        | Recommended Approach                | Reason                                                                 |
|-------------------------------------------------|-------------------------------------|------------------------------------------------------------------------|
| One-shot JSON read/write in an event or script  | `Json(path, mode='r').load()`       | Simple, no dependency injection required                               |
| Configurable / swappable config loading          | Inject `ConfigurationService`       | Allows mocking, swapping implementations, dependency management       |
| Domain object CRUD (features, errors, etc.)     | Inject corresponding `*Service`     | Keeps domain events decoupled from concrete file paths & formats       |
| Pre-flight JSON file validation                 | `JsonLoader.verify_json_file()`     | Static check for extension + existence before opening                  |
| Navigating nested JSON structures               | `JsonLoader.parse_json_path()`      | Static helper with dot-notation and array index support                |

## Basic Usage

```python
from tiferet.utils import Json, JsonLoader    # both names are exported

# Load a JSON file (returns a dict or list)
loader = Json('app/configs/settings.json', mode='r')
data = loader.load()

# Load with transformations
loader = JsonLoader(path='app/configs/feature_map.json', mode='r')
features = loader.load(
    start_node=lambda d: d['features'],        # navigate to a sub-key
    data_factory=lambda items: list(items),     # transform result
)

# Save data to JSON
saver = Json('output/result.json', mode='w')
saver.save({'status': 'complete', 'items': [1, 2, 3]})

# Navigate nested structures
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
name = JsonLoader.parse_json_path(data, 'users.1.name')  # returns 'Bob'
```

## Constructor Parameters

| Parameter   | Type               | Default    | Description                                                                 |
|-------------|--------------------|------------|-----------------------------------------------------------------------------|
| `path`      | `str \| pathlib.Path` | required | Path to the JSON file (automatically converted to `Path`)                   |
| `mode`      | `str`              | `'r'`      | File open mode (typically `'r'` for loading, `'w'` for saving)              |
| `encoding`  | `str`              | `'utf-8'`  | Text encoding (defaults to utf-8; JSON is always text-mode)                 |

## Methods

### `load(start_node, data_factory, **kwargs) -> Any`

Opens the file via the inherited context manager, parses JSON with `json.load`, and applies two optional transformation functions in sequence:

1. **`start_node`** — first transformation on the raw parsed data (e.g., navigate to a sub-key).
2. **`data_factory`** — final transformation on the result of `start_node` (e.g., cast to a list, build domain objects).

Unlike `YamlLoader`, empty JSON files are not coerced to `{}` — they will raise `JSON_FILE_LOAD_ERROR_ID` since empty content is not valid JSON.

### `save(data, data_path=None, **kwargs) -> None`

Serializes `data` with `json.dumps` (indent=2, sort_keys=False, ensure_ascii=False) and writes the result (with a trailing newline) to the file via the inherited context manager. The `data_path` parameter is reserved for future partial-update support and is currently ignored.

### `verify_json_file(loader, default_path=None)` (static)

Pre-flight validation that checks:
1. The file has a `.json` extension. If not, falls back to `default_path` if provided and valid; otherwise raises `INVALID_FILE_ID`.
2. The resolved file exists on disk; otherwise raises `JSON_FILE_NOT_FOUND_ID`.

### `parse_json_path(data, path) -> Any` (static)

Navigates nested JSON structures using dot-separated paths with array index support:
- Dict keys are resolved via `dict.get()`.
- List indices are resolved when the segment is numeric (e.g., `'users.0.name'`).
- Returns `None` if a key is missing (short-circuits).
- Raises `INVALID_JSON_PATH_ID` if navigation encounters a non-dict/non-list value.

## Error Handling

`JsonLoader` follows a layered error strategy:

- **`TiferetError` from `FileLoader`** (e.g., `FILE_NOT_FOUND_ID`, `INVALID_FILE_MODE_ID`) — propagated as-is, preserving the original error code.
- **`json.JSONDecodeError`** — caught and wrapped as `JSON_FILE_LOAD_ERROR_ID` with `error` and `path` kwargs.
- **All other exceptions** during load/save — caught and wrapped as `JSON_FILE_LOAD_ERROR_ID` or `JSON_FILE_SAVE_ERROR_ID` respectively.

All errors are raised via `RaiseError.execute()` with these constants (import via `from tiferet import a`):

- `a.const.JSON_FILE_NOT_FOUND_ID`
- `a.const.JSON_FILE_LOAD_ERROR_ID`
- `a.const.JSON_FILE_SAVE_ERROR_ID`
- `a.const.INVALID_JSON_PATH_ID`
- `a.const.INVALID_FILE_ID` (extension mismatch in `verify_json_file`)

Inherited from `FileLoader`:
- `a.const.FILE_NOT_FOUND_ID`
- `a.const.INVALID_FILE_MODE_ID`
- `a.const.INVALID_ENCODING_ID`
- `a.const.FILE_ALREADY_OPEN_ID`

## Example – Domain Event with Direct Usage

```python
from tiferet.events import DomainEvent, a
from tiferet.utils import Json

class LoadJsonConfig(DomainEvent):
    '''
    Load configuration from a JSON file.
    '''

    @DomainEvent.parameters_required(['config_path'])
    def execute(self, config_path: str, **kwargs) -> dict:
        '''
        :param config_path: Path to the JSON configuration file.
        :type config_path: str
        :return: The parsed configuration dict.
        :rtype: dict
        '''

        loader = Json(config_path, mode='r')
        return loader.load()
```

## Example – Pre-Flight Validation with Fallback

```python
from pathlib import Path
from tiferet.utils import Json, JsonLoader

# Validate a path before opening — with fallback
loader = JsonLoader(path='configs/app.conf', mode='r')
default = Path('configs/app.json')

JsonLoader.verify_json_file(loader, default_path=default)
# If 'app.conf' has an invalid extension but 'app.json' exists, validation passes.
```

## Example – Round-Trip Save and Reload

```python
from tiferet.utils import Json

# Save structured data
data = {'features': {'calc.add': {'name': 'Add Number'}}}
Json('output/features.json', mode='w').save(data)

# Reload and extract a sub-key
result = Json('output/features.json', mode='r').load(
    start_node=lambda d: d['features'],
)
assert 'calc.add' in result
```

## Example – Navigating Nested JSON with parse_json_path

```python
from tiferet.utils import JsonLoader

data = {
    'users': [
        {'name': 'Alice', 'roles': ['admin', 'editor']},
        {'name': 'Bob', 'roles': ['viewer']},
    ],
    'metadata': {'total': 2},
}

# Navigate to a nested dict value
total = JsonLoader.parse_json_path(data, 'metadata.total')  # 2

# Navigate through a list index
bob = JsonLoader.parse_json_path(data, 'users.1.name')  # 'Bob'

# Missing key returns None
missing = JsonLoader.parse_json_path(data, 'metadata.missing')  # None
```

## Testing Pattern

```python
# *** tests

# ** test: load_json_config_success
def test_load_json_config_success(tmp_path):
    config_file = tmp_path / 'app.json'
    config_file.write_text('{"name": "TestApp", "version": "1.0"}', encoding='utf-8')

    result = DomainEvent.handle(
        LoadJsonConfig,
        config_path=str(config_file),
    )

    assert result == {'name': 'TestApp', 'version': '1.0'}

# ** test: load_json_config_file_not_found
def test_load_json_config_file_not_found(tmp_path):
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            LoadJsonConfig,
            config_path=str(tmp_path / 'missing.json'),
        )

    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID
```

## Deviations from YamlLoader

- **No empty-file coercion**: `YamlLoader` returns `{}` for empty files; `JsonLoader` raises `JSON_FILE_LOAD_ERROR_ID` since empty content is not valid JSON per the specification.
- **Additional static method**: `parse_json_path` is unique to `JsonLoader`, providing dot-notation navigation with array index support — a pattern common in JSON tooling but not applicable to YAML's typical use cases in Tiferet.
- **New error constants**: `JSON_FILE_NOT_FOUND_ID` and `INVALID_JSON_PATH_ID` were added to `constants.py` beyond the TRD's original error codes (`JSON_FILE_LOAD_ERROR_ID`, `JSON_FILE_SAVE_ERROR_ID`), aligning with the `YamlLoader` pattern of having a dedicated file-not-found error for the `verify_*_file` static method.

## Related Documentation

- [docs/guides/utils/file.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/file.md) — FileLoader guide (parent class)
- [docs/guides/utils/yaml.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/yaml.md) — YamlLoader guide (sibling utility)
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
```
