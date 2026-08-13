# Blueprints – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/blueprints/`  
**Version:** 2.0.0

## Overview

Blueprints are the top-level orchestration layer in Tiferet v2.0+. They serve as the primary public entry point for applications, providing module-level functions that replace the previous class-based `AppBuilder`/`CliBuilder` pattern.

A blueprint is responsible for:

- Loading the application service (repository)
- Preparing default services and constants
- Resolving sessions via domain events
- Wiring dependency injection and the five required context handlers
- Executing features through the resolved session context

The canonical example is `build_app` in `tiferet/blueprints/core.py` (exported as `App`). Sibling entry points cover CLI (`build_cli` / `CLI`), admin app (`build_admin_app` / `AdminApp`), and admin CLI (`build_admin_cli` / `AdminCLI`).

## Role of Blueprints in the Architecture

Blueprints sit at the highest level of the runtime graph. They are what application code interacts with directly:

```python
from tiferet import App

app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 5, 'b': 3})
```

Key responsibilities:

- **Service loading** — dynamic import of the app service (usually a repository)
- **Default configuration** — seeding cache catalogs and merging session overrides
- **Session resolution** — calling `GetAppSession` / cache-seeded defaults and validating the result
- **Handler wiring** — injecting `build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, and `response_handler`
- **Execution** — delegating to `AppSessionContext.run()` or `CliSessionContext.run()`

Blueprints are intentionally **thin** — they coordinate rather than implement business logic.

## The build_app Blueprint

`build_app` follows a clear, composable pattern built from smaller blueprint functions in `tiferet/blueprints/core.py`:

### 1. Cache and catalogs

```python
cache = build_cache()  # default errors, app services, constants, logging settings, ...
```

### 2. Session resolution

```python
app_session = get_app_session(interface_id, cache, app_config='config.yml')
```

### 3. Container + resolver

```python
app_container = build_app_service_container(cache, app_session)
resolver = build_service_resolver(app_container)  # app container under 'app' flag
```

### 4. Five-handler session context

```python
handlers = dict(
    build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
    execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
    raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
    response_handler=response_handler,
    create_request_handler=create_session_request,
)
context = AppSessionContext.from_domain(
    app_session,
    get_dependency=resolver.get_dependency,
    cache=cache,
    **handlers,
)
```

### 5. High-level entry point

```python
def build_app(interface_id, ...) -> AppSessionContext:
    cache = build_cache()
    app_session = get_app_session(interface_id, cache, ...)
    return build_app_session_context(app_session, cache)
```

### Logging helpers

- `merge_logging_settings(cache, formatters, handlers, loggers)` — pure merge of repository logging sections over cache-seeded defaults by `.id`.
- `build_logger_handler(cache, get_dependency)` — returns a closure that caches loggers under `LOGGER_CACHE_PREFIX`, listing configs on miss, merging via `merge_logging_settings`, and building through `LoggingContext.from_domain(...).build_logger()`.

### Feature execution helpers

- `create_feature_context(get_dependency, cache, feature_id) -> FeatureContext` — resolves the feature and returns a **domain-bound** context (not a `(Feature, FeatureContext)` tuple).
- `execute_feature_handler(...)` — builds that context and calls `feature_context.execute_feature(request, *flags, **kwargs)` with **no** explicit `feature` argument.

## The build_cli Blueprint

The CLI blueprint is a thin entrypoint over a `CliSessionContext`. Argparse wiring lives behind an injected `parse_cli_args` closure; runtime execution reuses the hub's five handlers (including `build_logger_handler` — there is no standalone `LoggingContext` on the session).

### Usage

```python
from tiferet import CLI

if __name__ == '__main__':
    CLI('basic_calc_cli', app_config='config.yml')
```

### Build Procedure

`build_cli(interface_id, argv=None, ...)` follows these steps:

1. Build the CLI session context with all five handlers plus `parse_cli_args`.
2. Call `cli_context.run(argv)`.
3. On parse failure, exit `2`; on `TiferetAPIError`, exit `1`.

Consumer CLI sessions opt in with `module_path: tiferet.contexts.cli` / `class_name: CliSessionContext`.

## Building the Admin Application

The admin blueprints expose the framework's built-in configuration-management session without requiring a consumer-defined `admin` entry in `config.yml`.

### Admin App (`build_admin_app` / `AdminApp`)

```python
from tiferet.blueprints import AdminApp

admin = AdminApp()  # defaults to TIFERET_ADMIN_ID
response = admin.run('app.list')
```

What it does:

1. `admin.build_cache()` — core catalogs plus `ADMIN_DEFAULT_SERVICES`, `ADMIN_DEFAULT_CONSTANTS`, `ADMIN_DEFAULT_FEATURES`, and `ADMIN_DEFAULT_ERRORS`.
2. `get_app_session(TIFERET_ADMIN_ID, cache)` — cache-seeded built-in session.
3. `build_admin_service_resolver` — dual-container resolver:
   - app container under the `'app'` flag
   - admin container under `'admin'` **and** as the empty-flag default
4. `build_admin_app_session_context` — same five handlers as core, but with the admin resolver so feature steps resolve admin-scoped services by default.

```python
resolver.add_container(app_container, 'app')
resolver.add_container(admin_container, 'admin')
resolver.add_container(admin_container)  # default
```

### Admin CLI (`build_admin_cli` / `AdminCLI`)

```python
from tiferet.blueprints import AdminCLI

AdminCLI(app_config='config.yml', argv=['feature', 'list'])
```

Console usage (via `pyproject.toml` → `tiferet.blueprints.admin_cli:main`):

```bash
tiferet app list
tiferet --config custom_config.yml error list
tiferet feature add-step user.create "Validate" validate_user_evt --parameters mode=strict
```

What it does:

1. Layers `ADMIN_DEFAULT_COMMANDS` on the admin cache.
2. Resolves `TIFERET_ADMIN_CLI_ID`.
3. Re-seeds every `*_config` constant (`app_config`, `cli_config`, `di_config`, `error_config`, `feature_config`, `logging_config`) to the consumer-supplied path.
4. Wires `CliSessionContext` with the admin resolver and five handlers (including `build_logger_handler`).
5. Dispatches through `cli_context.run(argv)`.

Flat-map admin arguments use the CLI `'dict'` type (`key=value` pairs) rather than raw JSON. See [docs/guides/domain/cli.md](domain/cli.md) and the full six-domain catalog in [docs/guides/admin.md](admin.md).

## When to Create a New Blueprint

Create a new blueprint when you need a specialized entry point:

- Web blueprint — for Flask/FastAPI integration
- Test blueprint — for integration testing with mocked services
- Domain-specific admin or tooling sessions — mirror `admin.py` / `admin_cli.py` (custom cache seeders + resolver + five-handler wiring)

If you find yourself repeating the same loading and wiring logic in multiple scripts, extract it into a dedicated blueprint.

## Blueprint vs Context

| Concern | Blueprint | Context |
| --- | --- | --- |
| Public API | Yes (`App('basic_calc')`, `AdminApp()`) | Internal (used by blueprint) |
| Service loading | Yes | No |
| Default config injection | Yes | No |
| Five-handler wiring | Yes | Consumes handlers |
| Feature execution | Delegates to session context | Yes (`execute_feature`, `run`) |
| Lifecycle | Application-level | Per-session |

Blueprints are **application-level**; contexts are **session-level**.

## Best Practices

### 1. Single-call Entry Point

```python
from tiferet import App
from tiferet.blueprints import AdminApp

app = App('basic_calc', app_config='config.yml')
admin = AdminApp()
```

### 2. Consistent Error Handling

Use framework constants and `TiferetError.raise_error()` for all domain-outcome failure paths (e.g. `TiferetError.raise_error(a.error.INVALID_APP_SESSION_TYPE_ID, interface_id=interface_id)`).

### 3. Keep Blueprints Thin

Blueprints should **not** contain domain logic — only orchestration, wiring, and delegation.

### 4. Always Wire All Five Handlers

Never construct an `AppSessionContext` / `CliSessionContext` with a missing handler slot or a legacy `logging_context` constructor keyword keyword. Prefer the core helpers (`build_logger_handler`, `execute_feature_handler`, …).

### 5. Prefer Domain-Bound Feature Execution

Use `create_feature_context` → `feature_context.execute_feature(request, ...)` rather than passing a `feature` object into the context method.

## Related Documentation

- [docs/core/blueprints.md](../core/blueprints.md) — detailed blueprint implementation reference
- [docs/guides/admin.md](admin.md) — admin catalog domains and worked examples
- [docs/core/contexts.md](../core/contexts.md) — five-handler context contract
- [docs/guides/contexts.md](contexts.md) — context strategies and patterns
- [docs/guides/domain/app.md](domain/app.md) — application-level configuration and runtime orchestration
- [docs/guides/events/app.md](events/app.md) — app event usage in session resolution
- [docs/core/di.md](../core/di.md) — dependency injection and service resolver architecture
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
