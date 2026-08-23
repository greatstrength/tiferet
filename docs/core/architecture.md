# Architecture in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

> Generating a running program from a declaration of model properties is a kind of Holy Grail of MODEL-DRIVEN DESIGN, but it does have its pitfalls in practice...
>
> — Eric Evans, *Domain-Driven Design*, Chapter 10 (Supple Design)

## The problem

Evans names the ambition and then, in the same breath, names why it keeps failing. Two pitfalls in particular: a declaration language that is not expressive enough to do everything needed, inside a framework that makes it difficult to extend beyond the automated portion; and code generation that cripples the iterative cycle by merging generated output into handwritten code so that regeneration is destructive.

Both are failures of the same kind. They are not failures of ambition, and they are not failures of tooling. They are failures of *vocabulary*. A declarative system needs a fixed set of things a declaration can be about. Make that set too small and the domain cannot be said. Make it open and unconstrained and nothing can be composed from it, because no component can predict the shape of another.

So the grail is not a compiler trick, and the open question is not *whether* to declare. It is the **what**: which closed set of responsibilities can a whole application be declared against, such that the declaration is complete enough to run and constrained enough to compose?

## The thesis

Tiferet answers with a System Metaphor — the Sefirotic tree — used as a **stable intermediate representation of systemic responsibility**.

The claim is precise, and it is what the rest of this chapter defends:

> The Tree supplies a fixed set of representational coordinates for what a part of a system may *be*. Tiferet projects those ten positions into computational abstractions. A domain application extends those abstractions as a **dialect**, introducing unlimited new meaning without introducing new coordinates.

This is the bargain a multi-level compiler IR makes. MLIR is extensible because its representational grammar is stable: operations, regions, values, types, traits. A dialect adds semantics, never a new grammatical category. Stability at the coordinate level is exactly what makes openness at the semantic level safe — passes compose across dialects because every dialect is built from the same parts.

Tiferet makes the architectural version of that trade. Ten closed responsibilities, one operational center, and edges that refuse to let a factory become a client or an emitter become an absorber. A consumer does not add an eleventh position. A consumer extends the abstraction already sitting in one of the ten.

Evans' two pitfalls dissolve accordingly. Expressiveness is unbounded, because a dialect can say anything through `DomainObject` and `DomainEvent`. Regeneration is non-destructive, because the declaration and the handwritten extension occupy different levels — the coordinates belong to the framework, the meaning belongs to the domain.

### The price of declaring in advance

The epigraph has to be paid for, because Evans is explicit that what it promises should not be obtainable this way. Conceptual Contours, he writes, are "typically the outcome of refactoring: it is hard to produce up front," and they "may never emerge from a technically oriented refactoring" (261–262). That is what makes the deep model a grail: not unreachable, but not available on demand and not reachable by mechanical means.

The ten were not asserted ahead of that work. The axes were found the way Evans says axes are found — by successive refactoring, across this framework's own history — and the Tree was recognized afterward as the thing that had already named them. The direction of fit matters, because the reverse order would be a retrofit.

So the cost was paid, and what the coordinates do is **relocate** it. What is saved is the repetition, not the discovery, and the relocation lands on a dialect author rather than on the framework: a dialect author receives coordinates they did not find, for a domain — systemic responsibility — that was understood before they arrived. What refactoring would have taught them must instead be supplied as domain expertise at the moment the dialect is declared, which means the framework demands *more* of whoever declares one, not less. A reader who suspects the coordinates are a way of skipping the work is asking exactly the right question, and the honest answer is that the work was done once and the demand moved rather than disappeared.

Two guards keep the claim narrow. The coordinates are fixed for a domain that is *already* understood — systemic responsibility, worked out over this framework's own history — so a consumer's dialect still earns its own contours the slow way, inside the coordinates. And Evans' *never* is stronger than it looks: he is not saying mechanical work does this badly, he is saying it may not arrive at all. That is the next subsection's distinction, reached from the source side.

### Mechanical rules, semantic commitments

The obvious objection to all of this is that the import table could simply be published on its own and the Hebrew dropped. The answer is that the table is the **shadow**. The positions are what cast it. Every mechanical rule in this chapter is the enforceable form of a semantic one:

- `repos` may not import `domain` because a store must not claim to be the thing stored.
- `domain` is read-only because a noun that mutates itself has taken on an act.
- `di` stays event-free because a resolver that invoked what it holds would have joined the domain it serves.

Strip the positions and those become arbitrary lines to be memorized. Keep them and the rules are *derivable*, which is the difference between a convention and an architecture.

The general form: infrastructure verifies **shape**, and only the domain tier is answerable for **meaning**. Resolution matches a name and a flag, never a meaning. A loader preserves a structure, never a semantics. Exactly one position is required to be right in both registers at once and forbidden to trade either for the other, and that position is Gevurah.

The rider is load-bearing: the coordinates are **bounded, not checked**. They constrain the space of meanings a word can have. They never verify that the occupant means what it claims. Nothing here validates domain semantics, and the chapter should not be read as promising that it does.

### Influence and dependency are two graphs

One pattern recurs often enough to state once rather than re-explain defensively in every chapter: **influence travels by declaration, dependency travels by import, and the two are deliberately not the same graph.**

Three instances, all real:

- Bootstrap catalogs in `assets` shape what `di` resolves, and `di` may not import `assets`. The catalogs arrive as validated data, assembled by a blueprint.
- `di` constructs domain events from a declared `module_path` and `class_name`, and `di` may not import `events`. Contact is by dynamic resolution.
- Nothing above the veil imports `repos`, and the entire system runs on repositories. They arrive as `Service`-typed instances.

A real dependency with no import edge is not the law being fudged. It is the mechanism the law exists to permit.

### Why a framework at all

Every other borrowed pattern justifies a position or a rule. One justifies the decision to build a framework in the first place. Evans prescribes partitioning "a conceptually Cohesive Mechanism into a separate lightweight framework," exposing it "with an Intention-Revealing Interface," so the rest of the domain can "focus on expressing the problem, delegating the intricacies of the solution" (422–423). Tiferet is that partition, performed once and published.

The same passage divides the labor. The model "formulates a fact, rule, or problem"; the mechanism "resolves the rule or completes the computation as specified by the model." That is the split between `events` and `contexts` exactly — the operator formulates, the runtime resolves — and it means the framework's central paradox, that its most important artifact is inert until something resolves it, is an instance of a named pattern's internal structure rather than a local quirk. [events.md](events.md) carries the detail.

One caution travels with this and is not optional. Core-versus-mechanism is a **relative position, not a kind of code**. Tiferet is pure mechanism to a dialect, while internally holding its own core domain (the `Feature` family) and its own mechanisms (`utils`, `repos`). Read without that level named, the ten collapse into two.

### One structural claim, one reading aid

Two of Evans' patterns are in play in these chapters, and they are not doing the same job. Conflating them is the likeliest way to misread everything that follows.

The **System Metaphor** is the structural claim, and it is not hedged. The ten positions are Tiferet's large-scale structure. Every artifact in the framework, and every artifact in a dialect built on it, occupies exactly one. The import law, the placement test, and the composition order are consequences of it. Remove the metaphor and there is no architecture left to describe.

Evans' **Responsibility Layers** enters one tier down, as a reading aid — a metaphor read through a metaphor. Its *method* is used directly and stays in force: responsibilities were found by reading conceptual dependencies and the differing rates and sources of change, and each must be broad enough that an artifact fits inside one. Its *layer names* — Capability, Operations, Decision Support, Policy, Commitment — are borrowed only where they illuminate how a position behaves at runtime and what shape its artifacts tend to take, which is a question of code morphology as much as of contract.

The names are never identity claims. `events` is not a Policy layer; it reads usefully *through* Policy, because the comparison explains why the most important artifact in the system is completely inert until something resolves it. `interfaces` is not a Commitment layer; it reads usefully through Commitment, because a promise really does precede the thing promised.

Two consequences follow, and both are load-bearing. More than one position may be read through the same layer, to different depths, without any conflict to resolve. And a layer name that describes a position better than its own package name is a naming proposition to weigh on its own merits, not a structural finding — Policy is arguably the better name for what `events` holds, and a fair v3 rename candidate, but nothing in the structure depends on it.

Evans licenses this arrangement more directly than the demotion actually requires. He names "changing from one kind of structure to another, say from Metaphor to Layers" as a transition a well-structured design survives (482–483), which treats the two as interchangeable large-scale structures over one domain. Holding both at once, with one demoted to a lens, is therefore a *weaker* move than the outright swap he calls workable. This project produced an instance while settling the stance: relabeling `repos` from Operations to Potential changed nothing in the import law, only the label — which is what Evans predicts when the accumulated knowledge sits in the model rather than in the naming.

### Both halves of the claim

The stable-IR claim has two halves that pull against each other, and an older statement of the same tension describes it better than this chapter can from the inside. Abelson, introducing the Soncino *Zohar*, reads its treatment of the divine as an attempt to hold transcendence and immanence in a single concept: the great Unknowable, "exalted above human understanding," and simultaneously "very knowable, very fathomable," legible off the world itself (16).

Both halves are load-bearing here. The deep model is the transcendent half — approached by refactoring toward deeper insight, never fully possessed, which is the epigraph's whole point. The coordinates are the immanent half — fixed, present in every artifact, and readable straight off a class signature, which is why `class FeatureAggregate(Feature, Aggregate)` can be parsed for position without consulting anything else. An unreachable model and a completely present structure, at once.

The most useful line in the passage is its disclaimer: "Not that it does this with a strict scientific consistency. Far from it." The two doctrines are *interwoven*, not reconciled. That is precedent for what this chapter has to admit anyway — up-front coordinates and a deep model that cannot be produced up front are not reconciled here either. The cost is relocated instead, and a structure with that much precedent is better described as deliberate than as a concession.

One reading is out of bounds. The same passage describes "a constant and conscious interaction between 'the above' and 'the below'", and that must **not** be mapped onto the veil. The import graph is a one-way DAG, and a two-way-traffic reading would license precisely the reverse edge the law forbids. Take the legibility and leave the interaction — and leave the passage's microcosm imagery, organs and limbs reflecting the divine, alone for the same reason: neither predicts an import, an artifact, or a lifecycle rule, so neither survives the infusion test.

## Why this graph

A System Metaphor earns its place by being *already distilled* — a shape argued into stability, so that a team walking a scenario lands on the same objects the code already is. The ten-node graph qualifies on publication history.

The name and count of ten sefirot first appear in *Sefer Yetzirah*, securely attested by the early tenth century in Saadia Gaon's commentary. Its rule is already a closed-count rule: "ten and not nine, ten and not eleven." Completeness is the point, and the fixed cardinality is the oldest thing about it. The *theosophical* tree — named potencies in relation rather than a decad of numbers — is medieval: *Sefer ha-Bahir* in late-twelfth-century Provence, consolidated by the Zoharic literature of thirteenth-century Castile. The *diagram* as a circulated engineering object is early modern: Cordovero's *Pardes Rimonim* (composed 1548, printed in Kraków 1591), and Kircher's *Oedipus Aegyptiacus* (1652–54) for the Latin reception.

What survived that process is a relational model: how expansion is checked by form, how a middle holds both sides, how the last position absorbs what the first emits. That is what is borrowed here, and only that. A name is kept in these chapters only while it still predicts an import, an artifact, or a responsibility.

The Hebrew names and the package names occupy one ubiquitous language. Skills, guides, tutorials, and `AGENTS.md` stay in package names, so an implementor can write a correct `# ** app` import from the table below without knowing the Tree. These chapters carry both because they are the framework's own philosophy, not a template to copy into the next application.

## How to read the ten

### A heading is one job from two sides

A heading reads `### Gevurah — domain`. The two names give one responsibility from two sides. Each entry states the job, the imports that follow from it, and the constraint the position exists to enforce.

### Two orderings, inverted

A reader who takes the Tree for a layer cake will misread every row of the import table, because the two orderings run in opposite directions.

Evans' layering is a **dependency** ordering: the layer depended upon is the lower one. The Tree's is an **emanation** ordering: the first position is the origin. They invert, and not subtly. `assets` and `domain` import nothing whatsoever, which makes them Evans' floor while sitting at the very top of the Tree. `repos` imports three packages and is imported by none, which puts it at the top of a dependency stack while being the Tree's last position.

Two independent witnesses agree on the inversion: Evans' own observation that lower layers can exist without the higher ones, and the traditional reading of the tenth position as the most exalted of all — a claim that only makes sense against dependency, never against emanation. Neither was consulted for the other. Stating the inversion also disarms a reasonable suspicion, that the descent is a dependency diagram wearing borrowed labels. If it were, the two orderings would point the same way.

### Above and below the veil

The ten divide six from four. Declaration, composition, and orchestration sit above; contract, representation, capability, and persistence sit below. The traditional name for the division is Paroketh, and it falls in the same place Evans draws his own line between what *enables* work and what *is* work — two unrelated derivations landing together.

Below the veil the order is a construction sequence rather than a listing. A mechanism is revealed through its interface first, so assembling one begins at the contract and proceeds through representation and capability to persistence. Two facts make that checkable: `di` crosses the veil to hand instances upward and may import exactly one position below it, `interfaces`; and `repos`, at the far end, is never named above the veil at all.

## The ten positions

### Keter — `assets`

Composition has to begin from something that does not depend on the composition. `assets` holds shared primitives — exceptions, named error codes, bootstrap catalogs — and has no inbound framework edges.

- **Legal `# ** app`:** none.
- **Consumed by:** `blueprints`, `contexts`, `events`, typically `from .. import assets as a`. Core assets may be used by other assets. They do not automatically flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`.
- **Constraint:** Keter emits. It does not absorb, and it does not become runtime.

### Chochmah — `blueprints`

The spark, and the sustaining of it. A blueprint builds the cache, resolves the session, composes the container and the resolver, and builds the handler closures the hub will run for the rest of the session. It is not a step that completes and withdraws. Chochmah is drawn down continuously or the lower world does not persist, and that is the literal shape of the code: the handlers are closures bound to the cache and the resolver, and they stay resident.

- **Legal `# ** app`:** `assets`; `contexts`; `di` for container and resolver classes; `events` for pre-DI bootstrap only.
- **Illegal:** `domain`, `interfaces`, `mappers`, `utils`, `repos`.
- **Constraint:** service instances reach a blueprint only through `di` (`get_dependency`); domain types only through `contexts`.

Chochmah cannot elaborate itself; it requires Binah to become structure. That relation is the one-way construction edge: `blueprints` may import `contexts`, `contexts` may never import `blueprints`.

**The handler is the operation.** `build_app_session_context` builds five closures and injects them; the hub stores them privately and every public method on it is a guarded delegate. The consequences are concrete:

- `execute_feature_handler` constructs the `FeatureContext` per call, through the blueprint's own `create_feature_context`. The hub never constructs it and never imports it.
- `raise_error_handler` resolves the `ErrorContext` at error time via `BaseContext.for_domain(Error)`.
- The lazy-caching closures (`get_error`, `get_feature`, `build_logger_handler`) hold cache state across calls. Memoization lives in the blueprint, not in the hub — `dictConfig` runs once per logger id per process because a blueprint closure remembers.
- An unwired handler is a composition bug and fails loudly through `raise_unwired_handler_error`. A spark that was never sustained cannot run a feature.

So the execution workflow state is held here, in distilled functional form, and the session is what invokes it.

**The pattern is fixed; the arity and the composition are not.** `AppSessionContext` never learns which blueprint filled its slots, so execution is swapped by writing or extending a blueprint rather than by mutating a live session. But five handlers is Tiferet's own arity as a dialect of itself, not a coordinate. The calculator adds a sixth: `CalculatorAppContext` declares `record_run_handler`, guards it with the framework's own `raise_unwired_handler_error`, and fires it after a successful run, while `build_calculator_app_context` builds that closure alongside the other five. Context and blueprint extend in lockstep.

Four swap levels follow, in increasing strength:

1. **Change what a handler closes over.** `blueprints/admin.py` reuses all five core handler functions verbatim and substitutes only the resolver behind them; `build_admin_service_resolver` registers the admin container under both the `admin` flag and the empty-flag default, so admin steps resolve elsewhere while the hub is untouched. Its `build_cache` is the core builder under a different decorator stack, so catalogs layer as declared data rather than branching in code.
2. **Replace a handler function outright.** Available, and unexercised inside the framework.
3. **Add a slot.** The calculator's sixth handler, above.
4. **Compose the builder itself from published parts.** The strongest level, and currently *unavailable* — the session builders fuse resolver composition, handler-bundle construction, and context construction into one body. See [blueprints.md](blueprints.md).

Levels one through three are what keep the arrangement declarative: a new execution profile is a new declaration of the same closed set. They are also why the entry point matters — choosing `App` over `AdminApp` chooses which sustained composition runs. The seams at those levels are declared defaults rather than hooks: `service_container=`, `parse_parameter=`, and `**context_kwargs` on the composition functions.

The crossing for domain types is **Da'ath**: context modules re-export the types factory signatures need (`AppSession`, `Feature`, `Error`, `LoggingSettings`, CLI models). Write `from ..contexts.feature import Feature`, never `from ..domain import Feature`. That is how the factory sees a noun without growing a Gevurah edge — and it is one of two forward substitutions, not a lone exception. See [Crossings and reverse shapes](#crossings-and-reverse-shapes).

### Binah — `contexts`

The client-runtime graph: the session once it exists, able to run without knowing how it was assembled. A context binds a domain object (`from_domain`) and exposes operational behavior — a flat presentation container or a fluent API.

- **Legal `# ** app`:** `assets`; `domain`; sibling contexts; `events` as the client surface.
- **Illegal:** `blueprints` (construction flows down, never back); `interfaces`; `di`; `mappers`; `utils`; `repos`.
- **Constraint:** a context must not invent the work. The work is an event, and the operation is a handler.

The hub **sequences**; it does not implement. `AppSessionContext.run` orders one pass — build the logger, build the request, execute the feature, handle a raised error or build the response — and each of those five steps is a guarded delegate to a closure the blueprint built. Understanding is the vessel that gives the spark a form it can act through, which is why the hub owns order, timing, and lifecycle while owning none of the operations.

The framework's own slots are `build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, and `response_handler`, plus CLI `parse_cli_args`. That is Tiferet's arity, not a fixed contract: a dialect declaring a sixth slot extends the pattern rather than breaking it, and the count is determined by the domain a context serves. What is fixed is the shape — the hub calls slots rather than importing `FeatureContext` / `ErrorContext` / `LoggingContext` to build them, which is why Binah stays a graph instead of a circular import.

### Chesed — `di`

Expansion: a declared service id plus flags becomes a live instance. `di` does not decide what the work is; it expands a contract into something the middle can hold.

- **Legal `# ** app`:** `domain`; `interfaces` (including `ServiceError`).
- **Illegal:** `assets`; `events`; `repos`; `blueprints`; `contexts`; `mappers`; `utils`.
- **Constraint:** the layer stays event-free and asset-free. A missing provider raises `ServiceError`.

The package is `core.py` plus `dependency_injector.py`. There is no `di/settings.py`, and no `CreateServiceResolver` on the current `build_app` path.

### Gevurah — `domain`

Form: the noun that will not change itself. Domain objects house data and offer read-only behavior.

- **Legal `# ** app`:** none of the framework.
- **Consumed by:** `contexts`, `events`, `di`. Blueprints reach domain types only through Da'ath.
- **Constraint:** a `rename` or `set_*` on a domain object is in the wrong package. Mutation is Hod's job.

### Tiferet — `events`

The heart that must know both sides. An event is the only unit of work that commands, executes, and returns a noun — the bridge between session and store, between the human feature and the contract beneath it.

- **Legal `# ** app`:** `assets`, `domain`, `mappers`, `utils`, `interfaces`.
- **Illegal:** `di`, `repos`, `contexts`, `blueprints`. Inbound edges come from `assets`, `blueprints` (bootstrap), and `contexts` (client); `di` does not import events.
- **Constraint:** `execute` returns a domain model when one exists, otherwise anything it can legally reach beneath it — an aggregate, a transfer object, a util result, or an interface-shaped value. Never a context, a blueprint, or a repo. Error constants are `a.<submodule>.*` (`a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`), never `a.const`.

Without events there is nothing for a feature to wire and nothing for a user to mean. This is the position everything else is arranged around, and the reason a consumer's first act after configuration is writing an `execute`.

### Hod — `mappers`

Form-giving: the same noun, given a body that can change or a face that can cross a boundary.

- **Aggregate** — internal state. Factory and mutation methods (`set_attribute`, `rename`, …). `ModelError` on validation failure.
- **TransferObject** — cross-boundary state: how the noun is represented for a database, a config format, or a custom response, without breaking the model.
- **Legal `# ** app`:** `domain` only.
- **Consumed by:** `events`, `interfaces`, `utils`, `repos`.
- **Constraint:** mappers do not import `utils`. A mapper method may accept a `Callable` and receive a util at runtime — one of the three backward edges, not a general exemption.

### Netzach — `interfaces`

The promise that outlasts any one store. `Service` ABCs: vertical contracts for persistence, files, middleware, and DI.

- **Legal `# ** app`:** `mappers` — prefer the aggregate over the domain model when one exists, especially where the implementor will be a repository; sibling interfaces.
- **Consumed by:** `events` (injected services), `di` (`DIService`, `ServiceError`), `utils` (when a util must be injectable), `repos` (the Service being implemented).
- **Constraint:** presented to `blueprints` only through `di`. Contexts do not import interfaces.

### Yesod — `utils`

The capability the rest of the system stands on, physical or computational. Whether a util carries a Netzach contract is decided by two conditions, both required: the computation is genuinely **extensible** (a second implementation is plausible, not hypothetical), and the capability must be **reachable by a feature step**, since only a declared service id can be resolved. Physical-versus-computational is a separate question that does not bear on it — the middlewares are computational and service-backed both.

A contract-free util is therefore a real affordance with zero instances in the framework: `FileLoader` itself implements `FileService`, so every loader inherits a contract transitively, and the three middlewares implement `MiddlewareService`. Stated positively, every capability the framework placed here satisfied both conditions, which is why the arrangement looks like two kinds until you check.

- **Legal `# ** app`:** `interfaces` (including `ServiceError`); `mappers`; sibling utils.
- **Consumed by:** `events` (directly or via an interface), `repos` (loaders), `mappers` only as a runtime visitor callable.
- **Constraint:** a util may not form a semantic opinion. It preserves structure across contact with a substrate, and its failures are medium failures — not found, could not load, could not save.

### Malkuth — `repos`

Kingdom is Keter inverted, and the inversion is exact in cardinality. `assets` emits to exactly three positions — `blueprints`, `contexts`, `events` — and `repos` absorbs from exactly three — `interfaces`, `mappers`, `utils`. Neither end reaches the other seven, and neither end reaches the other.

- **Legal `# ** app`:** `interfaces` (the Service being implemented, and `ServiceError`); `mappers` (transfer objects and aggregates); `utils` (loaders).
- **Illegal:** `assets`, `domain` (use a mapper), `events`, `di`, `blueprints`, `contexts`.
- **Constraint:** nothing imports `repos`. They are never exported. Persistence is the last position, not a voice that speaks back into the factory.

Pattern, as in `ConfigurationRepository`: the repo knows the loader, performs transfer-object and aggregate mapping inside the interface methods, and never leaks a loader or a file path upward.

## Dialects: how a domain extends the coordinates

A domain application does not add a position. It extends the abstraction already occupying one. This is the rule that keeps the metaphor operational rather than decorative:

> **A dialect extends Tiferet's abstractions. It does not alter Tiferet's coordinates.**

Which yields a placement test for consumer code:

| The thing being added | Extends | Lands in |
|---|---|---|
| A new noun | `DomainObject` | Gevurah |
| A new operation | `DomainEvent` | Tiferet |
| A mutable form of a noun | `Aggregate` | Hod |
| A boundary representation | `TransferObject` | Hod |
| A vertical capability contract | `Service` | Netzach |
| A concrete store for that contract | implements the `Service` | Malkuth |
| A runtime mode or session surface | `BaseContext` | Binah |
| A physical or computational capability | util (service-backed or raw) | Yesod |
| Application composition | a build function | Chochmah |
| Bootstrap invariants and catalogs | constants and factories | Keter |

The literature-review dialect is a worked instance: `Source`, `Citation`, `Theme`, and `Linkage` through `DomainObject`; `AddCitation` and `RetireLinkage` through `DomainEvent`; persistence contracts through `Service`; concrete config-backed stores in `repos`. New meaning throughout, no new coordinates anywhere.

### A composite pattern decomposes without residue

Every row above maps one artifact to one position, which invites a fair objection: perhaps the ten only accommodate small things. They do not. A named large-scale pattern decomposes across them cleanly.

An **Anticorruption Layer** is four artifacts at once:

| Part of the pattern | Extends | Lands in |
|---|---|---|
| The capability the system wants from the foreign context | `Service` | Netzach |
| The adapter that speaks the foreign protocol | implements the `Service` | Malkuth |
| The translation between the two vocabularies | `TransferObject` | Hod |
| The operation that orchestrates the crossing | `DomainEvent` | Tiferet |

Nothing is left over, and nothing needed an eleventh position. That is better evidence for the completeness of the set than any single-artifact row.

### How a word declines

The table maps a *kind* of artifact to a position, which is correct and static. It does not show the thing that makes the coordinates worth having: a single domain word **inflects** across positions, and the suffix names what it accreted. A word does not *move* between positions. It picks one up.

The framework's own core domain is the complete worked case, and richer than any dialect's:

- **Gevurah** — five nouns: `Feature`, `FeatureStep`, `EventFeatureStep`, `ParameterSpecification`, `RequestSpecification`.
- **Hod** — two inflected pairs: `FeatureAggregate` / `FeatureConfigObject`, and `EventFeatureStepAggregate` / `EventFeatureStepConfigObject`. The two specification nouns get no mapper at all, because neither has to cross a boundary.
- **Netzach** — one `FeatureService`.
- **Malkuth** — one `FeatureConfigRepository`.
- **Tiferet** — a `FeatureEvent` base and nine concrete operators: `AddFeature`, `GetFeature`, `ListFeatures`, `RemoveFeature`, `UpdateFeature`, and four step operators.
- **Binah** — one `FeatureContext`.

The declension is legible in the signatures, because each one records a domain parent plus a position parent:

```python
class FeatureAggregate(Feature, Aggregate):
class FeatureConfigRepository(FeatureService, ConfigurationRepository):
```

The cardinality is informative too, and it is not uniform. Nouns fan out where variety is the point. Forms fan out only for the nouns that must cross a boundary. Verbs fan out hardest of all, because a noun admits many acts. Netzach, Malkuth, and Binah each collapse to exactly one — one promise, one store, one runtime surface serving the whole family.

Which settles the central misreading. A shared token does **not** imply shared behavior. The token carries the ontology and the suffix carries the position's obligations, and neither alone would do: token alone would imply the artifacts are interchangeable, suffix alone would lose that they are one concept.

### Declension is the membership test

Not every word declines, and that is the finding rather than a ragged edge.

`Feature` declines through six positions because it is core-domain vocabulary and every axis has something to do to it. `Sqlite` does not decline at all. There is no `SqliteAggregate` and no `SqliteContext`, and there should not be — a generic subdomain holds nothing for the axes to transform. So a noun that refuses to decline is announcing that it is generic.

That gives the reader a test rather than a taxonomy. Three questions:

1. Does the word decline across positions?
2. Does it carry domain invariants?
3. Does it contain any project-specific insight?

Three noes means a generic subdomain, and the industry-standard name is then the correct one — which is why `SqliteService` is named after its substrate and is right to be. See [interfaces.md](interfaces.md).

The same principle appears one magnitude down as **code style**, which is why style is a substrate here rather than a rival thesis. Side-effect-free functions, standalone classes, and module-level constants encapsulate non-domain mechanism and generic purpose *inside* a position without belonging to that position's axis. State the principle once and apply it at both scales: never stretch a position's characterization to cover generic machinery — attribute that machinery to style instead.

One question stays genuinely open, and is posed rather than answered. If a generic contract never traverses the axes, which position legitimately hosts it — and does an ABC that never declines sit comfortably above the veil at all?

### When nothing fits

When a domain concept genuinely cannot be expressed through the ten, one of two things is true: the framework is missing a primitive, or the concept belongs to another bounded context. Producing that diagnostic is what a stable intermediate representation is *for*.

### What this chapter does not do

The scope ends at the coordinates. This chapter states that the axes root an order that evolves, and that a dialect grows by extending abstractions rather than by adding positions. It does not show how to build one: worked construction belongs to the tutorial, and per-application distillation to `docs/guides/`. Answering how-to questions here would turn a constitution into a guide.

## Import law

The table restates what the entries above let a reader predict.

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

### Placement procedure

The table above says what an artifact may import once it has a home. This says how to find the home. It is ordered — take the first step that answers and stop.

1. Does it hold no behavior and import nothing from the framework? Shared bootstrap data — constants, error codes, catalogs — is `assets`. A noun carrying domain invariants is `domain`.
2. Does it perform an act: an `execute` that commands, computes, and returns a result? `events`.
3. Does it compose the application — build the cache, resolve the session, wire a container, produce handler closures? `blueprints`.
4. Does it hold a domain object and sequence behavior against it without implementing that behavior? `contexts`.
5. Does it turn a declared identifier plus flags into a live instance? `di`.
6. Is it declaration only — abstract, no body, binding its implementors and shaped by none of them? `interfaces`.
7. Is it derived by extension from a domain type, adding mutation or a boundary representation? `mappers`.
8. Does it touch a substrate the system does not control? If it exposes that substrate as a capability, `utils`. If it implements a domain-shaped contract over one and nothing imports it, `repos`.

Then verify against the table: read the chosen package's row, and if the artifact needs an import the row forbids, the placement is wrong rather than the row. If no step answers, run the three declension questions and then see [When nothing fits](#when-nothing-fits).

The procedure and the table are executable on their own. Everything above them explains why the rules are derivable rather than arbitrary, which is worth knowing and is not a prerequisite for applying them.

### Sparseness

**A position is realized on demand. An unrealized position is the normal case, not a gap.**

This is a rule, and it is stated beside the law because it is the one an unexamined symmetry gets wrong. Nothing obliges a domain word to appear in all ten positions, and the framework's own core domain is the proof: `ParameterSpecification` and `RequestSpecification` get no mapper at all, and `interfaces`, `repos`, and `contexts` hold exactly one artifact each for the entire `Feature` family — one promise, one store, one runtime surface — against five nouns and nine operators elsewhere.

So growth means adding a declension where the concept must genuinely appear, never populating a template. Left unstated, this is where a reader infers that symmetry implies completeness and generates ten artifacts to say what three would have said. A framework that produces ten artifacts for one concept is ceremony, and the sparseness rule is what distinguishes the coordinates from a form to be filled in.

## Crossings and reverse shapes

Edges are one-way by default, and there are exactly two ways around one. They differ in kind and must not be pooled: a backward edge runs against the graph, while a forward substitution runs with it and lands somewhere the direct edge was forbidden.

### Backward edges — three, and closed

A callable crossing backward is not a general exemption. Only these are allowed:

1. **Injected `get_dependency`** — `contexts` and `blueprints` resolve instances without importing `di` classes. `parse_parameter` is this shape.
2. **Blueprint handler slots** — the hub runs without constructing sibling contexts.
3. **A mapper method typed `Callable`** — a util may visit at runtime without `mappers` importing `utils`.

A fourth backward shape is a design change, not a reading of the Tree.

### Forward substitutions — two known

A forbidden *direct* edge may still be satisfied by a legal transitive route through the position in between. This is a category rather than a single named exception; Da'ath is simply the first instance anyone noticed. Two mechanisms are in evidence:

1. **Re-export.** The intermediate re-exports the target's name so the consumer may write it: `blueprints` → `contexts` → `domain`. This is Da'ath.
2. **Contract-typed.** The intermediate types its own signatures with the target, so the consumer handles values it can neither name nor import: `di` → `interfaces` → `mappers`. In code, `interfaces/di.py` declares `get_registration(...) -> ServiceRegistrationAggregate` and `di/dependency_injector.py` imports `DIService`, while `di/` contains zero references to `mappers` or `Aggregate` and demonstrably operates on them.

The contract-typed case is the purer specimen. The re-export still leaves a visible import line to follow; this one leaves nothing at either end.

## Runtime flow

Composition descends; execution runs the declared graph.

```
App('interface_id')                               # blueprints/core.py: build_app()
  └─ build_cache()                               # CacheContext pre-seeded with framework defaults
  └─ get_app_session(id, cache)                  # GetAppSession event → AppSession
  └─ build_app_session_context(session, cache)   # wires DI, constructs hub with five handlers
       └─ AppSessionContext.run(feature_id, data)
            ├─ build_request()                   # → RequestContext
            ├─ execute_feature()
            │    └─ injected execute_feature_handler   # blueprint closure, resident for the session
            │         └─ FeatureContext.execute_feature(request)
            │              └─ for each step:
            │                   get_dependency(service_id, *flags)
            │                       #  name in, instance out. Three possible provenances,
            │                       #  indistinguishable at the call site:
            │                       #    a bootstrap catalog seeded into the cache,
            │                       #    a session-scoped service on the resolved session,
            │                       #    the feature-level registry in config.yml.
            │                       #  A repository and a domain event compose identically.
            │                       └─ DomainEvent.handle(EventCls, dependencies, **kwargs)
            │                            └─ event.execute(**kwargs) → result on request
            └─ build_response()                  # → RequestContext.handle_response()
```

The blueprint composes and stays resident as the handlers. The session sequences them. The event does the work.

The unremarkable-looking line in the middle is where the whole arrangement is tested. A feature step names a service and receives a live operator, never learning which collection answered, how it was constructed, or what lifetime it was given. The calculator shows all three streams in one config file:

- `calc.safe_divide` names `divide_number_event`, which appears in no `services:` block at all — it resolves from the bootstrap catalog seeded into the cache (`app/assets/di.py`).
- `calc.history` names `list_recent_formulas_event`, declared in the feature-level `services:` registry.
- `record_run_event` is declared under `sessions.calc_client.services`, scoped to one session.

Same call, same handling, three provenances. Kind does not change treatment either: `formula_service` is a repository sitting in the same registry as the domain events beside it, composed the same way. That is what makes the declaration a declaration rather than a lookup with special cases — and it is why `di` can stay indifferent to meaning while remaining the thing the whole feature loop runs on.

## The ten chapters

- [assets.md](assets.md) — Keter: emit, no inbound edges
- [blueprints.md](blueprints.md) — Chochmah: the spark, sustained as the handlers
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

- The grail is Evans'; the open question is the *what* of declarative design. Its two pitfalls — an inexpressive declaration language and destructive regeneration — are failures of vocabulary.
- Tiferet answers with the Sefirotic tree as a stable intermediate representation of systemic responsibility: fixed coordinates, unlimited meaning.
- The ten were found by refactoring, not asserted ahead of it. What the coordinates relocate is the *repetition* of that work, onto whoever declares a dialect and must supply as expertise what refactoring would otherwise have discovered.
- The deep model is never fully possessed; the coordinates are fixed and legible off a class signature. The two are interwoven rather than reconciled, and the relocated cost is the price of holding both.
- Infrastructure verifies shape; only the domain tier is answerable for meaning. The coordinates are bounded, not checked — they constrain what a word can mean and never verify that it means it.
- Influence travels by declaration and dependency travels by import. They are deliberately not the same graph, which is why a real dependency can exist with no edge.
- The import table is the shadow; the positions are what cast it. Every mechanical rule is the enforceable form of a semantic one, which makes the rules derivable rather than memorized.
- The System Metaphor is the structural claim. Evans' Responsibility Layers is a reading aid: its method for finding broad responsibilities is used directly, its layer names are lenses on behavior and morphology, never placement claims.
- Evans' layering orders by dependency; the Tree orders by emanation. They invert, so the Tree is not a layer cake and the import table must not be read as one.
- Ten closed jobs. One operational center (`events`). Six positions above the veil, four below, and the four below are a construction sequence: contract, representation, capability, persistence.
- Two ways around a one-way edge, and they differ in kind: three backward edges, closed; and forward substitutions, of which Da'ath is one instance and the contract-typed crossing is the purer one.
- The blueprint does not withdraw after composition. Its handler closures stay resident and hold the execution workflow state; the session sequences them and implements none of them.
- The handler *pattern* is fixed; the arity and the composition are not. Five slots is Tiferet's own arity, the calculator declares a sixth, and four swap levels follow — the strongest of which is not yet available.
- A dialect extends the abstractions; it does not alter the coordinates. A concept that fits none of the ten is either a missing primitive or a different bounded context.
- A domain word declines across positions, and the suffix names what it accreted. A shared token does not imply shared behavior.
- A word that refuses to decline is announcing that it is generic — which makes declension the membership test for the core domain, and makes the industry-standard name the right one for everything that fails it.
- A position is realized on demand, and an unrealized position is the normal case rather than a gap. Growth adds a declension where the concept must appear; it never populates a template.
- The import table and the placement procedure are executable on their own. The philosophy explains why the rules are derivable; the rules do not depend on it.
- Hebrew and package names share one ubiquitous language. A name is kept only while it predicts an import, an artifact, or a responsibility.

## Sources

The works these chapters borrow vocabulary from. Two filters were applied: the term has to be *used* somewhere in `docs/core/`, and the work has to be established enough that a reader can be sent to it without qualification. Some entries are drawn on by the component chapters rather than by this one. The links are for acquisition, and the recommendation is sincere — read the originals.

- **Eric Evans, *Domain-Driven Design*** — System Metaphor, Responsibility Layers, Bounded Context, Cohesive Mechanism, Intention-Revealing Interface, Conceptual Contours, Anticorruption Layer, Published Language, Customer/Supplier, declarative design, and the grail passage this chapter opens on. [Find it](https://www.amazon.com/s?k=Domain-Driven+Design+Tackling+Complexity+in+the+Heart+of+Software)
- **Lattner et al., *MLIR: A Compiler Infrastructure for the End of Moore's Law*** — dialect, open extensible IR, progressive lowering. [arXiv:2002.11054](https://arxiv.org/abs/2002.11054)
- **Herbert Simon, *The Sciences of the Artificial*** — near-decomposability, stable intermediate forms, state versus process description. [Find it](https://www.amazon.com/s?k=The+Sciences+of+the+Artificial+Herbert+Simon)
- **Russell and Norvig, *Artificial Intelligence: A Modern Approach*** — production system, working memory, condition-action rules, knowledge base versus inference engine. [Find it](https://www.amazon.com/s?k=Artificial+Intelligence+A+Modern+Approach+Russell+Norvig)
- **Fred Brooks, *The Mythical Man-Month*** (anniversary edition, which contains "No Silver Bullet") — essential versus accidental complexity, conceptual integrity. [Find it](https://www.amazon.com/s?k=Mythical+Man-Month+Anniversary+Edition+Brooks)
- **Allen Newell, "The Knowledge Level"** — the principle of rationality, knowledge level versus symbol level. [doi:10.1016/0004-3702(82)90012-1](<https://doi.org/10.1016/0004-3702(82)90012-1>)
