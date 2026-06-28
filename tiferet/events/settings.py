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

        # Raise an error when the expression is falsy.
        if not expression:
            self.raise_error(
                error_code,
                message,
                **kwargs
            )

    # * method: _validate_required_parameters (static)
    @staticmethod
    def _validate_required_parameters(instance: 'DomainEvent', param_names: list, kwargs: dict):
        '''
        Validate that all required parameters are present and non-empty.

        Collects every missing, None, or blank-string parameter and raises a
        single aggregated COMMAND_PARAMETER_REQUIRED error if any are found.

        :param instance: The domain event instance being validated.
        :type instance: DomainEvent
        :param param_names: The list of required parameter names.
        :type param_names: list
        :param kwargs: The execution keyword arguments to validate.
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
    def _wrap_with_validation(param_names: list, method: Any) -> Any:
        '''
        Wrap an execute method with shared required-parameter validation.

        Returns an asynchronous wrapper when the method is a coroutine
        function, otherwise a synchronous wrapper; both validate the required
        parameters before invoking the wrapped method.

        :param param_names: The list of required parameter names.
        :type param_names: list
        :param method: The execute method to wrap.
        :type method: Any
        :return: The validation-wrapped method.
        :rtype: Any
        '''

        # Build an asynchronous wrapper when the method is a coroutine function.
        if asyncio.iscoroutinefunction(method):

            @functools.wraps(method)
            async def async_wrapper(self, *args, **kwargs):

                # Validate the required parameters before execution.
                DomainEvent._validate_required_parameters(self, param_names, kwargs)

                # Await the wrapped coroutine method.
                return await method(self, *args, **kwargs)

            return async_wrapper

        # Otherwise build a synchronous wrapper.
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):

            # Validate the required parameters before execution.
            DomainEvent._validate_required_parameters(self, param_names, kwargs)

            # Call the wrapped method.
            return method(self, *args, **kwargs)

        return wrapper

    # * method: parameters_required (static)
    @staticmethod
    def parameters_required(param_names: list):
        '''
        Declarative parameter validator decorator.

        Delegates to the shared validation helpers, transparently wrapping both
        synchronous and asynchronous execute methods so that any missing, None,
        or blank-string parameter raises a single aggregated TiferetError.

        :param param_names: The list of required parameter names.
        :type param_names: list
        :return: The decorator function.
        :rtype: callable
        '''

        # Delegate to the shared validation wrapper bound to the parameter names.
        return functools.partial(DomainEvent._wrap_with_validation, param_names)

    # * method: _run_base (static)
    @staticmethod
    def _run_base(event_handler: 'DomainEvent', kwargs: dict) -> Any:
        '''
        Execute the event handler as the innermost base of the chain.

        :param event_handler: The instantiated domain event.
        :type event_handler: DomainEvent
        :param kwargs: The execution keyword arguments.
        :type kwargs: dict
        :return: The result of the event execution.
        :rtype: Any
        '''

        # Execute the event handler with the given keyword arguments.
        return event_handler.execute(**kwargs)

    # * method: _run_middleware (static)
    @staticmethod
    def _run_middleware(mw: Any, event_handler: 'DomainEvent', kwargs: dict, next_fn: Any) -> Any:
        '''
        Invoke a single synchronous middleware in the chain.

        :param mw: The middleware callable.
        :type mw: Any
        :param event_handler: The instantiated domain event.
        :type event_handler: DomainEvent
        :param kwargs: The execution keyword arguments.
        :type kwargs: dict
        :param next_fn: The callable invoking the remainder of the chain.
        :type next_fn: Any
        :return: The result of the middleware execution.
        :rtype: Any
        '''

        # Invoke the middleware with the event, kwargs, and next callable.
        return mw(event_handler, kwargs, next_fn)

    # * method: handle (static)
    @staticmethod
    def handle(
            event_cls: type,
            dependencies: Dict[str, Any] = {},
            middleware: list = None,
            **kwargs) -> Any:
        '''
        Handle a domain event instance via the instantiate-execute pattern,
        optionally composing an ordered synchronous middleware chain.

        :param event_cls: The domain event class to handle.
        :type event_cls: type
        :param dependencies: The event dependencies.
        :type dependencies: Dict[str, Any]
        :param middleware: The ordered, outermost-first middleware callables.
        :type middleware: list
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the event.
        :rtype: Any
        '''

        # Instantiate the event with its dependencies.
        event_handler = event_cls(**dependencies)

        # Build the base callable bound to the handler and kwargs.
        base = functools.partial(DomainEvent._run_base, event_handler, kwargs)

        # Return the base result directly when no middleware is provided.
        if not middleware:
            return base()

        # Compose the middleware chain outermost-first.
        chain = base
        for mw in reversed(middleware):
            chain = functools.partial(DomainEvent._run_middleware, mw, event_handler, kwargs, chain)

        # Execute the composed chain.
        return chain()

    # * method: _run_base_async (static)
    @staticmethod
    async def _run_base_async(event_handler: 'DomainEvent', kwargs: dict) -> Any:
        '''
        Await the event handler as the innermost base of the async chain.

        :param event_handler: The instantiated domain event.
        :type event_handler: DomainEvent
        :param kwargs: The execution keyword arguments.
        :type kwargs: dict
        :return: The result of the event execution.
        :rtype: Any
        '''

        # Await the event handler execution with the given keyword arguments.
        return await event_handler.execute(**kwargs)

    # * method: _run_middleware_async (static)
    @staticmethod
    async def _run_middleware_async(mw: Any, event_handler: 'DomainEvent', kwargs: dict, next_fn: Any) -> Any:
        '''
        Invoke a single middleware in the asynchronous chain, awaiting any
        coroutine result so that async and sync middleware compose alike.

        :param mw: The middleware callable.
        :type mw: Any
        :param event_handler: The instantiated domain event.
        :type event_handler: DomainEvent
        :param kwargs: The execution keyword arguments.
        :type kwargs: dict
        :param next_fn: The coroutine callable invoking the remainder of the chain.
        :type next_fn: Any
        :return: The result of the middleware execution.
        :rtype: Any
        '''

        # Invoke the middleware with the event, kwargs, and next callable.
        result = mw(event_handler, kwargs, next_fn)

        # Await the result when the middleware returns a coroutine.
        if asyncio.iscoroutine(result):
            return await result

        # Return the synchronous result.
        return result

    # * method: handle_async (static)
    @staticmethod
    async def handle_async(
            event_cls: type,
            dependencies: Dict[str, Any] = {},
            middleware: list = None,
            **kwargs) -> Any:
        '''
        Handle a domain event asynchronously via the instantiate-execute
        pattern, optionally composing an ordered async middleware chain.

        Async middleware must ``await next_fn()``; synchronous middleware may
        call ``next_fn()`` but will receive a coroutine it cannot inspect
        directly.

        :param event_cls: The domain event class to handle.
        :type event_cls: type
        :param dependencies: The event dependencies.
        :type dependencies: Dict[str, Any]
        :param middleware: The ordered, outermost-first middleware callables.
        :type middleware: list
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the event.
        :rtype: Any
        '''

        # Instantiate the event with its dependencies.
        event_handler = event_cls(**dependencies)

        # Build the async base callable bound to the handler and kwargs.
        base = functools.partial(DomainEvent._run_base_async, event_handler, kwargs)

        # Await the base result directly when no middleware is provided.
        if not middleware:
            return await base()

        # Compose the async middleware chain outermost-first.
        chain = base
        for mw in reversed(middleware):
            chain = functools.partial(DomainEvent._run_middleware_async, mw, event_handler, kwargs, chain)

        # Await the composed chain.
        return await chain()

# ** class: async_domain_event
class AsyncDomainEvent(DomainEvent):
    '''
    A base class for an asynchronous domain event object.

    Extends ``DomainEvent`` with an async ``execute``. Inherits ``verify``,
    ``raise_error`` and ``parameters_required`` unchanged - the synchronous
    exception-raisers operate correctly in an async context.
    '''

    # * method: execute
    async def execute(self, **kwargs) -> Any:
        '''
        Execute the asynchronous domain event.

        :param kwargs: The event arguments.
        :type kwargs: dict
        :return: The event result.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError()
