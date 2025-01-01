# *** imports

# ** core
import json

# *** exceptions

# ** exceptions (class): tiferet_error
class TiferetError(Exception):
    '''
    A base exception for Tiferet.
    '''

    def __init__(self, error_code: str, message: str):
        '''
        Initialize the exception.
        :param message: The message.
        :type message: str
        '''

        # Set the message.
        self.error_code = error_code
        super().__init__(
            json.dumps(dict(
                error_code=error_code,
                message=message
            ))
        )
