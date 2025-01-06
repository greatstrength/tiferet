# *** imports

# ** app
from ..configs import *


# *** commands

# ** command: service_command
class ServiceCommand(object):
    '''
    A service command class.
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
    def verify(self, expression: bool, error_code: str, message: str, *args):
        '''
        Verify an expression and raise an error if it is false.

        :param expression: The expression to verify.
        :type expression: bool
        :param error_code: The error code.
        :type error_code: str
        :param args: Additional error arguments.
        :type args: tuple
        '''

        # Format the error message.
        if args:
            message = '{}: {}'.format(message, ', '.join(args))

        # Verify the expression.
        try:
            assert expression
        except AssertionError:
            raise TiferetError(
                message=message,
                error_code=error_code,
            )