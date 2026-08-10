# Utilities – FileLoader (alias: File)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 01, 2026  
**Version:** 2.0.0

<a id="fileloader"></a>
## Overview

`FileLoader` is the foundational utility for all file-based operations in Tiferet.  
It implements the `FileService` interface (`tiferet/interfaces/file.py`) and provides safe, validated file stream handling with full context-manager support.

All format-specific loaders (`YamlLoader`, `JsonLoader`, `CsvLoader`, etc.) inherit from `FileLoader` and override behavior such as file extension verification and content parsing/dumping.

Use `FileLoader` (or its alias `File`) directly when you need low-level file I/O inside domain events, scripts, or tests. For domain-model persistence use the corresponding repositories and injected services.

## Ubiquitous Language

- **Loader** — a `FileLoader` subclass exposing static, one-shot helpers for a specific file format.
- **Path/encoding validation** — the shared existence/mode/encoding checks `FileLoader` performs before any format-specific parsing runs, so every subclass gets `FILE_NOT_FOUND`/`INVALID_ENCODING` behavior for free.

## When to Use FileLoader vs. Injected FileService

| Scenario                              | Recommended Approach              | Reason                                                                 |
|---------------------------------------|-----------------------------------|------------------------------------------------------------------------|
| One-shot file read/write in an event  | `with FileLoader(...) as f:`      | Simple, no dependency injection required                               |
| Configurable / swappable file access  | Inject `FileService`              | Allows mocking, swapping implementations, dependency management       |
| YAML/JSON/CSV structured persistence  | Use `Yaml`, `Json`, `Csv` aliases | They inherit from `FileLoader` + add format-specific parsing           |
| Domain object CRUD                    | Inject corresponding `*Service`   | Keeps domain events decoupled from concrete file paths & formats       |

## Basic Usage

```python
from tiferet.utils import File, FileLoader    # both names are exported

# Text read (utf-8 default)
with File('data/input.txt', mode='r') as f:
    content = f.read()

# Text write with explicit encoding
with FileLoader(path='data/log.txt', mode='w', encoding='utf-8') as f:
    f.write("Operation completed\n")

# Binary read (no encoding needed)
with File('assets/logo.png', 'rb') as f:
    raw_bytes = f.read(1024)

# Append mode
with File('data/audit.log', 'a', encoding='utf-8') as f:
    f.write("User logged in\n")
```

## Constructor Parameters

| Parameter   | Type               | Default    | Description                                                                 |
|-------------|--------------------|------------|-----------------------------------------------------------------------------|
| `path`      | `str \| pathlib.Path` | required | File path (automatically converted to `Path`)                               |
| `mode`      | `str`              | `'r'`      | Standard file modes: `r w a x r+ w+ a+ rb wb ab xb rb+ wb+ ab+`            |
| `encoding`  | `str \| None`      | `'utf-8'` (text modes) | Text encoding; must be `None` for binary modes                             |
| `newline`   | `str \| None`      | `None`     | Passed directly to built-in `open()`                                        |

## Context Manager Behavior

`FileLoader` implements `__enter__` and `__exit__`:

- File is opened on `__enter__`
- File is properly closed on `__exit__` (even on exceptions)
- Reopening an already-open loader raises `ServiceError(FILE_ALREADY_OPEN_ID)`

## Common Error Codes

Every failure is a `ServiceError` (`tiferet.interfaces.core`), raised via
`ServiceError.raise_for`. It is deliberately **not** a `TiferetError`: an
infrastructural failure is not a domain outcome, so it is never resolved through
the error catalog or formatted into an API response, and it is not skippable via a
feature step's `pass_on_error`.

Codes are hosted by `tiferet/utils/file.py` — the module that raises them — rather
than by the error catalog:

```python
from tiferet.interfaces.core import ServiceError
from tiferet.utils.file import (
    FILE_NOT_FOUND_ID,
    FILE_ALREADY_OPEN_ID,
    INVALID_FILE_ID,
    INVALID_FILE_MODE_ID,
    INVALID_ENCODING_ID,
)
```

`INVALID_FILE_ID` is hosted here because both `YamlLoader` and `JsonLoader` raise it
for their extension checks and both already import from this module.

Each error carries the provenance of the failing service — `module_path`,
`class_name`, and `target_method` — so it names the loader subclass and the method
that failed.

## Example – Domain Event with Direct Usage

```python
from tiferet.events import DomainEvent, a
from tiferet.utils import File

class CountFileLines(DomainEvent):
    '''
    Count non-empty lines in a text file.
    '''

    @DomainEvent.parameters_required(['file_path'])
    def execute(self, file_path: str, encoding: str = 'utf-8', **kwargs) -> int:
        '''
        :return: Number of non-empty lines
        :rtype: int
        '''

        count = 0
        with File(file_path, mode='r', encoding=encoding) as f:
            for line in f:
                if line.strip():
                    count += 1

        return count
```

## When to Prefer Injected Service (example)

```python
class GenerateDailyReport(DomainEvent):

    def __init__(self, report_service: ReportService):
        self.report_service = report_service

    @DomainEvent.parameters_required(['report_id', 'output_path'])
    def execute(self, report_id: str, output_path: str, **kwargs) -> str:
        report = self.report_service.get_report(report_id)
        self.verify(report is not None,
                    a.const.REPORT_NOT_FOUND_ID,
                    report_id=report_id)

        with File(output_path, 'w', encoding='utf-8') as f:
            f.write(report.to_markdown())

        return output_path
```

## Testing Pattern

```python
# *** tests

# ** test: count_file_lines_success
def test_count_file_lines_success(tmp_path):
    test_file = tmp_path / 'sample.txt'
    test_file.write_text('line one\n\nline three\n', encoding='utf-8')

    result = DomainEvent.handle(
        CountFileLines,
        file_path=str(test_file)
    )

    assert result == 2   # only non-empty lines
```

## Boundaries

**Inside this domain:** low-level file stream lifecycle (open/close, path/mode/encoding validation) and the `FileService` contract implementation.
**Outside this domain:** format-specific parsing/serialization (`YamlLoader`, `JsonLoader`, `CsvLoader`, `TomlLoader` — their own guides); domain-object persistence (`ConfigurationRepository` — [docs/guides/repos.md](../repos.md)); the broader physical-vs-computational utility split ([docs/guides/utils.md](../utils.md)).

## Related Documentation

- [docs/guides/utils.md](../utils.md) — Utils layer strategy guide (physical vs. computational families)
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) — Full utilities architecture and style guide
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — `FileService` contract definition
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
