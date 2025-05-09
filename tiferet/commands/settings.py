# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..configs import TiferetError


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
    

    # * method: verify
    def verify(self, expression: bool, error_code: str, *args):
        '''
        Verify an expression and raise an error if it is false.

        :param expression: The expression to verify.
        :type expression: bool
        :param error_code: The error code.
        :type error_code: str
        :param args: Additional error arguments.
        :type args: tuple
        '''

        # Verify the expression.
        try:
            assert expression
        except AssertionError:
            TiferetError(
                error_code,
                *args
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
