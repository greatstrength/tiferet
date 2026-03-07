# Domain – CLI (Command-Line Interface)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/domain/cli.py`  
**Version:** 2.0.0a2

## Overview

The CLI domain defines **how users interact with the application from the command line**. It bridges the gap between raw terminal input and the feature execution engine by describing a structured command hierarchy — groups of commands, each with typed arguments — that maps directly to feature IDs.

A `CliCommand` represents a single CLI command (e.g., `calc add`) with its arguments, description, and group membership. A `CliArgument` represents a single argument or flag on that command (e.g., `a`, `b`, `--verbose`). Together, they generate the `argparse` configuration that `CliContext` uses to parse user input into feature execution requests.

## Domain Objects

### CliCommand

A single CLI command, identified by a composite `group_key.key` pattern that maps directly to a feature ID.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Composite identifier, derived as `{group_key}.{key}` |
| `name` | `str` (required) | Human-readable name |
| `description` | `str` | Brief description shown in CLI help |
| `key` | `str` (required) | Command key within its group (e.g., `add`, `sqrt`) |
| `group_key` | `str` (required) | Group key for organizing related commands (e.g., `calc`) |
| `arguments` | `List[CliArgument]` (default: `[]`) | Arguments for this command |

**Custom factory:**

- `CliCommand.new(group_key, key, name, ...)` — derives `id` from `group_key` and `key` by normalizing hyphens to underscores and joining with a dot. For example, `group_key='calc'`, `key='add'` produces `id='calc.add'`.

**Behavior method:**

- `has_argument(flags)` — checks if any of the provided flags match an existing argument's `name_or_flags`. Used to avoid adding duplicate parent arguments.

### CliArgument

A single command-line argument or flag. Maps directly to `argparse.add_argument()` parameters.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name_or_flags` | `List[str]` (required) | Argument name or flag strings (e.g., `['a']`, `['-v', '--verbose']`) |
| `description` | `str` | Help text shown in CLI usage |
| `type` | `str` (default: `'str'`) | Argument type: `str`, `int`, or `float` |
| `required` | `bool` | Whether the argument is required |
| `default` | `str` | Default value if not provided |
| `choices` | `List[str]` | Valid choices for the argument |
| `nargs` | `str` | Number of arguments: `?` (optional), `*` (zero+), `+` (one+) |
| `action` | `str` | Argparse action: `store`, `store_true`, `store_false`, `append`, `count`, etc. |

**Behavior method:**

- `get_type()` — maps the `type` string to a Python type object (`str`, `int`, `float`). Returns `str` for unrecognized values. This is passed directly to `argparse.add_argument(type=...)`.

### The CLI-to-Feature Bridge

The key architectural insight is that CLI command IDs are feature IDs. When a user runs:

```bash
python calc_cli.py calc add 1 2
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
