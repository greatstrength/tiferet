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

### Why Admin App is preferred

- **In-process objects**: Manipulates rich domain objects directly in Python without string serialization or parsing overhead.
- **No shell-quoting or string-escaping**: Complex parameter dicts and localized messages pass as native Python dicts, lists, and primitives without shell quoting risks.
- **Direct exception handling**: Returns structured response dicts or raises typed `TiferetError` instances that can be inspected and handled in code.

### Canonical usage pattern

```python
from tiferet import AdminApp

# Instantiate the admin app (defaults to app_config='config.yml')
admin = AdminApp()

# Execute a management feature against config.yml
response = admin.run('feature_id', data={'key': 'value'})
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
tiferet <group> <command> [options...]

# Target a specific configuration file
tiferet --config custom_config.yml <group> <command> [options...]
```

### Key-value dict syntax

Every flat-map/dict-typed argument on the Admin CLI accepts `key=value` pairs directly on the command line — raw JSON strings are **never** required.

```bash
# Correct: flat-map key=value pairs
tiferet error add --id INVALID_TOKEN_ID --name "Invalid Token" --message "Token is invalid." --additional-messages es_ES="El token no es válido."

# Correct: flat-map parameters
tiferet feature add-step --feature-id user.create --service-id validate_user_evt --name "Validate User" --parameters mode=strict timeout=5.0
```

## The Six Admin Domains

The admin surface spans six configuration management domains.

### 1. App Domain (`app`)

Manages application interface definitions, session parameters, and app constants.

- **Available features**: `app.add_session`, `app.list_sessions`, `app.get_session`, `app.delete_session`
- **CLI group**: `tiferet app <command>`

#### Python (`AdminApp`)

```python
from tiferet import AdminApp

admin = AdminApp()
admin.run(
    'app.add_session',
    data={
        'id': 'web_api',
        'name': 'Web API Session',
        'description': 'Main web API application session',
    },
)
```

#### CLI (`tiferet`)

```bash
tiferet app add-session --id web_api --name "Web API Session" --description "Main web API application session"
```

---

### 2. CLI Domain (`cli`)

Manages CLI command definitions, command groups, and argument specifications.

- **Available features**: `cli.add_command`, `cli.list_commands`, `cli.get_command`, `cli.delete_command`
- **CLI group**: `tiferet cli <command>`

#### Python (`AdminApp`)

```python
from tiferet import AdminApp

admin = AdminApp()
admin.run(
    'cli.add_command',
    data={
        'group_key': 'reports',
        'key': 'generate',
        'name': 'Generate Report',
        'description': 'Generate summary report',
    },
)
```

#### CLI (`tiferet`)

```bash
tiferet cli add-command --group-key reports --key generate --name "Generate Report" --description "Generate summary report"
```

---

### 3. Error Domain (`error`)

Manages structured error definitions, multilingual error messages, and error codes.

- **Available features**: `error.add`, `error.list_errors`, `error.get_error`, `error.delete_error`
- **CLI group**: `tiferet error <command>`

#### Python (`AdminApp`)

```python
from tiferet import AdminApp

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
tiferet error add --id INVALID_TOKEN_ID --name "Invalid Token" --message "The provided authentication token is invalid." --additional-messages es_ES="El token de autenticación proporcionado no es válido."
```

---

### 4. Feature Domain (`feature`)

Manages feature workflow definitions, steps, and feature parameters.

- **Available features**: `feature.add`, `feature.add_step`, `feature.list_features`, `feature.get_feature`, `feature.delete_feature`
- **CLI group**: `tiferet feature <command>`

#### Python (`AdminApp`)

```python
from tiferet import AdminApp

admin = AdminApp()

# Step 1: Define the feature workflow
admin.run(
    'feature.add',
    data={
        'id': 'user.create',
        'name': 'Create User Workflow',
        'description': 'Validates and registers a new user',
    },
)

# Step 2: Add a step to the workflow
admin.run(
    'feature.add_step',
    data={
        'feature_id': 'user.create',
        'service_id': 'validate_user_evt',
        'name': 'Validate User Step',
        'parameters': {'mode': 'strict'},
    },
)
```

#### CLI (`tiferet`)

```bash
tiferet feature add --id user.create --name "Create User Workflow" --description "Validates and registers a new user"
tiferet feature add-step --feature-id user.create --service-id validate_user_evt --name "Validate User Step" --parameters mode=strict
```

---

### 5. Service / DI Domain (`service`)

Manages feature-level service registrations, constructor parameters, and flagged overrides.

- **Available features**: `service.set_dependency`, `service.list_services`, `service.get_service`, `service.delete_service`
- **CLI group**: `tiferet service <command>`

#### Python (`AdminApp`)

```python
from tiferet import AdminApp

admin = AdminApp()
admin.run(
    'service.set_dependency',
    data={
        'registration_id': 'validate_user_evt',
        'module_path': 'app.events.user',
        'class_name': 'ValidateUserEvent',
        'parameters': {'timeout': '5.0'},
    },
)
```

#### CLI (`tiferet`)

```bash
tiferet service set-dependency --registration-id validate_user_evt --module-path app.events.user --class-name ValidateUserEvent --parameters timeout=5.0
```

---

### 6. Logging Domain (`logging`)

Manages logging formatters, handlers, loggers, and logging configuration.

- **Available features**: `logging.add_logger`, `logging.list_loggers`, `logging.get_logger`, `logging.delete_logger`
- **CLI group**: `tiferet logging <command>`

#### Python (`AdminApp`)

```python
from tiferet import AdminApp

admin = AdminApp()
admin.run(
    'logging.add_logger',
    data={
        'logger_id': 'app.audit',
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
)
```

#### CLI (`tiferet`)

```bash
tiferet logging add-logger --logger-id app.audit --level INFO --handlers console file
```

---

## Worked Example: Pairing a New Domain Event with Config Entries

When a new domain event module is authored (e.g. `VerifyPaymentEvent`), three corresponding entries must be configured in `config.yml` to make it operational:

1. **Error Definition** (`error.add`): Error constant and localized message for failure modes.
2. **Service Registration** (`service.set_dependency`): DI registration mapping the event ID to its class.
3. **Feature Step** (`feature.add_step`): Step entry referencing the service ID within a feature workflow.

### Complete Python script

```python
from tiferet import AdminApp

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

# 2. Register service dependency in DI
admin.run(
    'service.set_dependency',
    data={
        'registration_id': 'verify_payment_evt',
        'module_path': 'app.events.payment',
        'class_name': 'VerifyPaymentEvent',
        'parameters': {'gateway_timeout': '10.0'},
    },
)

# 3. Create or ensure feature workflow exists
admin.run(
    'feature.add',
    data={
        'id': 'payment.checkout',
        'name': 'Payment Checkout Feature',
    },
)

# 4. Attach domain event as a feature step
admin.run(
    'feature.add_step',
    data={
        'feature_id': 'payment.checkout',
        'service_id': 'verify_payment_evt',
        'name': 'Verify Payment Step',
        'parameters': {'require_3ds': 'true'},
    },
)
```

---

## Canonical Source

For full architectural details, resolver flag routing, and detailed blueprint specs, see:
- [docs/guides/admin.md](../../../guides/admin.md) — Admin Support Strategies and Patterns
- [docs/core/blueprints.md](../../../core/blueprints.md) — Blueprint Architecture and Entry Points
