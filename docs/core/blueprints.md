# Blueprints in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Wisdom, in this design, is the spark — and the sustaining of it. `blueprints` build the cache, resolve the session, compose the container and the resolver, and build the handler closures the hub will run for the rest of the session. They do not implement domain logic. That position is **Chochmah**. See [architecture.md](architecture.md).

The tempting description is a flash of composition that gets out of the way, and it is wrong. A blueprint does not complete and withdraw. The handlers it builds are closures bound to the cache and the resolver, and they stay resident for the life of the session — which means the execution workflow state lives *here*, in distilled functional form, and the hub merely sequences it. Chochmah drawn down continuously, or the lower world does not persist. That is not a flourish; it is the literal shape of the code, and the rest of this chapter depends on getting it right.

Legal `# ** app` imports: `assets`; `contexts`; `di` for container and resolver classes; `events` for pre-DI bootstrap only (`DomainEvent.handle(...)` or a direct event-class import). Illegal as a direct import: `domain`, `interfaces`, `mappers`, `utils`, `repos`. Domain types reach a blueprint only through context re-exports. Service instances reach a blueprint only through `di`. That is how the factory is allowed to see a noun and hold a contract without becoming Gevurah or Netzach.

## Life in the system

A blueprint is a module-level function, not a class. It orchestrates. It does not add two numbers, rename an error, open a file, or access a database. The public surface is four entry points: `build_app` / `App`, `build_cli` / `CLI`, `build_admin_app` / `AdminApp`, `build_admin_cli` / `AdminCLI`. All of them reuse the same core chain in `tiferet/blueprints/core.py`.

The chain is the factory’s entire job:

1. `build_cache()` — a `CacheContext` pre-seeded with framework catalogs (errors, default services, constants).
2. `get_app_session(interface_id, cache, ...)` — resolve the `AppSession` via the `GetAppSession` event. This is the legal Chochmah → Tiferet edge: bootstrap, before the container exists.
3. `build_app_session_context(session, cache)` — merge cache defaults with the session’s own services and constants, build the singleton app container, compose the feature-level resolver, import the context class, and construct it via `from_domain` with the five handlers.

`build_cli` is thinner still: call `core.build_app(...)`, then `cli_context.run(argv)`. Parsing is Binah’s. The blueprint does not own argparse.

**Da'ath** is the crossing that keeps this legal. Context modules re-export the types factory signatures need (`AppSession`, `Feature`, `Error`, `LoggingSettings`, CLI models). Write `from ..contexts.feature import Feature`, never `from ..domain import Feature`. Netzach instances arrive the same way through Chesed: `get_dependency`, never `from ..interfaces import AppService`. The remaining code violation — `AppSessionContext.load` importing `AppService` — is a factory method that still lives on the hub. It belongs here. That move is a code fork, not this chapter.

## The handlers, and what stays resident

The hub must run without knowing how it was assembled. The blueprint declares how:

```python
handlers = dict(
    build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
    execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
    raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
    response_handler=response_handler,
    create_request_handler=create_session_request,
)
return AppSessionContext.from_domain(
    app_session,
    get_dependency=resolver.get_dependency,
    cache=cache,
    **handlers,
    **collaborators,
)
```

What the reader just saw: five slots, plus `get_dependency`. The hub will call these. It will not import `FeatureContext` to build one. `build_logger_handler` is a cache-backed closure, not a long-lived `LoggingContext` stored on the hub. `execute_feature_handler` constructs a domain-bound `FeatureContext` and calls `execute_feature(request)`. That is Chochmah injecting Binah’s siblings so Binah does not construct them.

Five is **Tiferet's own arity**, not a coordinate. A dialect extends context and blueprint in lockstep, and the calculator does exactly that: `CalculatorAppContext` declares a sixth slot, `record_run_handler`, and `build_calculator_app_context` builds that closure alongside the other five. Any sentence of the form "five handlers is the whole contract" is false against the examples directory. What is fixed is the pattern — named slots, filled by a blueprint, called by a hub that never learns who filled them.

Notice what the closures carry. The lazy-caching ones (`get_error`, `get_feature`, `build_logger_handler`) hold cache state across calls, so `dictConfig` runs once per logger id per process because a blueprint closure remembers. Memoization lives in the factory, not in the hub. And an unwired slot is a composition bug that fails loudly through `raise_unwired_handler_error` — a spark that was never sustained cannot run a feature.

Side-effect-free helpers (`resolve_collaborators`, `merge_logging_settings`) live under `# *** functions`. Orchestration entry points live under `# *** blueprints`. Keep the factory thin enough that a new interface — web, test, gRPC — is another function that reuses the chain, not a new architecture.

## Four ways to swap a composition

Because the hub never learns which blueprint filled its slots, execution is swapped by writing or extending a blueprint rather than by mutating a live session. There are four levels of that, in increasing strength, and the fourth is the one to read carefully.

**1. Change what a handler closes over.** `blueprints/admin.py` reuses all five core handler functions verbatim and substitutes only the resolver behind them. `build_admin_service_resolver` registers the admin container under both the `admin` flag and the empty-flag default, so admin feature steps resolve elsewhere while the hub is untouched. Its `build_cache` is the core builder under a different decorator stack, so catalogs layer as declared data rather than branching in code. The seams are declared defaults, not hooks: `service_container=`, `parse_parameter=`, `**context_kwargs`.

**2. Replace a handler function outright.** Fully available. Nothing in the framework needs it, which is worth saying plainly rather than implying the level is hypothetical.

**3. Add a slot.** The calculator's `record_run_handler`, above. This is the level a dialect reaches for most naturally, because a new session concern usually wants a new phase rather than a different implementation of an existing one.

**4. Compose the builder itself from published parts.** The strongest level — and currently unavailable. `core.build_app_session_context` and `cli.build_cli_session_context` each fuse three jobs into one body: compose the resolver, build the handler bundle, construct the context. Both intermediates are locals, so a dialect that wants either must re-execute the whole thing. The consequence is visible in the examples directory: `build_calculator_cli_session_context` is a near-verbatim fifty-line copy of `cli.build_cli_session_context` whose entire difference is one inserted `register_calc_container(resolver, cache)` line, and it will drift from the original on every future change to CLI wiring. **Until that seam exists, do not treat the CLI path as extensible.**

Two precisions about that gap, because the obvious readings of it are both wrong.

It is **not an asymmetry between the app path and the CLI path.** Neither builder exposes its resolver; `**context_kwargs` forwards to the context constructor, not to the resolver, and neither path has a container-registration hook. The real difference is justification. `build_calculator_app_context` had to be a local copy regardless, because it selects a different context class and wires a sixth handler, so the container line rides along on a fork that earns its existence. The CLI copy has an identical context class and identical handlers, so it exists *purely* because the seam is missing — which makes it the clean specimen rather than the asymmetric one.

And **entry scripts are not the fix.** Moving the wiring into `calc_client`, `calc_fluent`, and `calc_cli` would duplicate it three ways. Scripts are occasions; composition stays in Chochmah.

There is a discipline missing behind all of this, and it is the same finding rather than a second one. The framework/dialect relation is Customer/Supplier with the framework upstream, and Evans gives that pattern a mechanism, not just a shape: the downstream's requirements are budgeted rather than hoped for, and the interface it depends on is written as automated acceptance tests living in the **upstream's** suite and running in the upstream's CI. That is what frees the upstream to change things without breaking the downstream. Tiferet has the relation with none of the mechanism — no dialect-owned acceptance suite runs in this repository's CI. The fifty-line fork is that absence already realized: the calculator needed a hook, upstream never budgeted it, and a copy was the result.

## The mechanism extends itself

The strongest available evidence that the ten positions are an intermediate representation rather than a package layout is that the extension mechanism extends itself, in the same shape, one level out.

`examples/basic_calculator/app/blueprints/calc.py` stacks its own `add_default_calc_features` and `add_default_calc_services` on the framework's `add_default_errors`, then delegates to `core.build_cache`. `contexts/calc.py` wraps the framework's `add_default_features`. A dialect builds its decorators the way the framework builds its decorators, and it needs no new vocabulary to do it. Nothing was added to the framework to make that possible.

**Bounded Context arrives here as a resolution namespace.** `add_default_calc_features` auto-tags every feature `flags=['calc']`, and `register_calc_container` registers a dedicated container under that flag, standing in Customer/Supplier relation to the app container. That is Evans' Bounded Context implemented as DI flags — the cleanest dialect illustration in the repository, and a good answer to anyone who suspects the pattern only exists in the prose.

**Differentiation happens between blueprints, not within one.** `build_calculator_app_context` and `build_calculator_fluent_context` are near-identical and differ only in the context class they realize. Which is why the entry point choice is load-bearing without being an eleventh position: choosing `App` over `AdminApp`, or `create_calculator_app` over `create_calculator_fluent`, chooses which sustained composition runs.

## Polarity originates here

One structural fact sets this position apart from the other nine, and it is checkable against the import table: **`blueprints` is the only package that imports both `di` and `contexts`.** Every other package sits on one side of that divide or on neither.

So the composition position is the single point where the whole graph is touched at once — resolution on one side, runtime on the other, and a factory holding both long enough to join them. It is also why the one-way construction edge matters so much: `blueprints` may import `contexts`, and `contexts` may never import `blueprints`. Chochmah cannot elaborate itself; it requires Binah to become structure.

Admin variants seed extra catalogs and keep two containers on the resolver (`app` and `admin`, with admin as the empty-flag default). The shape does not change. Expansion is still Chesed.

A consumer’s entire acquaintance with the factory is one call:

```python
app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 1, 'b': 2})
```

`run` is already Binah.

## Structured code design

Use `# *** functions` / `# ** function:` for pure helpers and `# *** blueprints` / `# ** blueprint:` for orchestration. Functions first when both appear. Validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in single-call entry points. Raise through `TiferetError.raise_error` with `a.<submodule>` constants. Full grammar: [code_style.md](code_style.md). Composition-chain walkthroughs live in [docs/guides/blueprints.md](../guides/blueprints.md).

## In short

- Blueprints compose a session and stay resident as its handlers. That sustained spark is Chochmah.
- The execution workflow state lives here in functional form. The hub sequences those closures and implements none of them.
- Legal imports: `assets`, `contexts`, `di`, `events` (bootstrap only). Never `domain`, `interfaces`, `mappers`, `utils`, `repos`.
- Domain types arrive through context re-exports (Da'ath). Service instances arrive through `di`.
- Five handlers is Tiferet's own arity, not the contract. The calculator declares a sixth. Wire every slot a context declares; an unwired one fails loudly.
- Four swap levels: change what a handler closes over, replace a handler, add a slot, or compose the builder from published parts. The fourth is not yet available, so the CLI path is not extensible today.
- The extension mechanism extends itself: a dialect stacks its own decorators on the framework's and needs no new vocabulary. Bounded Context lands as DI flags.
- This is the only package importing both `di` and `contexts`, which is why polarity originates here — and why construction flows one way only.
- After `build_app` returns, the feature loop belongs to the context.
