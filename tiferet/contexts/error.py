"""Tiferet Error Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict, Tuple

# ** app
from .core import BaseContext, add_default_cache_items
from ..assets import TiferetError
from ..domain import Error

# *** constants

# ** constant: error_cache_prefix
ERROR_CACHE_PREFIX: Tuple[str, ...] = ('app', 'errors')

# *** functions

# ** function: add_default_errors
def add_default_errors(errors: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default error domain objects.

    :param errors: A mapping of error-code IDs to raw error definition dicts.
    :type errors: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Delegate to the shared cache-seeding factory.
    return add_default_cache_items(errors, ERROR_CACHE_PREFIX, model=Error, id_field='id')

# *** contexts

# ** context: error_context
class ErrorContext(BaseContext):
    '''
    The error context formats structured error responses from loaded ``Error``
    domain objects. Error retrieval is owned by the application session hub.
    '''

    # * attribute: domain_type
    domain_type = Error

    # * method: format_response
    def format_response(self, error: Error, exception: TiferetError, lang: str = 'en_US') -> Dict[str, Any]:
        '''
        Format a structured error response dictionary from a loaded error.

        :param error: The loaded error domain object.
        :type error: Error
        :param exception: The raised Tiferet error carrying format kwargs.
        :type exception: TiferetError
        :param lang: The language to use for the error message.
        :type lang: str
        :return: The formatted error response dictionary.
        :rtype: Dict[str, Any]
        '''

        # Extract the format kwargs carried by the exception.
        kwargs = exception.kwargs

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
