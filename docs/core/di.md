# Dependency Injection in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Loving-kindness, here, is expansion: a declared service id plus flags becomes a live instance. `di` does not decide what the work is. It expands a contract into something the middle can hold. That position is **Chesed**. A missing provider raises `ServiceError`. The layer stays event-free and asset-free until a concrete resolution problem exists that `ServiceError` plus an injected callable cannot solve. See [architecture.md](architecture.md).

Legal `# ** app` imports: `domain`; `interfaces` (including `ServiceError`). Illegal: `assets`; `events`; `repos`; `blueprints`; `contexts`; `mappers`; `utils`. The package is `core.py` plus `dependency_injector.py`. There is no `di/settings.py` and no `CreateServiceResolver` on the current `build_app` path.

## Life in the system

Chesed is the generic subdomain that turns a registration into an object. It does not raise `TiferetError`. It does not call `DomainEvent.handle`. Parameter parsing (`$env.` references and the like) arrives as an injected `parse_parameter` callable so this package never imports `ParseParameter`. That is reverse shape (1): the factory and the client resolve without importing `di` classes, and `di` parses without importing events.

Two modules keep the boundary honest.

`tiferet/di/core.py` is domain-only. It defines `ServiceContainer` and `ServiceResolver` plus the pure helpers `injectable_parameter_names` and `normalize_flags`. It imports the standard library and `ServiceDependency`. Nothing from `interfaces`, nothing from `events`.

`tiferet/di/dependency_injector.py` is the engine. `DIDynamicServiceContainer` is feature-level and `Factory`-scoped: a new instance per resolution. `DIAppServiceContainer` is app-level and `Singleton`-scoped: one shared instance per app, built via `from_dependencies` keyed by `service_id`. `DIDynamicServiceResolver` holds a `DIService` and `parse_parameter`, implements `build_container`, and caches a container per flag set on the `ServiceResolver` ABC.

`ServiceResolver.get_dependency` is a template method. Normalize flags, fetch or build the container, delegate. Subclasses only implement `build_container`:

```python
# tiferet/di/core.py (excerpt)

class ServiceResolver(ABC):

    # * method: get_dependency
    def get_dependency(self, service_id: str, *flags) -> Any:
        # Normalize the provided flags.
        normalized = normalize_flags(*flags)

        # Retrieve the cached container, building and caching one on a miss.
        container = self.get_container(*normalized)
        if container is None:
            container = self.add_container(self.build_container(normalized), *normalized)

        # Resolve the dependency from the container.
        return container.get_dependency(service_id)
```

What the reader just saw: expansion is mechanical. Flags select a container. The container yields an instance. The flagged-override → default → `None` rule lives once, on `ServiceRegistration.resolve_service` in the domain. `get_service_type` delegates to it. Chesed does not invent precedence; it applies Gevurah’s.

A miss raises `ServiceError.raise_for(...)`. A registered provider that fails during construction still surfaces the underlying exception. The layer does not wrap those failures in an event or an asset constant. That is the event-free, asset-free constraint in operational form.

Contexts never hold a container. The blueprint injects `resolver.get_dependency` as a plain callable. `FeatureContext` writes `self.get_dependency(service_id, *flags)` and receives an event. Any callable with that signature will do, which is why a `mock.Mock()` is enough in tests.

The blueprint composes this without a wiring registry:

```python
app_container = build_app_service_container(cache, app_session)
resolver = build_service_resolver(app_container)
return context_cls.from_domain(
    app_session,
    get_dependency=resolver.get_dependency,
    **resolved_collaborators,
)
```

Cache defaults merge with the session’s own services and constants *before* the container is built, session winning. An interface constant override therefore reaches default services the session does not redeclare. That merge is Chochmah using Chesed. It is not Chesed importing blueprints.

## Structured code design

Use `# *** functions` for `injectable_parameter_names` / `normalize_flags` and `# *** di` / `# ** di:` (or `# *** classes` in `core.py`) for containers and resolvers. Every new DI class extends `ServiceContainer` or `ServiceResolver`. Full grammar: [code_style.md](code_style.md). Engine walkthroughs live in [docs/guides/di.md](../guides/di.md).

## In short

- `di` expands a declared id plus flags into a live instance. That expansion is Chesed.
- Legal imports: `domain`, `interfaces`. Never `assets`, `events`, `repos`, or the rest of the framework.
- Missing provider → `ServiceError`. Stay event-free and asset-free.
- App container is Singleton. Feature resolver is Factory, cached per flag set.
- Contexts consume an injected `get_dependency` callable. They do not import this package.
