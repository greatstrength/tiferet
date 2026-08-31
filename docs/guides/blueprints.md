# Blueprints – Composition Strategy

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/blueprints/`

## Overview

Blueprints create a ready-to-run session from an interface id without making
the caller construct caches, containers, or handlers. The standard app
entrypoint is `app.build_app`, exported as `App`; `core.py` holds the reusable
composition operations it invokes.

**Vision:** See `docs/core/blueprints.md` for blueprint placement and
artifact conventions.

## Ubiquitous Language

- **Bootstrap cache** — the shared, default-seeded `CacheContext`.
- **App service container** — the singleton container composed from defaults
  and the selected session's overrides.
- **Feature resolver** — the per-flag dependency resolver built from that
  container.
- **Runtime handler** — a callable supplied to `AppSessionContext` for one
  step of its runtime pipeline.
- **Dialect** — a standard app, CLI, or admin blueprint surface that shares
  composition helpers while selecting its own session behavior.

<a id="build-app"></a>
## Standard App Entry

`tiferet/blueprints/app.py::build_app()` is the public `App` entrypoint.
It builds the shared cache, resolves the app session, composes the standard
session context, validates that result, and returns it.

<a id="build-app-session-context"></a>
`app.build_app_session_context()` owns standard app realization. It builds the
container and resolver, then delegates common handler wiring to
`core.compose_session_context()`. The context receives a logger builder,
feature executor, request builder, error handler, and response builder rather
than importing sibling contexts or DI implementations itself.

## Cache-First Resolution

`core.build_cache()` seeds errors, app services, app constants, app sessions,
and logging settings. `core.get_app_session()` checks the app-session cache
first, so built-in sessions resolve without loading consumer configuration; a
miss composes the configured app service and invokes `GetAppSession`.

Before singleton construction, `build_app_service_container()` merges these
cache defaults with the app session's declarations. Session values win, so a
default service always receives the final constant values when it is wired.

## Shared Core and Specialized Dialects

`core.py` is the shared composition library, not the home of the public app
entrypoint. `app.py` selects `AppSessionContext`; `cli.py` selects
`CliSessionContext` and provides its parser plus CLI request/response handlers;
the admin modules provide their corresponding admin variants.

A new dialect should reuse the shared core operations and supply only the
context type or handlers that differ. It must not reimplement feature
execution, error formatting, or cache mechanics inside the blueprint.

## Boundaries

**Inside this domain:** construction order, cache/container/resolver
composition, and handler wiring.
**Outside this domain:** domain operations and feature-step behavior
(`events/` and `contexts/`), service implementation (`repos/` and `utils/`),
and dependency-provider internals (`di/`).

## Related Documentation

- [../core/blueprints.md](../core/blueprints.md) — blueprint reference
- [contexts.md](contexts.md) — session-context responsibilities
