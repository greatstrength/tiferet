# Blueprints in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Wisdom, in this design, is the flash of composition: a factory that wires a session and then gets out of the way. `blueprints` do not implement domain logic. That position is **Chochmah**. They build the cache, resolve the session, compose the container and the resolver, hand five handlers to the hub, and stop. After that, the feature loop is no longer theirs. See [architecture.md](architecture.md).

Legal `# ** app` imports: `assets`; `contexts`; `di` for container and resolver classes; `events` for pre-DI bootstrap only (`DomainEvent.handle(...)` or a direct event-class import). Illegal as a direct import: `domain`, `interfaces`, `mappers`, `utils`, `repos`. Domain types reach a blueprint only through context re-exports. Service instances reach a blueprint only through `di`. That is how the factory is allowed to see a noun and hold a contract without becoming Gevurah or Netzach.

## Life in the system

A blueprint is a module-level function, not a class. It orchestrates. It does not add two numbers, rename an error, open a file, or access a database. The public surface is four entry points: `build_app` / `App`, `build_cli` / `CLI`, `build_admin_app` / `AdminApp`, `build_admin_cli` / `AdminCLI`. All of them reuse the same core chain in `tiferet/blueprints/core.py`.

The chain is the factory’s entire job:

1. `build_cache()` — a `CacheContext` pre-seeded with framework catalogs (errors, default services, constants).
2. `get_app_session(interface_id, cache, ...)` — resolve the `AppSession` via the `GetAppSession` event. This is the legal Chochmah → Tiferet edge: bootstrap, before the container exists.
3. `build_app_session_context(session, cache)` — merge cache defaults with the session’s own services and constants, build the singleton app container, compose the feature-level resolver, import the context class, and construct it via `from_domain` with the five handlers.

`build_cli` is thinner still: call `core.build_app(...)`, then `cli_context.run(argv)`. Parsing is Binah’s. The blueprint does not own argparse.

**Da'ath** is the crossing that keeps this legal. Context modules re-export the types factory signatures need (`AppSession`, `Feature`, `Error`, `LoggingSettings`, CLI models). Write `from ..contexts.feature import Feature`, never `from ..domain import Feature`. Netzach instances arrive the same way through Chesed: `get_dependency`, never `from ..interfaces import AppService`. The remaining code violation — `AppSessionContext.load` importing `AppService` — is a factory method that still lives on the hub. It belongs here. That move is a code fork, not this chapter.

## The five handlers

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

Side-effect-free helpers (`resolve_collaborators`, `merge_logging_settings`) live under `# *** functions`. Orchestration entry points live under `# *** blueprints`. Keep the factory thin enough that a new interface — web, test, gRPC — is another function that reuses the chain, not a new architecture.

Admin variants seed extra catalogs and keep two containers on the resolver (`app` and `admin`, with admin as the empty-flag default). The shape does not change. Expansion is still Chesed. The factory still leaves.

A consumer’s entire acquaintance with the factory is one call:

```python
app = App('basic_calc', app_config='config.yml')
result = app.run('calc.add', data={'a': 1, 'b': 2})
```

`run` is already Binah.

## Structured code design

Use `# *** functions` / `# ** function:` for pure helpers and `# *** blueprints` / `# ** blueprint:` for orchestration. Functions first when both appear. Validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in single-call entry points. Raise through `TiferetError.raise_error` with `a.<submodule>` constants. Full grammar: [code_style.md](code_style.md). Composition-chain walkthroughs live in [docs/guides/blueprints.md](../guides/blueprints.md).

## In short

- Blueprints compose a session and get out of the way. That factory is Chochmah.
- Legal imports: `assets`, `contexts`, `di`, `events` (bootstrap only). Never `domain`, `interfaces`, `mappers`, `utils`, `repos`.
- Domain types arrive through context re-exports (Da'ath). Service instances arrive through `di`.
- Wire all five handlers. Do not leave a hub slot unset. Do not implement domain logic here.
- After `build_app` returns, the feature loop belongs to the context.
