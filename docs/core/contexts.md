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

## The five required handlers

| Template method | Handler slot | Role |
| --- | --- | --- |
| `build_logger` | `build_logger_handler` | Construct (and typically cache) the session logger |
| `build_request` | `create_request_handler` | Construct a `RequestContext` |
| `execute_feature` | `execute_feature_handler` | Drive the bound `FeatureContext` against the request |
| `handle_error` | `raise_error_handler` | Format a domain error into a structured API error |
| `build_response` | `response_handler` | Extract the final response from the completed request |

CLI adds `parse_cli_args`. `RESERVED_CONTEXT_PARAMETERS` in the blueprint keeps generic collaborator resolution from trying to DI-resolve these names.

## Structured code design

Use `# *** contexts`, `# ** context: <name>`, `# * attribute`, `# * init`, `# * method`. High-level contexts extend `AppSessionContext` and override only what the interface specializes. Low-level contexts extend `BaseContext` directly. Never instantiate with `ContextClass(...)` in application code; the blueprint constructs via `from_domain`. Full grammar: [code_style.md](code_style.md). Per-interface walkthroughs live in [docs/guides/contexts.md](../guides/contexts.md).

## In short

- Contexts are the runtime graph. The hub runs without knowing how it was wired. That client is Binah.
- Legal imports: `assets`, `domain`, sibling contexts, `events`. Never `blueprints`, `interfaces`, `di`, `mappers`, `utils`, `repos`.
- Prefer handler injection over constructing siblings. All five slots are required.
- Call events as a client (`DomainEvent.handle`). Do not bootstrap the session here.
- `CliSessionContext` owns CLI parsing. The blueprint does not.
