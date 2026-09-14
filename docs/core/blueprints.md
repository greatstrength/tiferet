# Blueprints in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

`blueprints` is decision support: application composition. A blueprint seeds the cache, resolves the session, composes the container and the resolver, and builds the handler closures the session hub will run. Those closures stay resident for the session. Composition is not a step that completes and withdraws. Blueprints do not implement domain work. See [architecture.md](architecture.md).

## Life in the system

A blueprint is a module-level function. It orchestrates. It does not add two numbers, rename an error, open a file, or access a database.

Public composition entry points are `App` (`build_app`), `CLI` (`build_cli`), `AdminApp` / `AdminCLI`, and `use_tester`. Choosing an entry point chooses which composition runs. Session-facing entry points reuse the same core chain: seed a cache from catalogs, resolve an `AppSession` (cache hit, or the `GetAppSession` bootstrap event before the container exists), compose the singleton app container and the feature-level resolver, then construct the session context via `from_domain` with the handler closures that context type declares.

`CLI` is thinner at the call site: compose a `CliSessionContext`, then `run(argv)`. Argparse is not hub-owned work. It arrives as an injected `parse_cli_args` slot.

`use_tester` is a composition entry point of a different kind. It does not call `get_app_session` and does not wire the session hub. See [The tester crossing](#the-tester-crossing).

A consumer's acquaintance with session composition is one call:

```python
app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 1, 'b': 2})
```

After `App` returns, `run` is already the hub.

## Why composition stays resident

The tempting description is a flash of wiring that gets out of the way. That description is wrong, and the rest of the package depends on it being wrong.

The handlers a blueprint builds are closures bound to the cache and to `get_dependency`. They remain on the hub for the life of the session. The execution workflow — how a logger is built, how a feature is bound, how an error is shaped — lives here in distilled functional form. The hub sequences those callables. It does not implement them, and it does not reconstruct them.

If composition withdrew, three things would break at once:

- The hub would have to import sibling contexts (`FeatureContext`, `ErrorContext`, `LoggingContext`) to rebuild operators. Import law forbids that edge, and it is how circular imports are born.
- Cache-backed work would have nowhere to live. Lazy feature and error resolution, and logger construction that runs `dictConfig` once per logger id per process, are memories of a closure. Memoization belongs to composition, not to the hub.
- Reverse dependency would collapse. The hub would need to know who produced its collaborators. Resident slots are how it runs without knowing how it was assembled.

Composition stays resident because the live session is not a second copy of the graph. It is the graph, held as callables the hub can invoke.

## The hub and its slots

The handler *pattern* is fixed: the hub calls injected slots rather than importing sibling contexts to build them. The arity is not. It is the constructor of the session context type — `AppSessionContext`, `CliSessionContext`, or a consumer subclass. An unwired required slot fails through `raise_unwired_handler_error`. There is no inline fallback. A silently degraded session is worse than a stopped one.

Slot count follows the nature of the application. A feature-dispatch hub needs a logger, a request, feature execution, error shaping, and a response. A command-line hub needs those plus argument parsing. A dialect adds a slot when its surface has a phase the existing ones cannot name. Context and blueprint extend in lockstep: the class declares capacity; the blueprint fills it. Declaring a slot and wiring it are different acts.

`AppSessionContext.run` is the public motion of a feature-dispatch hub. Each template method is a required slot:

- `build_logger` — obtain the session logger before work. Construction is a slot so the hub does not hold a long-lived `LoggingContext`; the closure may cache by logger id.
- `build_request` — construct the request the feature loop writes into.
- `execute_feature` — bind a `Feature` and drive `FeatureContext.execute_feature(request)`. The result accumulates on the request; extraction is the response step.
- `handle_error` — format a domain failure into a structured API error. An already-formatted `TiferetAPIError` is re-raised, not wrapped twice.
- `build_response` — extract the final response from the completed request.

`CliSessionContext` adds `parse_cli_args`. Its `run(argv)` derives `(feature_id, headers, data)` from that slot, then delegates to the inherited hub. Request and response slots are CLI-shaped (`CliRequestContext`, a response that can print) because the application is a CLI, not because the framework grew a second hub kind.

`get_dependency` sits beside the slots. It is the other reverse-dependency operating case: the hub resolves instances without importing `di`.

What generalizes is not a number. It is named slots, filled by a blueprint, called by a hub that never learns who filled them.

## Decision support

Decision support does not implement domain work. It holds bootstrap data (`assets`), composes the process (`blueprints`), and sequences the live session (`contexts`). Legal edges follow from that job, not from a list of forbidden names.

`blueprints` may import:

- `assets` — catalogs composition must begin from, and that do not depend on composition.
- `contexts` — the graph being composed. Domain types reach a blueprint only through context re-exports (`from ..contexts.feature import Feature`, never `from ..domain import Feature`).
- `di` — container and resolver *classes*. Service instances arrive through `get_dependency`, never as a direct interface import.
- `events` — pre-DI bootstrap only (`GetAppSession` before the container exists).

It may not import `domain`, `interfaces`, `mappers`, `utils`, or `repos`. Those are policy nouns, potentials, and operations. If composition imported a domain noun directly, it would couple to the noun's package instead of to the live graph. If it imported a `Service`, it would hold a contract instead of composing resolution. Repositories are never imported.

Intra-layer constraint: `blueprints` may not import `domain`; `contexts` may not import `blueprints`. Construction flows down.

## Composition touches the graph

One structural fact sets this package apart from the other nine: **`blueprints` is the only package that imports both `di` and `contexts`.** Every other package sits on one side of that divide or on neither.

Composition is the single point that touches the whole graph at once — rules of resolution on one side, the live session on the other — and holds both long enough to join them as resident closures. That join is why construction is one-way. The composer knows the hub; the hub never imports the composer. Runtime collaboration uses reverse dependency: handler slots and `get_dependency`.

A declared dependency without an import edge is an intended consequence of the law, not an exception to it.

## The tester crossing

The tester is both `blueprints` and `contexts`. It is not an import-law footnote.

The concept is the framework testing itself with components made from itself. A unit test occupies the same patterns it verifies: a domain noun (`TesterObject`), a context bound with `from_domain` (`TesterContext` and its type variants), and a request-shaped run (`TestSessionContext` is a `RequestContext`).

`use_tester` is the composition entry point. At decoration it constructs one `TesterObject`, binds the matching tester context, and wraps callables that declare `test_ctx` or `session` by name. Each call gets a fresh `TestSessionContext`; the master tester context is reused.

It is not a mini-App. It does not call `get_app_session`. It does not compose a container, a feature-level resolver, or the session hub's slots. A test is not feature dispatch. The crossing is that decision-support composition still builds a live graph from `BaseContext` / `from_domain`, so the suite does not stand up a parallel harness beside the patterns.

Operational recipes live in [testing.md](testing.md) and [docs/guides/blueprints.md](../guides/blueprints.md).

## Extensibility

A dialect extends composition. It does not mutate a live session, and it does not add an eleventh package.

The same moves apply whether the extra catalogs are configuration-management, CLI commands, or a consumer bounded context:

- Seed additional catalogs onto the cache. Decorator stacks on a cache builder are declared data, not branches in code.
- Close handlers over a different resolver. Extra containers under flags give feature steps a resolution namespace while the hub stays untouched.
- Replace a handler function.
- Add a slot. The context type declares it; the blueprint fills it. Arity follows the application.
- Reuse published composition helpers rather than re-executing the whole chain.

Sessions that look built-in are this shape, not a privileged path. Differentiation happens between entry points, not inside one function. Entry scripts are occasions; composition stays in `blueprints`.

Keep composition thin enough that a new surface — web, another CLI, another test graph — is another function that reuses the chain.

## Structured code design

Use `# *** functions` / `# ** function:` for pure helpers and `# *** blueprints` / `# ** blueprint:` for orchestration. Functions first when both appear. Validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in single-call session entry points. Raise through `TiferetError.raise_error` with `a.<submodule>` constants. Full grammar: [code_style.md](code_style.md). Composition-chain walkthroughs live in [docs/guides/blueprints.md](../guides/blueprints.md).

## In short

- Blueprints compose a session and stay resident as its handlers. Decision support; not domain work.
- The execution workflow lives here in functional form. The hub sequences those closures and implements none of them.
- Slot arity follows the session context type. Wire every slot that type declares; an unwired required slot fails loudly.
- Legal imports: `assets`, `contexts`, `di`, `events` (bootstrap only). Domain types through contexts; service instances through `di`. Never `domain`, `interfaces`, `mappers`, `utils`, `repos`.
- This is the only package that imports both `di` and `contexts`. Composition touches the whole graph at once; construction flows one way.
- `use_tester` is composition of a tester graph, not a mini-App. The framework tests itself with components made from itself.
- Extensibility is extra catalogs, extra resolution namespaces, replaced or added slots, and reused helpers. Built-in-looking sessions are the same shape.
- After composition returns, the feature loop belongs to the context.
