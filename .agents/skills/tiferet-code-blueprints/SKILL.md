---
name: tiferet-code-blueprints
description: Apply prototype blueprint composition conventions when modifying public entrypoints, cache construction, or session-context wiring.
---

# Blueprints Code Style — Tiferet Prototype

## When to use

Read this after `tiferet-code-style` when modifying `tiferet/blueprints/`.
Blueprints orchestrate; they do not contain domain logic.

## Module Roles

- `app.py` owns `build_app_session_context` and `build_app`, exported as `App`.
- `core.py` owns shared cache, session, container, resolver, and handler
  composition helpers.
- `cli.py` owns the consumer CLI entrypoint and its CLI-specific handlers.
- `admin.py` and `admin_cli.py` own the built-in admin dialects.

## Standard App Path

`app.build_app` calls `core.build_cache`, `core.get_app_session`, and
`app.build_app_session_context`. The cache is seeded with errors, app services,
app constants, app sessions, and logging settings. Session lookup is cache-first
and falls back to the configured app service.

`app.build_app_session_context` composes the app service container and feature
resolver, then calls `core.compose_session_context`. That helper supplies the
five runtime handlers: logger construction, feature execution, request
construction, error handling, and response building.

## Structure and Boundaries

Use `# *** functions` for pure input-to-value helpers and `# *** blueprints`
for orchestration functions. Blueprints may import assets, contexts, DI, and
bootstrap events. They must not directly import repositories, utilities,
mappers, or service interfaces.

## Canonical Sources

- `docs/core/blueprints.md`
- `docs/guides/blueprints.md`
- `tiferet-code-style`
