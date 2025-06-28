# *** imports

# ** core
from typing import Any, Tuple, List

# ** app
from .cache import CacheContext
from ..configs.error import ERRORS
from ..handlers.error import ErrorService
from ..models.error import Error, ModelObject
from ..commands import raise_error, TiferetError


# *** contexts

# ** context: error_context
class ErrorContext(object):
    '''
    The error context object.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * attribute: cache
    cache: CacheContext

    # * method: init
    def __init__(self, error_service: ErrorService, cache: CacheContext = None):
        '''
        Initialize the error context.

        :param error_service: The error service to use for handling errors.
        :type error_service: ErrorService
        :param cache: The cache context to use for caching error data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.error_service = error_service
        self.cache = cache if cache else CacheContext()

    # * method: load_errors
    def load_errors(self) -> List[Error]:
        '''
        Load errors from the error service.

        :return: The list of loaded errors.
        :rtype: List[Error]
        '''

        # Convert configured errors to a list of error objects.
        configured_errors = [
            ModelObject.new(
                Error,
                **error_data
        ) for error_data in ERRORS]

        # Load errors from the error service, including any configured errors.
        return self.error_service.load_errors(configured_errors)

    
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
        error_map = self.cache.get('error_map')

        # If there is no error map or the error code does not exist in the map,
        # we need to load the errors from the error service and create a new error map.
        # This is to ensure that we always have the latest errors available.
        if not error_map or not error_map.get(error_code):
            errors = self.load_errors()
            error_map = {error.error_code: error for error in errors}
            self.cache.set('error_map', error_map)

        # Raise an error if the error code does not exist in the error map.
        if not error_map or error_code not in error_map:
            raise_error.execute(
                'ERROR_NOT_FOUND', 
                f'Error not found: {error_code}.',
                error_code
            )

        # Return the error object from the error map.
        return error_map.get(error_code)

    # * method: handle_error
    def handle_error(self, exception: TiferetError, lang: str = 'en_US', **kwargs) -> Tuple[bool, Any]:
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
        if not isinstance(exception, TiferetError):
            raise exception

        # Get the error by its code from the error service.
        error = self.get_error_by_code(exception.error_code)
        
        # Format the error response.
        error_response = error.format_response(
            lang,
            *exception.args[1:],
            **kwargs
        )

        # Return the error response.
        return error_response
