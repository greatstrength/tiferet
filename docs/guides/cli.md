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

## JSON-Valued Arguments

Some commands accept structured values. These arguments are provided as JSON
strings on the command line and decoded before the feature executes:

- `--parameters`
- `--constants`
- `--services`
- `--flagged-dependencies`

Example — add a service registration with parameters:

```bash
tiferet --config app/config.yml service add my_svc \
  --module-path tiferet.repos.feature \
  --class-name FeatureConfigRepository \
  --parameters '{"feature_config": "app/config.yml"}'
```

Malformed JSON fails cleanly with a message on stderr and a non-zero exit code
rather than an unhandled traceback. Optional list/dict arguments that are omitted
are treated as empty (`[]` / `{}`) by the underlying domain events, except where
an explicit `null`/absence is meaningful (e.g. `set-constants` clearing all
constants).

## Exit Codes

- `0` — success.
- `1` — a `TiferetAPIError` was raised while executing the feature (the formatted
  error message is printed to stderr).
- `2` — argument parsing failed, or a JSON-valued argument was malformed.

## Programmatic Use

The same behavior is available without the console script by calling the
blueprint directly:

```python
from tiferet.blueprints.tiferet_cli import build_tiferet_cli

build_tiferet_cli(app_config='app/config.yml', argv=['feature', 'list'])
```
