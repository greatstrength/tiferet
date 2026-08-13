# Events – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/`  
**Version:** 2.0.0

## Overview

The events layer is where focused domain actions — validation, service interaction, computation, orchestration — get expressed as instantiate-and-execute classes. `DomainEvent` (`events/core.py`) supplies the shared mechanics every event inherits: the `execute` contract, declarative parameter validation, structured error raising, and the `handle`/`handle_async` invocation pattern (including optional middleware composition). This guide documents those cross-cutting mechanics; the per-module guides (`docs/guides/events/*.md`) document each module's CRUD-style operations. **Vision:** see the `DomainEvent` and `AsyncDomainEvent` class docstrings in `tiferet/events/core.py` for the value statements this guide distills.

## Ubiquitous Language

- **Domain event** — a `DomainEvent` subclass: a single-purpose, instantiate-then-`execute` domain operation, resolved and constructed by `DomainEvent.handle`/`handle_async`.
- **Per-module base event** — the one class per single-service event module (`AppEvent`, `CliEvent`, `DIEvent`, `ErrorEvent`, `FeatureEvent`, `LoggingEvent`, `SqliteEvent`) that owns the injected service dependency; concrete events in that module extend it and declare only `execute`.
- **Middleware chain** — an ordered, outermost-first list of `(event, kwargs, next_fn)` callables composed around an event's `execute`, supplied to `handle`/`handle_async` via the `middleware` argument.
- **Aggregated parameter validation** — the single `COMMAND_PARAMETER_REQUIRED` error `@DomainEvent.parameters_required([...])` raises, naming every missing/blank parameter at once rather than failing on the first one found.

## The DomainEvent Contract

`DomainEvent` (extends `object`, not `ABC`) declares four members the rest of the framework depends on:

- **`execute(**kwargs) -> Any`** — the operation itself; subclasses override this. The base raises `NotImplementedError()`.
- **`raise_error(error_code, message=None, **kwargs)`** (static) — delegates to `TiferetError.raise_error`, so an event never constructs a `TiferetError` directly.
- **`verify(expression, error_code, message=None, **kwargs)`** — calls `raise_error` when `expression` is falsy; the idiomatic way to assert a domain rule inside `execute`.
- **`parameters_required(param_names)`** (static) — a decorator factory; see below.

`AsyncDomainEvent` extends `DomainEvent` with an `async def execute`, inheriting `verify`/`raise_error`/`parameters_required` unchanged — the synchronous raisers work correctly from an async context since raising an exception is not itself async.

## The `parameters_required` Decorator

`@DomainEvent.parameters_required(['id', 'name'])` wraps `execute` (sync or async — `_wrap_with_validation` detects `asyncio.iscoroutinefunction` and builds the matching wrapper) with a call to `_validate_required_parameters`. A parameter is invalid if it is absent from `kwargs`, `None`, or an empty/whitespace-only string; every violation is collected before a single `COMMAND_PARAMETER_REQUIRED` error is raised naming them all, rather than failing fast on the first one. Falsy-but-valid values (`0`, `False`, `[]`) pass.

## The `handle`/`handle_async` Pattern

```python
result = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    middleware=[LoggingMiddleware('root'), TimingMiddleware('root')],
    id='ERR_001',
)
```

1. Instantiate the event class with `dependencies` as constructor kwargs.
2. Build the base callable: `event_handler.execute(**kwargs)`.
3. When `middleware` is supplied, compose it around the base **outermost-first** — the first list entry wraps everything else, and each middleware callable receives `(event, kwargs, next_fn)`, calling `next_fn()` to continue the chain.
4. Invoke the composed chain (or the bare base callable when no middleware is given).

`handle_async` mirrors this exactly for `AsyncDomainEvent` subclasses, except every step is awaited and a synchronous middleware's return value is inspected for `asyncio.iscoroutine` before being awaited — so sync and async middleware compose in either chain without the caller needing to know which is which.

## The Per-Module Base Event Pattern

Every event module with a single shared service dependency defines one base event that owns the `# * attribute` / `# * init` boilerplate:

```python
class ErrorEvent(DomainEvent):
    error_service: ErrorService

    def __init__(self, error_service: ErrorService):
        self.error_service = error_service

class GetError(ErrorEvent):
    def execute(self, id: str, **kwargs) -> Error:
        return self.error_service.get(id)
```

The seven base events — `AppEvent`, `CliEvent`, `DIEvent`, `ErrorEvent`, `FeatureEvent`, `LoggingEvent`, `SqliteEvent` — are documented alongside their module's CRUD surface in `docs/guides/events/*.md`, not here; this guide covers only the shared mechanism `DomainEvent` itself supplies.

## When to Extend DomainEvent Directly

Extend `DomainEvent` (or `AsyncDomainEvent`) directly, skipping a per-module base event, when an event has no shared service dependency to inject, or is the first (and so far only) event in a new module — a base event is worth introducing once a second event needs the same dependency.

## Boundaries

**Inside this domain:** the `execute`/`verify`/`raise_error` contract, declarative parameter validation, the `handle`/`handle_async` invocation and middleware-composition mechanics, and the per-module base event pattern.
**Outside this domain:** each module's actual CRUD operations and their required/optional parameters (`docs/guides/events/*.md`); the `MiddlewareService` interface and built-in middleware implementations ([docs/guides/utils.md](utils.md)); the three error families an event might raise or propagate ([docs/guides/errors.md](errors.md)).

## Related Documentation

- [docs/guides/events/app.md](events/app.md), [cli.md](events/cli.md), [di.md](events/di.md), [error.md](events/error.md), [feature.md](events/feature.md), [logging.md](events/logging.md), [sqlite.md](events/sqlite.md) — per-module CRUD event guides
- [docs/guides/utils.md](utils.md) — `MiddlewareService` and built-in middleware
- [docs/guides/errors.md](errors.md) — `TiferetError`/`ServiceError`/`ModelError`, raised or propagated by events
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Artifact comments and code-style conventions for events
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
