# Contexts – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/contexts/`  
**Version:** 2.0.0

## Overview

Contexts form the runtime "body" of a Tiferet application. While blueprints (`tiferet/blueprints/`) own application lifecycle and wiring, contexts own the per-session runtime shape — how requests are built, features are executed, errors are handled, and responses are returned. **Vision:** see the `BaseContext` class docstring in `tiferet/contexts/core.py` and the `AppSessionContext` class docstring in `tiferet/contexts/app.py` for the value statements this guide distills.

Tiferet distinguishes two categories of contexts:

- **High-level contexts** — extend `AppSessionContext`, the minimal application session hub. They are the runtime entry point for an interface (e.g. `CliSessionContext`).
- **Low-level contexts** — single-purpose orchestrators the hub builds on demand (`FeatureContext`, `ErrorContext`, `LoggingContext`, `RequestContext`, `CacheContext`).

## Ubiquitous Language

- **Hub** — `AppSessionContext`, the context bound to a loaded `AppSession` that owns the `run` pipeline and holds the shared `CacheContext`.
- **Template-method handler** — one of the hub's five injected callables (`build_logger_handler`, `create_request_handler`, `execute_feature_handler`, `raise_error_handler`, `response_handler`) supplied by the blueprint layer at construction time. Each backing template method (`build_logger`, `build_request`, `execute_feature`, `handle_error`, `build_response`) raises `APP_ERROR` when its handler is unwired rather than falling back to a hub-local implementation.
- **Domain-bound context** — a context constructed via `BaseContext.from_domain(domain_obj, **kwargs)`, which binds `domain_obj` as `self.domain` so the context reads its own subject rather than receiving one per call (e.g. a `FeatureContext` bound to the `Feature` it executes).
- **Registry resolution** — looking up a context class for a domain type via `BaseContext.for_domain(DomainType)`, backed by the `ContextMeta` metaclass registry.

## The BaseContext Registry

<a id="basecontext"></a><a id="contextmeta"></a>
Every context extends `BaseContext` (`tiferet/contexts/core.py`). Its `ContextMeta` metaclass registers each subclass that declares a non-`None` `domain_type` in its own namespace — so a subclass that merely inherits `domain_type` (e.g. `CliSessionContext` inheriting `AppSession` from `AppSessionContext`) does not overwrite the parent's registration.

- `BaseContext.for_domain(DomainType)` — resolves the registered context class, raising `CONTEXT_NOT_FOUND` when none is registered.
- `BaseContext.from_domain(domain_obj, **kwargs)` — resolves the target class (the registry, when called on `BaseContext` itself; `cls` directly, when called on a concrete subclass), constructs it, and binds `domain_obj` as `context.domain`.

Caching is intentionally **not** part of `BaseContext` — contexts that need one (`AppSessionContext`, `FeatureContext`) declare and own a `CacheContext` themselves.

## The AppSessionContext Hub

<a id="appsessioncontext"></a>
`AppSessionContext` binds a loaded `AppSession` and drives the standard `run(feature_id, headers, data, **kwargs)` pipeline:

```python
def run(self, feature_id, headers=None, data=None, **kwargs):
    logger = self.build_logger()
    request = self.build_request(feature_id, headers or {}, data or {})
    try:
        self.execute_feature(feature_id, request, logger=logger, **kwargs)
    except TiferetError as e:
        return self.handle_error(e, **kwargs)
    return self.build_response(request)
```

Each of the five steps — `build_logger`, `build_request`, `execute_feature`, `handle_error`, `build_response` — is a template method that delegates to an injected handler callable rather than implementing the work itself:

| Template method | Injected handler | Blueprint factory |
| --- | --- | --- |
| `build_logger()` | `build_logger_handler` | `build_logger_handler(cache, get_dependency)` |
| `build_request(feature_id, headers, data)` | `create_request_handler` | `create_session_request` |
| `execute_feature(feature_id, request, **kwargs)` | `execute_feature_handler` | `execute_feature_handler` |
| `handle_error(error, **kwargs)` | `raise_error_handler` | `raise_error_handler` |
| `build_response(request)` | `response_handler` | `response_handler` |

All five are required. An unwired handler is treated as a composition bug, not a degraded-mode condition: the template method calls the module-level `raise_unwired_handler_error` helper, which raises a `TiferetAPIError` naming the missing slot. Because that error is already the formatted, consumer-facing representation, `handle_error` re-raises any `TiferetAPIError` verbatim — before consulting `raise_error_handler` — so an unwired `execute_feature_handler` surfaces as itself rather than being masked by a missing `raise_error_handler`. `build_logger` additionally formats a `TiferetError` its own handler raises into a `TiferetAPIError` via `handle_error`, so the pre-`try` region of `run` never raises a bare `TiferetError`.

### Extending AppSessionContext

Subclass when an interface needs to translate a transport-specific payload into a request, or format a transport-specific response. Forward the hub's constructor kwargs via `**kwargs`, and call `super()` for shared behavior:

```python
class FlaskApiContext(AppSessionContext):
    def __init__(self, flask_handler, **kwargs):
        super().__init__(**kwargs)
        self.flask_handler = flask_handler

    def build_response(self, request):
        model = super().build_response(request)
        return jsonify(model)
```

### CLI: CliSessionContext and CliRequestContext

<a id="clisessioncontext"></a><a id="clirequestcontext"></a>
`CliSessionContext` (`tiferet/contexts/cli.py`) extends `AppSessionContext` with an injected `parse_cli_args` closure (built by the `build_cli` blueprint's `parse_cli_args_handler`) that owns argparse command discovery, parser construction, and request derivation. `run(argv=None)` parses `argv` via that closure into `(feature_id, headers, data)`, delegates to the inherited hub `run`, and translates failures into process exit codes: an argparse failure exits `2`; an unhandled `TiferetAPIError` exits `1`. It intentionally omits `domain_type`, so the `ContextMeta` registry keeps mapping `AppSession` to `AppSessionContext`.

`CliRequestContext` extends `RequestContext` with a CLI-specific `handle_response` that converts the raw feature result into a typed CLI output model via the module-level `build_cli_record` helper: a list becomes a `CliRecordList`, a `dict`/`DomainObject` becomes a `CliOutputRecord`, anything else passes through unchanged. It also omits `domain_type`. `CliSessionContext.build_response` extends the hub's response step (rather than reimplementing it) by printing the formatted or stringified model only when the request is a `CliRequestContext`.

A consumer interface reaches this path through the `CLI`/`build_cli` entry point, not through a `module_path`/`class_name` declaration — every interface resolved through `build_cli` gets a `CliSessionContext`.

## FeatureContext

<a id="featurecontext"></a>
`FeatureContext` (`tiferet/contexts/feature.py`) is a domain-bound context: constructed via `BaseContext.from_domain(feature, ...)`, it reads the bound `Feature` as `self.domain` and executes it through `execute_feature(request, *flags, **kwargs)`.

There is **no separate async context class** — a single `FeatureContext` handles all three dispatch cases based on `is_async` flags:

1. `feature.is_async=True` — the whole step loop runs via the private `_execute_async` coroutine, driven to completion by the module-level `run_coroutine(coro)` helper (`asyncio.run` when no event loop is running, otherwise a dedicated worker thread).
2. `feature.is_async=False`, `step.is_async=True` — an individual step is driven per-step via `run_coroutine(self._execute_step_async(...))` within an otherwise synchronous loop.
3. Both flags `False` — fully synchronous `execute_step`.

Before any step runs, `execute_feature` calls the module-level `validate_request(feature, request)`, which coerces `request.data` against `feature.params_schema` (a `RequestSpecification`) when one is declared, raising `REQUEST_VALIDATION_FAILED` on a schema violation. Each step is then resolved and executed:

- `resolve_step_event(step, feature_flags)` resolves the step's domain event via the injected `get_dependency` handler, combining feature-level and step-level flags (feature-level first).
- `resolve_middleware(middleware_ids)` resolves configured middleware service IDs to callables; `compose_step_middleware` concatenates feature-level (outer) and step-level (inner) middleware into one ordered list, and `build_step_chain` wraps the event's `execute` in that chain.
- `parse_request_parameter` resolves `$r.<key>`-prefixed parameters from `request.data`, delegating everything else to the injected `parse_parameter` callable (identity by default).
- `execute_step`/`_execute_step_async` run the built chain and store the result via `request.set_result(result, data_key)`. `pass_on_error=True` catches only a `TiferetError` — a `ModelError`, `ServiceError`, or any other exception is a defect, not a domain outcome, and always propagates.

### Conditional Step Execution

`EventFeatureStep.condition` is an optional boolean expression evaluated by the module-level `evaluate_condition(condition, request)` before a step runs. `None`/empty always executes; `$r.<key>` references are substituted from `request.data`; an unparseable expression defensively evaluates to `False` rather than raising.

```yaml
features:
  calc:
    safe_divide:
      commands:
        - service_id: divide_number_event
          condition: '$r.b != 0'
```

### Service Resolution (get_dependency)

Feature-step services are resolved through the injected `get_dependency(registration_id, *flags)` callable — the bound method of a `ServiceResolver` (`di/dependency_injector.py`), composed by `build_service_resolver` and injected into the hub at construction time, then forwarded unchanged into each `FeatureContext` the hub builds. See [docs/guides/di.md](di.md) for how `get_dependency` builds and caches per-flag containers; contexts never hold a container directly.

## RequestContext

<a id="requestcontext"></a>
`RequestContext` (`tiferet/contexts/request.py`) binds a `Request` domain value object as `self.domain` and exposes `session_id`, `feature_id`, `headers`, and `data` as read/write proxy properties delegating straight to it, while `result` is runtime-only context state with no `Request` counterpart. `set_result(result, data_key=None)` stores into `self.domain.data[data_key]` when a step declares a `data_key`, or into `self.result` directly otherwise; `handle_response()` returns `self.result` by default. See [docs/guides/domain/request.md](domain/request.md) for the full `Request`/`RequestContext` split.

## ErrorContext and LoggingContext

<a id="errorcontext"></a><a id="loggingcontext"></a>
`ErrorContext.format_response(error, exception, lang)` formats a structured, localized response dict from a pre-loaded `Error` domain object and the raised `TiferetError`'s `kwargs`; error retrieval itself is owned by the caller (the `raise_error_handler` the hub delegates to), not by `ErrorContext`.

`LoggingContext.build_logger()` assembles a `logging.config.dictConfig`-ready dict from a pre-assembled `LoggingSettings` domain object (which owns the `format_config()` assembly) and returns a configured `logging.Logger`. Neither context is typically subclassed — extend the underlying domain settings or error catalog instead.

## CacheContext

<a id="cachecontext"></a>
`CacheContext` (`tiferet/contexts/cache.py`) is a namespaced in-memory cache: every item is stored under a `*prefix` tuple (e.g. `('app', 'errors')`), with the empty prefix `()` addressing the root namespace. `get`/`set`/`delete` accept an optional `*prefix`; `get_by_prefix(*prefix)` returns a shallow copy of an entire namespace as a `Dict[str, Any]`, backing enumeration of the bootstrap catalogs `build_cache` seeds (app services/constants, default errors, features, CLI commands, logging settings). The hub owns one `CacheContext` per session and shares it with the `FeatureContext` it builds — treat it as per-session, never shared across sessions.

## Composition in the Application Graph

The `build_app` blueprint constructs the hub declaratively from the loaded `AppSession`, wiring the five handlers and the resolver's `get_dependency`:

```
build_app (blueprint)
  └── ServiceResolver            (owns DI assembly; get_dependency injected into the hub)
        └── AppSessionContext     (hub, bound to AppSession; owns CacheContext)
              ├── FeatureContext     ── get_dependency + shared CacheContext, built on demand
              ├── ErrorContext       ── built on demand by raise_error_handler
              └── LoggingContext     ── built by build_logger_handler (cache-first)
```

`CliSessionContext` composes in parallel through `build_cli`, substituting itself for `AppSessionContext` and overriding the `create_request_handler`/`response_handler` slots with CLI-specific closures. See [docs/guides/blueprints.md](blueprints.md) for the full composition chain.

## Testing Contexts

Context tests use `pytest` with `unittest.mock`, focused on behavior rather than implementation detail.

```python
# ** fixture: app_session_context
@pytest.fixture
def app_session_context(app_session, build_logger_handler):
    return AppSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        build_logger_handler=build_logger_handler,
        execute_feature_handler=mock.Mock(),
        create_request_handler=mock.Mock(return_value=RequestContext()),
        raise_error_handler=mock.Mock(),
        response_handler=mock.Mock(side_effect=lambda request: request.result),
    )

# ** test: run_success
def test_run_success(app_session_context, build_logger_handler):
    build_logger_handler.return_value = mock.Mock()
    result = app_session_context.run('calc.add', data={'a': 1, 'b': 2})
    assert result is not None
```

- **Mock every injected handler** — `AppSessionContext` has no fallback implementation for any of the five, so an unmocked handler in a test raises `APP_ERROR` exactly as it would in production.
- **Exercise the unwired-handler guard directly** — construct with a handler left `None` and assert the resulting `TiferetAPIError` names the correct slot.
- **Test `FeatureContext` in isolation** from the hub — bind a `Feature` via `from_domain`, inject a mock `get_dependency`, and assert on `resolve_step_event`/`execute_step` behavior rather than routing everything through `run`.

## Best Practices

### 1. Keep Contexts Focused
A context owns one runtime concern. If a context grows multiple responsibilities, split it into a high-level context plus one or more low-level contexts.

### 2. Prefer `super()` Over Reimplementation
When extending `AppSessionContext`, override only the template methods that differ and call `super()` for the rest — this preserves timing, logging, and the unwired-handler guarantees for free.

### 3. Never Inject Contexts into Domain Events
Domain events depend on **services**, not contexts. Passing a context into an event couples domain logic to the runtime graph and makes the event harder to test in isolation.

### 4. Use `TiferetError.raise_error()` for Context-Level Failures
Contexts raise structured `TiferetError` instances with framework error codes — never raw exceptions — so `handle_error` can format them. `raise_unwired_handler_error` is the one deliberate exception: it raises an already-formatted `TiferetAPIError` for a composition bug that a domain error code shouldn't need to catalog.

### 5. Treat CacheContext as Per-Session
Each `AppSessionContext` creates one `CacheContext` and shares it only with the `FeatureContext` it builds. Never share a single `CacheContext` across sessions.

## Boundaries

**Inside this domain:** binding domain objects to runtime orchestrators (`BaseContext`/`ContextMeta`), the hub's five-handler `run` pipeline, feature-step resolution and middleware composition, and the namespaced in-memory cache.
**Outside this domain:** wiring the handler callables themselves and choosing which context class backs a session (`build_app`/`build_cli` — [docs/guides/blueprints.md](blueprints.md)); resolving a service by id (`ServiceResolver` — [docs/guides/di.md](di.md)); the declared shape of the domain objects contexts bind (`Feature`, `AppSession`, `Request`, `Error`, `LoggingSettings` — `docs/guides/domain/`).

## Related Documentation

- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context base classes, artifact comments, and code style reference
- [docs/guides/blueprints.md](blueprints.md) — Blueprint composition chains that construct and wire contexts
- [docs/guides/di.md](di.md) — `ServiceResolver`/`get_dependency`, consumed by `FeatureContext`
- [docs/guides/domain/request.md](domain/request.md) — `Request`/`RequestContext` split
- [docs/guides/domain/feature.md](domain/feature.md) — `Feature`/`EventFeatureStep` domain objects `FeatureContext` executes
- [docs/guides/domain/app.md](domain/app.md) — `AppSession` domain object `AppSessionContext` binds
- [docs/guides/errors.md](errors.md) — `TiferetError`/`ServiceError`/`ModelError` families raised and handled across contexts
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting rules
