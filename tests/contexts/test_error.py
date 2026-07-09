"""Tiferet Error Context Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import (
    TiferetError,
    DEFAULT_ERRORS,
    ERROR_NOT_FOUND_ID,
)
from tiferet.contexts.cache import CacheContext
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

    :return: A dict of error-code ID to raw error definition dict.
    :rtype: dict
    '''

    # Return a representative slice of the default error catalog.
    return {
        k: DEFAULT_ERRORS[k]
        for k in list(DEFAULT_ERRORS)[:3]
    }


# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder():
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Return a minimal cache-builder that mirrors the unwrapped build_cache.
    def _build(cache=None):
        return CacheContext(cache=cache)

    return _build


# ** fixture: error_context
@pytest.fixture
def error_context() -> ErrorContext:
    '''
    Fixture to create a new ErrorContext object.

    :return: An ErrorContext instance.
    :rtype: ErrorContext
    '''

    # Create an instance of ErrorContext (pure formatting; no event needed).
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
    return Error(**DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID))

# *** tests

# ** test: add_default_errors_returns_callable
def test_add_default_errors_returns_callable(sample_errors, base_cache_builder):
    '''
    Test that add_default_errors returns a decorator that produces a callable.

    :param sample_errors: A small sample of error definitions.
    :type sample_errors: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Apply the decorator.
    wrapped = add_default_errors(sample_errors)(base_cache_builder)

    # Assert the result is callable.
    assert callable(wrapped)


# ** test: add_default_errors_seeds_cache_with_error_domain_objects
def test_add_default_errors_seeds_cache_with_error_domain_objects(sample_errors, base_cache_builder):
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
def test_add_default_errors_preserves_initial_cache_values(sample_errors, base_cache_builder):
    '''
    Test that pre-seeded errors do not overwrite an initial cache dict.

    :param sample_errors: A small sample of error definitions.
    :type sample_errors: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke with a pre-populated initial dict.
    wrapped = add_default_errors(sample_errors)(base_cache_builder)
    cache = wrapped(cache={'existing_key': 'existing_value'})

    # Assert the pre-existing root-namespace entry is still accessible.
    assert cache.get('existing_key') == 'existing_value'

    # Assert the error entries are also present in the error namespace.
    for error_id in sample_errors:
        assert isinstance(cache.get(error_id, *ERROR_CACHE_PREFIX), Error)


# ** test: add_default_errors_empty_dict_leaves_cache_clean
def test_add_default_errors_empty_dict_leaves_cache_clean(base_cache_builder):
    '''
    Test that wrapping with an empty errors dict results in an empty cache.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap with an empty errors dict.
    wrapped = add_default_errors({})(base_cache_builder)
    cache = wrapped()

    # Assert the cache contains no entries.
    assert cache._cache == {}


# ** test: error_cache_prefix_value
def test_error_cache_prefix_value():
    '''
    Test that ERROR_CACHE_PREFIX is the expected namespace tuple.
    '''

    # Assert the prefix constant has the correct value.
    assert ERROR_CACHE_PREFIX == ('app', 'errors')


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
    exception = TiferetError('ERROR_NOT_FOUND', id='NON_EXISTENT_ERROR')

    # Format the response.
    response = error_context.format_response(error, exception, lang='en_US')

    # Assert the response is a dict with the expected, formatted data.
    assert isinstance(response, dict)
    assert response.get('error_code') == 'ERROR_NOT_FOUND'
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
    exception = TiferetError('ERROR_NOT_FOUND', id='SOME_ID')

    # Format the response without specifying a language.
    response = error_context.format_response(error, exception)

    # Assert the formatted message uses the default language.
    assert response.get('error_code') == 'ERROR_NOT_FOUND'
    assert 'Error not found: SOME_ID.' in response.get('message', '')
