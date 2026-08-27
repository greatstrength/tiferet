---
name: tiferet-code-architecture
description: Understand the Tiferet v2 package architecture before starting any multi-component implementation. Read this when a task spans more than one package or when deciding where a new class belongs. Covers per-package import rules, reverse-shape principles, and the runtime execution flow.
---

# Architecture – Tiferet v2

## When to use
- Before starting any implementation that touches more than one package.
- When deciding which package a new class or function belongs in.
- When verifying that import statements respect package boundaries.
- Read in combination with `tiferet-code-style` and the relevant component skill.

## Import law

These rules govern what is valid in the `# ** app` import group of each package. The full systems write-up is `docs/core/architecture.md`. This skill uses package names only.

| Package | Legal `# ** app` | Never |
|---|---|---|
| `assets` | none | any other framework package |
| `blueprints` | `assets`, `contexts`, `di`, `events` (bootstrap only) | `domain`, `interfaces`, `mappers`, `utils`, `repos` |
| `contexts` | `assets`, `domain`, siblings, `events` | `blueprints`, `interfaces`, `di`, `mappers`, `utils`, `repos` |
| `di` | `domain`, `interfaces` | `assets`, `events`, `repos`, `blueprints`, `contexts`, `mappers`, `utils` |
| `domain` | none | any framework package |
| `events` | `assets`, `domain`, `mappers`, `utils`, `interfaces` | `di`, `repos`, `contexts`, `blueprints` |
| `mappers` | `domain` | `assets`, `events`, `interfaces`, `utils`, `repos`, `contexts`, `blueprints` |
| `interfaces` | `mappers` (aggregates), sibling interfaces | `domain` when an aggregate exists; `events`, `repos`, `utils`, `contexts`, `blueprints` |
| `utils` | `interfaces`, `mappers`, siblings | `events`, `domain`, `repos`, `di`, `contexts`, `blueprints` |
| `repos` | `interfaces`, `mappers`, `utils` | `assets`, `domain`, `events`, `di`, `contexts`, `blueprints` |

**Key notes:**
- `assets` has no framework imports. Only `blueprints`, `contexts`, and `events` import it (`from .. import assets as a`). Not every package may import assets.
- `domain` has no framework imports. Mutation belongs on the aggregate in `mappers`.
- `blueprints` reach domain types via `contexts` only (`from ..contexts.feature import Feature`, never `from ..domain`). They reach service instances via `di` (`get_dependency`), never by importing `interfaces`.
- `events` on blueprints are pre-DI bootstrap only (`DomainEvent.handle` or a direct event-class import). After composition, the feature loop is `contexts` plus injected `get_dependency`.
- `contexts` may call events as a client surface. Prefer blueprint handler injection over constructing sibling contexts.
- `interfaces` import aggregates from `mappers` to type outputs. That is legal.
- `utils` may import `mappers`. Implementing a Service is optional; it is warranted when the capability is extensible and must be reachable through a declared feature step.
- `repos` are never exported. They absorb `interfaces`, `mappers`, and `utils` only.
- `di` is event-free and asset-free. A missing provider raises `ServiceError`.

## Reverse shapes

Reverse shapes preserve package boundaries when runtime construction, resolution, or a callback needs a relationship that a direct import would forbid. They are mechanisms, not general import exemptions. Use an established shape where it fits; a new shape must state the boundary it preserves and why an ordinary import is not legal.

- **Injected `get_dependency`:** contexts and blueprints resolve instances without importing `di` classes. `parse_parameter` follows the same injected-callable pattern.
- **Runtime-handler slots:** a session hub invokes blueprint-supplied handlers without constructing sibling contexts. The core app wires logger, feature-execution, request, error, and response handlers; CLI adds argument parsing, and a dialect may declare additional slots.

## Runtime flow

```
App('interface_id')                               # blueprints/core.py: build_app()
  └─ build_cache()                               # CacheContext pre-seeded with framework defaults
  └─ get_app_session(id, cache)                  # GetAppSession event → AppSession
  └─ build_app_session_context(session, cache)   # wires DI and constructs the runtime-handler hub
       └─ AppSessionContext.run(feature_id, data)
            ├─ build_request()                   # → RequestContext
            ├─ execute_feature()
            │    └─ injected execute_feature_handler
            │         └─ FeatureContext.execute_feature(request)
            │              └─ for each step:
            │                   get_dependency(service_id, *flags)
            │                       └─ DomainEvent.handle(EventCls, dependencies, **kwargs)
            │                            └─ event.execute(**kwargs) → result on request
            └─ build_response()                  # → RequestContext.handle_response()
```

## Docstrings & guides

This skill documents the import law that every guide's `## Boundaries` section relies on — cross-reference it there rather than restating it. See `tiferet-guide-docs` for the vision-tier docstring / `# >> see:` convention.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/architecture.md
