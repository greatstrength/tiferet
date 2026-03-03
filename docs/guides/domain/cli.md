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

The two-level nesting (`calc.add`) mirrors the feature ID structure. The `args` list maps to `CliArgument` entries.

## Domain Events

| Event | Purpose |
|-------|---------|
| `ListCliCommands` | Retrieve all CLI commands (used during argument parsing) |
| `GetParentArguments` | Retrieve parent-level arguments added to all commands |
| `AddCliCommand` | Register a new CLI command |
| `AddCliArgument` | Add an argument to an existing command |

## Service Interface

`CliService` (`tiferet/interfaces/cli.py`) — abstracts access to CLI command configurations.

## Relationship to Other Domains

- **Feature domain** — CLI command IDs are feature IDs. The CLI domain is a thin translation layer that converts terminal input into feature execution requests.
- **App domain** — `CliContext` extends `AppInterfaceContext`, so a CLI application is defined as an app interface in `app.yml` with `module_path: tiferet.contexts.cli` and `class_name: CliContext`.
- **Error domain** — CLI errors are caught and formatted via `ErrorContext`, then printed to stderr with a non-zero exit code.

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/guides/domain/feature.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/guides/domain/feature.md) — Feature domain guide
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/guides/domain/app.md) — App domain guide
