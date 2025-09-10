# *** imports

# ** app
from ..commands import raise_error

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

        # Use the raise_error command class to raise the error.
        raise_error.execute(
            error_code,
            message,
            *args
        )