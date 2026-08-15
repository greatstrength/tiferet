# Architecture in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

The ten packages are not three stacked layers. Each package has a systems function: factory versus client, emit versus absorb, read-only noun versus mutable aggregate, contract versus computation versus persistence. After that function is stated, this page binds a Hebrew name to it. The name is a variable for a hard concept. It is not the argument.

Skills, guides, tutorials, and `AGENTS.md` use package names only. An implementor writes correct imports from the tables below without knowing the Tree.

Each `docs/core/<layer>.md` restates one systems line and its import law. This page is the only full binding.

## How to read a name

A heading may look like `### Gevurah — domain`. The first sentence is the systems claim. The Hebrew never *is* the claim.

Do not treat the names as self-explanatory. Define the concept, then bind the name.

## The ten positions

### Keter — `assets`

`assets` is the crown: no inbound framework edges. Core assets may be used by other assets. Core and other assets may be used by `blueprints`, `contexts`, and `events`, typically via `from .. import assets as a`. Assets do not automatically flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`.

Legal `# ** app` imports: none.

### Chochmah — `blueprints`

`blueprints` are composition and factory. They wire a session; they do not implement domain logic.

Legal `# ** app` imports: `assets`; `contexts`; `di` for container and resolver classes; `events` for pre-DI bootstrap only (`DomainEvent.handle(...)` or a direct event-class import). Illegal as a direct import: `domain`, `interfaces`, `mappers`, `utils`, `repos`.

Service instances reach a blueprint only through `di` (`get_dependency`). Domain types reach a blueprint only through `contexts`. That crossing is **Da'ath**: not a package. Context modules re-export the types factory signatures need (`AppSession`, `Feature`, `Error`, `LoggingSettings`, CLI models). Write `from ..contexts.feature import Feature`, never `from ..domain import Feature`.

After composition, the feature loop belongs to `contexts` plus the injected `get_dependency` callable. Blueprint event imports are bootstrap-only.

### Binah — `contexts`

`contexts` are the runtime graph. A context binds a domain object (`from_domain`) and exposes operational behavior. The hub (`AppSessionContext`) must be able to run without knowing how it was assembled.

Legal `# ** app` imports: `assets` (one way); `domain`; sibling contexts; `events` as the client surface. Illegal: `blueprints` (construction flows down, never back); `interfaces`; `di`; `mappers`; `utils`; `repos`.

Blueprints are the factory (`build_app` produces the hub). Contexts are the client: a flat presentation container or a fluent API that performs domain work by calling events. Prefer handler injection over constructing sibling contexts. The five required hub slots are `build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, and `response_handler`, plus CLI `parse_cli_args`. The hub calls those slots; it does not import `FeatureContext` / `ErrorContext` / `LoggingContext` to build them.

### Chesed — `di`

`di` is resolution: a declared service id plus flags becomes a live instance.

Legal `# ** app` imports: `domain`; `interfaces` (including `ServiceError`). Illegal: `assets`; `events` until a concrete resolution problem exists that `ServiceError` plus an injected callable cannot solve; `repos`; `blueprints`; `contexts`; `mappers`; `utils`.

The package is `core.py` plus `dependency_injector.py`. A missing provider raises `ServiceError`. The layer stays event-free and asset-free.

### Gevurah — `domain`

Domain objects are read-only nouns. They house data and offer read-only behavior. They do not mutate themselves. Mutation lives on the aggregate in `mappers`.

Used by `contexts`, `events`, and `di`. Blueprints reference domain types only through Da'ath.

Legal `# ** app` imports: none of the framework.

### Tiferet — `events`

Events are the unit of work. Inbound: `assets` (`a`), `blueprints` (bootstrap), `contexts` (client). `di` does not import events.

Outbound, concrete: `domain`, `mappers`, `utils`, `interfaces`. `execute` should return a domain model when one exists. Otherwise it may return anything it can legally reach beneath it — an aggregate or transfer object, a util result, or an interface-shaped value. It does not return contexts, blueprints, or repos.

Error constants are `a.<submodule>.*` (`a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`), never `a.const`.

### Hod — `mappers`

A mapper extends a domain type and adds either mutation or representation.

- **Aggregate** — internal state. Factory and mutation methods (`set_attribute`, `rename`, …). `ModelError` on validation failure.
- **TransferObject** — cross-platform state: how the same noun is represented for a database, a domain file format, or a custom event response, without breaking the model.

Legal `# ** app` imports: `domain` only. Used by `events`, `interfaces`, `utils`, and `repos`. A mapper method may accept a `Callable` and receive a util function at runtime. Mappers do not import `utils`.

### Netzach — `interfaces`

Interfaces are `Service` ABCs: vertical contracts for persistence, files, middleware, and DI.

Legal `# ** app` imports: `mappers` (aggregates) to type domain-related outputs, especially when the implementor will be a repository. Prefer the aggregate over the domain model when an aggregate exists. Sibling interface modules are legal.

Used by `events` (injected services), `di` (`DIService`, `ServiceError`), `utils` (only when a util must be injectable), and `repos` (the Service being implemented). Presented to `blueprints` only through `di`. `contexts` do not import `interfaces`.

### Yesod — `utils`

Utilities are domain-specific computation and physical infrastructure. Two shapes share the package:

1. **Service-backed** — implements an interface (`FileService`, `SqliteService`, `MiddlewareService`) and is therefore DI-injectable.
2. **Raw computational container** — algorithms and transforms with no external collaborator. Events may import and call these directly; they do not need a Service.

Legal `# ** app` imports: `interfaces` (including `ServiceError`); `mappers`; sibling utils. Used by `events` (direct or via an interface), `repos` (loaders), and `mappers` only as a runtime visitor callable.

### Malkuth — `repos`

Repositories are persistence: Keter inverted. Assets emit artifacts to the three above them (`blueprints`, `contexts`, `events`). Repositories only absorb artifacts from the three above them: `mappers`, `utils`, `interfaces`. Nothing else imports `repos`. They are never exported.

Legal `# ** app` imports: `interfaces` (the Service being implemented, and `ServiceError`); `mappers` (transfer objects and aggregates); `utils` (loaders). Illegal: `assets`, `domain` (use a mapper), `events`, `di`, `blueprints`, `contexts`.

Pattern, as in `ConfigurationRepository`: the repo knows the loader, performs transfer-object / aggregate mapping inside the interface methods, and never leaks a loader or a file path upward.

## Import law

| Package | Legal `# ** app` | Never |
|---|---|---|
| `assets` | none | any other framework package |
| `blueprints` | `assets`, `contexts`, `di`, `events` (bootstrap) | `domain`, `interfaces`, `mappers`, `utils`, `repos` |
| `contexts` | `assets`, `domain`, siblings, `events` | `blueprints`, `interfaces`, `di`, `mappers`, `utils`, `repos` |
| `di` | `domain`, `interfaces` | `assets`, `events`, `repos`, `blueprints`, `contexts`, `mappers`, `utils` |
| `domain` | none | any framework package |
| `events` | `assets`, `domain`, `mappers`, `utils`, `interfaces` | `di`, `repos`, `contexts`, `blueprints` |
| `mappers` | `domain` | `assets`, `events`, `interfaces`, `utils`, `repos`, `contexts`, `blueprints` |
| `interfaces` | `mappers` (aggregates), sibling interfaces | `domain` when an aggregate exists; `events`, `repos`, `utils`, `contexts`, `blueprints` |
| `utils` | `interfaces`, `mappers`, siblings | `events`, `domain`, `repos`, `di`, `contexts`, `blueprints` |
| `repos` | `interfaces`, `mappers`, `utils` | `assets`, `domain`, `events`, `di`, `contexts`, `blueprints` |

## Reverse shapes

Callable reverse is not a general exemption. Only these three backward walks are allowed:

1. **Injected `get_dependency`** — `contexts` and `blueprints` resolve instances without importing `di` classes. `parse_parameter` is this shape.
2. **Blueprint handler slots** — the hub runs without constructing sibling contexts.
3. **A mapper method typed `Callable`** — a util function may visit at runtime without `mappers` importing `utils`.

Do not write that every non-assets / non-repos edge may be walked backward.

## Runtime flow

```
App('interface_id')                               # blueprints/core.py: build_app()
  └─ build_cache()                               # CacheContext pre-seeded with framework defaults
  └─ get_app_session(id, cache)                  # GetAppSession event → AppSession
  └─ build_app_session_context(session, cache)   # wires DI, constructs hub with five handlers
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

## Related documentation

- [assets.md](assets.md)
- [blueprints.md](blueprints.md)
- [contexts.md](contexts.md)
- [di.md](di.md)
- [domain.md](domain.md)
- [events.md](events.md)
- [mappers.md](mappers.md)
- [interfaces.md](interfaces.md)
- [utils.md](utils.md)
- [repos.md](repos.md)
- [code_style.md](code_style.md)
