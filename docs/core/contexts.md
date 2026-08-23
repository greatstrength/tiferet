# Contexts in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Understanding is the client-runtime graph: the session once it exists, able to run without knowing how it was assembled. A context binds a domain object (`from_domain`) and exposes operational behavior. That position is **Binah**. It may be a flat presentation container or a fluent API. What it must not do is invent the work. The work is an event. See [architecture.md](architecture.md).

Legal `# ** app` imports: `assets` (one way); `domain`; sibling contexts; `events` as the client surface. Illegal: `blueprints` (construction flows down, never back); `interfaces`; `di`; `mappers`; `utils`; `repos`. Blueprints are the factory. Contexts are the client. Prefer handler injection over constructing sibling contexts.

## Life in the system

All contexts extend `BaseContext` (`tiferet/contexts/core.py`). `ContextMeta` registers each class by `domain_type`. `BaseContext.for_domain(DomainType)` resolves the class. `BaseContext.from_domain(domain_obj, **kwargs)` constructs it and binds the noun as `ctx.domain`. Caching is not in the base; contexts that need a `CacheContext` declare one.

Two kinds share the graph.

**High-level contexts** face a human. `AppSessionContext` is the minimal hub. `CliSessionContext` extends it and owns argparse behind an injected `parse_cli_args`. A future `FlaskApiContext` would extend the same hub. The CLI blueprint is a thin entrypoint; `CliSessionContext.run(argv)` is the client.

**Low-level contexts** support one concern: `FeatureContext`, `ErrorContext`, `LoggingContext`, `RequestContext`, `CacheContext`. Framework extensions add their own. The hub does not import them to build them. The blueprint injects handlers that do.

The hub’s public motion is `run(feature_id, headers, data)`:

```python
def run(self, feature_id, headers=None, data=None, **kwargs):
    logger = self.build_logger()
    request = self.build_request(feature_id, headers or {}, data or {})
    try:
        self.execute_feature(feature_id, request, logger=logger, **kwargs)
    except TiferetError as e:
        return self.handle_error(e)
    return self.build_response(request)
```

What the reader just saw: five template methods, each backed by a required handler slot. An unwired slot raises `APP_ERROR` on first use. There is no inline fallback. `handle_error` re-raises an incoming `TiferetAPIError` so an already-formatted response is never wrapped twice. Logger construction is a first-class slot (`build_logger_handler`), not a separately loaded `LoggingContext` hanging off the hub.

That is why Binah must not import `interfaces` or `di`. The hub asks `get_dependency`. It does not know `AppService`. The remaining violation — `AppSessionContext.load` typing `app_service: AppService` and calling `GetAppSession` — is factory work living on the client. It belongs on `blueprints/core.py`. Until that code fork lands, treat the method as in the wrong package.

`FeatureContext` is bound to a `Feature` via `from_domain`. Its `execute_feature(request)` takes no feature argument; the noun is `self.domain`. For each step it resolves the event through `get_dependency` and calls `DomainEvent.handle`. Async dispatch is owned here via `Feature.is_async`. There is no separate `AsyncFeatureContext`.

Sibling imports are legal and usually unwise. Constructing `FeatureContext` inside `AppSessionContext` is how circular imports are born. Let Chochmah inject the slot.

## Reciprocity at runtime, direction at construction

The relation between this position and the factory above it is the one the whole arrangement rests on, and it runs in two directions at once without producing a cycle.

At construction, direction is absolute. The composer builds the holder and knows it; the holder never learns who composed it. At runtime, the two are reciprocal: neither functions alone. A capability nobody holds does nothing, and a holder with nothing in its slots can do nothing either. **This is why the blueprint handler slot exists as a permitted backward shape** — it is the mechanism that buys reciprocity without a circular import, which makes it the load-bearing exemption rather than a listed curiosity.

The two failure modes are worth distinguishing, because they do not look alike in practice:

- **A capability nothing holds** is inert and silent. It is dead code. Nothing raises; a handler function simply never runs, and you find it by reading rather than by testing.
- **A holder whose slots were never wired** fails loudly at first invocation, through `raise_unwired_handler_error`. There is no inline fallback and no default behavior, deliberately, because a silently degraded session is worse than a stopped one.

## The position preserves; it does not produce

Contexts contribute no semantics of their own. They retain and order what the blueprint projected, and the vocabulary is worth noticing: the verbs available to this position are connect, order, transit, harmonize, mobilize. Every one is arrangement. None is production.

That is why the hub can own timing, sequence, and lifecycle while owning none of the operations — and it is the reason a context is the right place to ask "in what order, and when," and the wrong place to ask "what does this mean."

One distinction follows and explains a class of confusing bugs. **The capacity to hold is a type-level fact declared by the class. The joining is a separate event in time.** A context can be fully and correctly constructed and still be empty, because declaring a slot and filling it are different acts performed by different positions. Reading the class tells you what it is capable of holding; only reading the blueprint tells you what it actually holds.

## The handler slots

| Template method | Handler slot | Role |
| --- | --- | --- |
| `build_logger` | `build_logger_handler` | Construct (and typically cache) the session logger |
| `build_request` | `create_request_handler` | Construct a `RequestContext` |
| `execute_feature` | `execute_feature_handler` | Drive the bound `FeatureContext` against the request |
| `handle_error` | `raise_error_handler` | Format a domain error into a structured API error |
| `build_response` | `response_handler` | Extract the final response from the completed request |

CLI adds `parse_cli_args`. `RESERVED_CONTEXT_PARAMETERS` in the blueprint keeps generic collaborator resolution from trying to DI-resolve these names.

**The slot set is per context class, not framework-fixed.** Five is Tiferet's own arity as a dialect of itself; it is not a coordinate, and a chapter that called it the whole contract would be wrong against the examples directory. `CalculatorAppContext` (`examples/basic_calculator/app/contexts/calc.py`) declares a sixth slot, `record_run_handler`, stores it privately, guards it with the framework's own `raise_unwired_handler_error`, and overrides `execute_feature` to fire it after a successful run — while `build_calculator_app_context` builds that closure alongside the other five. Context and blueprint extend in lockstep, always. What generalizes is the pattern, and the arity is determined by the domain a context serves.

That same dialect file is worth reading for a second reason: it obeys the import law in its own comments. It keeps `resolver: Any` deliberately untyped, noting that contexts never import `di` directly, and it intentionally omits `domain_type` so the `ContextMeta` registry keeps mapping `AppSession` to `AppSessionContext`. A consumer explaining the law back to itself is the best available evidence that the law is teachable rather than merely enforced.

## Structured code design

Use `# *** contexts`, `# ** context: <name>`, `# * attribute`, `# * init`, `# * method`. High-level contexts extend `AppSessionContext` and override only what the interface specializes. Low-level contexts extend `BaseContext` directly. Never instantiate with `ContextClass(...)` in application code; the blueprint constructs via `from_domain`. Full grammar: [code_style.md](code_style.md). Per-interface walkthroughs live in [docs/guides/contexts.md](../guides/contexts.md).

## In short

- Contexts are the runtime graph. The hub runs without knowing how it was wired. That client is Binah.
- Direction at construction, reciprocity at runtime. The composer knows the holder; the holder never learns the composer; neither works alone.
- The handler slot is the backward shape that buys that reciprocity without a cycle. It is the mechanism, not an exemption.
- Two failure modes, and they differ: a capability nothing holds is silent dead code; an unwired slot fails loudly on first use.
- The position preserves and orders. It produces no semantics of its own, which is why it owns timing and not meaning.
- Capacity to hold is declared by the class; the joining happens later. A context can be fully constructed and still empty.
- Legal imports: `assets`, `domain`, sibling contexts, `events`. Never `blueprints`, `interfaces`, `di`, `mappers`, `utils`, `repos`.
- Prefer handler injection over constructing siblings. Wire every slot the class declares — five is Tiferet's arity, not the contract; the calculator declares six.
- Call events as a client (`DomainEvent.handle`). Do not bootstrap the session here.
- `CliSessionContext` owns CLI parsing. The blueprint does not.
