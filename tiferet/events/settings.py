"""Tiferet Events Settings"""

# *** imports

# ** core
import asyncio
import functools
from typing import Dict, Any

# ** app
from ..assets import TiferetError
from .. import assets as a

# *** classes

# ** class: domain_event
class DomainEvent(object):
    '''
    A base class for a domain event object.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Any:
        '''
        Execute the domain event.

        :param kwargs: The event arguments.
        :type kwargs: dict
        :return: The event result.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError()

    # * method: raise_error (static)
    @staticmethod
    def raise_error(error_code: str, message: str = None, **kwargs):
        '''
        Raise a structured TiferetError.

        :param error_code: The error code.
        :type error_code: str
        :param message: The error message.
        :type message: str
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Raise the TiferetError with the given error code and arguments.
        raise TiferetError(
            error_code,
            message,
            **kwargs
        )

    # * method: verify
    def verify(self, expression: bool, error_code: str, message: str = None, **kwargs):
        '''
        Verify an expression and raise an error if it is false.

        :param expression: The expression to verify.
        :type expression: bool
        :param error_code: The error code.
        :type error_code: str
        :param message: The error message.
        :type message: str
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Raise a structured error when the expression is falsy.
        if not expression:
            self.raise_error(
                error_code,
                message,
                **kwargs
            )

    # * method: _validate_required_parameters (static)
    @staticmethod
    def _validate_required_parameters(instance: Any, param_names: list, kwargs: dict):
        '''
        Validate that all required parameters are present and non-empty,
        raising a single aggregated TiferetError when any are missing.

        :param instance: The domain event instance being validated.
        :type instance: Any
        :param param_names: The list of required parameter names.
        :type param_names: list
        :param kwargs: The keyword arguments supplied to the decorated method.
        :type kwargs: dict
        '''

        # Collect all missing or invalid parameters.
        missing = []
        for name in param_names:
            if name not in kwargs:
                missing.append(name)
                continue

            value = kwargs[name]

            # None is invalid.
            if value is None:
                missing.append(name)
                continue

            # Empty or whitespace-only strings are invalid.
            if isinstance(value, str) and not value.strip():
                missing.append(name)
                continue

        # Raise a single error with all violations if any found.
        if missing:
            DomainEvent.raise_error(
                a.const.COMMAND_PARAMETER_REQUIRED_ID,
                message=f'Required parameters missing for {instance.__class__.__name__}.',
                parameters=missing,
                command=instance.__class__.__name__,
            )

    # * method: _wrap_with_validation (static)
    @staticmethod
    def _wrap_with_validation(param_names: list, method):
        '''
        Wrap a method with required-parameter validation, returning a sync or
        async wrapper that matches the decorated method.

        :param param_names: The list of required parameter names.
        :type param_names: list
        :param method: The method being decorated.
        :type method: callable
        :return: The validating wrapper function.
        :rtype: callable
        '''

        # Emit an async wrapper when the decorated method is a coroutine function.
        if asyncio.iscoroutinefunction(method):
            async def async_wrapper(self, *args, **kwargs):
                DomainEvent._validate_required_parameters(self, param_names, kwargs)
                return await method(self, *args, **kwargs)
            return async_wrapper

        # Otherwise emit a synchronous wrapper.
        def wrapper(self, *args, **kwargs):
            DomainEvent._validate_required_parameters(self, param_names, kwargs)
            return method(self, *args, **kwargs)

        return wrapper

    # * method: parameters_required (static)
    @staticmethod
    def parameters_required(param_names: list):
        '''
        Declarative parameter validator decorator.

        Inspects kwargs for required parameters and raises a single
        aggregated TiferetError if any are missing, None, or empty strings.

        :param param_names: The list of required parameter names.
        :type param_names: list
        :return: The decorator function.
        :rtype: callable
        '''

        # Return a decorator bound to the required parameter names.
        return functools.partial(DomainEvent._wrap_with_validation, param_names)

    # * method: _run_base (static)
    @staticmethod
    def _run_base(event_handler: Any, kwargs: dict) -> Any:
        '''
        Execute the event handler with the given keyword arguments.

        :param event_handler: The instantiated domain event.
        :type event_handler: Any
        :param kwargs: The event keyword arguments.
        :type kwargs: dict
        :return: The result of executing the event.
        :rtype: Any
        '''

        # Execute the event handler.
        return event_handler.execute(**kwargs)

    # * method: _run_middleware (static)
    @staticmethod
    def _run_middleware(mw: Any, event_handler: Any, kwargs: dict, next_fn: Any) -> Any:
        '''
        Invoke a single middleware callable around the next chain link.

        :param mw: The middleware callable receiving (event, kwargs, next_fn).
        :type mw: Any
        :param event_handler: The instantiated domain event.
        :type event_handler: Any
        :param kwargs: The event keyword arguments.
        :type kwargs: dict
        :param next_fn: The next callable in the middleware chain.
        :type next_fn: Any
        :return: The result of the middleware invocation.
        :rtype: Any
        '''

        # Invoke the middleware with the next chain link.
        return mw(event_handler, kwargs, next_fn)

    # * method: handle (static)
    @staticmethod
    def handle(
            event_cls: type,
            dependencies: Dict[str, Any] = {},
            middleware: list = None,
            **kwargs) -> Any:
        '''
        Handle a domain event instance via the instantiate-execute pattern.

        When ``middleware`` is provided, the event execution is wrapped in an
        ordered middleware chain.  Each middleware callable receives
        ``(event, kwargs, next_fn)`` and must call ``next_fn()`` to continue.
        The first entry in the list is the outermost wrapper.

        :param event_cls: The domain event class to handle.
        :type event_cls: type
        :param dependencies: The event dependencies.
        :type dependencies: Dict[str, Any]
        :param middleware: Optional ordered list of middleware callables.
        :type middleware: list | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the event.
        :rtype: Any
        '''

        # Instantiate the event with its dependencies.
        event_handler = event_cls(**dependencies)

        # Build the base execution callable bound to the handler and kwargs.
        base = functools.partial(DomainEvent._run_base, event_handler, kwargs)

        # Return immediately when no middleware is configured.
        if not middleware:
            return base()

        # Compose the middleware chain (outermost = first in list).
        chain = base
        for mw in reversed(middleware):
            chain = functools.partial(DomainEvent._run_middleware, mw, event_handler, kwargs, chain)

        # Execute the composed chain.
        return chain()

    # * method: _run_base_async (static)
    @staticmethod
    async def _run_base_async(event_handler: Any, kwargs: dict) -> Any:
        '''
        Await the async event handler with the given keyword arguments.

        :param event_handler: The instantiated domain event.
        :type event_handler: Any
        :param kwargs: The event keyword arguments.
        :type kwargs: dict
        :return: The result of awaiting the event.
        :rtype: Any
        '''

        # Await the async event handler.
        return await event_handler.execute(**kwargs)

    # * method: _run_middleware_async (static)
    @staticmethod
    async def _run_middleware_async(mw: Any, event_handler: Any, kwargs: dict, next_fn: Any) -> Any:
        '''
        Invoke a middleware callable, awaiting the result when it is a coroutine
        (handles both async def functions and async def __call__ instances).

        :param mw: The middleware callable receiving (event, kwargs, next_fn).
        :type mw: Any
        :param event_handler: The instantiated domain event.
        :type event_handler: Any
        :param kwargs: The event keyword arguments.
        :type kwargs: dict
        :param next_fn: The next callable in the async middleware chain.
        :type next_fn: Any
        :return: The result of the middleware invocation.
        :rtype: Any
        '''

        # Invoke the middleware; await the result when it is a coroutine.
        result = mw(event_handler, kwargs, next_fn)
        if asyncio.iscoroutine(result):
            return await result
        return result

    # * method: handle_async (static)
    @staticmethod
    async def handle_async(
            event_cls: type,
            dependencies: Dict[str, Any] = {},
            middleware: list = None,
            **kwargs) -> Any:
        '''
        Handle an async domain event instance via the instantiate-await pattern.

        When ``middleware`` is provided, the event execution is wrapped in an
        ordered async middleware chain.  Each middleware callable receives
        ``(event, kwargs, next_fn)`` where ``next_fn`` is a coroutine function.
        Async middleware must ``await next_fn()``; sync middleware may call
        ``next_fn()`` but will receive a coroutine it cannot inspect directly.
        The first entry in the list is the outermost wrapper.

        :param event_cls: The domain event class to handle.
        :type event_cls: type
        :param dependencies: The event dependencies.
        :type dependencies: Dict[str, Any]
        :param middleware: Optional ordered list of middleware callables.
        :type middleware: list | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the event.
        :rtype: Any
        '''

        # Instantiate the event with its dependencies.
        event_handler = event_cls(**dependencies)

        # Build the base async execution callable bound to the handler and kwargs.
        base = functools.partial(DomainEvent._run_base_async, event_handler, kwargs)

        # Return immediately when no middleware is configured.
        if not middleware:
            return await base()

        # Compose the async middleware chain (outermost = first in list).
        chain = base
        for mw in reversed(middleware):
            chain = functools.partial(DomainEvent._run_middleware_async, mw, event_handler, kwargs, chain)

        # Execute the composed async chain.
        return await chain()


# ** class: async_domain_event
class AsyncDomainEvent(DomainEvent):
    '''
    A base class for an async domain event object.

    Extends :class:`DomainEvent` with an async ``execute`` method.
    Inherits ``verify``, ``raise_error``, and ``parameters_required``
    unchanged — synchronous exception-raisers work correctly in async context.
    '''

    # * method: execute
    async def execute(self, **kwargs) -> Any:
        '''
        Execute the async domain event.

        :param kwargs: The event arguments.
        :type kwargs: dict
        :return: The event result.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError()
