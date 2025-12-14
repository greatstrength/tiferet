"""Tiferet Exceptions (Assets)"""

# *** imports
from typing import Dict, Any
import json

# *** exceptions

# ** exception: tiferet_error
class TiferetError(Exception):
    '''
    A base exception for handling internal errors in Tiferet.
    '''

    # * attribute: error_code
    error_code: str

    # * attribute: kwargs
    kwargs: Dict[str, Any]

    def __init__(self, error_code: str, message: str = None, **kwargs):
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
        self.kwargs = kwargs

        # Initialize base exception with error data.
        super().__init__(
            json.dumps(dict(
                error_code=error_code,
                message=message,
                **kwargs
            ))
        )