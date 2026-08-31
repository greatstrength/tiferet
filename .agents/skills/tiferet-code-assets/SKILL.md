---
name: tiferet-code-assets
description: Apply prototype assets conventions when modifying constants, exception classes, or bootstrap-default catalogs in a Tiferet-family repository.
---

# Assets Code Style — Tiferet Prototype

## When to use

Read this before changing `tiferet/assets/` on the prototype strand. Read
`tiferet-code-style` first for the shared artifact and spacing rules.

## Layer Boundary

Assets is dependency-light: its modules do not import another Tiferet package.
It contains only imports, constants, stateless functions, standalone classes,
and package exports. Domain models, events, services, mappers, repositories,
contexts, and blueprint orchestration belong elsewhere.

## Root Alias

`tiferet/__init__.py` exports `a` first and binds it to `tiferet.assets`.
Consumer code imports framework assets with `from tiferet import a`; framework
code uses `from .. import a`. Do not reuse `a` for a consumer-local assets
module or create a competing root asset alias.

## Catalogs and Exports

- Use `SCREAMING_SNAKE_CASE` names for constants.
- Build structured default entries through `create_*` factories in `core.py`.
- Keep related catalogs in `ids`, `data`, and `groups` sections when the
  collection has a stable multi-entry shape.
- `error.py` holds catalogued domain outcomes only; infrastructure codes remain
  with their service raise sites.
- `app.py`, `feature.py`, `cli.py`, `di.py`, and `logging.py` hold their
  respective bootstrap/default data.
- Exports occur only in `assets/__init__.py` under `# *** exports`.

## Canonical Sources

- `docs/core/assets.md`
- `docs/guides/assets.md`
- `tiferet-code-style`
