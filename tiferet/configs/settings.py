# *** imports

# ** core
import json


# *** classes


# ** class: tiferet_error
class TiferetError(Exception):
    '''
    A base exception for Tiferet.
    '''

    def __init__(self, error_code: str, message: str = None, *args):
        '''
        Initialize the exception.
        
        :param error_code: The error code.
        :type error_code: str
        :param message: An optional error message for internal exception handling.
        :type message: str
        :param args: Additional arguments for the error message.
        :type args: tuple
        '''

        # Set the error code and arguments.
        self.error_code = error_code

        # Initialize base exception with error data.
        super().__init__(
            json.dumps(dict(
                error_code=error_code,
                message=message,
            )), *args
        )