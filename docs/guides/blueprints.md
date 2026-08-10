# Blueprints – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/blueprints/`  
**Version:** 2.0.0

## Overview

Blueprints are the top-level orchestration layer in Tiferet. They serve as the primary public entry point for applications, providing module-level functions that orchestrate service loading, default configuration, and interface resolution.

A blueprint is responsible for:

- Loading the application service (repository)
- Preparing default services and constants
- Resolving interfaces via domain events
- Composing the app service container and feature-level `ServiceResolver` via the core composition functions
- Executing features through the resolved interface context

The canonical example is `build_app` in `tiferet/blueprints/core.py` (exported as `App`). The framework's own built-in sessions (`admin`, `admin_cli`) are composed by a parallel pair of blueprints, `tiferet/blueprints/admin.py` / `admin_cli.py` — see the Admin Blueprints section below.

## Role of Blueprints in the Architecture

Blueprints sit at the highest level of the runtime graph. They are what application code interacts with directly:

```python
from tiferet import App

app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 5, 'b': 3})
```

Key responsibilities:

- **Service loading** — dynamic import of the app service (usually a repository)
- **Default configuration** — injecting `CORE_DEFAULT_SERVICES` and `CORE_DEFAULT_CONSTANTS` from `assets.app` (`a.app`)
- **Session resolution** — calling `GetAppSession` and validating the result
- **Execution** — delegating to `AppSessionContext.run()`

Blueprints are intentionally **thin** — they coordinate rather than implement business logic.

<a id="build-app"></a>
## The build_app Blueprint

`core.build_app` is the single-call entry point (exported as `App`). It chains smaller `core.py` composition functions in a fixed order:

```python
def build_app(interface_id, module_path=..., class_name=..., **parameters) -> AppSessionContext:
    cache = build_cache()                                              # errors + app services + constants
    app_session = get_app_session(interface_id, cache, module_path, class_name, **parameters)
    app_session_context = build_app_session_context(app_session, cache)
    if not isinstance(app_session_context, AppSessionContext):
        TiferetError.raise_error(a.const.INVALID_APP_SESSION_TYPE_ID, ..., interface_id=interface_id)
    return app_session_context
```

### 1. Shared Cache

`build_cache()` returns a `CacheContext` pre-seeded (via stacked decorators) with the framework's default errors, app service dependencies, and bootstrap constants, each namespaced under its own cache-key prefix.

### 2. App Session Resolution

`get_app_session(interface_id, cache, ...)` composes the app service through `create_app_service` and loads the session via the `GetAppSession` event, which raises `APP_SESSION_NOT_FOUND` when the session is absent — the core path has no built-in fallback.

### 3. Context Composition

`build_app_session_context(app_session, cache)`:

- builds the singleton app service container from the cache defaults merged with the session's own constants/services, session winning (`build_app_service_container`);
- composes the feature-level `ServiceResolver` (`build_service_resolver`, caching the app container under the `app` flag);
- hardcodes `context_cls = AppSessionContext` (blueprint functions are the declarative owner of context class selection — a session's `module_path`/`class_name` fields are no longer consulted at runtime), resolves any remaining event collaborators from the app container, wires the five hub handler callables (`build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, `response_handler`), and constructs the context via `BaseContext.from_domain`.

No `apply_defaults` is called on the core path — all framework defaults come from the cache.

<a id="build-cli"></a>
## The build_cli Blueprint

The CLI blueprint (`build_cli`, `tiferet/blueprints/cli.py`, exported as `CLI`) does not delegate through `core.build_app` — it runs its own parallel composition chain, substituting `CliSessionContext` for `AppSessionContext` throughout. Argparse parsing and CLI-specific request/response handling live in blueprint-level closures (`parse_cli_args_handler`, `create_cli_request_context`, `cli_response_handler`), not in a context method.

### Usage

```python
from tiferet import CLI

if __name__ == '__main__':
    CLI('basic_calc_cli', app_config='config.yml')
```

### Build Procedure

`build_cli(interface_id, argv=None, ...)` follows these steps:

1. `build_cli_cache()` — builds the shared cache via `core.build_cache`, then layers `add_default_cli_commands(a.cli.ADMIN_DEFAULT_COMMANDS)` on top so CLI command definitions are seeded alongside the standard defaults.
2. `core.get_app_session(interface_id, cache, ...)` — resolves the app session exactly as the core path does.
3. `build_cli_session_context(app_session, cache)` — parallel to `core.build_app_session_context`, but hardcodes `CliSessionContext`, resolves `list_commands_evt`/`get_parent_args_evt` to build the injected `parse_cli_args` closure, and overrides the `create_request_handler`/`response_handler` slots with `create_cli_request_context`/`cli_response_handler`.
4. `cli_context.run(argv)` — parses `argv` via the injected closure (argparse failures exit `2`), dispatches through the inherited `AppSessionContext.run`, and exits `1` on an unhandled `TiferetAPIError`.

There is no interface-config opt-in (no `module_path`/`class_name` declaration selects the CLI context) — any interface resolved through the `CLI`/`build_cli` entry point always gets a `CliSessionContext`.

## When to Create a New Blueprint

Create a new blueprint when you need a specialized entry point:

- Web blueprint — for Flask/FastAPI integration
- Test blueprint — for integration testing with mocked services

If you find yourself repeating the same loading and wiring logic in multiple scripts, extract it into a dedicated blueprint.

## Blueprint vs Context

| Concern | Blueprint | Context |
| --- | --- | --- |
| Public API | Yes (`App('basic_calc')`) | Internal (used by blueprint) |
| Service loading | Yes | No |
| Default config injection | Yes | No |
| Feature execution | Delegates to interface context | Yes (`execute_feature`, `run`) |
| Lifecycle | Application-level | Per-interface |

Blueprints are **application-level**; contexts are **interface-level**.

## Best Practices

### 1. Single-call Entry Point

`build_app` resolves and realizes in one call:

```python
app = App('basic_calc', app_config='config.yml')
```

### 2. Consistent Error Handling

Use framework constants and `TiferetError.raise_error()` for all failure paths.

### 3. Keep Blueprints Thin

Blueprints should **not** contain domain logic — only orchestration, wiring, and delegation.

### 4. Inject `get_dependency` into the Context

Compose a `ServiceResolver` from the app service container (`build_service_resolver`) and inject its `get_dependency` handler so contexts resolve feature-step services without coupling to the DI engine (`build_app_session_context` does this):

```python
resolver = build_service_resolver(app_container)
return context_cls.from_domain(app_session, get_dependency=resolver.get_dependency, ...)
```

<a id="admin-blueprints"></a>
## Admin Blueprints

`tiferet/blueprints/admin.py` and `tiferet/blueprints/admin_cli.py` compose the built-in admin app and admin CLI sessions (`admin` / `admin_cli`) that ship with the framework rather than being defined in a consumer's config file. Both are **parallel, not derived** implementations of the core path: they mirror `core.build_app`/`core.build_app_session_context` function-for-function but substitute an admin-aware cache and resolver at each step.

### `admin.py` — the admin app session

- **`build_cache()`** — stacks `add_default_admin_services`/`add_default_admin_constants`/`add_default_features`/`add_default_errors` (seeded from `a.app.ADMIN_DEFAULT_SERVICES`/`ADMIN_DEFAULT_CONSTANTS`, `a.feat.ADMIN_DEFAULT_FEATURES`, `a.error.ADMIN_DEFAULT_ERRORS`) on top of `core.build_cache`, giving the admin blueprints their full catalog without touching a consumer config file.
- **`build_admin_service_resolver(app_container, cache, parse_parameter=core.parse_parameter)`** — parallel to `core.build_service_resolver`, but builds a **second** `DIAppServiceContainer` from the cache-seeded admin services/constants and registers it under both the `'admin'` flag and as the default (empty-flag) container, so admin feature steps resolve without explicit flag annotations.
- **`build_admin_app_session_context(app_session, cache, **context_kwargs)`** — parallel to `core.build_app_session_context`, substituting `build_admin_service_resolver` for `core.build_service_resolver`. Hardcodes `context_cls = AppSessionContext` (no declarative context-class resolution, since the admin app path only ever composes the base hub).
<a id="build-admin-app"></a>
- **`build_admin_app(interface_id=a.app.TIFERET_ADMIN_ID, **parameters)`** — the single-call entry point, parallel to `core.build_app`.

### `admin_cli.py` — the admin CLI session

- **`build_cache()`** — extends `admin.build_cache` with `add_default_cli_commands(a.cli.ADMIN_DEFAULT_COMMANDS)`, adding the built-in admin CLI command definitions.
- **`build_admin_cli_session_context(app_session, cache)`** — parallel to the consumer-facing CLI session composition, substituting `admin.build_admin_service_resolver` and wiring CLI-specific `create_request_handler`/`response_handler` slots (`create_cli_request_context`/`cli_response_handler`).
<a id="build-admin-cli"></a>
- **`build_admin_cli(app_config, argv=None)`** — resolves the `admin_cli` session, **re-seeds its constants** so every config-file-backed repo (`app_config`, `cli_config`, `di_config`, `error_config`, `feature_config`, `logging_config`) points at the consumer's `app_config` path instead of the seeded `'config.yml'` placeholders, then dispatches `argv` via `CliSessionContext.run`.
- **`main()`** — the `tiferet` console-script entry point; pre-parses `--config` before delegating to `build_admin_cli`.

### Known gap: `build_logger_handler` is not wired

Unlike `core.build_app_session_context` (which wires `build_logger_handler=build_logger_handler(cache, resolver.get_dependency)` into every session's handler dict), **neither** `build_admin_app_session_context` nor `build_admin_cli_session_context` supplies a `build_logger_handler` slot. Both blueprints predate the fifth handler slot and were never updated when it was introduced (they also never wired the earlier `logging_context` predecessor).

The practical effect: an admin or admin-CLI session's first `run()` call hits `AppSessionContext.build_logger`'s unwired-handler guard and raises a clean `APP_ERROR` naming the missing `build_logger_handler` slot — a **strict improvement** over the previously unguarded `AttributeError` this gap produced before the guard existed, but still a gap relative to the core path's logging behavior. Closing it (wiring `build_logger_handler(cache, resolver.get_dependency)` into both admin handler dicts, mirroring the core path) is left as a follow-up item; it is not yet scheduled.

## Related Documentation

- [docs/core/blueprints.md](../core/blueprints.md) — detailed blueprint implementation reference
- [docs/guides/domain/app.md](../guides/domain/app.md) — application-level configuration and runtime orchestration
- [docs/guides/events/app.md](../guides/events/app.md) — app event usage in interface resolution
- [docs/core/di.md](../core/di.md) — dependency injection and service provider architecture
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
