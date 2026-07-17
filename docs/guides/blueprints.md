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

The canonical example is `build_app` in `tiferet/blueprints/core.py` (exported as `App`). The built-in CLI bootstrapper (`build_tiferet_cli`) uses a separate declarative bootstrap path in `tiferet/blueprints/tiferet_cli.py`.

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
- **Interface resolution** — calling `GetAppInterface` and validating the result
- **Execution** — delegating to `AppInterfaceContext.run()`

Blueprints are intentionally **thin** — they coordinate rather than implement business logic.

## The build_app Blueprint

`core.build_app` is the single-call entry point (exported as `App`). It chains smaller `core.py` composition functions in a fixed order:

```python
def build_app(interface_id, module_path=..., class_name=..., **parameters) -> AppSessionContext:
    cache = build_cache()                                              # errors + app services + constants
    app_session = get_app_session(interface_id, cache, module_path, class_name, **parameters)
    app_session_context = build_app_session_context(app_session, cache)
    if not isinstance(app_session_context, AppSessionContext):
        RaiseError.execute(a.const.INVALID_APP_SESSION_TYPE_ID, ..., interface_id=interface_id)
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
- imports the declared context class, resolves its event collaborators from the app container, wires the four hub handler callables, and constructs the context via `BaseContext.from_domain`.

No `apply_defaults` is called on the core path — all framework defaults come from the cache.

### Built-in Bootstrappers

`build_tiferet_app` (`TiferetApp`) and `build_tiferet_cli` (`TiferetCLI`) target built-in sessions (`tiferet_app` / `tiferet_cli`) that are not defined in the consumer config. They resolve through a shared `_resolve_bootstrap_session` helper (module-private in `tiferet/blueprints/tiferet_cli.py`) that falls back to the built-in session definition via `resolve_default_interface` and applies `apply_defaults`. `build_tiferet_cli` additionally uses the `_load_app_instance` / `_wire_services` declarative feature-DI bootstrap (via the `CreateServiceResolver` event) in `tiferet/blueprints/tiferet_cli.py`.

## The build_cli Blueprint

The CLI blueprint is a thin entrypoint. Argparse parsing and request derivation are owned by `CliContext` (`tiferet/contexts/cli.py`); the blueprint only resolves, realizes, and delegates.

### Usage

```python
from tiferet import CLI

if __name__ == '__main__':
    CLI('basic_calc_cli', app_config='config.yml')
```

### Build Procedure

`build_cli(interface_id, argv=None, ...)` follows these steps:

1. Build the context via `core.build_app(interface_id, ...)`. Because the interface points at `CliContext`, the composed context exposes `run_cli`.
2. Delegate to `cli_context.run_cli(argv)`, which builds the parser, parses `argv` (exiting `2` on failure), derives the feature request, dispatches through the inherited `run`, prints the response, and converts a `TiferetAPIError` into `sys.exit(1)`.

Consumer CLI interfaces opt in by declaring `module_path: tiferet.contexts.cli` / `class_name: CliContext` in their interface config.

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

Use framework constants and `RaiseError.execute()` for all failure paths.

### 3. Keep Blueprints Thin

Blueprints should **not** contain domain logic — only orchestration, wiring, and delegation.

### 4. Inject `get_dependency` into the Context

Compose a `ServiceResolver` from the app service container (`build_service_resolver`) and inject its `get_dependency` handler so contexts resolve feature-step services without coupling to the DI engine (`build_app_session_context` does this):

```python
resolver = build_service_resolver(app_container)
return context_cls.from_domain(app_session, get_dependency=resolver.get_dependency, ...)
```

(The `CreateServiceResolver` bootstrap event is used by the `_load_app_instance` path in `tiferet/blueprints/tiferet_cli.py` for the built-in CLI bootstrapper.)

## Related Documentation

- [docs/core/blueprints.md](../core/blueprints.md) — detailed blueprint implementation reference
- [docs/guides/domain/app.md](../guides/domain/app.md) — application-level configuration and runtime orchestration
- [docs/guides/events/app.md](../guides/events/app.md) — app event usage in interface resolution
- [docs/core/di.md](../core/di.md) — dependency injection and service provider architecture
- [docs/core/code_style.md](../core/code_style.md) — artifact comments and formatting
