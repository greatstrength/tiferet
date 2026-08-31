---
name: tiferet-code-architecture
description: Understand the Tiferet prototype package boundaries before a change spans multiple packages or introduces a new runtime-construction relationship.
---

# Architecture — Tiferet Prototype

## When to use

Read this with `tiferet-code-style` before multi-package implementation or
when deciding where a new artifact belongs.

## Package Boundaries

- `assets` and `domain` do not import another Tiferet package.
- `mappers` depends on `domain`.
- `interfaces` owns service contracts; `utils` and `repos` implement them.
- `events` performs domain operations using injected dependencies.
- `contexts` owns runtime behavior and may invoke events.
- `di` assembles dependency providers without importing assets, events,
  repositories, contexts, or blueprints.
- `blueprints` own top-level composition and may depend on assets, contexts,
  DI, and bootstrap events; they do not implement domain behavior.

## Reverse Shapes

Preserve a boundary with an injected callable or handler rather than an
illegal import. `get_dependency` resolves feature services without coupling a
context to a DI implementation. `AppSessionContext` receives logger, feature,
request, error, and response handlers from blueprint composition instead of
constructing its collaborators.

## Standard Runtime Flow

`App` resolves to `tiferet.blueprints.app.build_app`. It builds a default-seeded
cache, resolves an app session, and delegates session realization to
`app.build_app_session_context`. Shared functions in `blueprints/core.py` build
the app container and resolver, then `compose_session_context` wires the
runtime handlers and binds the session. Feature execution resolves step
dependencies through the injected resolver.

## Canonical Sources

- `AGENTS.md`
- `docs/core/blueprints.md`
- `tiferet-code-style`
