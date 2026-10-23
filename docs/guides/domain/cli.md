# Domain - CLI: CliRecord, CliTable, CliOutputLines, CliOutputRecord, CliRecordList, CliArgument, and CliCommand

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

The CLI domain defines two related concerns: the structural configuration for command-line interface commands, and the typed output-rendering models a CLI response is displayed through. `CliCommand` is the **terminal-to-feature bridge**: it has a composite identifier (`group_key.key`) that maps directly to a feature ID in `feature.yml`, enabling seamless execution of domain features via `argparse`-driven command-line input. `CliRecord`/`CliOutputRecord`/`CliRecordList` are a separate, independent concern — rendering a raw feature result as vertical or tabular stdout text — that has no relationship to the command/argument configuration shape.

- `CliRecord` — a typed atomic record unit both output models are built from.
- `CliTable` - the aligned table a `CliRecordList` computes: keys, widths, header, separator, and rows.
- `CliOutputLines` - the indented `attribute: value` lines a `CliOutputRecord` computes: indent, key width, and lines.
- `CliOutputRecord` — renders a single `CliRecord` as a vertical attribute-value list.
- `CliRecordList` — renders multiple `CliRecord` rows as an aligned table.
- `CliArgument` — represents a single command-line argument or flag, mapping to `argparse.add_argument()` parameters.
- `CliCommand` — represents a CLI command with a composite ID (derived by a `@model_validator`) and a `has_argument()` query method.

All seven domain objects are **immutable value objects**: they carry no mutation methods (the two output-rendering classes carry a pure `format_output()` query instead) and expose only read-only queries. `CliTable` and `CliOutputLines` are the computed pieces behind those two queries; each `format_output()` is only the newline join of its own noun. All state changes to `CliCommand`/`CliArgument` (adding/removing arguments, renaming commands) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/cli.py`
**Vision:** See the `CliCommand` and `CliRecordList` class docstrings in `tiferet/domain/cli.py` for the value statements this guide distills.

## Ubiquitous Language

- **Terminal-to-feature bridge** — the design pattern where `CliCommand.id` maps 1:1 to a feature ID, so a CLI command is a thin entry point rather than its own business-logic surface.
- **Record** — one `CliRecord`: an ordered, string-coerced attribute-value mapping extracted from a raw domain result, independent of how it is ultimately rendered.
- **Vertical output** - `CliOutputRecord`'s rendering shape: one `attribute: value` line per field, for a single record. The lines are a `CliOutputLines`, not a one-row table.
- **Tabular output** - `CliRecordList`'s rendering shape: an aligned, header-plus-rows table across multiple records. The table is a `CliTable`.
- **Argument dest** — the argparse destination key `CliArgument.get_dest()` derives from `name_or_flags`, mirroring argparse's own long-flag-wins derivation.

## Domain Objects

### CliRecord

The atomic unit both output models are built from: an ordered mapping of attribute names to string values, with all values coerced to `str` so column/line output never needs a type check.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="clirecord-fields"></a>`fields` | `Dict[str, str]` | No | `{}` | Ordered attribute-to-string-value pairs extracted from the raw result. |

No methods — `CliRecord` is a pure data container; both rendering classes below own the formatting behavior.

### CliTable

The aligned table a `CliRecordList` renders, named rather than discarded: the ordered column keys, the per-column widths, the header and separator rows, and one row string per record. It stores no records, and it has no `format_output()` or other join method. Only `CliRecordList` builds one.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="clitable-keys"></a>`keys` | `List[str]` | Yes | - | The column keys, in encounter order across all records. Not sorted. |
| <a id="clitable-widths"></a>`widths` | `Dict[str, int]` | Yes | - | The width of each column, the max of the key and every value. `list(widths)` equals `keys`. |
| <a id="clitable-header"></a>`header` | `str` | Yes | - | Each key left-justified to its width, joined on two spaces. |
| <a id="clitable-separator"></a>`separator` | `str` | Yes | - | One dash run per column width, joined on two spaces. |
| <a id="clitable-rows"></a>`rows` | `List[str]` | Yes | - | One left-justified row per record, in record order. A missing key and a present `''` render the same empty cell. |

#### Methods

<a id="clitable-from-records"></a>
**`from_records(records: List[CliRecord]) -> CliTable | None`** (classmethod)

The only list width and row builder. Returns `None` when `records` is empty or every record has no fields; it never returns an empty table, since joining an empty header and separator would be `'\n'`, not `''`.

```python
table = CliTable.from_records([
    CliRecord(fields={'id': '1', 'name': 'A'}),
    CliRecord(fields={'id': '2', 'extra': 'Z'}),
])
# table.keys == ['id', 'name', 'extra']
# table.widths == {'id': 2, 'name': 4, 'extra': 5}
# table.header == 'id  name  extra'
# table.rows == ['1   A          ', '2         Z    ']
```

### CliOutputLines

The indented `attribute: value` lines a `CliOutputRecord` renders: the indent, the width of the widest attribute name, and one line per field. These are vertical lines, not table rows: there is no header, separator, or `widths`, and no `format_output()`. A one-record result is never rendered as a one-row `CliTable`.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="clioutputlines-indent"></a>`indent` | `int` | Yes | - | The number of leading spaces before each line. |
| <a id="clioutputlines-key-width"></a>`key_width` | `int` | Yes | - | The width of the widest attribute name; every name is padded to it. |
| <a id="clioutputlines-lines"></a>`lines` | `List[str]` | Yes | - | One `<indent><attribute padded to key_width>: <value>` line per field, in field order. |

#### Methods

<a id="clioutputlines-from-record"></a>
**`from_record(record: CliRecord, indent: int = 2) -> CliOutputLines | None`** (classmethod)

Builds the lines for one record. Returns `None` when the record has no fields.

```python
lines = CliOutputLines.from_record(CliRecord(fields={'id': '42', 'name': 'foo bar'}))
# lines.key_width == 4
# lines.lines == ['  id  : 42', '  name: foo bar']
```

### CliOutputRecord

Wraps one `CliRecord` and renders it as a top-down attribute-value list, with attribute names left-padded to a consistent width.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="clioutputrecord-record"></a>`record` | `CliRecord` | Yes | — | The typed record to display. |

#### Methods

<a id="clioutputrecord-output-lines"></a>
**`output_lines(indent: int = 2) -> CliOutputLines | None`**

Returns `CliOutputLines.from_record(self.record, indent=indent)`. It does not build a `CliTable`, and `CliOutputRecord` has no `table()` method.

<a id="clioutputrecord-format-output"></a>
**`format_output(indent: int = 2) -> str`**

Renders one `<indent><attribute padded to max width>: <value>` line per field: the newline join of `output_lines(indent).lines`, with no header, no separator, and no trailing newline. Returns an empty string when the record has no fields.

```python
CliOutputRecord(record=CliRecord(fields={'id': 'calc.add', 'name': 'Add'})).format_output()
# '  id  : calc.add\n  name: Add'
```

### CliRecordList

Wraps a list of `CliRecord` rows and renders them as an aligned table: a header row derived from the union of all field keys (in encounter order), a separator row, then one row per record, with each column aligned to its widest value.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="clirecordlist-records"></a>`records` | `List[CliRecord]` | No | `[]` | The typed record rows; each `CliRecord` represents one table row. |

#### Methods

<a id="clirecordlist-table"></a>
**`table() -> CliTable | None`**

Returns `CliTable.from_records(self.records)`. The table is computed on demand, not stored, so construction is unchanged.

<a id="clirecordlist-format-output"></a>
**`format_output() -> str`**

Renders the aligned table described above: the newline join of the table's header, separator, and rows, with no trailing newline. Returns an empty string when `table()` is `None`, that is, when the list is empty or every record has no fields.

```python
CliRecordList(records=[
    CliRecord(fields={'id': 'calc.add', 'name': 'Add'}),
    CliRecord(fields={'id': 'calc.sqrt', 'name': 'Square Root'}),
]).format_output()
# 'id         name       \n---------  -----------\ncalc.add   Add        \ncalc.sqrt  Square Root'
```

### CliArgument

Represents a single command-line argument or flag. The `type` field is a `Literal` driving materially different `to_argparse_kwargs()` branching — there is no separate `action` field; action is derived from `type`.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="cliargument-name-or-flags"></a>`name_or_flags` | `List[str]` | Yes | — | The name or flags of the argument (e.g., `["-f", "--flag"]`). |
| <a id="cliargument-description"></a>`description` | `str \| None` | No | `None` | A brief description of the argument. |
| <a id="cliargument-type"></a>`type` | `Literal['str', 'int', 'float', 'bool', 'json', 'list', 'dict']` | No | `'str'` | The argument input shape — see the `type`-to-argparse mapping table below. |
| <a id="cliargument-required"></a>`required` | `bool \| None` | No | `None` | Whether the argument is required. |
| <a id="cliargument-default"></a>`default` | `str \| None` | No | `None` | The default value if not provided. |
| <a id="cliargument-choices"></a>`choices` | `List[str] \| None` | No | `None` | Valid choices for the argument (scalar and `list` types only). |
| <a id="cliargument-nargs"></a>`nargs` | `str \| None` | No | `None` | Number of arguments: `"?"`, `"*"`, `"+"`, or an integer. Defaults to `'*'` for `list`/`dict` when unset. |

**The `type` → argparse mapping:**

| `type` | `to_argparse_kwargs()` behavior |
|---|---|
| `'str'` / `'int'` / `'float'` | Resolves the Python builtin via `get_type()`; honors `nargs`/`choices` when set. |
| `'bool'` | `action='store_true'` — no value consumed; `nargs`/`choices`/`type` are omitted entirely. |
| `'json'` | `type=json.loads` — decodes a single JSON string at parse time. |
| `'list'` | `type=str`, `nargs=self.nargs or '*'` — collects space-separated tokens; `choices` still applies per-element. |
| `'dict'` | `type=str`, `nargs=self.nargs or '*'` — collects space-separated tokens later reassembled by `parse_value()`. |

#### Methods

<a id="cliargument-get-type"></a>
**`get_type() -> type`**

Maps a scalar `type` string (`'str'`, `'int'`, `'float'`) to its Python builtin. Non-scalar types are handled directly by `to_argparse_kwargs()`; this method returns `str` as a safe fallback for any unrecognised value.

```python
arg = CliArgument(name_or_flags=['--count'], type='int')
assert arg.get_type() is int
```

<a id="cliargument-to-argparse-kwargs"></a>
**`to_argparse_kwargs() -> Dict[str, Any]`**

Builds the keyword arguments for `argparse.add_argument()` per the `type` → argparse mapping table above. `name_or_flags` is excluded because it is passed positionally to `add_argument`.

```python
arg = CliArgument(name_or_flags=['a'], description='First operand.', type='int')
arg.to_argparse_kwargs()  # {'help': 'First operand.', 'type': int}

flag = CliArgument(name_or_flags=['--verbose'], description='Verbose.', type='bool')
flag.to_argparse_kwargs()  # {'help': 'Verbose.', 'action': 'store_true'}
```

<a id="cliargument-get-dest"></a>
**`get_dest() -> str`**

Derives the argparse destination name, mirroring argparse's own dest derivation: the first long flag (`--foo-bar`) wins, normalizing hyphens to underscores; falls back to the first short flag; a positional argument returns its name directly.

```python
CliArgument(name_or_flags=['-c', '--count']).get_dest()  # 'count'
CliArgument(name_or_flags=['a']).get_dest()               # 'a'
```

<a id="cliargument-parse-value"></a>
**`parse_value(value: Any) -> Any`**

Interprets the raw value argparse returns for this argument. A `'dict'`-typed argument arrives as a list of `key=value` strings (from `nargs='*'`); this method assembles them into a mapping via `DICT_ARGUMENT_DELIMITER` (`'='`). Every other type is already in its correct Python form and is returned unchanged.

```python
CliArgument(name_or_flags=['--tag'], type='dict').parse_value(['env=prod', 'region=us'])
# {'env': 'prod', 'region': 'us'}
```

### CliCommand

Represents a CLI command with a composite identifier.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="clicommand-id"></a>`id` | `str` | Yes | — | The unique identifier, formatted as `"group_key.key"`. |
| <a id="clicommand-name"></a>`name` | `str` | Yes | — | The name of the command. |
| <a id="clicommand-description"></a>`description` | `str \| None` | No | `None` | A brief description of the command. |
| <a id="clicommand-key"></a>`key` | `str` | Yes | — | The unique key for the command. |
| <a id="clicommand-group-key"></a>`group_key` | `str` | Yes | — | The group key the command belongs to. |
| <a id="clicommand-arguments"></a>`arguments` | `List[CliArgument]` | No | `[]` | A list of arguments for the command. |

#### Methods

<a id="clicommand-derive-id"></a>
**ID Derivation via `@model_validator`**

The `id` is automatically derived by a `@model_validator(mode='before')` that normalizes hyphens to underscores in both `group_key` and `key`, then joins them with a dot:

```python
cmd = CliCommand(group_key='calc', key='add', name='Add Number')
assert cmd.id == 'calc.add'

cmd = CliCommand(group_key='my-group', key='my-cmd', name='My Command')
assert cmd.id == 'my_group.my_cmd'
```

<a id="clicommand-has-argument"></a>
**`has_argument(flags: List[str]) -> bool`**

Returns `True` if any of the provided flags match the `name_or_flags` of an existing argument in the command.

```python
cmd.has_argument(['-a', '--arg1'])  # True if arg1 exists
cmd.has_argument(['-z'])            # False if no match
```

## The CLI-to-Feature Bridge

The CLI domain's key design pattern is the **CLI-to-Feature bridge**: every `CliCommand.id` corresponds exactly to a feature ID in `feature.yml`. When a user runs a CLI command, the `CliContext` maps the parsed command to a feature and executes it via `FeatureContext`.

For example:
- CLI command `calc.add` → Feature `calc.add` (defined in `feature.yml`)
- CLI command `calc.sqrt` → Feature `calc.sqrt`

This 1:1 mapping ensures CLI commands are thin entry points that delegate all business logic to the feature layer.

## Runtime Role

`CliContext` (`tiferet/contexts/cli.py`) is the primary consumer of the CLI domain at runtime; the `build_cli` blueprint is a thin entrypoint that realizes the context and calls `run_cli`:

1. **`get_commands()`** resolves all `CliCommand` entries via the injected `list_commands_evt` (backed by `CliService`) and groups them by `group_key` (`group_commands_by_key`).
2. **`build_parser(commands, parent_arguments)`** iterates each `CliCommand`, registering subparsers and adding each argument via `CliArgument.to_argparse_kwargs()`.
3. **`parse_cli_request(argv)`** parses the user's CLI input, derives the feature ID (`derive_feature_request`), and builds a `RequestContext`.
4. **`run_cli(argv)`** dispatches the request through the inherited `AppInterfaceContext.run`, which executes the corresponding feature via `FeatureContext`.

## Configuration Mapping

CLI commands are defined in the `cli` section of the configuration file (typically `config.yml`, though per-file configs such as `cli.yml` are also supported). Each entry under `cli.cmds.<group>.<key>` maps to a `CliCommand`:

```yaml
cli:
  cmds:
    calc:
      add:
        group_key: calc
        key: add
        description: Adds two numbers.
        args:
          - name_or_flags:
              - a
            description: The first number to add.
          - name_or_flags:
              - b
            description: The second number to add.
        name: Add Number Command
      sqrt:
        group_key: calc
        key: sqrt
        description: Calculates the square root of a number.
        args:
          - name_or_flags:
              - a
            description: The number to square root.
        name: Square Root Command
```

## Domain Events

The following domain events interact with `CliCommand` and `CliArgument`:

| Event                | Description                                              |
|----------------------|----------------------------------------------------------|
| `ListCliCommands`    | Lists all `CliCommand` entries.                          |
| `GetParentArguments` | Retrieves shared arguments for a command group.          |
| `AddCliCommand`      | Creates and persists a new `CliCommand`.                  |
| `AddCliArgument`     | Adds an argument to an existing `CliCommand` via aggregate.|

These events depend on the `CliService` interface for persistence operations.

## Service Interface

**`CliService`** (`tiferet/interfaces/cli.py`) defines the abstract contract for CLI configuration persistence:

- `exists(id: str) -> bool`
- `get(id: str) -> CliCommandAggregate`
- `list() -> List[CliCommandAggregate]`
- `save(command: CliCommandAggregate) -> None`
- `delete(id: str) -> None`
- `get_parent_arguments() -> List[CliArgumentAggregate]`
- `save_parent_arguments(parent_arguments: List[CliArgumentAggregate]) -> None`

Concrete implementations (e.g., `CliConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **Feature:** `CliCommand.id` maps 1:1 to feature IDs in `feature.yml`. CLI commands are thin entry points that delegate to the feature layer.
- **App:** The CLI session in the configuration points at `CliContext` and specifies `CliService` as a service dependency. `CliContext` handles argparse wiring; the `build_cli` blueprint realizes the context and delegates to `CliContext.run_cli`.
- **Error:** CLI error responses are formatted via `ErrorContext`, providing user-friendly messages for validation failures and domain errors.
- **Output rendering:** `CliOutputRecord`/`CliRecordList` are independent of `CliCommand`/`CliArgument` — they render whatever a feature's response contains, regardless of which command produced it.

## Boundaries

**Inside this domain:** the CLI command/argument configuration shape and the terminal-to-feature id mapping; the record-based vertical/tabular output-rendering shape.
**Outside this domain:** argparse wiring, subparser construction, and CLI request dispatch (`CliContext`, `docs/core/contexts.md`); mutation of a `CliCommand`/`CliArgument` (`CliCommandAggregate`/`CliArgumentAggregate` in `mappers`); which service produces the raw result a `CliRecord` wraps (that belongs to the feature/event layer, not this domain).

## Instantiation

```python
from tiferet.domain import CliArgument, CliCommand, CliRecord, CliRecordList

# Create an argument directly via Pydantic constructor
arg = CliArgument(
    name_or_flags=['--count', '-c'],
    description='Number of iterations.',
    type='int',
    required=True,
)

# Create a command — id is derived automatically via @model_validator
cmd = CliCommand(
    group_key='calc',
    key='add',
    name='Add Number',
    description='Adds two numbers.',
    arguments=[arg],
)
# cmd.id == 'calc.add'

# Render a tabular result
table = CliRecordList(records=[CliRecord(fields={'id': cmd.id, 'name': cmd.name})])
print(table.format_output())
```

## Related Documentation

- [docs/guides/domain/app.md](app.md) — App domain guide (session configuration)
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
