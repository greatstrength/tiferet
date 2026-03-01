**This conversation is part of the Tiferet Framework project.**  
**Repository:** https://github.com/greatstrength/tiferet – Tiferet Framework  

```markdown
# Utilities – CsvLoader (alias: Csv) & CsvDictLoader (alias: CsvDict)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 01, 2026  
**Version:** 2.0.0a1

## Overview

`CsvLoader` and `CsvDictLoader` are format-specific utilities for reading and writing CSV files in Tiferet.  
Both extend `FileLoader` (`tiferet/utils/file.py`), inheriting full context-manager lifecycle and file validation, while adding CSV parsing via Python's built-in `csv` module.

`CsvLoader` handles list-based rows (`csv.reader` / `csv.writer`), while `CsvDictLoader` extends `CsvLoader` with dict-based rows (`csv.DictReader` / `csv.DictWriter`) and fieldnames control.

Use `CsvLoader` (or its alias `Csv`) for positional row data and `CsvDictLoader` (or its alias `CsvDict`) for header-based dict data. For domain-model persistence (features, errors, containers, etc.) use the corresponding repositories and injected services.

Neither class implements `ConfigurationService` — this is an intentional v2.0 design choice that keeps the utilities as a pure infrastructure layer.

## When to Use CsvLoader vs. CsvDictLoader vs. Injected Service

| Scenario                                        | Recommended Approach                | Reason                                                                 |
|-------------------------------------------------|-------------------------------------|------------------------------------------------------------------------|
| Positional CSV data (no header)                 | `Csv(path, mode='r').read_all()`    | Simple list-based rows, no header parsing                              |
| Header-based CSV data                           | `CsvDict(path).read_all()`         | Dict-based rows with automatic header inference                        |
| One-shot bulk load                              | `CsvLoader.load_rows(path)`        | Static helper, no context manager needed                               |
| One-shot bulk save                              | `CsvLoader.save_rows(path, data)`  | Static helper, supports both list and dict datasets                    |
| Configurable / swappable config loading          | Inject `ConfigurationService`       | Allows mocking, swapping implementations, dependency management       |
| Domain object CRUD (features, errors, etc.)     | Inject corresponding `*Service`     | Keeps domain events decoupled from concrete file paths & formats       |

## CsvLoader – Basic Usage

```python
from tiferet.utils import Csv, CsvLoader    # both names are exported

# Read all rows (including header)
with Csv('data/records.csv', mode='r') as loader:
    rows = loader.read_all()

# Read rows one at a time
with CsvLoader(path='data/records.csv', mode='r') as loader:
    header = loader.read_row()
    first_data = loader.read_row()

# Write rows to a new file
with Csv('output/results.csv', mode='w') as loader:
    loader.write_row(['name', 'score'])
    loader.write_all([['Alice', '95'], ['Bob', '88']])

# Static helpers
rows = CsvLoader.load_rows('data/records.csv')
CsvLoader.save_rows('output/new.csv', [['a', 'b'], ['1', '2']])
CsvLoader.append_row('output/new.csv', ['3', '4'])

# Generator with line-range filtering
with Csv('data/large.csv', mode='r') as loader:
    for row in loader.yield_rows(start_line=10, end_line=20):
        process(row)
```

## CsvDictLoader – Basic Usage

```python
from tiferet.utils import CsvDict, CsvDictLoader    # both names are exported

# Read all rows as dicts (header inferred from first row)
with CsvDict('data/records.csv', mode='r') as loader:
    records = loader.read_all()
    # [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]

# Write dict rows with header
with CsvDictLoader(path='output/report.csv', mode='w', fieldnames=['name', 'score']) as loader:
    loader.write_header()
    loader.write_all([{'name': 'Alice', 'score': '95'}, {'name': 'Bob', 'score': '88'}])

# Static helpers
records = CsvDictLoader.load_rows('data/records.csv')
CsvDictLoader.save_rows('output/new.csv', records, fieldnames=['name', 'age'])
```

## Constructor Parameters

### CsvLoader

| Parameter   | Type               | Default    | Description                                                                 |
|-------------|--------------------|------------|-----------------------------------------------------------------------------|
| `path`      | `str \| pathlib.Path` | required | Path to the CSV file (automatically converted to `Path`)                    |
| `mode`      | `str`              | `'r'`      | File open mode (`'r'`, `'w'`, `'a'`, `'r+'`, `'w+'`, `'a+'`)               |
| `encoding`  | `str`              | `'utf-8'`  | Text encoding                                                               |

### CsvDictLoader (extends CsvLoader)

| Parameter    | Type                    | Default    | Description                                                               |
|--------------|-------------------------|------------|---------------------------------------------------------------------------|
| `path`       | `str \| pathlib.Path`   | required   | Path to the CSV file                                                      |
| `mode`       | `str`                   | `'r'`      | File open mode                                                            |
| `encoding`   | `str`                   | `'utf-8'`  | Text encoding                                                             |
| `fieldnames` | `Optional[List[str]]`   | `None`     | Field names for DictReader/DictWriter (inferred from header if `None`)    |

## CsvLoader Methods

### `read_row() -> List[str]`
Read the next row. Returns an empty list at EOF.

### `read_all() -> List[List[str]]`
Read all remaining rows.

### `write_row(row: List[Any])`
Write a single row.

### `write_all(rows: Iterable[List[Any]])`
Write multiple rows.

### `yield_rows(start_line=None, end_line=None) -> Generator`
Yield rows with optional 1-based line-range filtering. Efficient for large files — rows are not materialized into memory.

### `load_rows(csv_file, **kwargs) -> List[List[str]]` (static)
One-shot load of all rows from a CSV file.

### `save_rows(csv_file, dataset, mode='w', **kwargs)` (static)
One-shot save of rows. Supports both list and dict datasets (dict mode requires `fieldnames` in kwargs, with optional `include_header` defaulting to `True`).

### `append_row(csv_file, row)` (static)
Append a single row to an existing CSV file.

## CsvDictLoader Methods

### `read_row() -> Dict[str, Any]`
Read the next row as a dict. Returns an empty dict at EOF.

### `read_all() -> List[Dict[str, Any]]`
Read all remaining rows as dicts.

### `write_row(row: Dict[str, Any])`
Write a single dict row.

### `write_all(rows: Iterable[Dict[str, Any]])`
Write multiple dict rows.

### `write_header()`
Write the header row (using `fieldnames`).

### `yield_rows(start_line=None, end_line=None) -> Generator`
Yield dict rows with optional 1-based line-range filtering (header row excluded from counting).

### `load_rows(csv_file, fieldnames=None, **kwargs) -> List[Dict[str, Any]]` (static)
One-shot load of all rows as dicts. If `fieldnames` is `None`, the first row is used as the header.

### `save_rows(csv_file, dataset, fieldnames=None, mode='w', include_header=True, **kwargs)` (static)
One-shot save of dict rows. `fieldnames` is required. Set `include_header=False` to omit the header row.

## Context Manager Behavior

Unlike `FileLoader` (which returns the file stream from `__enter__`), `CsvLoader` and `CsvDictLoader` override `__enter__` to return the **loader instance**, enabling access to reader/writer methods within `with` blocks:

```python
with CsvLoader(path='data.csv', mode='r') as loader:
    rows = loader.read_all()    # access instance methods
```

On `__exit__`, the reader, writer, and file stream are all reset to `None`.

## Error Handling

CSV utilities follow a layered error strategy:

- **`TiferetError` from `FileLoader`** (e.g., `FILE_NOT_FOUND_ID`, `INVALID_FILE_MODE_ID`) — propagated as-is.
- **`CSV_INVALID_READ_MODE_ID`** — raised when `build_reader()` is called in a non-readable mode.
- **`CSV_INVALID_WRITE_MODE_ID`** — raised when `build_writer()` is called in a non-writable mode.
- **`CSV_FIELDNAMES_REQUIRED_ID`** — raised when writing dicts without providing `fieldnames`.

All errors are raised via `RaiseError.execute()` with constants from `tiferet.assets.constants`:

- `a.const.CSV_INVALID_READ_MODE_ID`
- `a.const.CSV_INVALID_WRITE_MODE_ID`
- `a.const.CSV_FIELDNAMES_REQUIRED_ID`
- `a.const.CSV_DICT_NO_HEADER_ID`

Inherited from `FileLoader`:
- `a.const.FILE_NOT_FOUND_ID`
- `a.const.INVALID_FILE_MODE_ID`
- `a.const.INVALID_ENCODING_ID`
- `a.const.FILE_ALREADY_OPEN_ID`

## Example – Domain Event with Direct Usage

```python
from tiferet.events import DomainEvent, a
from tiferet.utils import Csv, CsvDict

class ImportCsvRecords(DomainEvent):
    '''
    Import records from a CSV file as dicts.
    '''

    @DomainEvent.parameters_required(['csv_path'])
    def execute(self, csv_path: str, **kwargs) -> list:
        '''
        :param csv_path: Path to the CSV file.
        :type csv_path: str
        :return: A list of record dicts.
        :rtype: list
        '''

        return CsvDict.load_rows(csv_path)
```

## Example – Round-Trip Save and Reload

```python
from tiferet.utils import Csv, CsvDict

# Save list-based data
CsvLoader.save_rows('output/scores.csv', [['name', 'score'], ['Alice', '95'], ['Bob', '88']])

# Reload as dicts
records = CsvDict.load_rows('output/scores.csv')
assert records[0] == {'name': 'Alice', 'score': '95'}
```

## Example – Appending and Streaming

```python
from tiferet.utils import Csv

# Append a row to an existing file
Csv.append_row('output/log.csv', ['2026-03-01', 'event_123', 'completed'])

# Stream large files with line-range filtering
with Csv('data/large_dataset.csv', mode='r') as loader:
    for row in loader.yield_rows(start_line=1000, end_line=2000):
        process(row)
```

## Testing Pattern

```python
# *** tests

# ** test: import_csv_records_success
def test_import_csv_records_success(tmp_path):
    csv_file = tmp_path / 'records.csv'
    csv_file.write_text('name,age\nAlice,30\nBob,25\n', encoding='utf-8')

    result = DomainEvent.handle(
        ImportCsvRecords,
        csv_path=str(csv_file),
    )

    assert len(result) == 2
    assert result[0] == {'name': 'Alice', 'age': '30'}

# ** test: import_csv_records_file_not_found
def test_import_csv_records_file_not_found(tmp_path):
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ImportCsvRecords,
            csv_path=str(tmp_path / 'missing.csv'),
        )

    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID
```

## Deviations from YamlLoader / JsonLoader

- **Context manager returns loader instance**: `CsvLoader.__enter__` returns `self` (not the file stream) to enable access to `read_row()`, `write_row()`, and other instance methods within `with` blocks. `YamlLoader` and `JsonLoader` return the file stream via the inherited `FileLoader.__enter__`.
- **Lazy reader/writer initialization**: CSV reader and writer objects are created on first use via `build_reader()` / `build_writer()`, not at construction time. This enables opening a file in `r+` mode and using both reader and writer.
- **Two-class design**: `CsvDictLoader` extends `CsvLoader` for dict-based operations, whereas YAML and JSON each have a single class. This reflects CSV's dual nature (positional vs. header-based).
- **Rich static helpers**: `load_rows`, `save_rows`, `append_row` provide convenience without requiring context management. `save_rows` on `CsvLoader` auto-detects dict datasets and switches to `DictWriter` when `fieldnames` is provided.
- **`newline=''` default**: CSV files are opened with `newline=''` per Python `csv` module requirements, ensuring correct newline handling across platforms.
- **New CSV-specific error constants**: `CSV_INVALID_READ_MODE_ID`, `CSV_INVALID_WRITE_MODE_ID`, `CSV_FIELDNAMES_REQUIRED_ID`, `CSV_DICT_NO_HEADER_ID` were added to `constants.py` for CSV-specific guard conditions.
- **Documentation guide**: A `docs/guides/utils/csv.md` guide was created alongside the implementation, following the pattern of the existing `yaml.md` and `json.md` guides. This was not in the original TRD scope but adds consistency to the documentation suite.

## Related Documentation

- [docs/guides/utils/file.md](https://github.com/greatstrength/tiferet/blob/v2.0a1-release/docs/guides/utils/file.md) — FileLoader guide (parent class)
- [docs/guides/utils/yaml.md](https://github.com/greatstrength/tiferet/blob/v2.0a1-release/docs/guides/utils/yaml.md) — YamlLoader guide (sibling utility)
- [docs/guides/utils/json.md](https://github.com/greatstrength/tiferet/blob/v2.0a1-release/docs/guides/utils/json.md) — JsonLoader guide (sibling utility)
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/v2.0a1-release/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/v2.0a1-release/docs/core/events.md) — Domain event patterns & testing
```
