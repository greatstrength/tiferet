# Architecture in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

## The problem

Declarative design fails in two related ways. A declaration language that cannot name the required domain behavior cannot generate a running program. Code generation that merges generated output with handwritten code makes regeneration destructive.

Both failures are failures of *vocabulary*. A declaration needs a closed set of responsibilities it can address. Too small a set cannot express the domain. An unconstrained set cannot predict the shape of its neighbors.

Without that closed set, a program is not a composition of structural patterns. It is a variety of objects and functions in modules. Every module is a room; nothing in the language says which rooms may call which, or what job each room is for.

The open question is not whether to declare. It is **what** a declaration may address: which closed set of responsibilities lets an application run and still compose as its domain evolves.

## The thesis

Tiferet answers with Evans' **Responsibility Layers** as structural patterns.

Four layers hold ten pattern cores — the packages. An application extends those cores as its domain dialect. It does not add a layer, and it does not add a package.

The layers are:

- **Decision support** — `assets`, `blueprints`, `contexts`. Catalogs, composition, and the live session graph.
- **Policy** — `domain`, `di`, `events`. Nouns, resolution, and units of work.
- **Potentials** — `mappers`, `interfaces`, `utils`. Mutation and representation, contracts, and substrate capability.
- **Operations** — `repos`. Persistence that implements a contract and is never imported.

Import law, placement, and the live session graph follow from those layers and from the job of each pattern inside them.

## Why a framework

A framework exists so a new or extended application does not rebuild the same machinery. Feature dispatch, session composition, resolution, error shaping, and configuration persistence are the same jobs in every dialect. The pattern set is the shared machinery; the dialect supplies domain meaning.

Tiferet is mechanism to a dialect. Internally it still has its own core domain (the `Feature` family) and its own operations (`repos`) and potentials (`utils`). Core-versus-mechanism is relative to the reader, not a kind of code.

## Responsibility layers

A layer is a structural pattern: a band of responsibility broad enough that an artifact fits inside one of them, found by reading conceptual dependencies and rates of change.

The ten packages are the pattern cores inside those bands. They are not coordinates on another diagram. Naming a package is naming a job.

Two consequences are mechanical:

- An artifact occupies exactly one pattern. A composite design (an anticorruption layer, a config-backed store, a CLI session) decomposes across patterns; it does not invent an eleventh package.
- A pattern is realized on demand. An unrealized pattern is the normal case, not a gap.

Infrastructure verifies **shape** — names, flags, file structure, constructor signatures. Policy is answerable for **meaning**. The layers bound what a word can mean. They do not check that a dialect's conceptual contours are coherent.

## The ten patterns

Each entry states the job, the imports that follow from it, and the constraint the pattern exists to enforce.

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

Policy names what the system is allowed to mean: the noun, the resolution of a declared id, and the unit of work.

#### `domain`

The noun that will not change itself. Domain objects house data and offer read-only behavior.

- **Legal `# ** app`:** none of the framework.
- **Consumed by:** `contexts`, `events`, `di`. Blueprints reach domain types only through `contexts`.
- **Constraint:** a `rename` or `set_*` on a domain object is in the wrong package. Mutation is `mappers`.

#### `di`

Resolution: a declared service id plus flags becomes a live instance. `di` does not decide what the work is.

- **Legal `# ** app`:** `domain`; `interfaces` (including `ServiceError`).
- **Illegal:** `assets`; `events`; `repos`; `blueprints`; `contexts`; `mappers`; `utils`.
- **Constraint:** the layer stays event-free and asset-free. A missing provider raises `ServiceError`. A resolver that invoked the work it holds would have joined the domain it serves.

The package is `core.py` plus `dependency_injector.py`. There is no `di/settings.py`.

#### `events`

The unit of work. An event commands, executes, and returns a noun. It is the only pattern that legally sees both policy nouns and potential contracts.

- **Legal `# ** app`:** `assets`, `domain`, `mappers`, `utils`, `interfaces`.
- **Illegal:** `di`, `repos`, `contexts`, `blueprints`. Inbound edges come from `assets`, `blueprints` (bootstrap), and `contexts` (client); `di` does not import events.
- **Constraint:** `execute` returns a domain model when one exists, otherwise anything it can legally reach beneath it — an aggregate, a transfer object, a util result, or an interface-shaped value. Never a context, a blueprint, or a repo. Error constants are `a.<submodule>.*` (`a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`), never `a.const`.

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

A domain word inflects across patterns. The token carries the ontology; the suffix names the pattern's obligations. `Feature` / `FeatureAggregate` / `FeatureConfigObject` / `FeatureService` / `FeatureConfigRepository` / `FeatureEvent` / `FeatureContext` are one concept, not interchangeable artifacts. A shared token does not imply shared behavior.

Not every word inflects. `Sqlite` has no aggregate and no context; a generic subdomain holds nothing for the patterns to transform. A noun that refuses to decline is announcing that it is generic, and the industry-standard name is then the correct one.

Growth adds an inflection where the concept must appear. It never populates a template.

When a domain concept cannot be expressed through the ten, the framework is missing a primitive, or the concept belongs to another bounded context.

This chapter states the layers and the pattern cores. It does not show how to build a dialect: worked construction belongs to the tutorial, and per-application distillation to `docs/guides/`.

## Runtime

Composition and the live session graph are specified in [blueprints.md](blueprints.md) and [contexts.md](contexts.md). This chapter does not walk the call tree.

The session context is a handler hub. It sequences injected callables whose arity is that of the context type. The event remains the unit of work. A feature step names a service id and receives a live operator; provenance (bootstrap catalog, session-scoped service, feature-level registry) is not visible at the call site.

## Pattern chapters

- [assets.md](assets.md) — bootstrap primitives, no inbound edges
- [blueprints.md](blueprints.md) — composition; handler closures that stay resident
- [contexts.md](contexts.md) — live session graph; runtime handler hub
- [di.md](di.md) — resolution of a declared id
- [domain.md](domain.md) — the noun that will not mutate itself
- [events.md](events.md) — the unit of work
- [mappers.md](mappers.md) — mutation and representation
- [interfaces.md](interfaces.md) — the enduring contract
- [utils.md](utils.md) — substrate capability, physical or computational
- [repos.md](repos.md) — persistence; never imported, never exported

Style and annotation grammar live in [code_style.md](code_style.md). Per-application distillation lives in `docs/guides/` and is not this constitution.
