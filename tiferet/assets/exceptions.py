"""Tiferet Exceptions (Assets)"""

# *** imports

# ** core
from typing import Dict, Any
import json

# *** exceptions

# ** exception: tiferet_error
class TiferetError(Exception):
    '''
    The TiferetError is the base exception for all Tiferet-related errors.
    It extends the built-in Exception class.
    '''
    
    # * attribute: error_code
    error_code: str

    # * attribute
    kwargs: Dict[str, Any]

    # * init
    def __init__(self, error_code: str, message: str = None, **kwargs):
        '''
        Initialize the TiferetError with an error code, message, and additional arguments.

        :param error_code: The error code.
        :type error_code: str
        :param message: The error message.
        :type message: str
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Set the error code and additional arguments.
        self.error_code = error_code
        self.kwargs = kwargs

        # Initialize base exception with error data.
        super().__init__(
            json.dumps({
                'error_code': error_code,
                'message': message,
                **kwargs
            })
        )

# ** exception: tiferet_api_error
class TiferetAPIError(TiferetError):
    '''
    The TiferetAPIError is the exception returned for all Tiferet API-related errors by default.
    '''
    
    # * attribute: name
    name: str

    # * attribute: message
    message: str

    # * init
    def __init__(self, error_code: str, name: str,  message: str, **kwargs):
        '''
        Initialize the TiferetError with an error code, message, and additional arguments.

        :param error_code: The error code.
        :type error_code: str
        :param name: A descriptive name for the error.
        :type name: str
        :param message: The error message.
        :type message: str
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Set the name and the message.
        self.name = name
        self.message = message

        # Initialize base exception with error data.
        super().__init__(
            error_code=error_code,
            message=message,
            **kwargs
        )
