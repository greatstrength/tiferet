# DI – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/di/`  
**Version:** 2.0.0

## Overview

The DI layer is Tiferet's dependency-injection contract, split deliberately into two files: `di/core.py` declares an abstract `ServiceContainer`/`ServiceResolver` contract with zero third-party imports, and `di/dependency_injector.py` backs that contract with the `dependency-injector` library. The split means the DI *engine* is swappable — a future backend implements the same two ABCs — without touching any call site that depends on `get_dependency`. For the concrete engine classes' constructors, methods, and usage, see [docs/guides/di/dependency_injector.md](di/dependency_injector.md).

The DI layer is deliberately **event-free and asset-free**: it imports only stdlib, `dependency-injector`, `..domain`, and `..interfaces.di`/`..interfaces.core`. Being asset-free is why it raises `ServiceError` rather than a catalogued `TiferetError` — it has no access to the error catalog and forms no opinion about domain meaning. A missing provider raises `ServiceError.raise_for(...)`; a registration that resolves to nothing for the active flags is skipped rather than raised on.

## Ubiquitous Language

- **Service container** — resolves dependencies (services or constants) by id from a fixed registration set.
- **Service resolver** — the per-flag-set owner of containers; builds and caches one container per distinct flag combination.
- **Flag set** — the ordered combination of interface-, feature-, and step-level flags that selects which concrete implementation a `ServiceRegistration` resolves to.
- **Scope** — whether a provider yields a new instance per resolution (Factory) or one shared instance (Singleton).

## The ServiceContainer Contract

`ServiceContainer` (`di/core.py`) is an ABC declaring six operations: `add_service`, `add_constant`, `get_dependency`, `has_dependency`, `remove_dependency`, `load_container`. It says nothing about *how* a service is instantiated or cached — only that a container can register, resolve, check, remove, and bulk-load dependencies. `load_container` is expected to register constants before services, since services typically wire their constructor kwargs to sibling constant providers.

## The ServiceResolver Contract

`ServiceResolver` (`di/core.py`) is an ABC that is *not* purely abstract — it implements a **template method**, `get_dependency(service_id, *flags)`:

1. Normalize the flags (`normalize_flags`).
2. Look up a cached container for that exact flag combination (`get_container`).
3. On a cache miss, call the abstract `build_container(flags)` (left to concrete subclasses) and cache the result (`add_container`).
4. Resolve `service_id` from the container.

Concrete subclasses only need to implement `build_container` — the per-flag caching and lookup machinery is shared. This is why `di/dependency_injector.py`'s `DIDynamicServiceResolver` is a small class: it implements exactly one method.

## Why Two Layers

The abstract/concrete split exists so the framework's public surface (`get_dependency`, injected everywhere from `AppSessionContext` down to `FeatureContext`) never mentions `dependency_injector` by name. Swapping the underlying engine — or unit-testing against a fake `ServiceContainer`/`ServiceResolver` pair — requires no change above `di/core.py`.

## The Factory vs. Singleton Scope Decision

`di/dependency_injector.py` provides two container flavors built on the same `dependency_injector.providers` primitives:

| Container | Provider scope | Used for | Built from |
|---|---|---|---|
| `DIDynamicServiceContainer` | `Factory` (new instance per resolution) | Feature-level, per-flag service graphs | `ServiceDependency` dicts |
| `DIAppServiceContainer` (extends the above) | `Singleton` (one shared instance per app) | The app-level service graph (events, repos wired once per interface) | `AppServiceDependency` list, via `from_dependencies` |

`DIAppServiceContainer` overrides only `add_service`/`build_singleton` and adds `from_dependencies` — it otherwise inherits `add_constant`, `get_dependency`, `has_dependency`, `remove_dependency`, and `load_container` from `DIDynamicServiceContainer` unchanged, since those operations don't depend on provider scope.

Both wire constructor kwargs to already-registered sibling providers via the shared `injectable_parameter_names(service_type)` helper — a service's dependencies are resolved by matching constructor parameter names against other registered ids, not by explicit wiring declarations.

## Pure Helper Functions

`di/core.py` exports two side-effect-free `# *** functions`:

- **`injectable_parameter_names(service_type)`** — the constructor parameter names eligible for sibling-provider wiring (excludes `self` and variadic parameters).
- **`normalize_flags(*flags)`** — flattens a mixed sequence of strings/lists/tuples into one flat list of strings, used both for cache-key construction and dependency-list lookups.

## Relationship to ServiceRegistration

`ServiceRegistration.resolve_service(*flags)` (a domain object in `tiferet/domain/di.py`) — not this layer — owns the flagged-override-then-default precedence for a single registration. `DIDynamicServiceResolver.build_container` calls it once per registration per flag set and only registers the result when it isn't `None`, so a registration with no resolvable service for the active flags is silently omitted from that flag set's container rather than raising.

## Relationships to Other Layers

- **Domain:** `ServiceRegistration`/`FlaggedDependency` (`docs/guides/domain/di.md`) supply the declarative configuration this layer resolves against; `ServiceDependency`/`AppServiceDependency` (`docs/guides/domain/core.md`) are the core dependency shape both container flavors consume.
- **Blueprints:** `build_service_resolver` (`tiferet/blueprints/core.py`) composes a `DIDynamicServiceResolver` from the interface's `DIService`, and `build_app_service_container` composes the `DIAppServiceContainer` for the app-level graph.
- **Contexts:** the resolver's bound `get_dependency` method is injected into `AppSessionContext` and forwarded to each `FeatureContext` to resolve feature-step events and middleware.
- **Interfaces:** `DI_DEPENDENCY_NOT_REGISTERED` is raised as a `ServiceError` (`interfaces/core.py`), not a `TiferetError` — an unregistered id is treated as infrastructural misconfiguration.

## Boundaries

**Inside this domain:** the abstract DI contract, the concrete `dependency_injector`-backed engine, provider-scope decisions, and per-flag container caching.
**Outside this domain:** the declarative registration data itself (`domain/di.py`'s `ServiceRegistration`), and how/when `get_dependency` gets called during feature execution (`docs/guides/contexts.md`).

## Related Documentation

- [docs/guides/di/dependency_injector.md](di/dependency_injector.md) — `DIDynamicServiceContainer`, `DIAppServiceContainer`, `DIDynamicServiceResolver` constructors, methods, and examples
- [docs/guides/domain/di.md](domain/di.md) — `ServiceRegistration` and `FlaggedDependency` domain objects
- [docs/guides/domain/core.md](domain/core.md) — `ServiceDependency` core model
- [docs/core/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md) — DI layer code-style conventions
- [docs/guides/contexts.md](contexts.md) — how `get_dependency` is consumed during feature execution
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
