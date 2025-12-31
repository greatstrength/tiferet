# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..assets import TiferetError, constants as const

# *** classes

# ** class: command
class Command(object):
    '''
    A base class for an app command object.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Any:
        '''
        Execute the service command.
        
        :param kwargs: The command arguments.
        :type kwargs: dict
        :return: The command result.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError()

    # * method: raise_error
    def raise_error(self, error_code: str, message: str = None, **kwargs):
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

    # * method: verify_parameter
    def verify_parameter(self, parameter: Any, parameter_name: str, command_name: str):
        '''
        Verify that a command parameter is not null or empty.

        :param parameter: The parameter to verify.
        :type parameter: Any
        :param parameter_name: The name of the parameter.
        :type parameter_name: str
        :param command_name: The name of the command.
        :type command_name: str
        '''

        # Verify the parameter is not null or empty.
        self.verify(
            expression=parameter is not None and (not isinstance(parameter, str) or bool(parameter.strip())),
            error_code=const.COMMAND_PARAMETER_REQUIRED_ID,
            message=f'The "{parameter_name}" parameter is required for the "{command_name}" command.',
            parameter=parameter_name,
            command=command_name
        )

    # * method: handle
    @staticmethod
    def handle(
            command: type,
            dependencies: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Handle an app command instance.

        :param command: The command to handle.
        :type command: type
        :param dependencies: The command dependencies.
        :type dependencies: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the command.
        :rtype: Any
        '''

        # Get the command handler.
        command_handler = command(**dependencies)

        # Execute the command handler.
        result = command_handler.execute(**kwargs)
        return result