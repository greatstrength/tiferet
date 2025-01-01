# *** imports

# ** core
import json

# *** exceptions

# ** exceptions (class): tiferet_error
class TiferetError(Exception):
    '''
    A base exception for Tiferet.
    '''

    def __init__(self, error_code: str, message: str, *args):
        '''
        Initialize the exception.
        :param message: The message.
        :type message: str
        '''

        # Set the error code and arguments.
        self.error_code = error_code
        self.args = args
        
        super().__init__(
            json.dumps(dict(
                error_code=error_code,
                message=message
            ))
        )
