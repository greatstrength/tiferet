# Middleware Guide

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

## Overview

Middleware provides a standardized attachment point for cross-cutting concerns — audit logging, execution timing, distributed tracing, metrics, and retry logic — without modifying domain event code. Middleware instances are resolved from the DI container, composed into an ordered chain, and called around every event execution.

## Built-in Middleware

Tiferet ships two ready-to-use implementations in `tiferet.utils.middleware`, exported directly from the top-level package:

| Class | Alias | Purpose |
|---|---|---|
| `LoggingMiddleware` | — | DEBUG/ERROR logging via stdlib `logging` |
| `TimingMiddleware` | — | Wall-clock timing logged at DEBUG via stdlib `logging` |

Both take a single `logger_id: str` parameter (defaults to `'root'`) and rely on `LoggingContext` having configured the logging subsystem at startup, which happens automatically in any standard Tiferet application.

```python
from tiferet import LoggingMiddleware, TimingMiddleware

result = DomainEvent.handle(
    AddNumber,
    middleware=[
        TimingMiddleware(logger_id='my_app'),   # outermost
        LoggingMiddleware(logger_id='my_app'),  # innermost
    ],
    a=1, b=2,
)
```

## The MiddlewareService Interface

For custom middleware, extend `tiferet.interfaces.MiddlewareService`:

```python
from tiferet.interfaces import MiddlewareService

class TraceMiddleware(MiddlewareService):
    def __call__(self, event, kwargs, next_fn):
        # inject trace context, call next, clean up
        result = next_fn()
        return result
```

The three arguments:

| Argument  | Type                     | Description                                                                       |
|-----------|--------------------------|-----------------------------------------------------------------------------------|
| `event`   | `DomainEvent` instance   | The instantiated domain event — inspect type, attributes, or service dependencies |
| `kwargs`  | `Dict[str, Any]`         | The merged execution keyword arguments passed to `execute`                        |
| `next_fn` | `Callable[[], Any]`      | Calls the next middleware or the event itself; always call it to continue         |

## Sync vs Async

### Sync middleware

Implement `def __call__` for use in synchronous execution paths (`execute_feature`, `DomainEvent.handle`):

```python
class AuditMiddleware(MiddlewareService):
    def __init__(self, audit_log_service):
        self.log = audit_log_service

    def __call__(self, event, kwargs, next_fn):
        self.log.record(event.__class__.__name__, kwargs)
        result = next_fn()
        return result
```

### Async middleware

Implement `async def __call__` and `await next_fn()` for use in async execution paths (`execute_feature_async`, `DomainEvent.handle_async`):

```python
class AsyncAuditMiddleware(MiddlewareService):
    async def __call__(self, event, kwargs, next_fn):
        print(f"Before: {event.__class__.__name__}")
        result = await next_fn()
        print(f"After: {event.__class__.__name__}")
        return result
```

> **Note:** Async middleware works in both sync and async contexts. Sync middleware used in an async context will receive an async `next_fn` — calling `next_fn()` returns a coroutine that the framework awaits for transparent pass-through middleware. For pre/post inspection in async contexts always use `async def __call__`.

## Ordering

Middleware is composed **outermost-first**: the first entry in the list runs first on entry and last on exit. Feature-level middleware wraps step-level middleware:

```
Feature-level outer  →  Step-level inner  →  Event execution
```

For a feature with `middleware: [timing]` and a step with `middleware: [audit]`:

```
timing.pre → audit.pre → event.execute() → audit.post → timing.post
```

## Registering Middleware in config.yml

Declare middleware as `service_id` values — the same convention used for feature steps. The DI container resolves them at runtime.

### Feature-level middleware (applies to every step)

```yaml
features:
  calc:
    middleware:
      - timing_middleware    # service_id registered in services section
    add:
      name: Add Number
      commands:
        - attribute_id: add_number_event
          name: Add a and b
```

### Step-level middleware (applies to one step only)

```yaml
features:
  calc:
    add:
      name: Add Number
      commands:
        - attribute_id: add_number_event
          name: Add a and b
          middleware:
            - audit_middleware
```

### Both levels combined

```yaml
features:
  calc:
    middleware:
      - timing_middleware    # outermost — wraps all steps
    add:
      commands:
        - attribute_id: add_number_event
          middleware:
            - audit_middleware  # innermost — step-specific
```

### Registering the service

Register the middleware implementation in the `services` section just like any other dependency. Use the built-in utilities directly by pointing at `tiferet.utils.middleware`:

```yaml
services:
  timing_middleware:
    module_path: tiferet.utils.middleware
    class_name: TimingMiddleware
    parameters:
      logger_id: my_app_logger
  logging_middleware:
    module_path: tiferet.utils.middleware
    class_name: LoggingMiddleware
    parameters:
      logger_id: my_app_logger
  audit_middleware:
    module_path: myapp.middleware
    class_name: AuditMiddleware
```

## Using Middleware Directly via handle()

For ad-hoc use or testing, pass middleware directly to `DomainEvent.handle` or `DomainEvent.handle_async`:

```python
from tiferet.events import DomainEvent

result = DomainEvent.handle(
    AddNumber,
    dependencies={'number_service': svc},
    middleware=[TimingMiddleware(), AuditMiddleware()],
    a=1,
    b=2,
)
```

```python
result = await DomainEvent.handle_async(
    AsyncAddNumber,
    dependencies={'number_service': svc},
    middleware=[AsyncAuditMiddleware()],
    a=1,
    b=2,
)
```

## Error Handling in Middleware

Middleware can intercept, transform, or suppress exceptions raised by the event or downstream middleware:

```python
class RetryMiddleware(MiddlewareService):
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def __call__(self, event, kwargs, next_fn):
        last_exc = None
        for attempt in range(self.max_attempts):
            try:
                return next_fn()
            except Exception as e:
                last_exc = e
        raise last_exc
```

If middleware raises, the exception propagates normally through `handle_feature_step` — `pass_on_error` on the step still applies.

## Testing Middleware

Test middleware in isolation by providing a `next_fn` mock:

```python
def test_timing_middleware_calls_next():
    mw = TimingMiddleware()
    called = {}

    class FakeEvent:
        pass

    def next_fn():
        called['ran'] = True
        return 'result'

    result = mw(FakeEvent(), {}, next_fn)
    assert result == 'result'
    assert called.get('ran') is True
```

For integration-style tests, use `DomainEvent.handle` with a real event and inline middleware.
