# Middleware – Cross-Cutting Concerns for Domain Events

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/utils/middleware.py`  
**Version:** 2.0.0

## Overview

Middleware wraps domain event execution with cross-cutting concerns — logging, timing, tracing, retries, auditing — without modifying the event itself. A middleware is a callable that receives the event, its execution kwargs, and a `next_fn` callable that invokes the remainder of the chain.

Middleware is applied through the `DomainEvent.handle()` and `DomainEvent.handle_async()` static methods, both of which accept an optional `middleware` list. When no middleware is supplied, execution is unchanged; when middleware is supplied, the entries are composed into an ordered chain around the event's `execute` method.

See the [Middleware Support](../core/events.md#middleware-support) section of the events core doc for the base-class mechanics.

## Built-in Middleware

Two infrastructure middleware ship in `tiferet.utils.middleware`. Each is a `MiddlewareService` subclass that takes a single `logger_id: str` parameter (default `'root'`) and resolves the matching stdlib logger via `logging.getLogger(logger_id)`. They rely on `LoggingContext` having configured Python logging at application startup; on their own they emit records to whichever logger `logger_id` names.

- **`LoggingMiddleware`** — emits a `DEBUG` record before execution and after success, and an `ERROR` record (with traceback via `exc_info=True`) when the chain raises. The exception is always re-raised.
- **`TimingMiddleware`** — measures elapsed wall-clock time with `time.perf_counter` and emits a single `DEBUG` record reporting the duration in milliseconds on both the success and exception paths. The exception is always re-raised.

```python
from tiferet.events import DomainEvent
from tiferet.utils.middleware import LoggingMiddleware, TimingMiddleware

result = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    middleware=[LoggingMiddleware('root'), TimingMiddleware('root')],
    id='ERR_001',
)
```

Both are infrastructure-only: they contain no domain logic and never raise a `TiferetError` of their own.

## The MiddlewareService Interface

Custom middleware extends `MiddlewareService` from `tiferet.interfaces.middleware` and implements a single `__call__` method:

```python
# *** imports

# ** app
from tiferet.interfaces.middleware import MiddlewareService

# *** utils

# ** util: audit_middleware
class AuditMiddleware(MiddlewareService):
    '''
    Records an audit trail around domain event execution.
    '''

    # * method: __call__
    def __call__(self, event, kwargs, next_fn):
        '''
        Invoke the chain, recording the event class name.
        '''

        # Execute the remainder of the chain and return its result.
        return next_fn()
```

`__call__` receives three arguments:

| Argument | Type | Description |
|---|---|---|
| `event` | `DomainEvent` | The instantiated domain event (or `AsyncDomainEvent`) instance. |
| `kwargs` | `Dict[str, Any]` | The merged execution keyword arguments passed to `execute`. |
| `next_fn` | `Callable[[], Any]` | Zero-argument callable that invokes the next middleware in the chain, or the event's `execute` when none remain. In asynchronous paths it is a coroutine function and must be awaited. |

## Sync vs Async

### Synchronous middleware

Synchronous middleware is used with `DomainEvent.handle()`. It calls `next_fn()` directly and returns (or transforms) its result:

```python
class TimingMiddleware(MiddlewareService):

    # * method: __call__
    def __call__(self, event, kwargs, next_fn):
        start = time.perf_counter()
        try:
            result = next_fn()
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            self.logger.debug('%s raised after %.2fms', event.__class__.__name__, elapsed)
            raise
        elapsed = (time.perf_counter() - start) * 1000
        self.logger.debug('%s completed in %.2fms', event.__class__.__name__, elapsed)
        return result
```

### Asynchronous middleware

Asynchronous middleware is used with `DomainEvent.handle_async()` and `AsyncDomainEvent` subclasses. It must be implemented as `async def __call__` and must `await next_fn()`:

```python
class AsyncAuditMiddleware(MiddlewareService):

    # * method: __call__
    async def __call__(self, event, kwargs, next_fn):
        result = await next_fn()
        return result
```

`handle_async` awaits any coroutine returned by a middleware, so async and sync middleware compose alike within an async chain. A synchronous middleware may call `next_fn()` in an async chain, but it will receive a coroutine it cannot inspect directly — prefer `async def __call__` for async contexts.

## Ordering

Middleware is composed **outermost-first**: the first entry in the list is the outermost wrapper. It runs first on the way in and last on the way out.

```python
middleware=[LoggingMiddleware('root'), TimingMiddleware('root')]
```

For the list above, execution flows:

```
LoggingMiddleware → TimingMiddleware → event.execute → TimingMiddleware → LoggingMiddleware
```

When middleware is resolved from configuration, feature-level middleware is composed outside step-level middleware, so feature-level middleware wraps every step.

## Registering Middleware in config.yml

Middleware can also be declared in `config.yml` and resolved from the DI container by `FeatureContext` during `execute_feature` / `execute_feature_async`. First register the middleware as a service, pointing `module_path` at `tiferet.utils.middleware` (or your own module):

```yaml
services:
  logging_middleware:
    module_path: tiferet.utils.middleware
    class_name: LoggingMiddleware
    parameters:
      logger_id: root
  timing_middleware:
    module_path: tiferet.utils.middleware
    class_name: TimingMiddleware
    parameters:
      logger_id: root
```

### Feature-level

Feature-level middleware wraps **every step** in the feature:

```yaml
features:
  calc:
    add:
      name: Add Numbers
      middleware:
        - logging_middleware
      commands:
        - service_id: add_number_event
```

### Step-level

Step-level middleware applies to a **single command** only:

```yaml
features:
  calc:
    add:
      name: Add Numbers
      commands:
        - service_id: add_number_event
          middleware:
            - timing_middleware
```

### Both levels combined

Feature-level and step-level middleware compose together, feature-level outermost:

```yaml
features:
  calc:
    add:
      name: Add Numbers
      middleware:
        - logging_middleware
      commands:
        - service_id: add_number_event
          middleware:
            - timing_middleware
```

Each named entry is resolved from the `services` registration and composed into the chain before the step executes.

## Using Middleware Directly via handle()

Outside feature execution, compose middleware programmatically by passing the `middleware` list to `handle()` or `handle_async()`:

```python
# Synchronous
result = DomainEvent.handle(
    GetError,
    dependencies={'error_service': error_service},
    middleware=[LoggingMiddleware('root')],
    id='ERR_001',
)

# Asynchronous
result = await DomainEvent.handle_async(
    GetErrorAsync,
    dependencies={'error_service': error_service},
    middleware=[AsyncAuditMiddleware()],
    id='ERR_001',
)
```

## Error Handling in Middleware

Middleware **observes and re-raises**; it must not suppress exceptions. Both built-in middleware log on the exception path and then re-raise the original exception unchanged, so error propagation and structured `TiferetError` handling continue to work exactly as they would without middleware:

```python
try:
    result = next_fn()
except Exception:
    # Observe (log, time, trace) ...
    raise
```

Middleware should not convert, swallow, or replace exceptions raised by the event; doing so would hide domain errors from callers and contexts.

## Testing Middleware

Middleware is straightforward to unit test with a stub `event` and a controllable `next_fn`. Assert against captured log records for the built-in middleware, and against `next_fn` invocation for custom middleware:

```python
# *** imports

# ** infra
import logging
import pytest
from unittest import mock

# ** app
from tiferet.utils.middleware import LoggingMiddleware

# *** tests

# ** test: logging_middleware_success
def test_logging_middleware_success(caplog):
    '''
    LoggingMiddleware logs around a successful call and returns its result.
    '''

    # Arrange a stub event and a next_fn returning a sentinel.
    event = mock.Mock()
    event.__class__.__name__ = 'GetError'
    next_fn = mock.Mock(return_value='ok')

    # Act with DEBUG capture on the resolved logger.
    with caplog.at_level(logging.DEBUG):
        result = LoggingMiddleware('root')(event, {}, next_fn)

    # Assert the chain result is returned unchanged and next_fn ran once.
    assert result == 'ok'
    next_fn.assert_called_once_with()

# ** test: logging_middleware_reraises
def test_logging_middleware_reraises(caplog):
    '''
    LoggingMiddleware logs an ERROR and re-raises the original exception.
    '''

    # Arrange a next_fn that raises.
    event = mock.Mock()
    event.__class__.__name__ = 'GetError'
    next_fn = mock.Mock(side_effect=ValueError('boom'))

    # Act / assert the exception propagates unchanged.
    with pytest.raises(ValueError):
        LoggingMiddleware('root')(event, {}, next_fn)
```

For async middleware, drive `__call__` with `asyncio.run` (or an async test) and an `async def` `next_fn`.

## Related Documentation

- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns, `handle` / `handle_async`, and the Middleware Support section
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions (`MiddlewareService`)
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) — Utility and infrastructure conventions
- [docs/guides/domain/logging.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/logging.md) — Logging configuration consumed by the built-in middleware
