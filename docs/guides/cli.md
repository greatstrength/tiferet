# Tiferet Built-in CLI

Tiferet ships a built-in command-line interface for managing a Tiferet
application's configuration file (features, errors, service registrations, app
interfaces, CLI commands, and logging). It is installed as the `tiferet` console
script and is implemented by the `build_tiferet_cli` blueprint
(`tiferet/blueprints/tiferet_cli.py`, exported as `TiferetCLI`).

The CLI's command catalog and feature workflows are bootstrapped from framework
asset modules — they are **not** read from your configuration file. Every CRUD
operation, however, reads from and writes to the configuration file you supply.

## Installation

Install the package so the console script is on your `PATH`:

```bash
source .venv/bin/activate
pip install -e .
```

This registers the `tiferet` entry point (declared under `[project.scripts]` in
`pyproject.toml` as `tiferet = "tiferet.blueprints.tiferet_cli:main"`).

## Invocation

```bash
tiferet --config <file> <group> <command> [args]
```

- `--config <file>` selects the configuration file all commands read from and
  write to. It defaults to `config.yml` in the current directory when omitted.
- `<group>` and `<command>` select the operation; together they map to a feature
  id (`<group>.<command>`, with hyphens normalized to underscores).

Examples:

```bash
# Add a feature to config.yml (default config path)
tiferet feature add "My Feature" my_group

# List features from an explicit config file
tiferet --config app/config.yml feature list

# Remove an error definition
tiferet --config app/config.yml error remove INVALID_INPUT
```

## Command Groups

The built-in CLI exposes these command groups:

- `feature` — manage feature workflows and their steps.
- `error` — manage error definitions and localized messages.
- `service` — manage feature-level DI service registrations.
- `app` — manage application interface definitions and their service dependencies.
- `cli` — manage CLI command definitions and arguments.
- `logging` — manage logging formatters, handlers, and loggers.

Run a group with no command, or an unknown command, to see argparse usage for
that group.

## Dict-Valued Arguments

The admin CLI is JSON-free: flat string-to-string map arguments are provided
as `key=value` tokens rather than JSON strings, and are parsed by
`CliArgument.parse_value()` before the feature executes:

- `--parameters`
- `--constants`
- `--additional-messages`

Example — add a service registration with parameters:

```bash
tiferet --config app/config.yml service add my_svc \
  --module-path tiferet.repos.feature \
  --class-name FeatureConfigRepository \
  --parameters feature_config=app/config.yml
```

A `dict` value may contain `=` because `parse_value()` splits on the first
delimiter only. Optional dict arguments that are omitted are treated as empty
(`{}`) by the underlying domain events, except where an explicit
`null`/absence is meaningful (e.g. `set-constants` clearing all constants).

Bulk-record arguments (nested records rather than flat maps, e.g. a service's
dependency list) are not encoded through the CLI at all. Create the parent
record first, then use the granular follow-up commands (`app.set-service`,
`service.set-dependency`) to add records one at a time.

## Exit Codes

- `0` — success.
- `1` — a `TiferetAPIError` was raised while executing the feature (the formatted
  error message is printed to stderr).
- `2` — argument parsing failed.

## Programmatic Use

The same behavior is available without the console script by calling the
blueprint directly:

```python
from tiferet.blueprints.tiferet_cli import build_tiferet_cli

build_tiferet_cli(app_config='app/config.yml', argv=['feature', 'list'])
```
