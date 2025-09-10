# *** imports

# ** app
from ..commands import Command

# *** classes

# ** class: service_handler
class ServiceHandler(object):
    '''
    A base class for a service handler object.
    '''

    # * method: raise_error
    def raise_error(self, error_code: str, message: str = None, *args):
        '''
        Raise an error with the given error code and arguments.

        :param error_code: The error code.
        :type error_code: str
        :param message: The error message.
        :type message: str
        :param args: Additional error arguments.
        :type args: tuple
        '''

        # Use the Command class to raise the error.
        Command.raise_error(
            error_code,
            message,
            *args
        )