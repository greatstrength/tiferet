# Blueprints in Tiferet

## Overview

Blueprints are module-level orchestration functions. They assemble caches, containers, resolvers, and session contexts; domain behavior remains in the contexts and events they wire together.

The standard application entrypoint lives in `tiferet/blueprints/app.py`:

- `build_app_session_context()` builds the standard `AppSessionContext`;
- `build_app()` is the public single-call entrypoint exported as `App`.

`tiferet/blueprints/core.py` owns the composition primitives reused by app, CLI, and admin dialects. This separation keeps the standard app boundary small without duplicating cache or DI wiring.

## Standard App Composition

`app.build_app(interface_id, ...)` performs this fixed sequence:

1. `core.build_cache()` creates a `CacheContext` seeded with default errors,
 app services, app constants, app sessions, and logging settings.
2. `core.get_app_session()` returns a cache-seeded default session when one
 exists; otherwise it composes the app service and invokes `GetAppSession`.
3. `app.build_app_session_context()` builds the app service container and
 feature-level resolver, then calls `core.compose_session_context()`.
4. The resulting `AppSessionContext` is type-checked before `App` returns it.

`build_app_session_context()` binds the loaded session through `AppSessionContext.from_domain()` and supplies the standard request and response handlers. `compose_session_context()` supplies the remaining runtime handlers: logger construction, feature execution, error handling, and any declared collaborators that the app container can resolve.

## Shared Core Composition

`core.py` contains reusable blueprint operations:

- `build_cache()` and `get_app_session()` establish bootstrap state;
- `build_app_service_container()` merges cache defaults with a session's own
 services and constants before constructing the singleton container;
- `build_service_resolver()` registers that container under the `app` flag;
- `compose_session_context()` wires the five handler slots and binds a session
 to the requested context class;
- `get_error()`, `get_feature()`, and `build_logger_handler()` resolve and
 cache runtime objects lazily.

The core module is not the standard application entrypoint. It exists so `app.py`, `cli.py`, `admin.py`, and `admin_cli.py` can reuse one composition vocabulary while choosing their own session-context and request/response surfaces.

## CLI and Admin Blueprints

`cli.py` builds a CLI cache, composes `CliSessionContext`, and injects the argument-parsing plus CLI request/response handlers before dispatching `argv`. `admin.py` and `admin_cli.py` provide the parallel built-in admin surfaces and their admin-aware cache/resolver variants.

These dialects reuse core helpers where their contracts match. They do not move the standard app entrypoint back into `core.py`.

## Blueprint Conventions

- Blueprints are functions under `# *** blueprints`; they are not classes.
- Pure input-to-value helpers belong under `# *** functions` above the
 blueprint group.
- Blueprints may import `assets`, `contexts`, `di`, and bootstrap events; they
 must not implement domain logic or reach directly into repositories, utils,   mappers, or service interfaces.
- Errors representing a domain outcome use `TiferetError.raise_error()`.

## Related Documentation

- [../guides/blueprints.md](../guides/blueprints.md) — composition strategy
- [code_style.md](code_style.md) — artifact-comment conventions
