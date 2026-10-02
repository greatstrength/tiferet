# Architecture in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

> Generating a running program from a declaration of model properties is a kind of Holy Grail of MODEL-DRIVEN DESIGN, but it does have its pitfalls in practice. For example, I have encountered the following problems more than once:
>
> - A declaration language not expressive enough to do everything needed, yet a framework that makes it very difficult to extend the software beyond the automated portion.
> - Code generation techniques that cripple the iterative cycle by merging generated code into handwritten code in a way that makes regeneration very destructive.
>
> — Eric Evans, *Domain-Driven Design*, Chapter 10, Declarative Design

## The problem

The aim of declarative design is a running program from a declaration of model properties. It fails in two ways.

The **transcendent** failure is unknown meaning. The declaration language is not expressive enough for the needed domain behavior, and the framework is hard to extend beyond the automated portion. That meaning sits above the current vocabulary and cannot be approached from inside it.

The **immanent** crisis is that there is no structural pattern language isomorphic to a whole, unified system. A program is then not a composition of defined structural patterns but a variety of objects and functions in modules — everything is an object, everything is a room. Such a language would be the intrinsic rule for where a concept belongs: a named pattern, with an obligation, that a novel concept can occupy and still do its job without interfering with the others, mechanically or conceptually. What exists instead are patterns that pack some structure into a short declaration and then stop. They do not map the system being modeled, so a variety the running system actually produces can be left unnamed. Patterns stay generally defined and locally undefined, which is undefined when the thing has to run. The team pretends an existing pattern covers the leftover, invents a local trick, or fills the hole in handwriting. Ordinary frameworks pick a few mature parts — container, repository, handler, transfer object — and treat the rest as "your objects." That is still one letter wearing a coat of many.

Without that isomorphism, the declared structure cannot be taken at face value. Generated code has no structural place that corresponds to the whole, so it is merged with handwriting and regeneration is destructive. Agentic generation does not close the gap. Without a pattern language the generated code can be an instance of, it is handwriting at speed, and both failures get worse.

A third failure is rigid architecture. Guiding rules are not the problem; rigidity and the source of the rules are. Developers dumb the application down to fit, or subvert the structure and return to a free-for-all. Large-scale structure must be allowed to evolve. Do not saddle the project with a design conceived before the domain was understood.

## The thesis

Tiferet answers with a structural pattern language isomorphic to the whole system: a finite alphabet of ten pattern cores, held in Evans' **Responsibility Layers**, on which a dialect writes its own words.

An application does not add a letter. It writes its ontology onto the letters already there. New meaning arrives as a new word, or as a word occupying a face it did not occupy before — never as an unnamed leftover between "the model" and "the framework," and never as an eleventh package.

That writing is the application.

## Why a framework

A framework exists so a new or extended application does not rebuild the same machinery. Feature dispatch, session composition, resolution, error shaping, and configuration persistence are the same jobs in every dialect. The pattern set is the shared machinery; the dialect supplies domain meaning.

The standard set is what makes the machinery transferable across dialects. A dialect that needed its own composition model, its own resolution rules, and its own persistence shape would be starting over, which is the cost the framework exists to remove.

Tiferet is mechanism to a dialect. Internally it still has its own core domain (the `Feature` family) and its own operations (`repos`) and potentials (`utils`). Core-versus-mechanism is relative to the reader, not a kind of code.

## Responsibility layers

A layer is a structural pattern: a band of responsibility broad enough that an artifact fits inside one of them, found by reading conceptual dependencies and rates of change.

Four layers hold the ten pattern cores:

- **Decision support** — `assets`, `blueprints`, `contexts`. Catalogs, composition, and the live session graph. These decide what runs and in what order; they do not do the work.
- **Policy** — `domain`, `di`, `events`. The noun, the rules of its resolution, and the unit of work. Policy names what the work is and does not implement a store.
- **Potentials** — `mappers`, `interfaces`, `utils`. Mutation and representation, the enduring contract, and substrate capability. Potentials are what the work can become; they do not declare what the work is.
- **Operations** — `repos`. Persistence that implements a contract and is never imported. Operations is what is actually done to a substrate.

Two consequences are mechanical:

- An artifact occupies exactly one pattern. A composite design (an anticorruption layer, a config-backed store, a CLI session) decomposes across patterns; it does not invent an eleventh package.
- A pattern is realized on demand. An unrealized pattern is the normal case, not a gap.

Infrastructure verifies **shape** — names, flags, file structure, constructor signatures. Policy is answerable for **meaning**. The layers bound what a word can mean. They do not check that a dialect's conceptual contours are coherent.

## The ten pattern cores

The cores are the permutable components a domain concept can occupy. They were not derived from examples. A permutation space defined from "the patterns we have seen" leaves the next variety off the page, which is how a pattern language stays generally defined and locally undefined. The cores are ten abstract jobs that can be realized or left empty. None of them is a domain word. The words decline around them.

The mapping only becomes possible by defining those permutations around the ten sefirot of the Tree of Life. The sefirot are ten states of conscious existence — jobs, not rooms and not modules — and they are the functional mechanism by which an application is represented as a network of terms linked across ten given states, each open or closed according to what the application requires. A state with no term occupying it is not missing. It is closed.

| # | State | Package | Job |
|---|---|---|---|
| 1 | Keter | `assets` | emit catalogs; do not become runtime |
| 2 | Chochmah | `blueprints` | compose, and stay resident as closures |
| 3 | Binah | `contexts` | the live session graph; sequence, do not invent work |
| 4 | Chesed | `di` | receive a declaration; emanate an instance; do not use it |
| 5 | Gevurah | `domain` | the noun that will not mutate itself |
| 6 | Tiferet | `events` | the unit of work; hold both sides; return narrowly |
| 7 | Netzach | `interfaces` | the enduring contract |
| 8 | Hod | `mappers` | mutation and representation |
| 9 | Yesod | `utils` | substrate capability |
| 10 | Malkuth | `repos` | persistence; never imported, never exported |

The sixth core is why the framework is named as it is. It is the middle that may know the session and the store without becoming either. Without a middle, contour and mechanism only stack. A middle that swallows both is a god object. The join has to stay a permutation of its own.

A core used as a nickname for leftover code is the old failure returning. The jobs below are stated in structural terms; the table is the reference that fixes their count and their order.

Each entry states the job, the imports that follow from it, and the constraint the pattern exists to enforce. The package chapters are the full write-ups:

- [assets.md](assets.md) — bootstrap primitives, no inbound edges
- [blueprints.md](blueprints.md) — composition; handler closures that stay resident
- [contexts.md](contexts.md) — live session graph; runtime handler hub
- [domain.md](domain.md) — the noun that will not mutate itself
- [di.md](di.md) — rules of resolution for dialect services
- [events.md](events.md) — the unit of work
- [mappers.md](mappers.md) — mutation and representation
- [interfaces.md](interfaces.md) — the enduring contract
- [utils.md](utils.md) — substrate capability, physical or computational
- [repos.md](repos.md) — persistence; never imported, never exported

### Decision support

Decision support does not implement domain work. It holds bootstrap data, composes the process, and sequences the live session.

#### `assets`

Shared primitives: exceptions, named error codes, bootstrap catalogs. Composition has to begin from something that does not depend on the composition.

- **Legal `# ** app`:** none.
- **Consumed by:** `blueprints`, `contexts`, `events`, typically `from .. import assets as a`. Core assets may be used by other assets. They do not automatically flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`.
- **Constraint:** `assets` emits catalogs and constants. It does not become runtime.

#### `blueprints`

Application composition. A blueprint builds the cache, resolves the session, composes the container and the resolver, and builds the handler closures the session hub will run. Those closures stay resident for the session; composition is not a step that completes and withdraws.

- **Legal `# ** app`:** `assets`; `contexts`; `di` for container and resolver classes; `events` for pre-DI bootstrap only.
- **Illegal:** `domain`, `interfaces`, `mappers`, `utils`, `repos`.
- **Constraint:** service instances reach a blueprint only through `di` (`get_dependency`); domain types only through `contexts`. Write `from ..contexts.feature import Feature`, never `from ..domain import Feature`.

The handler *pattern* is fixed: the hub calls injected slots rather than importing sibling contexts to build them. The arity is not. It is the constructor of the session context type — `AppSessionContext`, `CliSessionContext`, or a consumer subclass. An unwired required slot fails through `raise_unwired_handler_error`.

Public composition entry points are `build_app` (`App`) and `build_cli` (`CLI`). Choosing an entry point chooses which composition runs. See [blueprints.md](blueprints.md).

#### `contexts`

The live session graph: the session once it exists, able to run without knowing how it was assembled. A context binds a domain object (`from_domain`) and exposes operational behavior.

- **Legal `# ** app`:** `assets`; `domain`; sibling contexts; `events` as the client surface.
- **Illegal:** `blueprints` (construction flows down, never back); `interfaces`; `di`; `mappers`; `utils`; `repos`.
- **Constraint:** a context must not invent the work. The work is an event. The operation is a handler slot.

The session context is a **runtime handler hub**. It sequences injected callables — logger, request, feature execution, error, response, and any slots the context type adds (CLI `parse_cli_args` is one). It does not implement those operations, and it does not construct `FeatureContext` / `ErrorContext` / `LoggingContext` by importing them. See [contexts.md](contexts.md).

### Policy

Policy names the noun, the rules of its resolution, and the unit of work.

#### `domain`

The noun that will not change itself. Domain objects house data and offer read-only behavior.

- **Legal `# ** app`:** none of the framework.
- **Consumed by:** `contexts`, `events`, `di`. Blueprints reach domain types only through `contexts`.
- **Constraint:** a `rename` or `set_*` on a domain object is in the wrong package. Mutation is `mappers`.

#### `di`

Services and utilities belong to the dialect. `di` holds the rules of their resolution: a declared service id plus flags becomes a live instance. That is why `di` sits in policy. It does not decide what the work is, and it does not implement a dialect service.

- **Legal `# ** app`:** `domain`; `interfaces` (including `ServiceError`).
- **Illegal:** `assets`; `events`; `repos`; `blueprints`; `contexts`; `mappers`; `utils`.
- **Constraint:** the layer stays event-free and asset-free. A missing provider raises `ServiceError`. A resolver that invoked the work it holds would have joined the domain it serves.

The package is `core.py` plus `dependency_injector.py`. There is no `di/settings.py`.

#### `events`

The unit of work. An event commands, executes, and returns a noun. It is the only pattern that legally sees both policy nouns and potential contracts.

- **Legal `# ** app`:** `assets`, `domain`, `mappers`, `utils`, `interfaces`.
- **Illegal:** `di`, `repos`, `contexts`, `blueprints`. Inbound edges come from `assets`, `blueprints` (bootstrap), and `contexts` (client); `di` does not import events.
- **Constraint:** `execute` returns a domain model when one exists, otherwise anything it can legally reach beneath it — an aggregate, a transfer object, a util result, or an interface-shaped value. Never a context, a blueprint, or a repo. Error constants are `a.<submodule>.*` (`a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`).

Without events there is nothing for a feature to wire. A consumer's first act after configuration is writing an `execute`.

### Potentials

Potentials are the forms a policy noun can take at a boundary: a mutable body, a contract, a substrate capability. They do not declare what the work *is*.

#### `mappers`

The same noun, given a body that can change or a face that can cross a boundary.

- **Aggregate** — internal state. Factory and mutation methods (`set_attribute`, `rename`, …). `ModelError` on validation failure.
- **TransferObject** — cross-boundary state: how the noun is represented for a database, a config format, or a custom response, without breaking the model.
- **Legal `# ** app`:** `domain` only.
- **Consumed by:** `events`, `interfaces`, `utils`, `repos`.
- **Constraint:** mappers do not import `utils`.

#### `interfaces`

The contract that outlasts any one store. `Service` ABCs: vertical contracts for persistence, files, middleware, and DI.

- **Legal `# ** app`:** `mappers` — prefer the aggregate over the domain model when one exists, especially where the implementor will be a repository; sibling interfaces.
- **Consumed by:** `events` (injected services), `di` (`DIService`, `ServiceError`), `utils` (when a util must be injectable), `repos` (the Service being implemented).
- **Constraint:** presented to `blueprints` only through `di`. Contexts do not import interfaces.

#### `utils`

Substrate capability, physical or computational. A util carries a `Service` contract when the computation is extensible (a second implementation is plausible) *and* a feature step must be able to resolve it by service id. Otherwise it remains a raw computational container that events import and call.

- **Legal `# ** app`:** `interfaces` (including `ServiceError`); `mappers`; sibling utils.
- **Consumed by:** `events` (directly or via an interface), `repos` (loaders).
- **Constraint:** a util may not form a semantic opinion. It preserves structure across contact with a substrate. Its failures are medium failures — not found, could not load, could not save.

### Operations

#### `repos`

Persistence. A repository implements a `Service`, maps through transfer objects and aggregates, and is never imported by the rest of the framework.

- **Legal `# ** app`:** `interfaces` (the Service being implemented, and `ServiceError`); `mappers` (transfer objects and aggregates); `utils` (loaders).
- **Illegal:** `assets`, `domain` (use a mapper), `events`, `di`, `blueprints`, `contexts`.
- **Constraint:** nothing imports `repos`. They are never exported. A store must not claim to be the thing stored.

Pattern, as in `ConfigurationRepository`: the repo knows the loader, performs transfer-object and aggregate mapping inside the interface methods, and never leaks a loader or a file path upward.

## Import law

The table is the enforceable form of the layers and the pattern jobs above.

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

Decision support does not import potentials or operations. Policy does not import operations. Potentials do not import decision support or `events`. Operations import only potentials. Intra-layer edges are narrower still: `blueprints` may not import `domain`; `di` may not import `events`; `mappers` may not import `interfaces`.

If an artifact needs an import its row forbids, the placement is wrong rather than the row.

## Collaboration without a direct import

Import law forbids a package edge. Components still collaborate.

The general shape is a reverse dependency: a caller receives a collaborator without importing the package that produced it. Two operating cases:

- **Injected `get_dependency`.** `contexts` and `blueprints` resolve instances without importing `di` classes. `parse_parameter` is this shape.
- **Blueprint handler slots.** The session hub runs without constructing sibling contexts. The blueprint closes over cache and resolver; the hub stores the callables and delegates.

Other contact that is not an import edge uses the same idea through a legal neighbor. Bootstrap catalogs in `assets` shape what `di` resolves, and `di` may not import `assets` — the catalogs arrive as validated data assembled by a blueprint. `di` constructs domain events from a declared `module_path` and `class_name`, and `di` may not import `events` — contact is dynamic resolution. Nothing above operations imports `repos`, and the system runs on repositories — they arrive as `Service`-typed instances.

A declared dependency without an import edge is an intended consequence of the law, not an exception to it.

## The domain map

A state is a cell. A domain concept is a word. The word declines across the ten cores: present or absent, under the obligation that cell already owns. That occupancy is the concept's vector.

The token carries the ontology; the suffix names the obligation. `Feature` / `FeatureEvent` / `FeatureContext` / `FeatureAggregate` / `FeatureService` / `FeatureConfigRepository` are one concept seen across six cells, not six artifacts that happen to share a prefix. A shared token does not imply shared behavior, and two concepts with the same vector are the same concept wearing two labels — or the map is lying.

The domain map is the matrix of every concept in the bounded context against the ten cores. It is immanent: capturable from catalogs, class names, suffixes, service ids, and the repositories that implement a `Service`, and regenerable from them. Transcendent knowledge lands as a new row, a newly filled cell, or a newly emptied cell. It does not land as an eleventh package, and it does not land as a `set_*` on the noun. Reception is inflection.

A full mapping is not a fully populated grid. Empty is allowed. Empty is information: a mapped refusal. `Sqlite` occupying `utils` and refusing `domain` and `contexts` is a mapped refusal, and it is why the industry-standard name is the correct one. What is not allowed is a permutation the running system actually produces that has no cell, no obligation, and no name.

Contour and mechanism are the two faces of the same word, and both have to be mapped or the word is only generally defined.

- **Conceptual contour** lives first at `domain` and inflects only where the word is still that noun: what the word may mean, where it stops, what it refuses. A contour mapped without a mechanism leaves the mechanism generally undefined.
- **Cohesive mechanism** lives first at `events` and is sequenced at `contexts`, resolved at `di`, contracted at `interfaces`, and stored at `repos`: how a declared fact, rule, or problem is completed without becoming a second model. Evans' distinction holds — the model formulates, the mechanism completes. A mechanism written against a shadow of the objects it governs leaves the contours anemic to match it.

A dialect grows by declension, not by fork. New meaning arrives as a new row or a newly occupied cell of an existing core. It does not arrive as a framework fork, and it does not arrive by lowering the domain until it fits the generator. The first cannot say what it does not already have words for. The second cannot regenerate what it has already mixed.

## What the mapping refuses

The mapping stays safe while it grows because three refusals hold, and each is the import law of one core stated as an obligation:

- **The noun will not change itself.** Mutation on a domain object is a contour that has taken on an act. It belongs to the aggregate.
- **The resolver will not use what it holds.** A resolver that invoked the instance it resolved would have joined the domain it serves, and could no longer resolve every dialect alike.
- **The store will not claim to be the thing stored.** A repository that imported the domain type would be asserting identity with what it persists, and the round trip would have nowhere to be lossy.

The refusals are immanent — they are readable off the import table and enforceable by it. What they protect is transcendent: the meaning a dialect has not yet found words for, which can only arrive if the cells it would occupy are still empty and still named.

## Extending the patterns

A domain application does not add a pattern. It extends the abstraction already occupying one.

| The thing being added | Extends | Lands in |
|---|---|---|
| A new noun | `DomainObject` | `domain` |
| A new operation | `DomainEvent` | `events` |
| A mutable form of a noun | `Aggregate` | `mappers` |
| A boundary representation | `TransferObject` | `mappers` |
| A vertical capability contract | `Service` | `interfaces` |
| A concrete store for that contract | implements the `Service` | `repos` |
| A runtime mode or session surface | `BaseContext` | `contexts` |
| A physical or computational capability | util (service-backed or raw) | `utils` |
| Application composition | a build function | `blueprints` |
| Bootstrap invariants and catalogs | constants and factories | `assets` |

Growth adds an inflection where the concept must appear. It never populates a template.

When a domain concept cannot be expressed through the ten, the framework is missing a primitive, or the concept belongs to another bounded context.

This chapter states the layers, the pattern cores, and the map. It does not show how to build a dialect: worked construction belongs to the tutorial, and per-application distillation to `docs/guides/`.

## Runtime

Composition and the live session graph are specified in [blueprints.md](blueprints.md) and [contexts.md](contexts.md). This chapter does not walk the call tree.

The session context is a handler hub. It sequences injected callables whose arity is that of the context type. The event remains the unit of work. A feature step names a service id and receives a live operator; provenance (bootstrap catalog, session-scoped service, feature-level registry) is not visible at the call site.

Style and annotation grammar live in [code_style.md](code_style.md). Per-application distillation lives in `docs/guides/` and is not this constitution.
