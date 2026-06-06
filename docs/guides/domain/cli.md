# Domain – CLI: CliArgument and CliCommand

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

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

Represents a CLI command with a composite identifier.

| Attribute    | Type                              | Required | Default | Description                                                  |
|--------------|-----------------------------------|----------|---------|--------------------------------------------------------------|
| `id`         | `str`                             | Yes      | —       | The unique identifier, formatted as `"group_key.key"`.        |
| `name`       | `str`                             | Yes      | —       | The name of the command.                                      |
| `description`| `str \| None`                     | No       | `None`  | A brief description of the command.                           |
| `key`        | `str`                             | Yes      | —       | The unique key for the command.                               |
| `group_key`  | `str`                             | Yes      | —       | The group key the command belongs to.                         |
| `arguments`  | `List[CliArgument]`               | No       | `[]`    | A list of arguments for the command.                          |

#### Methods

**ID Derivation via `@model_validator`**

The `id` is automatically derived by a `@model_validator(mode='before')` that normalizes hyphens to underscores in both `group_key` and `key`, then joins them with a dot:

```python
cmd = CliCommand(group_key='calc', key='add', name='Add Number')
assert cmd.id == 'calc.add'

cmd = CliCommand(group_key='my-group', key='my-cmd', name='My Command')
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

The `build_cli` blueprint (`tiferet/blueprints/cli.py`) is the primary consumer of the CLI domain at runtime:

1. **`get_commands(service_provider)`** resolves all `CliCommand` entries from the configuration via `CliService`.
2. **`build_parser()`** iterates each `CliCommand`, registering subparsers and arguments with `argparse` using `CliArgument` attributes (`name_or_flags`, `type`, `required`, `default`, `choices`, `nargs`, `action`).
3. **`parse_argv()`** parses the user's CLI input and returns the matched command group and key.
4. **`derive_feature_request()`** maps the parsed arguments to a feature ID (`group_key.key`) and dispatches to `AppInterfaceContext.run()`.
5. **`FeatureContext`** executes the corresponding feature with the parsed data.

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
- `get(id: str) -> CliCommand`
- `list() -> List[CliCommand]`
- `save(cli_command) -> None`
- `delete(id: str) -> None`

Concrete implementations (e.g., `CliConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **Feature:** `CliCommand.id` maps 1:1 to feature IDs in `feature.yml`. CLI commands are thin entry points that delegate to the feature layer.
- **App:** The CLI interface in the configuration specifies `CliService` as a service dependency. The `build_cli` blueprint handles argparse wiring and dispatches to `AppInterfaceContext`.
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
