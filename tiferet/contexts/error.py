"""Tiferet Error Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from .settings import BaseContext
from .cache import CacheContext
from ..assets import TiferetError
from ..domain import Error

# *** constants

# ** constant: error_cache_key_prefix
ERROR_CACHE_KEY_PREFIX = 'error_'

# *** functions

# ** function: error_cache_key
def error_cache_key(error_code: str) -> str:
    '''
    Compose the shared-cache key for an error code.

    :param error_code: The error code to key.
    :type error_code: str
    :return: The prefixed cache key.
    :rtype: str
    '''

    # Prefix the error code to namespace it within the shared cache.
    return f'{ERROR_CACHE_KEY_PREFIX}{error_code}'

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

            # Reconstitute each raw error dict into an Error domain object and
            # cache it under its prefixed cache key.
            for error_id, error_data in errors.items():
                cache.set(error_cache_key(error_id), Error.model_validate(error_data))

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

        # Extract the format kwargs carried by the error.
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
