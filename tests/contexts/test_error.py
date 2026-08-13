"""Tiferet Error Context Tests"""

# *** imports

# ** core
from typing import Callable

# ** infra
import pytest

# ** app
from tiferet.assets import (
    TiferetError,
    ERROR_NOT_FOUND_ID,
)
from tiferet.assets.error import CORE_DEFAULT_ERRORS
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.contexts.error import (
    ErrorContext,
    add_default_errors,
    ERROR_CACHE_PREFIX,
)
from tiferet.domain import Error

# *** fixtures

# ** fixture: sample_errors
@pytest.fixture
def sample_errors() -> dict:
    '''
    Fixture providing a small subset of default error definitions for decorator tests.

    :return: A mapping of error-code ID to raw error definition dict.
    :rtype: dict
    '''

    # Return a representative slice of the default error catalog.
    return {
        key: CORE_DEFAULT_ERRORS[key]
        for key in list(CORE_DEFAULT_ERRORS)[:3]
    }

# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder() -> Callable:
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Define a minimal cache-builder mirroring the unwrapped build_cache.
    def build_cache(cache: dict = None) -> CacheContext:
        return CacheContext(cache=cache)

    # Return the cache-builder.
    return build_cache

# ** fixture: error_context
@pytest.fixture
def error_context() -> ErrorContext:
    '''
    Fixture to create a new ErrorContext object.

    :return: An ErrorContext instance.
    :rtype: ErrorContext
    '''

    # Create an instance of ErrorContext (pure formatting; no collaborators needed).
    return ErrorContext()

# ** fixture: error
@pytest.fixture
def error() -> Error:
    '''
    Fixture to create a sample Error domain object.

    :return: The ERROR_NOT_FOUND error domain object.
    :rtype: Error
    '''

    # Build and return the ERROR_NOT_FOUND error.
    return Error(id=ERROR_NOT_FOUND_ID, **CORE_DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID))

# *** tests

# ** test: error_cache_prefix_value
def test_error_cache_prefix_value():
    '''
    Test that ERROR_CACHE_PREFIX is the expected namespace tuple.
    '''

    # Assert the prefix constant has the correct value.
    assert ERROR_CACHE_PREFIX == ('app', 'errors')

# ** test: add_default_errors_returns_callable
def test_add_default_errors_returns_callable(sample_errors: dict, base_cache_builder: Callable):
    '''
    Test that add_default_errors returns a decorator that produces a callable.

    :param sample_errors: A small sample of error definitions.
    :type sample_errors: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Apply the decorator to the cache-builder.
    wrapped = add_default_errors(sample_errors)(base_cache_builder)

    # Assert the decorated builder is callable.
    assert callable(wrapped)

# ** test: add_default_errors_seeds_cache_with_error_domain_objects
def test_add_default_errors_seeds_cache_with_error_domain_objects(sample_errors: dict, base_cache_builder: Callable):
    '''
    Test that the decorated builder stores Error domain objects in the cache.

    :param sample_errors: A small sample of error definitions.
    :type sample_errors: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_errors(sample_errors)(base_cache_builder)
    cache = wrapped()

    # Assert each error ID maps to an Error domain object in the error namespace.
    for error_id in sample_errors:
        cached = cache.get(error_id, *ERROR_CACHE_PREFIX)
        assert isinstance(cached, Error)
        assert cached.id == error_id

# ** test: add_default_errors_preserves_initial_cache_values
def test_add_default_errors_preserves_initial_cache_values(sample_errors: dict, base_cache_builder: Callable):
    '''
    Test that pre-seeded errors do not overwrite an initial cache dict.

    :param sample_errors: A small sample of error definitions.
    :type sample_errors: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke it with a pre-populated initial dict.
    wrapped = add_default_errors(sample_errors)(base_cache_builder)
    cache = wrapped(cache={'existing_key': 'existing_value'})

    # Assert the pre-existing root-namespace entry is still accessible.
    assert cache.get('existing_key') == 'existing_value'

    # Assert the error entries are also present in the error namespace.
    for error_id in sample_errors:
        assert isinstance(cache.get(error_id, *ERROR_CACHE_PREFIX), Error)

# ** test: add_default_errors_empty_dict_leaves_cache_clean
def test_add_default_errors_empty_dict_leaves_cache_clean(base_cache_builder: Callable):
    '''
    Test that wrapping with an empty errors dict leaves the cache empty.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder with an empty errors dict and invoke it.
    wrapped = add_default_errors({})(base_cache_builder)
    cache = wrapped()

    # Assert neither the root namespace nor the error namespace holds any entries.
    assert cache.get_by_prefix() == {}
    assert cache.get_by_prefix(*ERROR_CACHE_PREFIX) == {}

# ** test: error_context_format_response
def test_error_context_format_response(error_context: ErrorContext, error: Error):
    '''
    Test formatting a structured error response from a loaded error.

    :param error_context: The error context to test.
    :type error_context: ErrorContext
    :param error: The sample error domain object.
    :type error: Error
    '''

    # Build a TiferetError carrying format kwargs.
    exception = TiferetError(ERROR_NOT_FOUND_ID, id='NON_EXISTENT_ERROR')

    # Format the response.
    response = error_context.format_response(error, exception, lang='en_US')

    # Assert the response is a dict with the expected, formatted data.
    assert isinstance(response, dict)
    assert response.get('error_code') == ERROR_NOT_FOUND_ID
    assert response.get('name') == 'Error Not Found'
    assert 'Error not found: NON_EXISTENT_ERROR.' in response.get('message', '')
    assert response.get('id') == 'NON_EXISTENT_ERROR'

# ** test: error_context_format_response_default_lang
def test_error_context_format_response_default_lang(error_context: ErrorContext, error: Error):
    '''
    Test that format_response defaults to en_US and uses the exception kwargs.

    :param error_context: The error context to test.
    :type error_context: ErrorContext
    :param error: The sample error domain object.
    :type error: Error
    '''

    # Build a TiferetError with the required id kwarg.
    exception = TiferetError(ERROR_NOT_FOUND_ID, id='SOME_ID')

    # Format the response without specifying a language.
    response = error_context.format_response(error, exception)

    # Assert the formatted message uses the default language.
    assert response.get('error_code') == ERROR_NOT_FOUND_ID
    assert 'Error not found: SOME_ID.' in response.get('message', '')

# ** test: error_context_format_response_no_message
def test_error_context_format_response_no_message(error_context: ErrorContext, error: Error):
    '''
    Test that format_response returns None when no message matches the language.

    :param error_context: The error context to test.
    :type error_context: ErrorContext
    :param error: The sample error domain object.
    :type error: Error
    '''

    # Build a TiferetError carrying format kwargs.
    exception = TiferetError(ERROR_NOT_FOUND_ID, id='SOME_ID')

    # Format the response for a language with no registered message.
    response = error_context.format_response(error, exception, lang='fr_FR')

    # Assert no response is produced.
    assert response is None

# ** test: error_context_domain_type
def test_error_context_domain_type():
    '''
    Test that ErrorContext declares Error as its domain type.
    '''

    # Assert the domain type ClassVar is the Error domain object.
    assert ErrorContext.domain_type is Error

# ** test: error_context_registered_for_error_domain
def test_error_context_registered_for_error_domain():
    '''
    Test that ErrorContext is the context registered for the Error domain type.
    '''

    # Assert the registry resolves ErrorContext for the Error domain type.
    assert BaseContext.for_domain(Error) is ErrorContext
