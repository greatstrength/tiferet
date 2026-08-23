# Interfaces in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Endurance is the promise that outlasts any one store. Interfaces are `Service` ABCs: vertical contracts for persistence, files, middleware, and DI. That position is **Netzach**. A service does not run a feature and does not open a file. It names what any implementor — a repo, a util, a test double — must be able to do. See [architecture.md](architecture.md).

Legal `# ** app` imports: `mappers` (aggregates) to type domain-related outputs, especially when the implementor will be a repository. Prefer the aggregate over the domain model when an aggregate exists. Sibling interface modules are legal. `contexts` and `blueprints` do not import this package. Service instances reach a blueprint only through `di`.

## Life in the system

`Service` (`tiferet/interfaces/core.py`) is a minimal ABC. Everything vertical converges on it: error catalogs, feature workflows, files, SQLite, configuration, cache, middleware, DI registrations. Commands and domain events depend on the contract (`error_service.save(error)`). They never name `ErrorConfigRepository`. Chesed expands the registration into an instance. Malkuth or Yesod satisfies it.

That is why interfaces may import aggregates. `ErrorService.get` returns `ErrorAggregate` because the implementor is a repo that maps a transfer object into mutable form. Typing the method as `Error` would lie about what the caller can do next, or force the event to re-wrap the noun before it can mutate. Six interface modules already import `*Aggregate`. That is correct. The old skill line “never mappers” was inverted on purpose.

Binah does not import Netzach. The hub asks `get_dependency`. Chochmah does not import Netzach. The factory asks Chesed. If a context grows an `AppService` parameter, the contract has leaked into the client — the `AppSessionContext.load` violation, in other words.

`MiddlewareService` is the same endurance applied to the event chain. It is callable: `__call__(self, event, kwargs, next_fn)`. Async middleware awaits `next_fn()`. The event does not know it is wrapped. The contract endures around the heart without becoming the heart.

## What a promise is, and which way it binds

Evans' **Commitment** layer is the sharpest lens available on this position, and — as everywhere in these chapters — it is a lens rather than an identity. He characterizes it as having "the nature of Policy, in that it states goals that direct future operations," while having "the nature of Operations in that commitments emerge and can change as part of ongoing business activity." That dual nature maps onto a contract tier immediately. See [architecture.md](architecture.md) for why the layer names are readings and never placement claims.

What makes the lens *sharp* here rather than merely apt is the **direction of obligation**: the contract binds its implementors and is shaped by none of them. Protect that distinction, because it is the whole difference between this position and Hod, where a comparable-looking promise to an external format binds nobody at all. See [mappers.md](mappers.md).

**Endurance is relative, not absolute.** The contract outlasts any one implementation; the contract *set* evolves with the domain like anything else. Claim stability against implementors, never against time.

**Hidden in both directions.** The contract conceals the implementation from its caller and the caller from its implementation. `events` import `interfaces`, `repos` import `interfaces`, and `interfaces` imports neither — so the contract sits upstream of both sides and is shaped by neither.

**Why the register here is desire rather than knowledge.** A promise precedes the thing promised, so a contract cannot be *known*; it can only be wanted, specified, and committed to. That makes determining it the highest-leverage design act available in the framework, because everything downstream is fitted to it. Promises divide neatly into functionality that can be performed and data that can be stored, retrieved, and conveyed.

The desire has an owner, and Evans states this position's rule outright. Intention-Revealing Interfaces (247) says to name classes and operations for their effects and purpose, "without reference to the means by which they do what they promise," and to write the test before the behavior in order "to force your thinking into client development mode."

Two consequences. First, **the register of desire is authored from the calling side**, which refines "hidden in both directions" rather than contradicting it: mechanically, `interfaces` imports neither `events` nor `repos` and no implementor shapes the ABC, while semantically the want arrives from above. The position is two-faced by design — it receives desire from the caller and imposes obligation on the implementor. Do not let this slide into "the caller shapes the interface." The caller supplies the *want*, not the signature.

Second, the naming rule supplies the failure mode: **a contract that names its means has already leaked.**

### One asymmetry at three scales

That relation shows up at three independent scales, which is what converts it from an evocative reading into a structural regularity:

- **Signature.** The want is authored from the calling side (247).
- **Position.** This tier receives desire and imposes obligation.
- **Team.** In Customer/Supplier Development Teams, the downstream plays the customer, so requirements are authored downstream while the obligation is carried upstream.

Keep the direction precise in all three. Supply travels down; what travels back up is narrower and of a different kind — feedback on the interface, **and the vocabulary itself.** That second half matters. Ubiquitous Language means the words a contract is written in came from the caller. Without it, "the contract is authored from above" quietly becomes a claim that the upper tier invents the language, which is the opposite of the practice.

### A rejection criterion: perceived, not invented

Intuition perceives something that is already true; imagination creates from the mind. A contract must name a capability that genuinely exists in the domain — not one introduced for symmetry, or because a layer looked bare, or because a second implementor might appear someday.

Speculative interfaces, one-contract-per-class, and abstraction introduced before the second implementor exists are false abstractions in the precise sense. **The signature is the entire artifact**: an ABC has no runtime behavior to observe and nothing to step through, so the whole burden falls on the name, the types, and the parameters. The position is beheld only as declaration, which is why a careless name here costs more than a careless name anywhere else.

### The naming audit, including the case that looks like a violation

Run Evans' rule across the framework's contracts and it passes. `MiddlewareService`, `DIService`, `ErrorService`, `FeatureService`, `AppService`, `CliService`, and `LoggingService` all name a capability rather than a means.

Then there is `SqliteService`, which names a substrate outright and looks like a leak on the face of the rule. **It is correctly named, and the reasoning matters more than the verdict.**

The rule proves too much if applied here. `FileService` names a substrate too, as do `Yaml`, `Json`, and `Csv` one position down. A rule that condemns `SqliteService` condemns the file contract nobody has ever objected to, and most of `utils` along with it. That is a reductio, and the lesson is that the rule was being applied at the wrong level.

Generic Subdomain gets it right for the actual reason: **there is no framework-specific insight about SQLite, so there is no domain intention left for the name to reveal.** The intention *is* "speak SQLite." The industry-standard name is therefore the intention-revealing one. Renaming toward abstraction — `TabularStoreService` and the like — would manufacture a false abstraction in exactly the sense this position already rejects, and would destroy information besides, since a caller reaching for this contract wants SQLite's single-file semantics specifically. The code says as much structurally: `SqliteService` extends `FileService`, so the substrate-named contract inherits the other substrate-named contract.

The neighbor comparison is the clean illustration, and there is no inconsistency between the two. `LoggingService` is intention-named because logging is a genuinely substrate-independent want — a file, stdout, or syslog each satisfy it. `SqliteService` is substrate-named because the substrate is the point. Different kinds of contract, both named correctly.

Keep the test explicit or the pattern becomes an excuse — the same hazard as declaring something an anticorruption layer to license any foreign name. An artifact is generic when it fails all three of declining across positions, carrying domain invariants, and containing project-specific insight. Three noes, generic. Anything else answers to Evans' rule in full. See [architecture.md](architecture.md) for the membership test.

### First below the veil

Evans prescribes exposing a partitioned Cohesive Mechanism through an Intention-Revealing Interface (422–423), which makes the contract the first — and the only — part of a mechanism that is ever revealed. So assembling one begins here.

Against the ten positions that is checkable rather than decorative. This position is seventh, and therefore the first of the four below the veil; the ordering beneath runs contract, representation, capability, persistence; and `di`, which crosses the boundary to hand instances upward, may import exactly one position below it — this one. `repos`, at the far end, is never named above the veil at all. The first revelation is also the only one the resolver gets.

**Two faiths, paired with Chesed.** The resolution tier trusts the declaration; the caller trusts the contract. Between them, that is why a call can succeed with no party verifying anything. See [di.md](di.md).

## A vertical contract

```python
# tiferet/interfaces/error.py

# *** interfaces

# ** interface: error_service
class ErrorService(Service):
    '''
    Vertical interface for managing error domain objects.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if an error exists.
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str) -> ErrorAggregate:
        '''
        Retrieve an error by ID.
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, error: ErrorAggregate) -> None:
        '''
        Persist an error.
        '''
        raise NotImplementedError()
```

What the reader just saw: every method is abstract. The return type is the aggregate, not the noun. `save` accepts the aggregate because mutation already happened in Hod. The repo will turn that into a transfer object. The event never sees the file.

`ConfigurationService` and `FileService` follow the same shape for loaders. `DIService` is the contract Chesed reads when it builds a container. `ServiceError` is the miss that Chesed raises — an interface error, not an asset catalog entry — so `di` can fail without importing `TiferetError`.

## Structured code design

Use `# *** interfaces` / `# ** interface:` / `# * method` with `@abstractmethod`. No `# * method: new`. Implementors live in `repos/` or `utils/`, never in this package. Full grammar: [code_style.md](code_style.md). Pattern notes live in [docs/guides/interfaces.md](../guides/interfaces.md).

## In short

- Interfaces are enduring Service ABCs. That contract is Netzach.
- The contract binds its implementors and is shaped by none of them. That direction of obligation is what separates this position from Hod.
- Endurance is relative: stable against implementations, never against time.
- The want is authored from the calling side; the obligation is carried by the implementor. Same asymmetry at signature, position, and team scale.
- Vocabulary travels *up* from the caller. "Authored from above" never means the upper tier invents the language.
- Perceived, not invented. A contract with no second implementor and no domain capability behind it is a false abstraction.
- The signature is the entire artifact. A contract that names its means has already leaked.
- Except where there is no domain intention left to reveal: `SqliteService` is correctly named, because "speak SQLite" *is* the intention. Contrast `LoggingService`, intention-named because logging is substrate-independent.
- First below the veil, and the only part of a mechanism the resolver ever sees.
- Import aggregates from `mappers` to type outputs. Do not type a domain model when an aggregate exists.
- Used by events, di, utils (when injectable), and repos. Not imported by contexts or blueprints.
- Depend on the contract in events. Never name the concrete repository.
- `MiddlewareService` wraps `execute` without becoming an event.
