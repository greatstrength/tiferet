"""Tiferet Error Contexts"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .base import BaseContext
from .cache import CacheContext
from ..domain import Error

# *** contexts

# ** context: error_context
class ErrorContext(BaseContext):
    '''
    The error context formats structured error responses from loaded ``Error``
    domain objects. Error retrieval is owned by the application interface hub.
    '''

    # * attribute: domain_type
    domain_type = Error

    # * init
    def __init__(self, cache: CacheContext = None):
        '''
        Initialize the error context.

        :param cache: The shared cache context.
        :type cache: CacheContext
        '''

        # Initialize the shared cache via the base context.
        super().__init__(cache=cache)

    # * method: format_response
    def format_response(self, error: Error, exception: Exception, lang: str = 'en_US') -> Dict[str, Any]:
        '''
        Format a structured error response dictionary from a loaded error.

        :param error: The loaded error domain object.
        :type error: Error
        :param exception: The raised exception carrying format kwargs.
        :type exception: Exception
        :param lang: The language to use for the error message.
        :type lang: str
        :return: The formatted error response dictionary.
        :rtype: Dict[str, Any]
        '''

        # Extract any format kwargs carried by the exception.
        kwargs = getattr(exception, 'kwargs', {})

        # Format the localized message; return no response when none is found.
        error_message = error.format_message(lang, **kwargs)
        if not error_message:
            return None

        # Assemble and return the structured error response.
        return {
            'error_code': error.id,
            'name': error.name,
            'message': error_message,
            **kwargs,
        }
