# *** imports

# ** core
from typing import Any, Callable

# ** app
from .cache import CacheContext
from ..assets import (
    TiferetError, 
    TiferetAPIError,
    ERROR_NOT_FOUND_ID,
    DEFAULT_ERRORS
)
from ..models import Error
from ..commands.error import GetError
from ..configs import TiferetError as LegacyTiferetError

# *** contexts

# ** context: error_context
class ErrorContext(object):
    '''
    The error context object.
    '''

    # * attribute: error_service
    get_error_handler: Callable

    # * method: init
    def __init__(self, get_error_cmd: GetError):
        '''
        Initialize the error context.

        :param get_error_cmd: The command to get an error by id.
        :type get_error_cmd: GetError
        :param cache: The cache context to use for caching error data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.get_error_handler = get_error_cmd.execute
    
    # * method: get_error_by_code
    def get_error_by_code(self, error_code: str) -> Error:
        '''
        Get an error by its code.

        :param error_code: The error code to retrieve.
        :type error_code: str
        :return: The error object.
        :rtype: Error
        '''

        # Try to retrieve the error by its code.
        try:
            return self.get_error_handler(error_code, include_defaults=True)
        
        # If the error is not found, raise the "error not found" error.
        except TiferetError:
            
            # Retrieve and raise the "error not found" error to use its details.
            error: Error = Error.new(**DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID))
            raise TiferetAPIError(
                **error.format_response(),
                id=error_code
            )
        
        # Return the retrieved error.
        return error

    # * method: handle_error
    def handle_error(self, exception: TiferetError | LegacyTiferetError, lang: str = 'en_US') -> Any:
        '''
        Handle an error.

        :param exception: The exception to handle.
        :type exception: Exception
        :param lang: The language to use for the error message.
        :type lang: str
        :return: Whether the error was handled.
        :rtype: bool
        '''

        # Raise the exception if it is not a Tiferet error.
        if not isinstance(exception, (TiferetError, LegacyTiferetError)):
            raise exception

        # Get the error by its code from the error service.
        error = self.get_error_by_code(exception.error_code)
        
        # Format the error response.
        if isinstance(exception, LegacyTiferetError):
            error_message = error.format_message(
                lang,
                *exception.args
            )
        else:
            error_message = error.format_message(
                lang,
                **exception.kwargs
            )

        # Raise a new TiferetAPIError with the formatted error message.
        raise TiferetAPIError(**error.format_response(lang=lang, **exception.kwargs))
