# *** imports

# ** infra
import pytest

# ** app
from ..error import *
from ...configs.tests.test_error import *


# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    return ModelObject.new(
        ErrorMessage,
        **TEST_ERROR_MESSAGE
    )


# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    return ModelObject.new(
        ErrorMessage,
        **TEST_FORMATTED_ERROR_MESSAGE
    )


# ** fixture: error
@pytest.fixture
def error() -> Error:
    return ModelObject.new(
        Error,
        **TEST_ERROR,
    )


# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message() -> Error:
    return ValueObject.new(
        Error,
        **TEST_ERROR_WITH_FORMATTED_MESSAGE
    )


# ** fixture: error_context 
@pytest.fixture
def error_context(error, error_with_formatted_message):
    return ErrorContext(
        errors=[
            error,
            error_with_formatted_message
        ]
    )


# *** tests

# ** test: test_format_error_response_error_not_found
def test_handle_error_error_not_found(error_context):

    # Create an exception using an unknown error code.
    exception = TiferetError(
        error_code='UNKNOWN_ERROR'
    )

    # Test handling an error and raising an exception
    with pytest.raises(TiferetError) as excinfo:
        error_context.handle_error(
            exception, 
            lang='en_US'
        )

    # Check that the error code is correct.
    assert excinfo.value.error_code == 'ERROR_NOT_FOUND'
    assert 'Error not found: UNKNOWN_ERROR.' in str(excinfo.value)


# ** test: test_format_error_response_with_args
def test_format_error_response(error_context, error, error_with_formatted_message):

    # Test formatting an error response with no arguments.
    message = error_context.format_error_response(error, lang='en_US')

    # Check if the error message is correctly formatted
    assert message['error_code'] == 'TEST_ERROR'
    assert message['message'] == 'An error occurred.'

    # Test formatting an error response with arguments
    formatted_message = error_context.format_error_response(error_with_formatted_message, lang='en_US', error_data=['This is the error.'])

    # Check if the error message is correctly formatted
    assert formatted_message['error_code'] == 'TEST_FORMATTED_ERROR'
    assert formatted_message['message'] == 'An error occurred: This is the error.'


# ** test: test_handle_error_raise_exception
def test_handle_error_raise_exception(error_context):

    # Create an exception using an unknown error code.
    exception = Exception('An error occurred.')

    # Test handling an error and raising an exception
    with pytest.raises(Exception):
        error_context.handle_error(
            exception, 
            lang='en_US'
        )


# ** test: test_handle_error_return_formatted_error_response
def test_handle_error_return_formatted_error_response(error_context):

    # Create Tiferet Error using a known error code.
    exception = TiferetError(
        'TEST_ERROR',
    )

    # Test handling an error and returning a formatted error response
    formatted_message = error_context.handle_error(
        exception, 
        lang='en_US'
    )

    # Check if the error message is correctly formatted
    assert formatted_message['error_code'] == 'TEST_ERROR'
    assert formatted_message['message'] == 'An error occurred.'


# ** test: test_handle_error_raise_exception
def test_handle_error_raise_tiferet_error_exception(error_context):

    # Create an exception using an unknown error code.
    exception = TiferetError(
        'ERROR_NOT_FOUND'
    )

    # Test handling an error and raising an exception
    with pytest.raises(TiferetError) as excinfo:
        error_context.handle_error(
            exception, 
            lang='en_US'
        )

    # Check if the error message is correctly formatted
    assert excinfo.value.error_code == 'ERROR_NOT_FOUND'
    assert 'Error not found: ERROR_NOT_FOUND.' in str(excinfo.value)