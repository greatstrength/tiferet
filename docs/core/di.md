# Dependency Injection in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

This position is defined by the direction of its traffic, not by its contents. It **receives** declarations sent down to it and emanates instances below. It originates nothing. Loving-kindness as expansion means exactly that: a declared service id plus flags becomes a live instance, and the giving is downstream of a receiving. That position is **Chesed**. See [architecture.md](architecture.md).

Starting there rather than at the import list matters, because every rule this package obeys is a consequence of the direction. `di` does not decide what the work is; it expands a contract into something the middle can hold. A missing provider raises `ServiceError`. The layer stays event-free and asset-free until a concrete resolution problem exists that `ServiceError` plus an injected callable cannot solve.

Legal `# ** app` imports: `domain`; `interfaces` (including `ServiceError`). Illegal: `assets`; `events`; `repos`; `blueprints`; `contexts`; `mappers`; `utils`. The package is `core.py` plus `dependency_injector.py`. There is no `di/settings.py` and no `CreateServiceResolver` on the current `build_app` path.

## Life in the system

Chesed is the generic subdomain that turns a registration into an object. It does not raise `TiferetError`. It does not call `DomainEvent.handle`. Parameter parsing (`$env.` references and the like) arrives as an injected `parse_parameter` callable — a module-level function in `blueprints/core.py`, not an event — so this package never imports a parser at all. That is reverse shape (1): the factory and the client resolve without importing `di` classes, and `di` parses without importing what does the parsing.

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

## Three declaration streams, one protocol

Services reach this tier from three places, and the position's whole claim is that it cannot tell them apart.

1. **Bootstrap catalogs** seeded into the shared cache — `a.di.CALC_DEFAULT_SERVICES` in a dialect, flowing into a flagged container at Factory scope.
2. **Session-scoped services** declared on the resolved session (`sessions.<id>.services`), landing in the app container under the `app` flag.
3. **The feature-level registry** — the `services:` block in `config.yml` — which supplies the operator that every feature step names.

The production system runs on the third. Without a declared operator registry there is a hub with nothing to execute.

**Provenance and kind do not change treatment, and it is checkable in six lines of YAML.** In one feature group of the calculator, `calc.safe_divide` names `divide_number_event`, which appears in no `services:` block and resolves from the cache-seeded defaults; `calc.history` names `list_recent_formulas_event`, declared in the config registry. Same call, same handling. And `formula_service` — a configuration repository, not a domain event — sits in that same registry with a `params` block, composed identically to the events beside it.

**Declarations arrive as data, never as an import edge.** This is why the tier can stay asset-free while genuinely depending on the bootstrap catalogs: those catalogs are validated into `AppServiceDependency` values and assembled by a blueprint before this package ever sees them. The dependency is real and the edge is absent. Both halves have to be said, or the rule looks like it is being fudged — see [architecture.md](architecture.md) for why influence and dependency are deliberately different graphs.

**Subtlety at the call site.** At step time the caller passes an identifier and receives a live operator, never learning which collection answered, how the thing was constructed, or what lifetime it was given. Name in, instance out.

## Custody without use

The tier assembles what it is given, safeguards it under a declared lifetime, and disseminates it on request. What it never does is exercise it.

That is the argument behind the event-free rule, and it is worth having as an argument rather than as a boundary someone asserted. **A resolver that invoked what it holds would have joined the domain it serves.** It would need to know what a successful call looks like, which means knowing what the call means, which is precisely the knowledge this position is built not to have. The feature context executes. The resolver hands over and stops.

**Restraint is what buys generality.** This tier resolves by name and by flag, never by meaning, and forms no opinion whatsoever about whether a domain hangs together. Any semantic judgment would couple it to the domains it serves, and it serves all of them. So its only legitimate failure is `ServiceError` — not found. There is no error here for "that does not make sense," and there should not be.

Namespacing follows from the same purpose rather than from convenience: distinct containers exist because they are meant for distinct things, which is how a dialect's flag becomes a bounded context's resolution namespace.

This is the expansion pole of a pair. The judgment this position declines to make is real work, and someone has to do it — it lives at Gevurah, one position down the other side, where a noun refuses what it cannot vouch for. See [domain.md](domain.md). Chesed does not apologize for having no opinions; it points at where the opinions belong.

## Structured code design

Use `# *** functions` for `injectable_parameter_names` / `normalize_flags` and `# *** di` / `# ** di:` (or `# *** classes` in `core.py`) for containers and resolvers. Every new DI class extends `ServiceContainer` or `ServiceResolver`. Full grammar: [code_style.md](code_style.md). Engine walkthroughs live in [docs/guides/di.md](../guides/di.md).

## In short

- The position is defined by direction: it receives declarations and emanates instances. It originates nothing. That expansion is Chesed.
- Three declaration streams — bootstrap catalog, session-scoped, feature registry — and the call site cannot tell them apart. A repository and a domain event compose identically.
- Declarations arrive as data, not as import edges. That is how the tier stays asset-free while depending on the catalogs.
- Custody without use: it assembles, holds, and hands over, and never executes what it holds. A resolver that invoked anything would have joined the domain it serves.
- Restraint buys generality. Resolution matches name and flag, never meaning, so the only legitimate failure is `ServiceError`.
- Legal imports: `domain`, `interfaces`. Never `assets`, `events`, `repos`, or the rest of the framework.
- App container is Singleton. Feature resolver is Factory, cached per flag set.
- Contexts consume an injected `get_dependency` callable. They do not import this package.
- The judgment this position declines to make lives at Gevurah. Point there rather than apologizing for its absence.
