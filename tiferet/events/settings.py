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
    
    # * method: raise_error
    @staticmethod
    def raise_error(error_code: str, message: str = None, **kwargs):
        '''
        Raise an error with the given error code and arguments.

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
        Decorator to require one or more named parameters in **kwargs.

        Validates all named parameters and raises a single TiferetError
        with COMMAND_PARAMETER_REQUIRED_ID listing all missing or invalid
        parameters if any fail validation.

        A parameter is invalid if it is missing from kwargs, is None, or
        is an empty string (after strip). Non-string falsy values (0, [],
        {}, False) are considered valid.

        :param param_names: The list of parameter names to require.
        :type param_names: list

        Usage::

            @DomainEvent.parameters_required(['id', 'name'])
            def execute(self, id: str, name: str, **kwargs) -> Any:
                ...
        '''

        def decorator(method):
            def wrapper(self, *args, **kwargs):

                # Collect all missing or invalid parameters.
                missing = []
                for name in param_names:
                    value = kwargs.get(name)
                    is_valid = (
                        value is not None
                        and (not isinstance(value, str) or bool(value.strip()))
                    )
                    if not is_valid:
                        missing.append(name)

                # Raise a single error if any parameters are missing.
                if missing:
                    self.raise_error(
                        a.const.COMMAND_PARAMETER_REQUIRED_ID,
                        f'Required parameter(s) {missing} missing for the "{self.__class__.__name__}" command.',
                        parameters=missing,
                        command=self.__class__.__name__,
                    )

                # Proceed with original method.
                return method(self, *args, **kwargs)

            return wrapper
        return decorator

    # * method: handle
    @staticmethod
    def handle(
            command: type,
            dependencies: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Handle a domain event instance.

        :param command: The domain event class to handle.
        :type command: type
        :param dependencies: The event dependencies.
        :type dependencies: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the event.
        :rtype: Any
        '''

        # Get the command handler.
        command_handler = command(**dependencies)

        # Execute the command handler.
        result = command_handler.execute(**kwargs)
        return result
