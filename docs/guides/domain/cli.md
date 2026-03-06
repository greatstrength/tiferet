**This conversation is part of the Tiferet Framework project.**  
**Repository:** https://github.com/greatstrength/tiferet – Tiferet Framework  

```markdown
# Domain – CLI: CliArgument and CliCommand

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 06, 2026  
**Version:** 2.0.0a2

## Overview

The CLI domain defines the structural configuration for command-line interface commands in Tiferet. CLI commands serve as the **terminal-to-feature bridge**: each `CliCommand` has a composite identifier (`group_key.key`) that maps directly to a feature ID in `feature.yml`, enabling seamless execution of domain features via `argparse`-driven command-line input.

- `CliArgument` — represents a single command-line argument or flag, mapping to `argparse.add_argument()` parameters.
- `CliCommand` — represents a CLI command with a composite ID, a custom `new()` factory for ID derivation, and a `has_argument()` query method.

Both domain objects are **immutable value objects**: they carry no mutation methods and expose only read-only queries. All state changes (adding/removing arguments, renaming commands) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/cli.py`

## Domain Objects

### CliArgument

Represents a single command-line argument or flag.

| Attribute       | Type                   | Required | Default | Description                                                                      |
|-----------------|------------------------|----------|---------|----------------------------------------------------------------------------------|
| `name_or_flags` | `ListType(StringType)` | Yes      | —       | The name or flags of the argument (e.g., `["-f", "--flag"]`).                     |
| `description`   | `StringType`           | No       | —       | A brief description of the argument.                                              |
| `type`          | `StringType`           | No       | `'str'` | The type: `"str"`, `"int"`, or `"float"`.                                         |
| `required`      | `BooleanType`          | No       | —       | Whether the argument is required.                                                 |
| `default`       | `StringType`           | No       | —       | The default value if not provided.                                                |
| `choices`       | `ListType(StringType)` | No       | —       | Valid choices for the argument.                                                   |
| `nargs`         | `StringType`           | No       | —       | Number of arguments: `"?"`, `"*"`, `"+"`, or an integer.                          |
| `action`        | `StringType`           | No       | —       | The action: `store`, `store_true`, `store_false`, `append`, `count`, `help`, etc. |

#### Methods

**`get_type() -> str | int | float`**

Maps the stored `type` string to a Python type object. Falls back to `str` if the type is `None` or unrecognized.

```python
arg = DomainObject.new(CliArgument, name_or_flags=['--count'], type='int')
assert arg.get_type() is int
```

### CliCommand

Represents a CLI command with a composite identifier.

| Attribute    | Type                              | Required | Default | Description                                                  |
|--------------|-----------------------------------|----------|---------|--------------------------------------------------------------|
| `id`         | `StringType`                      | Yes      | —       | The unique identifier, formatted as `"group_key.key"`.        |
| `name`       | `StringType`                      | Yes      | —       | The name of the command.                                      |
| `description`| `StringType`                      | No       | —       | A brief description of the command.                           |
| `key`        | `StringType`                      | Yes      | —       | The unique key for the command.                               |
| `group_key`  | `StringType`                      | Yes      | —       | The group key the command belongs to.                         |
| `arguments`  | `ListType(ModelType(CliArgument))`| No       | `[]`    | A list of arguments for the command.                          |

#### Methods

**`new(group_key, key, name, description=None, arguments=[]) -> CliCommand`** (static)

Custom factory that derives the `id` by normalizing hyphens to underscores in both `group_key` and `key`, then joining with a dot:

```python
cmd = CliCommand.new(group_key='calc', key='add', name='Add Number')
assert cmd.id == 'calc.add'

cmd = CliCommand.new(group_key='my-group', key='my-cmd', name='My Command')
assert cmd.id == 'my_group.my_cmd'
```

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

The CLI domain objects participate in the command-line execution flow:

1. **`CliContext.get_commands()`** loads all `CliCommand` entries from `app/configs/cli.yml` via `CliService`.
2. **`parse_arguments()`** iterates each `CliCommand`, registering subparsers and arguments with `argparse` using `CliArgument` attributes (`name_or_flags`, `type`, `required`, `default`, `choices`, `nargs`, `action`).
3. **`argparse`** parses the user's CLI input and returns the matched command group and key.
4. **`parse_request()`** maps the parsed arguments to a feature ID (`group_key.key`) and data dictionary.
5. **`FeatureContext`** executes the corresponding feature with the parsed data.

## Configuration Mapping

CLI commands are defined in `app/configs/cli.yml`. Each entry under `cli.cmds.<group>.<key>` maps to a `CliCommand`:

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
from tiferet.domain import DomainObject, CliArgument, CliCommand

# Create an argument directly
arg = DomainObject.new(
    CliArgument,
    name_or_flags=['--count', '-c'],
    description='Number of iterations.',
    type='int',
    required=True,
)

# Create a command via the custom factory
cmd = CliCommand.new(
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
