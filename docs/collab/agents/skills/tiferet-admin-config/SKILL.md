---
name: tiferet-admin-config
description: Use the Tiferet Admin App or Admin CLI to add or update errors, service registrations, and features in a consumer's config.yml. Use this when a TRD introduces a new domain event module and needs an accompanying error, service registration, and feature entry, or when asked to manage/add/update Tiferet application configuration (errors, services, features, CLI commands, sessions, logging) via the built-in admin surface.
---

# Tiferet Admin Config Management

## When to use

- **New domain event module integration**: When a TRD or implementation session adds a new domain event module and requires adding or updating an accompanying error definition, service registration, and feature workflow in a consumer's `config.yml`.
- **Configuration management**: When asked to inspect, add, update, or remove application configuration records (errors, services, features, CLI commands, sessions, logging) in `config.yml` or custom configuration files via the built-in admin surface.

## Primary path: Admin App (Python)

The **Admin App** (`AdminApp` / `build_admin_app`) is the strongly recommended primary path for programmatic configuration management.

Import from the blueprints package (not the package root):

```python
from tiferet.blueprints import AdminApp, AdminCLI
```

### Why Admin App is preferred

- **In-process objects**: Manipulates rich domain objects directly in Python without string serialization or parsing overhead.
- **No shell-quoting or string-escaping**: Complex parameter dicts and localized messages pass as native Python dicts, lists, and primitives without shell quoting risks.
- **Direct exception handling**: Returns structured response dicts or raises typed `TiferetError` instances that can be inspected and handled in code.

### Canonical usage pattern

```python
from tiferet.blueprints import AdminApp

# Instantiate the admin app (defaults to app_config='config.yml')
admin = AdminApp()

# Execute a management feature against config.yml
response = admin.run('feature.list', data={})
```

To target a specific configuration file other than `config.yml`:

```python
admin = AdminApp(app_config='custom_config.yml')
```

## Secondary path: Admin CLI

The **Admin CLI** (`AdminCLI` / `build_admin_cli` / `tiferet`) is the secondary path for interactive or command-line administration.

### Command-line syntax

```bash
# Target default config.yml in current working directory
tiferet <group> <command> [args...]

# Target a specific configuration file
tiferet --config custom_config.yml <group> <command> [args...]
```

### Key-value dict syntax

Every flat-map/dict-typed argument on the Admin CLI accepts `key=value` pairs directly on the command line — raw JSON strings are **never** required for dict args (only for the few `type: json` args such as `cli.add_argument --name-or-flags`).

```bash
# Correct: positional id/name/message; flat-map additional messages
tiferet error add INVALID_TOKEN_ID "Invalid Token" "Token is invalid." --additional-messages es_ES="El token no es válido."

# Correct: positional feature id + step name + service_id; flat-map parameters
tiferet feature add-step user.create "Validate User" validate_user_evt --parameters mode=strict timeout=5.0
```

## Catalog source of truth

Landed IDs come from:
- `ADMIN_DEFAULT_FEATURES` — `tiferet/assets/feature.py` (41 features)
- `ADMIN_DEFAULT_COMMANDS` — `tiferet/assets/cli.py` (40 commands; `feature.get` is Python-only)

Do **not** invent verbs such as `app.add_session`, `list-sessions`, `list-errors`, `list-features`, or `delete_*`. Use the pairs below.

## The Six Admin Domains

### 1. App Domain (`app`)

Manages application interface / session definitions, constants, and app-level service dependencies.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `app.add` | Add a new application session configuration | `tiferet app add <id> <name> <module_path> <class_name> [--description] [--logger-id] [--flags] [--constants]` |
| `app.get` | Retrieve an app session by ID | `tiferet app get <interface_id>` |
| `app.list` | List all configured app sessions | `tiferet app list` |
| `app.update` | Update a scalar attribute on an app session | `tiferet app update <id> <attribute> <value>` |
| `app.set_constants` | Set or clear constants on an app session | `tiferet app set-constants <id> [--constants]` |
| `app.set_service` | Set or update a service dependency on an app session | `tiferet app set-service <id> <service_id> <module_path> <class_name> [--parameters]` |
| `app.remove_service` | Remove a service dependency from an app session | `tiferet app remove-service <id> <service_id>` |
| `app.remove` | Remove an app session by ID | `tiferet app remove <id>` |

#### Python (`AdminApp`)

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()
admin.run(
    'app.add',
    data={
        'id': 'web_api',
        'name': 'Web API Session',
        'module_path': 'app.contexts.api',
        'class_name': 'ApiSessionContext',
        'description': 'Main web API application session',
    },
)
```

#### CLI (`tiferet`)

```bash
tiferet app add web_api "Web API Session" app.contexts.api ApiSessionContext --description "Main web API application session"
tiferet app list
```

---

### 2. CLI Domain (`cli`)

Manages CLI command definitions and argument specifications.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `cli.list_commands` | List all configured CLI commands | `tiferet cli list-commands` |
| `cli.add_command` | Add a new CLI command definition | `tiferet cli add-command <id> <name> <key> <group_key> [--description]` |
| `cli.add_argument` | Add an argument to an existing CLI command | `tiferet cli add-argument <command_id> --name-or-flags <json> [--description]` |

#### Python (`AdminApp`)

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

#### CLI (`tiferet`)

```bash
tiferet cli add-command reports.generate "Generate Report" generate reports --description "Generate summary report"
tiferet cli list-commands
```

---

### 3. Error Domain (`error`)

Manages structured error definitions and multilingual messages.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `error.list` | List all error definitions | `tiferet error list [--include-defaults]` |
| `error.add` | Add a new error definition | `tiferet error add <id> <name> <message> [--lang] [--additional-messages]` |
| `error.get` | Retrieve an error by ID | `tiferet error get <id>` |
| `error.rename` | Rename an existing error definition | `tiferet error rename <id> <new_name>` |
| `error.set_message` | Set the message text on an existing error | `tiferet error set-message <id> <message> [--lang]` |
| `error.remove_message` | Remove a language message from an error | `tiferet error remove-message <id> [--lang]` |
| `error.remove` | Remove an error definition | `tiferet error remove <id>` |

#### Python (`AdminApp`)

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

#### CLI (`tiferet`)

```bash
tiferet error add INVALID_TOKEN_ID "Invalid Token" "The provided authentication token is invalid." --additional-messages es_ES="El token de autenticación proporcionado no es válido."
tiferet error list
```

---

### 4. Feature Domain (`feature`)

Manages feature workflow definitions and steps.

| Feature | Purpose | CLI |
| --- | --- | --- |
| `feature.list` | List all feature workflow definitions | `tiferet feature list [--group-id]` |
| `feature.add` | Add a new feature workflow definition | `tiferet feature add <name> <group_id> [--feature-key] [--description]` |
| `feature.get` | Retrieve a feature by ID | *(Python only — no CLI command)* |
| `feature.update` | Update a metadata attribute on a feature | `tiferet feature update <id> <attribute> <value>` |
| `feature.add_step` | Add a step to an existing feature workflow | `tiferet feature add-step <id> <name> <service_id> [--parameters] [--data-key] [--pass-on-error] [--position]` |
| `feature.update_step` | Update an attribute on an existing feature step | `tiferet feature update-step <id> <position> <attribute> [--value]` |
| `feature.remove_step` | Remove a step from an existing feature workflow | `tiferet feature remove-step <id> <position>` |
| `feature.reorder_step` | Reorder a step within an existing feature workflow | `tiferet feature reorder-step <id> <start_position> <end_position>` |
| `feature.remove` | Remove an existing feature workflow definition | `tiferet feature remove <id>` |

#### Python (`AdminApp`)

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()

# Step 1: Define the feature workflow
admin.run(
    'feature.add',
    data={
        'name': 'Create User Workflow',
        'group_id': 'user',
        'feature_key': 'create',
        'description': 'Validates and registers a new user',
    },
)

# Step 2: Add a step to the workflow
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

#### CLI (`tiferet`)

```bash
tiferet feature add "Create User Workflow" user --feature-key create --description "Validates and registers a new user"
tiferet feature add-step user.create "Validate User Step" validate_user_evt --parameters mode=strict
tiferet feature list
```

---

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

#### Python (`AdminApp`)

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

#### CLI (`tiferet`)

```bash
tiferet service add validate_user_evt --module-path app.events.user --class-name ValidateUserEvent --parameters timeout=5.0
tiferet service set-dependency validate_user_evt test app.events.user StubValidateUserEvent
tiferet service list
```

---

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

#### Python (`AdminApp`)

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

#### CLI (`tiferet`)

```bash
tiferet logging add-logger app.audit app.audit INFO console,file
tiferet logging list
```

---

## Worked Example: Pairing a New Domain Event with Config Entries

When a new domain event module is authored (e.g. `VerifyPaymentEvent`), three corresponding entries must be configured in `config.yml` to make it operational:

1. **Error Definition** (`error.add`): Error constant and localized message for failure modes.
2. **Service Registration** (`service.add` / optional `service.set_dependency`): DI registration mapping the event ID to its class (and any flagged override).
3. **Feature Step** (`feature.add` / `feature.add_step`): Feature workflow plus step entry referencing the service ID.

### Complete Python script

```python
from tiferet.blueprints import AdminApp

# Initialize AdminApp against the target configuration file
admin = AdminApp(app_config='config.yml')

# 1. Add error definition
admin.run(
    'error.add',
    data={
        'id': 'PAYMENT_VERIFICATION_FAILED_ID',
        'name': 'Payment Verification Failed',
        'message': 'Unable to verify payment transaction.',
        'additional_messages': {
            'es_ES': 'No se pudo verificar la transacción de pago.',
        },
    },
)

# 2. Register the service (default type)
admin.run(
    'service.add',
    data={
        'id': 'verify_payment_evt',
        'module_path': 'app.events.payment',
        'class_name': 'VerifyPaymentEvent',
        'parameters': {'gateway_timeout': '10.0'},
    },
)

# 3. Create or ensure feature workflow exists
admin.run(
    'feature.add',
    data={
        'name': 'Payment Checkout Feature',
        'group_id': 'payment',
        'feature_key': 'checkout',
    },
)

# 4. Attach domain event as a feature step
admin.run(
    'feature.add_step',
    data={
        'id': 'payment.checkout',
        'name': 'Verify Payment Step',
        'service_id': 'verify_payment_evt',
        'parameters': {'require_3ds': 'true'},
    },
)
```

---

## Canonical Source

For full architectural details, resolver flag routing, and detailed blueprint specs, see:
- [docs/guides/admin.md](../../../guides/admin.md) — Admin Support Strategies and Patterns
- [docs/core/blueprints.md](../../../core/blueprints.md) — Blueprint Architecture and Entry Points
