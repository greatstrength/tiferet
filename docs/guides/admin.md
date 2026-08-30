# Admin Support – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Modules:** `tiferet/blueprints/admin.py`, `tiferet/blueprints/admin_cli.py`  
**Version:** 2.0.0

## Overview

The Tiferet framework provides a built-in admin support layer that allows application developers and operators to inspect, add, update, and remove configuration records directly in consumer `config.yml` files (and YAML/JSON repositories) without building custom management interfaces.

The admin layer is exposed through two single-call entry points:
- **`AdminApp`** / **`build_admin_app`** — Python entry point returning a fully wired `AppSessionContext` bound to the built-in `admin` session.
- **`AdminCLI`** / **`build_admin_cli`** — Console entry point (`tiferet`) returning a `CliSessionContext` bound to the built-in `admin_cli` session.

Import both from the blueprints package (they are not re-exported from the package root):

```python
from tiferet.blueprints import AdminApp, AdminCLI
# also: build_admin_app, build_admin_cli
```

Both entry points pre-seed an admin bootstrap cache containing the framework's full six-domain CRUD catalog and wire an admin service resolver that resolves admin-scoped feature steps from an admin container by default.

Source of truth for catalog IDs:
- Features: `ADMIN_DEFAULT_FEATURES` in `tiferet/assets/feature.py` (41 features)
- Commands: `ADMIN_DEFAULT_COMMANDS` in `tiferet/assets/cli.py` (41 commands, including `feature.get`)

## Ubiquitous Language

- **Admin Session**: A built-in application session (`admin` or `admin_cli`) configured with default repositories and management workflows.
- **Admin CLI**: The `tiferet` command-line entry point that pre-parses `--config` options and dispatches administrative CLI requests.
- **Six Admin Domains**: The functional CRUD management domains exposed by the admin catalog: App, CLI, Error, Feature, Service/DI, and Logging.
- **Admin-Scoped Resolution**: Service resolution where default feature steps resolve against the admin service container rather than consumer application overrides.

## Building an Admin Session

The `build_admin_app` blueprint function (exported as `AdminApp`) builds a complete admin session context:

```python
from tiferet.blueprints import AdminApp

# Bootstrap the admin application session
admin = AdminApp()

# Execute a management feature against the consumer's config.yml
response = admin.run('app.list')
```

### Resolver Flag Routing

`build_admin_service_resolver` registers the `app` container under the `'app'` flag, while the admin container is registered under both the `'admin'` flag and the empty-flag default:

```python
# Resolves from the consumer app container
app_dep = resolver.get_dependency('service_id', 'app')

# Resolves from the admin container
admin_dep = resolver.get_dependency('service_id', 'admin')

# Resolves from the admin container by default
default_dep = resolver.get_dependency('service_id')
```

This guarantees that admin management workflows execute against the framework's administrative services and repositories without interfering with consumer application registrations.

## Building an Admin CLI Session

The `build_admin_cli` blueprint function (exported as `AdminCLI`) and its `main()` console wrapper power the `tiferet` script:

```bash
# Manage config.yml in the current directory
tiferet app list

# Manage a specific configuration file
tiferet --config custom_config.yml error list
```

Programmatically, `build_admin_cli` re-seeds the resolved session's constants so every config-file repository points directly at the consumer-supplied configuration file:

```python
from tiferet.blueprints import AdminCLI

# Execute an administrative CLI command against a custom config file
response = AdminCLI(app_config='app_config.yml', argv=['feature', 'list'])
```

## The Six Admin Domains

The admin catalog spans six configuration management domains. Each subsection lists every landed feature ID with a one-line purpose and its CLI verb (group + key). CLI shapes use positional arguments unless a flag is shown with `--`.

All flat-map arguments accept `key=value` pairs on the CLI (`type: dict`); raw JSON is only used where the catalog marks `type: json`.

### 1. App Domain (`app`)

Manages application interface / session definitions, constants, and app-level service dependencies.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `app.add` | Add a new application session configuration | `tiferet app add <id> <name> [--description] [--logger-id] [--flags] [--constants]` |
| `app.get` | Retrieve an app session by ID | `tiferet app get <interface_id>` |
| `app.list` | List all configured app sessions | `tiferet app list` |
| `app.update` | Update a scalar attribute on an app session | `tiferet app update <id> <attribute> <value>` |
| `app.set_constants` | Set or clear constants on an app session | `tiferet app set-constants <id> [--constants]` |
| `app.set_service` | Set or update a service dependency on an app session | `tiferet app set-service <id> <service_id> <module_path> <class_name> [--parameters]` |
| `app.remove_service` | Remove a service dependency from an app session | `tiferet app remove-service <id> <service_id>` |
| `app.remove` | Remove an app session by ID | `tiferet app remove <id>` |

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'app.add',
    data={
        'id': 'web_api',
        'name': 'Web API Session',
        'description': 'Main web API application session',
    },
)
```

```bash
tiferet app add web_api "Web API Session" --description "Main web API application session"
tiferet app list
```

### 2. CLI Domain (`cli`)

Manages CLI command definitions and argument specifications.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `cli.list_commands` | List all configured CLI commands | `tiferet cli list-commands` |
| `cli.add_command` | Add a new CLI command definition | `tiferet cli add-command <id> <name> <key> <group_key> [--description]` |
| `cli.add_argument` | Add an argument to an existing CLI command | `tiferet cli add-argument <command_id> --name-or-flags <json> [--description]` |

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'cli.add_command',
    data={
        'id': 'reports.generate',
        'name': 'Generate Report',
        'key': 'generate',
        'group_key': 'reports',
        'description': 'Generate summary report',
    },
)
```

```bash
tiferet cli add-command reports.generate "Generate Report" generate reports --description "Generate summary report"
tiferet cli list-commands
```

### 3. Error Domain (`error`)

Manages structured error definitions and multilingual messages.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `error.list` | List all error definitions | `tiferet error list` |
| `error.add` | Add a new error definition | `tiferet error add <id> <name> <message> [--lang] [--additional-messages]` |
| `error.get` | Retrieve an error by ID | `tiferet error get <id>` |
| `error.rename` | Rename an existing error definition | `tiferet error rename <id> <new_name>` |
| `error.set_message` | Set the message text on an existing error | `tiferet error set-message <id> <message> [--lang]` |
| `error.remove_message` | Remove a language message from an error | `tiferet error remove-message <id> [--lang]` |
| `error.remove` | Remove an error definition | `tiferet error remove <id>` |

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'error.add',
    data={
        'id': 'INVALID_TOKEN_ID',
        'name': 'Invalid Token',
        'message': 'The provided authentication token is invalid.',
        'additional_messages': {
            'es_ES': 'El token de autenticación proporcionado no es válido.',
        },
    },
)
```

```bash
tiferet error add INVALID_TOKEN_ID "Invalid Token" "The provided authentication token is invalid." --additional-messages es_ES="El token de autenticación proporcionado no es válido."
tiferet error list
```

### 4. Feature Domain (`feature`)

Manages feature workflow definitions and steps.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `feature.list` | List all feature workflow definitions | `tiferet feature list [--group-id]` |
| `feature.add` | Add a new feature workflow definition | `tiferet feature add <name> <group_id> [--feature-key] [--description]` |
| `feature.get` | Retrieve a feature by ID | `tiferet feature get <id>` |
| `feature.update` | Update a metadata attribute on a feature | `tiferet feature update <id> <attribute> <value>` |
| `feature.add_step` | Add a step to an existing feature workflow | `tiferet feature add-step <id> <name> <service_id> [--parameters] [--data-key] [--pass-on-error] [--position]` |
| `feature.update_step` | Update an attribute on an existing feature step | `tiferet feature update-step <id> <position> <attribute> [--value]` |
| `feature.remove_step` | Remove a step from an existing feature workflow | `tiferet feature remove-step <id> <position>` |
| `feature.reorder_step` | Reorder a step within an existing feature workflow | `tiferet feature reorder-step <id> <start_position> <end_position>` |
| `feature.remove` | Remove an existing feature workflow definition | `tiferet feature remove <id>` |

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'feature.add',
    data={
        'name': 'Create User Workflow',
        'group_id': 'user',
        'feature_key': 'create',
        'description': 'Validates and registers a new user',
    },
)
admin.run(
    'feature.add_step',
    data={
        'id': 'user.create',
        'name': 'Validate User Step',
        'service_id': 'validate_user_evt',
        'parameters': {'mode': 'strict'},
    },
)
```

```bash
tiferet feature add "Create User Workflow" user --feature-key create --description "Validates and registers a new user"
tiferet feature add-step user.create "Validate User Step" validate_user_evt --parameters mode=strict
tiferet feature list
```

### 5. Service / DI Domain (`service`)

Manages feature-level service registrations, flagged dependencies, and DI constants.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `service.list` | List all DI service registrations and constants | `tiferet service list` |
| `service.add` | Add a new DI service registration | `tiferet service add <id> [--module-path] [--class-name] [--parameters]` |
| `service.set_default` | Set or update the default type for a registration | `tiferet service set-default <id> [--module-path] [--class-name] [--parameters]` |
| `service.set_dependency` | Set or update a flagged dependency on a registration | `tiferet service set-dependency <id> <flag> <module_path> <class_name> [--parameters]` |
| `service.remove_dependency` | Remove a flagged dependency from a registration | `tiferet service remove-dependency <id> <flag>` |
| `service.set_constants` | Set or clear DI service constants | `tiferet service set-constants [--constants]` |
| `service.remove` | Remove a DI service registration | `tiferet service remove <id>` |

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'service.add',
    data={
        'id': 'validate_user_evt',
        'module_path': 'app.events.user',
        'class_name': 'ValidateUserEvent',
        'parameters': {'timeout': '5.0'},
    },
)
admin.run(
    'service.set_dependency',
    data={
        'id': 'validate_user_evt',
        'flag': 'test',
        'module_path': 'app.events.user',
        'class_name': 'StubValidateUserEvent',
    },
)
```

```bash
tiferet service add validate_user_evt --module-path app.events.user --class-name ValidateUserEvent --parameters timeout=5.0
tiferet service set-dependency validate_user_evt test app.events.user StubValidateUserEvent
tiferet service list
```

### 6. Logging Domain (`logging`)

Manages logging formatters, handlers, and loggers.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `logging.add_formatter` | Add a new logging formatter configuration | `tiferet logging add-formatter <id> <name> <format> [--description] [--datefmt]` |
| `logging.remove_formatter` | Remove a logging formatter by ID | `tiferet logging remove-formatter <id>` |
| `logging.add_handler` | Add a new logging handler configuration | `tiferet logging add-handler <id> <name> <module_path> <class_name> <level> <formatter> [--description] [--stream] [--filename]` |
| `logging.remove_handler` | Remove a logging handler by ID | `tiferet logging remove-handler <id>` |
| `logging.add_logger` | Add a new logger configuration | `tiferet logging add-logger <id> <name> <level> <handlers> [--description] [--no-propagate]` |
| `logging.remove_logger` | Remove a logger by ID | `tiferet logging remove-logger <id>` |
| `logging.list` | List all logging configurations | `tiferet logging list` |

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'logging.add_logger',
    data={
        'id': 'app.audit',
        'name': 'app.audit',
        'level': 'INFO',
        'handlers': 'console,file',
    },
)
```

```bash
tiferet logging add-logger app.audit app.audit INFO console,file
tiferet logging list
```

## Boundaries

- **Inside this domain**: Invoking the built-in `admin` and `admin_cli` application sessions, resolving admin catalog features, executing CRUD management operations against consumer YAML/JSON configuration files, and utilizing flat-map key-value CLI options.
- **Outside this domain**:
  - Authoring new domain events, services, or features for a consumer's own domain logic — see [docs/core/blueprints.md](../core/blueprints.md) and component code-style skills (`tiferet-code-domain`, `tiferet-code-events`).
  - Internal blueprint handler composition and context construction details — see [docs/core/blueprints.md](../core/blueprints.md) and [docs/core/contexts.md](../core/contexts.md).

## Related Documentation

- [docs/core/blueprints.md](../core/blueprints.md) — Blueprint architecture and single-call entry points
- [docs/core/contexts.md](../core/contexts.md) — Runtime context hub architecture and handler wiring
- [docs/guides/blueprints.md](blueprints.md) — Blueprint design strategies and patterns
- [docs/guides/contexts.md](contexts.md) — Context strategies and runtime execution patterns
- [docs/guides/domain/cli.md](domain/cli.md) — CLI domain models and argument parsing
