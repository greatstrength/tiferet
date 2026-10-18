# Tiferet Built-in CLI

Tiferet ships a built-in command-line interface for managing a Tiferet
application's configuration file (features, errors, service registrations, app
interfaces, CLI commands, and logging). It is installed as the `tiferet` console
script and is implemented by the `build_admin_cli` blueprint
(`tiferet/blueprints/admin_cli.py`, exported as `AdminCLI`).

The CLI's command catalog and feature workflows are intended to be bootstrapped
from framework asset modules rather than read from your configuration file.
Every CRUD operation is intended to read from and write to the configuration file you supply (see the known issue below).

> **Known issue (v2.2.0):** the `tiferet` admin CLI currently builds its command list from the `cli` section of the file passed to `--config`, not from the built-in admin catalog. If that file has no `cli:` section (or `cli: {}`), no command groups are available: every invocation, including the examples on this page, exits `2` with `invalid choice: '<group>' (choose from )`. If the file does define `cli.cmds`, those consumer commands replace the admin groups. Separately, `--config` does not yet redirect writes: the admin repositories are wired from the built-in admin constants, so CRUD commands read from and write to `./config.yml` in the current directory rather than the file you pass. A code fix for both is pending as a separate hotfix.

## Installation

Install the package so the console script is on your `PATH`:

```bash
source .venv/bin/activate
pip install tiferet
```

From a checkout of this repository, use `pip install -e '.[test]'` instead, so the test suite runs too ([CONTRIBUTING.md](../../CONTRIBUTING.md)).

This registers the `tiferet` entry point (declared under `[project.scripts]` in
`pyproject.toml` as `tiferet = "tiferet.blueprints.admin_cli:main"`).

## Invocation

```bash
tiferet --config <file> <group> <command> [args]
```

- `--config <file>` is meant to select the configuration file all commands read
  from and write to (today writes still go to `./config.yml`; see the known issue
  above). It defaults to `config.yml` in the current directory when omitted.
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
from tiferet.blueprints import build_admin_cli

build_admin_cli(app_config='app/config.yml', argv=['feature', 'list'])
```
