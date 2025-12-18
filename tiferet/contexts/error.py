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
from ..configs.error import ERRORS
from ..models.error import Error
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

    # * attribute: cache
    cache: CacheContext

    # * method: init
    def __init__(self, get_error_cmd: GetError, cache: CacheContext = None):
        '''
        Initialize the error context.

        :param error_service: The error service to use for handling errors.
        :type error_service: ErrorService
        :param cache: The cache context to use for caching error data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.get_error_handler = get_error_cmd.execute
        self.cache = cache if cache else CacheContext()

        # Load errors into the cache.
        # - obsolete with on-demand loading.
        self.load_errors()

    # * method: load_errors
    def load_errors(self):
        '''
        Load errors from the error service.

        :return: The list of loaded errors.
        :rtype: List[Error]
        '''

        # Load temporary configured errors and add them to the cache.
        configured_errors = [Error.new(**error_data) for error_data in ERRORS]

        # Add the configured errors to the cache.
        error_map: dict = self.cache.get('error_map')

        # Add configured errors to the error map if not already present.
        if not error_map:
            error_map = {error.id: error for error in configured_errors}

        # Update the cache with the error map.
        self.cache.set('error_map', error_map)
    
    # * method: get_error_by_code
    def get_error_by_code(self, error_code: str) -> Error:
        '''
        Get an error by its code.

        :param error_code: The error code to retrieve.
        :type error_code: str
        :return: The error object.
        :rtype: Error
        '''

        # Check to see if there is an error map in the cache.
        error_map: dict = self.cache.get('error_map')

        # Pull the error code from the error map if it exists.
        error = error_map.get(error_code)

        # If the error does not exist in the map, attempt to load it using the get_error_handler.
        if not error:
            error = self.get_error_handler(error_code, include_defaults=True)

        # If the error was not found, raise an API error with the error not found details.
        if not error:

            # Retrieve and raise the "error not found" error to use its details.
            error = Error.new(**DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID))
            raise TiferetAPIError(
                error_code=ERROR_NOT_FOUND_ID,
                name=error.name,
                message=error.format_message(
                    'en_US',
                    id=error_code
                ),
                id=error_code
            )
        
        # Add the error to the error map and update the cache.
        error_map[error_code] = error
        self.cache.set('error_map', error_map)

        # Return the error object from the error map.
        return error_map.get(error_code)

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
        raise TiferetAPIError(
            error_code=error.error_code,
            name=error.name,
            message=error_message,
            **exception.kwargs if hasattr(exception, 'kwargs') else {}
        )
