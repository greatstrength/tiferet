# Events – CLI Command Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/cli.py`  
**Version:** 2.0.0b1

## Overview

The CLI event module provides domain events for managing `CliCommand` configurations — the definitions that drive Tiferet's command-line interface. Every event depends on an injected `CliService` and operates on `CliCommand` domain objects through the `CliCommandAggregate` mapper.

These events are consumed by CLI management tooling and by contexts that need to inspect or modify the CLI command tree at runtime.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddCliCommand` | Create | `id` | `CliCommand` |
| `AddCliArgument` | Update (add arg) | `command_id` | `str` (ID) |
| `ListCliCommands` | Read (all) | *(none)* | `List[CliCommand]` |
| `GetParentArguments` | Read (parent args) | *(none)* | `List` |

## Dependency

All events inject a single dependency:

- **`cli_service: CliService`** — the service interface for persisting, retrieving, and querying `CliCommand` configurations.

## Event Details

### AddCliCommand

Creates a new `CliCommand` and persists it via `CliService.save()`. Verifies the command ID does not already exist before creation.

**Required:** `id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | The command name |
| `key` | `str` | — | The command key (used in CLI parsing) |
| `group_key` | `str` | — | The group key for command grouping |
| `description` | `str \| None` | `None` | Human-readable description |
| `arguments` | `list` | `[]` | Initial list of argument definitions |

**Returns:** The created `CliCommand` instance.

**Errors:**
- `CLI_COMMAND_ALREADY_EXISTS` if a command with the given ID already exists.

**Behavior:**
1. Verifies the ID is not already in use via `cli_service.exists(id)`.
2. Creates the command via the `CliCommandAggregate` Pydantic constructor.
3. Saves via `cli_service.save(command)`.

```python
result = DomainEvent.handle(
    AddCliCommand,
    dependencies={'cli_service': cli_service},
    id='calc.add',
    name='Add Number Command',
    key='add',
    group_key='calc',
    description='Adds two numbers.',
    arguments=[
        {
            'name_or_flags': ['a'],
            'description': 'The first number.',
        },
        {
            'name_or_flags': ['b'],
            'description': 'The second number.',
        },
    ],
)
```

### AddCliArgument

Adds an argument to an existing CLI command. Retrieves the command, delegates to `CliCommandAggregate.add_argument()`, and persists the result.

**Required:** `command_id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name_or_flags` | `list` | — | The argument name or flags (e.g., `['a']` or `['-v', '--verbose']`) |
| `description` | `str \| None` | `None` | Argument description |

Additional kwargs (`type`, `required`, `default`, `choices`, `nargs`, `action`) are forwarded to `CliCommandAggregate.add_argument()`.

**Returns:** `str` — the command ID.

**Errors:**
- `CLI_COMMAND_NOT_FOUND` if the command does not exist.

```python
DomainEvent.handle(
    AddCliArgument,
    dependencies={'cli_service': cli_service},
    command_id='calc.add',
    name_or_flags=['-p', '--precision'],
    description='Decimal precision for the result.',
    type='int',
    default='2',
)
```

### ListCliCommands

Lists all configured CLI commands. No required parameters.

**Returns:** `List[CliCommand]` — may be empty.

```python
commands = DomainEvent.handle(
    ListCliCommands,
    dependencies={'cli_service': cli_service},
)
```

### GetParentArguments

Retrieves parent-level CLI arguments — arguments that apply globally across all commands (e.g., `--verbose`, `--config`). Delegates to `CliService.get_parent_arguments()`.

**Returns:** `List` — list of `CliArgument` instances; may be empty.

```python
parent_args = DomainEvent.handle(
    GetParentArguments,
    dependencies={'cli_service': cli_service},
)
```

## Common Patterns

### Existence Check Before Creation

`AddCliCommand` uses `self.verify(not cli_service.exists(id), ...)` to prevent duplicate commands. This differs from the retrieve→verify→mutate→save pattern used in most other events because creation only needs an existence check, not a full retrieval.

### Retrieve → Verify → Mutate → Save

`AddCliArgument` follows the standard four-step pattern: retrieve the command, verify it exists, mutate it via the aggregate method, and save the updated aggregate.

### Kwargs Forwarding

`AddCliArgument` forwards additional `**kwargs` to `CliCommandAggregate.add_argument()`, allowing callers to pass argument metadata (`type`, `required`, `default`, `choices`, `nargs`, `action`) without the event needing to enumerate every field.

## Related Documentation

- [docs/guides/domain/cli.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/cli.md) — CLI domain objects
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/events/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/events/app.md) — App event guide
