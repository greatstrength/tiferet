"""Tiferet Middleware Interface"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Callable, Dict

# ** app
from .core import Service

# *** interfaces

# ** interface: middleware_service
class MiddlewareService(Service):
    '''
    Abstract service interface for domain event middleware.

    Middleware wraps domain event execution with cross-cutting concerns such
    as audit logging, execution timing, distributed tracing, and retry logic.
    Middleware instances are resolved from the DI container by ``service_id``
    and composed into an ordered chain before the event executes.

    **Protocol**

    Each middleware receives:

    - ``event`` — the instantiated ``DomainEvent`` (or ``AsyncDomainEvent``) instance.
    - ``kwargs`` — the merged execution kwargs dict passed to ``execute``.
    - ``next_fn`` — a zero-argument callable that invokes the next middleware in
      the chain, or the event itself when no further middleware remains.
      In synchronous execution paths ``next_fn`` is a plain callable.
      In asynchronous execution paths ``next_fn`` is a coroutine function —
      middleware intended for async contexts must be implemented as
      ``async def __call__`` and must ``await next_fn()``.

    **Ordering**

    Middleware is composed outermost-first: the first entry in the list is the
    outermost wrapper (first to run on entry, last to run on exit).  Feature-level
    middleware wraps step-level middleware.

    **Sync example**::

        class TimingMiddleware(MiddlewareService):
            def __call__(self, event, kwargs, next_fn):
                start = time.perf_counter()
                result = next_fn()
                elapsed = time.perf_counter() - start
                print(f"{event.__class__.__name__} took {elapsed:.4f}s")
                return result

    **Async example**::

        class AsyncAuditMiddleware(MiddlewareService):
            async def __call__(self, event, kwargs, next_fn):
                print(f"Before: {event.__class__.__name__}")
                result = await next_fn()
                print(f"After: {event.__class__.__name__}")
                return result
    '''

    # * method: __call__
    @abstractmethod
    def __call__(self,
            event: Any,
            kwargs: Dict[str, Any],
            next_fn: Callable[[], Any]) -> Any:
        '''
        Execute the middleware, calling ``next_fn()`` to continue the chain.

        :param event: The instantiated domain event instance.
        :type event: Any
        :param kwargs: The merged execution keyword arguments.
        :type kwargs: Dict[str, Any]
        :param next_fn: Zero-argument callable that invokes the remainder of
            the chain.  In async execution contexts this is a coroutine function
            and must be awaited.
        :type next_fn: Callable[[], Any]
        :return: The result of the event execution.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError()
