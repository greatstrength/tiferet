# Domain – CLI (Command-Line Interface)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0b1

## Overview

The CLI domain defines **how users interact with the application from the command line**. It bridges the gap between raw terminal input and the feature execution engine by describing a structured command hierarchy — groups of commands, each with typed arguments — that maps directly to feature IDs.

A `CliCommand` represents a single CLI command (e.g., `calc add`) with its arguments, description, and group membership. A `CliArgument` represents a single argument or flag on that command (e.g., `a`, `b`, `--verbose`). Together, they generate the `argparse` configuration that `CliContext` uses to parse user input into feature execution requests.

## Domain Objects

### CliArgument

Represents a single command-line argument or flag.

| Attribute       | Type                   | Required | Default | Description                                                                      |
|-----------------|------------------------|----------|---------|----------------------------------------------------------------------------------|
| `name_or_flags` | `List[str]`            | Yes      | —       | The name or flags of the argument (e.g., `["-f", "--flag"]`).                     |
| `description`   | `str \| None`          | No       | `None`  | A brief description of the argument.                                              |
| `type`          | `str \| None`          | No       | `'str'` | The type: `"str"`, `"int"`, or `"float"`.                                         |
| `required`      | `bool \| None`         | No       | `None`  | Whether the argument is required.                                                 |
| `default`       | `str \| None`          | No       | `None`  | The default value if not provided.                                                |
| `choices`       | `List[str] \| None`    | No       | `None`  | Valid choices for the argument.                                                   |
| `nargs`         | `str \| None`          | No       | `None`  | Number of arguments: `"?"`, `"*"`, `"+"`, or an integer.                          |
| `action`        | `str \| None`          | No       | `None`  | The action: `store`, `store_true`, `store_false`, `append`, `count`, `help`, etc. |

#### Methods

**`get_type() -> str | int | float`**

Maps the stored `type` string to a Python type object. Falls back to `str` if the type is `None` or unrecognized.

```python
arg = CliArgument(name_or_flags=['--count'], type='int')
assert arg.get_type() is int
```

### CliCommand

A single CLI command, identified by a composite `group_key.key` pattern that maps directly to a feature ID.

| Attribute    | Type                              | Required | Default | Description                                                  |
|--------------|-----------------------------------|----------|---------|--------------------------------------------------------------|
| `id`         | `str`                             | Yes      | —       | The unique identifier, formatted as `"group_key.key"`.        |
| `name`       | `str`                             | Yes      | —       | The name of the command.                                      |
| `description`| `str \| None`                     | No       | `None`  | A brief description of the command.                           |
| `key`        | `str`                             | Yes      | —       | The unique key for the command.                               |
| `group_key`  | `str`                             | Yes      | —       | The group key the command belongs to.                         |
| `arguments`  | `List[CliArgument]`               | No       | `[]`    | A list of arguments for the command.                          |

**Custom factory:**

**ID Derivation via `@model_validator`**

The `id` is automatically derived by a `@model_validator(mode='before')` that normalizes hyphens to underscores in both `group_key` and `key`, then joins them with a dot:

```python
cmd = CliCommand(group_key='calc', key='add', name='Add Number')
assert cmd.id == 'calc.add'

cmd = CliCommand(group_key='my-group', key='my-cmd', name='My Command')
assert cmd.id == 'my_group.my_cmd'
```

`CliContext` parses `group='calc'` and `command='add'`, constructs `feature_id = 'calc.add'`, and delegates to `FeatureContext.execute_feature('calc.add', request)`. The arguments (`1`, `2`) become the request data that the feature's domain event receives.

## Runtime Role

`CliContext` (which extends `AppInterfaceContext`) is the sole consumer of the CLI domain at runtime:

1. **`get_commands()`** retrieves all `CliCommand` objects via `ListCliCommands` and groups them by `group_key`.
2. **`parse_arguments(cli_commands)`** builds a nested `argparse` parser:
   - Top-level subparsers for each group (e.g., `calc`).
   - Sub-subparsers for each command within a group (e.g., `add`, `sqrt`).
   - Each `CliArgument` is added via `add_argument()` with its type, default, choices, etc.
   - **Parent arguments** (retrieved via `GetParentArguments`) are added to all commands that don't already define them.
3. **`parse_request()`** calls `parse_arguments()`, extracts `group` and `command` from the result, constructs the feature ID, and creates a `RequestContext` with the parsed data.
4. **`run()`** executes the feature via the inherited `AppInterfaceContext.execute_feature()`.

```python
# CliContext constructs the feature ID from parsed arguments:
feature_id = '{}.{}'.format(
    data.get('group').replace('-', '_'),
    data.get('command').replace('-', '_')
)
# 'calc' + 'add' → 'calc.add'
```

## Configuration

CLI commands are defined in `app/configs/cli.yml`:

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
- `get(id: str) -> CliCommand`
- `list() -> List[CliCommand]`
- `save(cli_command) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `CliYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **Feature:** `CliCommand.id` maps 1:1 to feature IDs in `feature.yml`. CLI commands are thin entry points that delegate to the feature layer.
- **App:** The `calc_cli` interface in `app.yml` specifies `CliContext` as its implementation, with `CliService` and `CliHandler` as service dependencies.
- **Error:** CLI error responses are formatted via `ErrorContext`, providing user-friendly messages for validation failures and domain errors.

## Instantiation

```python
from tiferet.domain import CliArgument, CliCommand

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
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide (interface configuration)
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
```
