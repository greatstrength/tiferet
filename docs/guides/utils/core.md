# Utilities – LoggingMiddleware, CacheMiddleware, TimingMiddleware

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

`tiferet/utils/core.py` ships three concrete `MiddlewareService` implementations — infrastructure-only callables that wrap domain event execution with a single cross-cutting concern (logging, cache injection, or timing) without touching the event itself. All three share the same `__call__(event, kwargs, next_fn)` contract; see [docs/guides/utils.md](../utils.md#the-middlewareservice-pattern) for the composition mechanics (ordering, sync vs. async, config.yml registration) that apply to any middleware, built-in or custom.

**Module:** `tiferet/utils/core.py`
**Vision:** See each class's docstring in `tiferet/utils/core.py` for its value statement.

## Ubiquitous Language

- **Chain** — the ordered sequence of middleware wrapping a single domain event's `execute` call.
- **`next_fn`** — the zero-argument callable a middleware invokes to continue the chain; the innermost `next_fn` invokes the event's `execute`.
- **Observe-and-reraise** — the required middleware discipline: react to success/failure (log, time, inject) without suppressing or transforming exceptions.

## When should you reach for which one?

| Use case | Best choice | Why it fits |
|---|---|---|
| Trace execution start/success/failure in logs | `LoggingMiddleware` | DEBUG before/after, ERROR with traceback on failure |
| Measure elapsed wall-clock time | `TimingMiddleware` | `time.perf_counter`-based duration logging on both paths |
| Share a cache snapshot across steps without coupling to `CacheContext` | `CacheMiddleware` | additive `kwargs['cache']` injection; no-op when unset |

## Quick example

```python
from tiferet.events import DomainEvent
from tiferet.utils.core import LoggingMiddleware, CacheMiddleware, TimingMiddleware

result = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    middleware=[LoggingMiddleware('root'), CacheMiddleware(load_cache), TimingMiddleware('root')],
    id='ERR_001',
)
```

## Domain Objects

### LoggingMiddleware

Emits a `DEBUG` record before and after the wrapped execution and an `ERROR` record (with traceback via `exc_info=True`) when the chain raises. Contains no domain logic and raises no `TiferetError`.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="loggingmiddleware-logger"></a>`logger` | `logging.Logger` | — | — | Resolved via `logging.getLogger(logger_id)` at construction. |

#### Methods

<a id="loggingmiddleware-init"></a>
**`__init__(logger_id: str = 'root')`**

Resolves the named stdlib logger. Relies on `LoggingContext` having configured Python logging at application startup; used standalone it emits to whichever logger `logger_id` names regardless.

<a id="loggingmiddleware-call"></a>
**`__call__(event, kwargs, next_fn) -> Any`**

Logs `DEBUG` before and after a successful call; on exception, logs `ERROR` with `exc_info=True` and re-raises unchanged. The chain result is returned unmodified.

### CacheMiddleware

Injects a cache snapshot into event kwargs, sourced from an injected `load_cache` callable rather than importing `CacheContext` directly — preserving the utils/contexts layer boundary (`utils` may not depend on `contexts`).

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="cachemiddleware-load-cache"></a>`load_cache` | `Callable[[], Dict[str, Any]] \| None` | No | `None` | Zero-argument callable returning a cache snapshot dict. `None` makes the middleware a transparent no-op. |

#### Methods

<a id="cachemiddleware-call"></a>
**`__call__(event, kwargs, next_fn) -> Any`**

Injects the loaded snapshot as `kwargs['cache']` **only** when a loader is configured and no `'cache'` key is already present (additive, never overwrites). Always invokes `next_fn()`.

### TimingMiddleware

Measures elapsed wall-clock time with `time.perf_counter` and emits a single `DEBUG` record reporting the duration in milliseconds on both the success and exception paths. Contains no domain logic and raises no `TiferetError`.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="timingmiddleware-logger"></a>`logger` | `logging.Logger` | — | — | Resolved via `logging.getLogger(logger_id)` at construction. |

#### Methods

<a id="timingmiddleware-init"></a>
**`__init__(logger_id: str = 'root')`**

Resolves the named stdlib logger, mirroring `LoggingMiddleware`.

<a id="timingmiddleware-call"></a>
**`__call__(event, kwargs, next_fn) -> Any`**

Captures `perf_counter()` before invoking `next_fn()`, logs the elapsed milliseconds on either the success or exception path, and re-raises exceptions unchanged.

## Registering Middleware in config.yml

Register as a service, pointing `module_path` at `tiferet.utils.core`:

```yaml
services:
  logging_middleware:
    module_path: tiferet.utils.core
    class_name: LoggingMiddleware
    parameters:
      logger_id: root
  timing_middleware:
    module_path: tiferet.utils.core
    class_name: TimingMiddleware
```

Then reference the service id at feature level (wraps every step) or step level (wraps a single command) — see [docs/guides/utils.md](../utils.md#the-middlewareservice-pattern) for the combined-levels composition order.

## Testing

Middleware is straightforward to unit test with a stub `event` and a controllable `next_fn`:

```python
def test_logging_middleware_success(caplog):
    event = mock.Mock()
    event.__class__.__name__ = 'GetError'
    next_fn = mock.Mock(return_value='ok')

    with caplog.at_level(logging.DEBUG):
        result = LoggingMiddleware('root')(event, {}, next_fn)

    assert result == 'ok'
    next_fn.assert_called_once_with()
```

For `CacheMiddleware`, assert on the `kwargs` dict passed to `next_fn` (via a `next_fn` that captures its call context) rather than on log output.

## Boundaries

**Inside this domain:** the three built-in, infrastructure-only middleware implementations and their construction/behavior.
**Outside this domain:** the `MiddlewareService` ABC contract and the chain-composition mechanics (ordering, sync/async, config.yml wiring) — see [docs/guides/utils.md](../utils.md#the-middlewareservice-pattern) and [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md#middleware-support). Writing custom middleware is also out of scope here — see `docs/core/interfaces.md`.

## Related Documentation

- [docs/guides/utils.md](../utils.md) — Utils layer strategy guide, including the MiddlewareService pattern
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns, `handle` / `handle_async`, and the Middleware Support section
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — `MiddlewareService` ABC
- [docs/guides/domain/logging.md](../domain/logging.md) — Logging configuration consumed by `LoggingMiddleware`/`TimingMiddleware`
