"""Tiferet Events Settings"""

# *** imports

# ** core
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

        # Verify the expression.
        try:
            assert expression
        except AssertionError:
            self.raise_error(
                error_code,
                message,
                **kwargs
            )

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

        def decorator(method):
            def wrapper(self, *args, **kwargs):

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
                        message=f'Required parameters missing for {self.__class__.__name__}.',
                        parameters=missing,
                        command=self.__class__.__name__,
                    )

                # Call the wrapped method.
                return method(self, *args, **kwargs)

            return wrapper

        return decorator

    # * method: handle (static)
    @staticmethod
    def handle(
            command: type,
            dependencies: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Handle a domain event instance via the instantiate-execute pattern.

        :param command: The domain event class to handle.
        :type command: type
        :param dependencies: The event dependencies.
        :type dependencies: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the event.
        :rtype: Any
        '''

        # Get the event handler.
        command_handler = command(**dependencies)

        # Execute the event handler.
        result = command_handler.execute(**kwargs)
        return result
