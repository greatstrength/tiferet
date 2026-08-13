# Utils – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/utils/`  
**Version:** 2.0.0

## Overview

Utilities are Tiferet's injectable, testable infrastructure layer — repeatable processes, physical (file I/O, database) and computational (algorithms, transformations, cross-cutting execution wrapping), exposed behind contracts other layers can depend on without coupling to a specific implementation. Two families live under `tiferet/utils/`, sharing the directory for infrastructure reasons rather than a common base class:

- **`FileLoader`-based utilities** (`file.py`, `csv.py`, `json.py`, `toml.py`, `yaml.py`, `sqlite.py`) — physical I/O, each satisfying a `Service` interface and usable directly via the context-manager protocol.
- **`MiddlewareService`-based utilities** (`core.py`) — computational, cross-cutting wrappers around domain event execution.

This guide covers the cross-cutting strategies for both families. For any single concrete utility's constructor, methods, and usage examples, see its dedicated guide under `docs/guides/utils/*.md`.

## Ubiquitous Language

- **Physical infrastructure** — utilities that perform actual I/O (reading/writing files, querying a database).
- **Computational infrastructure** — utilities that transform or wrap execution without I/O of their own (e.g., middleware).
- **Loader** — a `FileLoader` subclass exposing static, one-shot helpers for a specific file format.
- **Client** — a `FileLoader` subclass exposing an instance-level, stateful API (e.g., `SqliteClient` holding an open connection).

## The FileLoader Foundation

Every physical-I/O utility extends `FileLoader` (`tiferet/utils/file.py`), which provides:

- **Context manager protocol** (`__enter__`/`__exit__`) — for stateful clients (`SqliteClient`), commits/closes cleanly on success and rolls back/closes on exception. For stateless loaders, the protocol is present for consistency even where each call is already atomic.
- **Path and encoding handling** — shared `path`, `encoding` (default `'utf-8'`), and existence/mode validation, so every concrete utility gets consistent `FILE_NOT_FOUND` / `INVALID_ENCODING` behavior for free.
- **Static one-shot helpers** — most loaders (`Yaml`, `Json`, `Csv`, `Toml`) expose static methods (`Yaml.load(path)`, `Json.save(path, data)`) for callers who need a single read/write without holding a connection open.

`SqliteClient` is the exception among physical utilities: it also implements a domain-facing `Service` interface (`SqliteService`), so it can be constructor-injected into events and repositories exactly like any other service, in addition to being used directly. See [docs/guides/utils/sqlite.md](utils/sqlite.md).

## The MiddlewareService Pattern

`MiddlewareService` (`tiferet/interfaces/middleware.py`) is an abstract callable wrapping domain event execution: `__call__(self, event, kwargs, next_fn)` for sync middleware, `async def __call__` for async. It is applied via `DomainEvent.handle()` / `handle_async()`'s optional `middleware` argument, or resolved from `config.yml` service registrations by `FeatureContext` during step execution. The three built-in implementations live in `tiferet/utils/core.py` — see [docs/guides/utils/core.md](utils/core.md) for their individual constructors, methods, and examples.

### Contract

`__call__` receives three arguments: the instantiated `event`, the merged execution `kwargs`, and `next_fn` — a zero-argument callable invoking the next middleware in the chain, or the event's `execute` when none remain (a coroutine function in async chains, which must be awaited).

### Sync vs. Async

Synchronous middleware (used with `DomainEvent.handle()`) calls `next_fn()` directly. Asynchronous middleware (used with `DomainEvent.handle_async()` and `AsyncDomainEvent` subclasses) must be implemented as `async def __call__` and must `await next_fn()`. `handle_async` awaits any coroutine returned by a middleware, so sync and async middleware compose within an async chain, but a sync middleware calling `next_fn()` there receives an unawaited coroutine it cannot inspect — prefer `async def __call__` in async contexts.

### Ordering

Middleware composes **outermost-first**: the first entry in the list runs first on the way in and last on the way out.

```python
middleware=[LoggingMiddleware('root'), TimingMiddleware('root')]
# LoggingMiddleware → TimingMiddleware → event.execute → TimingMiddleware → LoggingMiddleware
```

When resolved from `config.yml`, feature-level middleware composes outside step-level middleware, so feature-level middleware wraps every step including any step-level middleware.

### Registration in config.yml

Register a middleware as a service (`module_path`/`class_name`), then reference its service id in a feature's or step's `middleware` list:

```yaml
services:
  logging_middleware:
    module_path: tiferet.utils.core
    class_name: LoggingMiddleware

features:
  calc:
    add:
      middleware: [logging_middleware]        # feature-level: wraps every step
      commands:
        - service_id: add_number_event
          middleware: [timing_middleware]      # step-level: wraps this command only
```

### Error Handling Discipline

Middleware must **observe and re-raise** — never suppress, convert, or replace an exception raised by the chain. Doing so would hide domain errors from callers and contexts:

```python
try:
    result = next_fn()
except Exception:
    # Observe (log, time, trace) ...
    raise
```

### Writing Custom Middleware

Extend `MiddlewareService` and implement `__call__`. Custom middleware is not restricted to `tiferet/utils/` — it may live in application code and be registered the same way. See [docs/guides/utils/core.md](utils/core.md) for the three built-in implementations as worked examples.

## Error Handling Convention (Physical Utilities)

Every physical utility wraps its underlying library/driver exceptions as a `ServiceError` (`tiferet.interfaces.core`) with the original exception preserved as `__cause__`, so no `sqlite3`/`yaml`/`json` exception type ever escapes to calling code. `ServiceError` is deliberately not a `TiferetError` — an infrastructural failure is not a domain outcome, so it is never resolved through the error catalog and is not skippable via a feature step's `pass_on_error`. See [docs/guides/utils/sqlite.md](utils/sqlite.md#error-handling) for the fullest worked example of this convention.

## Creating a New Utility

1. **Physical utility**: extend `FileLoader` in a new `tiferet/utils/<format>.py`; implement static one-shot helpers or a stateful client as appropriate; wrap all underlying exceptions as `ServiceError`.
2. **Computational utility (middleware)**: extend `MiddlewareService` in `tiferet/utils/core.py` (or application code); implement `__call__` (or `async def __call__`); observe-and-reraise; register via `config.yml` if it needs to be resolved by id.
3. **Write tests** in `tests/utils/test_<name>.py`, exercising the utility directly and, for physical utilities, via `tmp_path` fixtures rather than mocks.
4. **Document** — add a `docs/guides/utils/<name>.md` cookbook entry following the utils-flavored shape demonstrated by `utils/core.md`/`utils/sqlite.md` (see the canonical guide template suite in `docs/guides/templates/TEMPLATE-utils.md`).

## Boundaries

**Inside this domain:** infrastructure that domain events, repositories, and contexts inject and call directly for I/O or cross-cutting execution wrapping — the physical and computational utility families described above.
**Outside this domain:** domain logic and persistence mapping (`events`, `mappers`, `repos`), the `MiddlewareService` ABC's own definition (`docs/core/interfaces.md`), and how `FeatureContext` resolves and composes middleware at runtime (`docs/core/events.md`'s Middleware Support section).

## Related Documentation

- [docs/guides/utils/core.md](utils/core.md) — LoggingMiddleware, CacheMiddleware, TimingMiddleware
- [docs/guides/utils/sqlite.md](utils/sqlite.md) — SqliteClient (the only utility that is also a Service)
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) — Utility and infrastructure code-style conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — `Service` and `MiddlewareService` contracts
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and the Middleware Support section
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
