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

Both entry points pre-seed an admin bootstrap cache containing the framework's full six-domain CRUD catalog and wire an admin service resolver that resolves admin-scoped feature steps from an admin container by default.

## Ubiquitous Language

- **Admin Session**: A built-in application session (`admin` or `admin_cli`) configured with default repositories and management workflows.
- **Admin CLI**: The `tiferet` command-line entry point that pre-parses `--config` options and dispatches administrative CLI requests.
- **Six Admin Domains**: The functional CRUD management domains exposed by the admin catalog: App, CLI, Error, Feature, Service/DI, and Logging.
- **Admin-Scoped Resolution**: Service resolution where default feature steps resolve against the admin service container rather than consumer application overrides.

## Building an Admin Session

The `build_admin_app` blueprint function (exported as `AdminApp`) builds a complete admin session context:

```python
from tiferet import AdminApp

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
tiferet app list-sessions

# Manage a specific configuration file
tiferet --config custom_config.yml error list-errors
```

Programmatically, `build_admin_cli` re-seeds the resolved session's constants so every config-file repository points directly at the consumer-supplied configuration file:

```python
from tiferet import AdminCLI

# Execute an administrative CLI command against a custom config file
response = AdminCLI(app_config='app_config.yml', argv=['feature', 'list-features'])
```

## The Six Admin Domains

The admin catalog spans six configuration management domains:

1. **App Domain (`app`)**: Manages application interface definitions, session parameters, and app constants.
2. **CLI Domain (`cli`)**: Manages CLI command definitions, command groups, and argument specifications.
3. **Error Domain (`error`)**: Manages structured error definitions, multilingual error messages, and codes.
4. **Feature Domain (`feature`)**: Manages feature workflow definitions, steps, and feature parameters.
5. **Service/DI Domain (`service`)**: Manages feature-level service registrations, constructor parameters, and flagged overrides.
6. **Logging Domain (`logging`)**: Manages logging formatters, handlers, loggers, and logging configuration.

All flat-map arguments across administrative commands accept key-value dict pairs in `key=value` format when invoked via the CLI, eliminating the need for raw JSON strings.

## Worked Examples

Below are side-by-side Python (`AdminApp`) and CLI (`tiferet`) worked examples for all six admin domains.

### 1. App Domain

Adding a new application session definition:

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

Equivalent CLI command:

```bash
tiferet app add-session --id web_api --name "Web API Session" --description "Main web API application session"
```

### 2. CLI Domain

Adding a new CLI command to a command group:

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

Equivalent CLI command:

```bash
tiferet cli add-command --group-key reports --key generate --name "Generate Report" --description "Generate summary report"
```

### 3. Error Domain

Adding a new structured error with additional localized messages using `key=value` pairs:

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

Equivalent CLI command using flat-map dict syntax (`--additional-messages es_ES="El token..."`):

```bash
tiferet error add --id INVALID_TOKEN_ID --name "Invalid Token" --message "The provided authentication token is invalid." --additional-messages es_ES="El token de autenticación proporcionado no es válido."
```

### 4. Feature Domain

Adding a feature step to a feature workflow:

```python
from tiferet import AdminApp

admin = AdminApp()
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

Equivalent CLI command using flat-map dict parameters (`--parameters mode=strict`):

```bash
tiferet feature add-step --feature-id user.create --service-id validate_user_evt --name "Validate User Step" --parameters mode=strict
```

### 5. Service / DI Domain

Registering a feature-level service dependency:

```python
from tiferet import AdminApp

admin = AdminApp()
admin.run(
    'service.set_dependency',
    data={
        'registration_id': 'user_service',
        'module_path': 'app.services.user',
        'class_name': 'UserService',
        'parameters': {'timeout': '5.0'},
    },
)
```

Equivalent CLI command using flat-map dict parameters (`--parameters timeout=5.0`):

```bash
tiferet service set-dependency --registration-id user_service --module-path app.services.user --class-name UserService --parameters timeout=5.0
```

### 6. Logging Domain

Adding a logger configuration:

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

Equivalent CLI command:

```bash
tiferet logging add-logger --logger-id app.audit --level INFO --handlers console file
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
