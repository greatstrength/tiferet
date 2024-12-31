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
    def execute(**kwargs) -> Any:
        '''
        Execute the service command.
        '''

        # Not implemented.
        raise NotImplementedError()
    

    # * method: verify
    def verify(self, expression: bool, error_code: str, *args):
        '''
        Verify an expression and raise an error if it is false.
        '''

        # Format the error message.
        message = error_code
        if args:
            message = '{}: {}'.format(message, ', '.join(args))

        # Verify the expression.
        assert expression, message