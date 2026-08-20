# Architecture in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

> Generating a running program from a declaration of model properties is a kind of Holy Grail of MODEL-DRIVEN DESIGN, but it does have its pitfalls in practice...
>
> — Eric Evans, *Domain-Driven Design*, Chapter 10 (Supple Design)

Software architecture is hard because the parts that must remain one system keep coming apart. Session and store, intention and mechanism, the human request and the contract beneath it — each has a way of swallowing the other, and the usual defense is another layer, another pile of utilities, another object that knows too much. Evans named the deeper ambition; the grail is not a compiler trick. It is a holistic, if not declarative, system: say what the application *is*, and have that saying be enough to run.

The wish has never been the problem. The problem has been the *what*. What, exactly, composes a holistic declarative design of an application — not a slogan about layers, but a closed set of responsibilities whose relations can be declared, and whose runtime can be composed, without either side erasing the other?

Tiferet is an answer to that *what*. It does not reach the grail by inventing a new stack. It takes as its System Metaphor the Sefirotic tree: a historically distilled design of balance, used here as a theoretical model of a holistic system. Ten closed jobs, one operational center, edges that keep factory from becoming client and emit from becoming absorb. The framework is the technical projection of that model, and a philosophical engagement with it. To write a Tiferet application is to declare against that graph; to run one is to watch the declaration become a session. This page states the problem, the desired outcome, and the path. Each [component chapter](#the-ten-chapters) is where a single responsibility is lived in.

The Hebrew names and the package names occupy the same ubiquitous language. Skills, guides, tutorials, and `AGENTS.md` stay in package names, so an implementor can write a correct `# ** app` import from the table below without knowing the Tree. The Tree is here because the core docs are unique to this framework: they are the philosophy of the work, not a template to copy into the next application.

## A published design of balance

The ten-node graph is a historically attested instrument for thinking creation as composition — a design of balance distilled across recensions until the nodes had stable jobs. What follows is when that graph entered the printed record, and what kind of object it was in each period.

The *name and count* of ten sefirot first appear in *Sefer Yetzirah* (Book of Formation), a short Hebrew cosmological treatise first securely attested by the early tenth century in Saadia Gaon’s commentary. Its composition date is contested — late antiquity through the early Islamic centuries. In that text the ten are closer to dimensions or enumerations than to later named attributes. “Ten and not nine, ten and not eleven” is already a closed-count rule: the system is complete, and completeness is the point.

The *theosophical* tree — named potencies in relation, not just a decad of numbers — is a medieval publication event. *Sefer ha-Bahir* surfaces in late-twelfth-century Provence. The Zoharic literature of thirteenth-century Castile consolidates the named system. A ten-node graph with a named center became a public way to talk about how expansion is checked by form, how a middle holds both sides, and how the last node absorbs what the first emits.

The *diagram* as a public engineering object is early modern. Moses Cordovero’s *Pardes Rimonim*, composed in 1548 and printed in Kraków in 1591, is the first widely circulated Hebrew printed ilan. Athanasius Kircher’s *Oedipus Aegyptiacus* (1652–54) is the first European print that fixed lettered paths in the Latin imagination.

These packages already cluster as that graph. The metaphor is how a team walks a scenario and lands on the same objects the code already is.

## How to read a name

A heading may look like `### Gevurah — domain`. The Hebrew and the package name one responsibility from two sides. The chapter defines the job, then lets the name sit in the same sentence.

## The ten positions

The answer is not three stacked layers. It is ten closed responsibilities, one operational center, and edges that refuse to collapse the whole into a factory that never stops composing or a client that starts inventing work. The packages already cluster that way: factory versus client, emit versus absorb, read-only noun versus form-giving, contract versus resolution. What follows is the map.

### Keter — `assets`

A system that can be composed has to begin with something that does not depend on the composition. `assets` is that crown: shared primitives — exceptions, named error codes, bootstrap catalogs — with no inbound framework edges. Core assets may be used by other assets. Core and other assets may be used by `blueprints`, `contexts`, and `events`, typically via `from .. import assets as a`. They do not automatically flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`. Keter emits. It does not absorb, and it does not become runtime.

Legal `# ** app` imports: none.

### Chochmah — `blueprints`

Wisdom, in this design, is the flash of composition: a factory that wires a session and then gets out of the way. `blueprints` do not implement domain logic. They build the cache, resolve the session, compose the container and the resolver, and hand five handlers to the hub. After that, the feature loop is no longer theirs.

Legal `# ** app` imports: `assets`; `contexts`; `di` for container and resolver classes; `events` for pre-DI bootstrap only (`DomainEvent.handle(...)` or a direct event-class import). Illegal as a direct import: `domain`, `interfaces`, `mappers`, `utils`, `repos`.

Service instances reach a blueprint only through `di` (`get_dependency`). Domain types reach a blueprint only through `contexts`. That crossing is **Da'ath**: not a package. Context modules re-export the types factory signatures need (`AppSession`, `Feature`, `Error`, `LoggingSettings`, CLI models). Write `from ..contexts.feature import Feature`, never `from ..domain import Feature`. Da'ath is how the factory is allowed to see a noun without growing a Gevurah import.

### Binah — `contexts`

Understanding is the client-runtime graph: the session once it exists, able to run without knowing how it was assembled. A context binds a domain object (`from_domain`) and exposes operational behavior. It may be a flat presentation container or a fluent API. What it must not do is invent the work. The work is an event.

Legal `# ** app` imports: `assets` (one way); `domain`; sibling contexts; `events` as the client surface. Illegal: `blueprints` (construction flows down, never back); `interfaces`; `di`; `mappers`; `utils`; `repos`.

Blueprints are the factory (`build_app` produces the hub). Contexts are the client. Prefer handler injection over constructing sibling contexts. The five required hub slots are `build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, and `response_handler`, plus CLI `parse_cli_args`. The hub calls those slots. It does not import `FeatureContext` / `ErrorContext` / `LoggingContext` to build them. That is how Binah stays a graph without becoming a circular import.

### Chesed — `di`

Loving-kindness, here, is expansion: a declared service id plus flags becomes a live instance. `di` does not decide what the work is. It expands a contract into something the middle can hold. A missing provider raises `ServiceError`. The layer stays event-free and asset-free until a concrete resolution problem exists that `ServiceError` plus an injected callable cannot solve.

Legal `# ** app` imports: `domain`; `interfaces` (including `ServiceError`). Illegal: `assets`; `events`; `repos`; `blueprints`; `contexts`; `mappers`; `utils`.

The package is `core.py` plus `dependency_injector.py`. There is no `di/settings.py` and no `CreateServiceResolver` on the current `build_app` path.

### Gevurah — `domain`

Severity is form: the noun that will not change itself. Domain objects house data and offer read-only behavior. They do not mutate. A `rename` or `set_*` on a domain object is in the wrong package. Mutation is Hod’s job.

Used by `contexts`, `events`, and `di`. Blueprints reference domain types only through Da'ath.

Legal `# ** app` imports: none of the framework.

### Tiferet — `events`

Beauty is the heart that must know both sides. An event is the only unit of work that commands, executes, and returns a noun — the bridge between session and store, between the human feature and the contract beneath it. Without events there is nothing for a feature to wire and nothing for a user to mean. The calculator begins its story here for that reason. That position is Tiferet.

Inbound: `assets` (`a`), `blueprints` (bootstrap), `contexts` (client). `di` does not import events. Outbound: `domain`, `mappers`, `utils`, `interfaces`. `execute` should return a domain model when one exists. Otherwise it may return anything it can legally reach beneath it — an aggregate or transfer object, a util result, or an interface-shaped value. It does not return contexts, blueprints, or repos.

Error constants are `a.<submodule>.*` (`a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`), never `a.const`.

### Hod — `mappers`

Splendor is form-giving: the same noun, given a body that can change or a face that can cross a boundary. A mapper extends a domain type and adds either mutation or representation.

- **Aggregate** — internal state. Factory and mutation methods (`set_attribute`, `rename`, …). `ModelError` on validation failure.
- **TransferObject** — cross-platform state: how the same noun is represented for a database, a domain file format, or a custom event response, without breaking the model.

Legal `# ** app` imports: `domain` only. Used by `events`, `interfaces`, `utils`, and `repos`. A mapper method may accept a `Callable` and receive a util function at runtime. Mappers do not import `utils`. That visitor is one of the three reverse shapes, not a general exemption.

### Netzach — `interfaces`

Endurance is the promise that outlasts any one store. Interfaces are `Service` ABCs: vertical contracts for persistence, files, middleware, and DI. They may import aggregates from `mappers` to type domain-related outputs, especially when the implementor will be a repository. Prefer the aggregate over the domain model when an aggregate exists. Sibling interface modules are legal.

Used by `events` (injected services), `di` (`DIService`, `ServiceError`), `utils` (only when a util must be injectable), and `repos` (the Service being implemented). Presented to `blueprints` only through `di`. `contexts` do not import `interfaces`.

### Yesod — `utils`

Foundation is the capability the rest of the system stands on — physical or computational. Two shapes share the package:

1. **Service-backed** — implements an interface (`FileService`, `SqliteService`, `MiddlewareService`) and is therefore DI-injectable.
2. **Raw computational container** — algorithms and transforms with no external collaborator. Events may import and call these directly; they do not need a Service.

Legal `# ** app` imports: `interfaces` (including `ServiceError`); `mappers`; sibling utils. Used by `events` (direct or via an interface), `repos` (loaders), and `mappers` only as a runtime visitor callable.

### Malkuth — `repos`

Kingdom is Keter inverted. Assets emit artifacts to the three above them (`blueprints`, `contexts`, `events`). Repositories only absorb artifacts from the three above them: `mappers`, `utils`, `interfaces`. Nothing else imports `repos`. They are never exported. Persistence is the last node, not a voice that speaks back into the factory.

Legal `# ** app` imports: `interfaces` (the Service being implemented, and `ServiceError`); `mappers` (transfer objects and aggregates); `utils` (loaders). Illegal: `assets`, `domain` (use a mapper), `events`, `di`, `blueprints`, `contexts`.

Pattern, as in `ConfigurationRepository`: the repo knows the loader, performs transfer-object / aggregate mapping inside the interface methods, and never leaks a loader or a file path upward.

## Import law

The table restates what the essays above let a reader predict.

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

Edges are one-way by default. Callable reverse is not a general exemption. Only these three backward walks are allowed:

1. **Injected `get_dependency`** — `contexts` and `blueprints` resolve instances without importing `di` classes. `parse_parameter` is this shape.
2. **Blueprint handler slots** — the hub runs without constructing sibling contexts.
3. **A mapper method typed `Callable`** — a util function may visit at runtime without `mappers` importing `utils`.

Do not write that every non-assets / non-repos edge may be walked backward. A fourth reverse shape is a design change, not a reading of the Tree.

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

The factory composes. The client runs. The event does the work. Resolution expands a contract into an instance at the moment a step needs one. That is the whole motion.

## The ten chapters

- [assets.md](assets.md) — Keter: emit, no inbound edges
- [blueprints.md](blueprints.md) — Chochmah: factory, then get out of the way
- [contexts.md](contexts.md) — Binah: client-runtime graph
- [di.md](di.md) — Chesed: expansion / resolution
- [domain.md](domain.md) — Gevurah: the noun that will not mutate itself
- [events.md](events.md) — Tiferet: the unit of work
- [mappers.md](mappers.md) — Hod: mutation and representation
- [interfaces.md](interfaces.md) — Netzach: the enduring contract
- [utils.md](utils.md) — Yesod: foundation, physical or computational
- [repos.md](repos.md) — Malkuth: absorb, never exported

Style and annotation grammar live in [code_style.md](code_style.md). Per-application distillation lives in `docs/guides/` and is not this constitution.

## In short

- The problem is the *what* of holistic, declarative design — Evans’ grail in *Domain-Driven Design*, Chapter 10. Tiferet answers with the Sefirotic tree as System Metaphor.
- The framework is the technical and philosophical projection of that model. Hebrew and package names share one ubiquitous language.
- The historical note is publication history. A name is kept only while it still predicts an import, an artifact, or a responsibility.
- Ten closed jobs. One operational center (`events`). Da'ath is a crossing, not a package. Three reverse shapes only.
- Skills and AGENTS.md stay in package names. These chapters are unique to this framework.
