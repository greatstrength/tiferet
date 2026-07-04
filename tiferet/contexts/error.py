"""Tiferet Error Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from .base import BaseContext
from .cache import CacheContext
from ..domain import Error

# *** functions

# ** function: add_default_errors
def add_default_errors(errors: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default error domain objects.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each entry in ``errors`` is reconstituted into an ``Error`` domain object
    and stored in the cache under its error-code key.

    :param errors: A mapping of error-code IDs to raw error definition dicts.
    :type errors: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default error domain objects.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw error dict into an Error domain object and cache it.
            for error_id, error_data in errors.items():
                cache.set(error_id, Error.model_validate(error_data))

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

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
