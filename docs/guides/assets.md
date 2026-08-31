# Assets – Catalog and Alias Strategy

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/assets/`

## Overview

Assets gives every layer one stable vocabulary for framework defaults and
domain-error definitions. Its module catalogs remain primitive data; contexts
and blueprints reconstitute and consume that data at runtime.

**Vision:** See `docs/core/assets.md` for the package layout and artifact
constraints this guide distills.

## Ubiquitous Language

- **Root asset alias** — `a`, the first `tiferet` root export, bound to
  `tiferet.assets`.
- **ID constant** — the `SCREAMING_SNAKE_CASE` key for one catalog entry.
- **Data constant** — factory-built primitive data for that entry.
- **Group mapping** — an ID-to-data catalog such as `CORE_DEFAULT_SERVICES`.
- **Cache seeding** — a context decorator’s conversion of a group mapping into
  cached domain objects or scalar constants.

## The Root Alias

Consumers import framework assets with `from tiferet import a`. Framework
modules use `from .. import a`, so public and internal callers name the same
object. This is a narrowly ordered root-package contract: `a` is bound before
the root imports packages that consume it.

The alias is only for framework assets. It neither imports nor defines a
consumer application’s own assets package.

## The Catalog Pattern

An assets module names an ID constant, creates the corresponding primitive data
with a `create_*` factory, and adds the pair to its group mapping. For example,
`app.py` holds the services and constants that core bootstrapping uses; `error.py`
holds domain-error defaults; `feature.py`, `cli.py`, and `logging.py` provide
their respective default definitions.

Assets stops at data. `add_default_*` decorators in `contexts/` provide the
runtime conversion and cache namespace; blueprints decide when that cache is
built.

## When to Deviate

Do not introduce a catalog simply to wrap one unrelated primitive. Use a named
constant or factory when no stable collection of related default definitions is
needed. Do not place infrastructure-error codes in `error.py`; those remain
beside their service raise sites.

## Boundaries

**Inside this domain:** asset aliases, primitive default catalogs, factories,
and standalone framework exceptions.
**Outside this domain:** cache construction and domain-object reconstitution
(`contexts/`), and application composition (`blueprints/`).

## Related Documentation

- [../core/assets.md](../core/assets.md) — assets code-style constraints
- [blueprints.md](blueprints.md) — bootstrap composition
- [errors.md](errors.md) — domain error behavior
