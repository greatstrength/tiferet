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

        # Format and return the structured response using the exception kwargs.
        return error.format_response(lang=lang, **getattr(exception, 'kwargs', {}))
