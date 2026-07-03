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
from tiferet.contexts.error import ErrorContext
from tiferet.domain import Error

# *** fixtures

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
