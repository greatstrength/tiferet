"""Tests for Tiferet Domain Error"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import DomainObject
from ..error import (
    Error,
    ErrorMessage,
)

# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    '''
    Fixture for a basic ErrorMessage instance.

    :return: The ErrorMessage instance.
    :rtype: ErrorMessage
    '''

    # Create and return a new ErrorMessage.
    return DomainObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred.',
    )

# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    '''
    Fixture for an ErrorMessage instance with a format placeholder.

    :return: The ErrorMessage instance.
    :rtype: ErrorMessage
    '''

    # Create and return a new ErrorMessage with a format placeholder.
    return DomainObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred: {error}',
    )

# ** fixture: error
@pytest.fixture
def error(error_message: ErrorMessage) -> Error:
    '''
    Fixture for an Error instance.

    :param error_message: The ErrorMessage fixture.
    :type error_message: ErrorMessage
    :return: The Error instance.
    :rtype: Error
    '''

    # Create and return a new Error via the custom factory.
    return Error.new(
        id='TEST_ERROR',
        name='Test Error',
        message=[error_message],
    )

# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message: ErrorMessage) -> Error:
    '''
    Fixture for an Error instance with a formatted message.

    :param formatted_error_message: The formatted ErrorMessage fixture.
    :type formatted_error_message: ErrorMessage
    :return: The Error instance.
    :rtype: Error
    '''

    # Create and return a new Error with a formatted message.
    return Error.new(
        id='TEST_FORMATTED_ERROR',
        name='Test Formatted Error',
        message=[formatted_error_message],
    )

# *** tests

# ** test: error_new
def test_error_new(error: Error) -> None:
    '''
    Test that Error.new() sets id, name, error_code, and message correctly.

    :param error: The Error fixture.
    :type error: Error
    '''

    # Assert the error fields are set correctly.
    assert error.id == 'TEST_ERROR'
    assert error.name == 'Test Error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0].lang == 'en_US'
    assert error.message[0].text == 'An error occurred.'

# ** test: error_message_format
def test_error_message_format(error_message: ErrorMessage, formatted_error_message: ErrorMessage) -> None:
    '''
    Test that ErrorMessage.format() returns raw text with no args and formatted text with kwargs.

    :param error_message: The basic ErrorMessage fixture.
    :type error_message: ErrorMessage
    :param formatted_error_message: The formatted ErrorMessage fixture.
    :type formatted_error_message: ErrorMessage
    '''

    # Assert raw text is returned with no arguments.
    assert error_message.format() == 'An error occurred.'

    # Assert formatted text is returned with kwargs.
    assert formatted_error_message.format(error='test failure') == 'An error occurred: test failure'

# ** test: error_format_method
def test_error_format_method(error: Error, error_with_formatted_message: Error) -> None:
    '''
    Test that Error.format_message() returns correct text with and without format arguments.

    :param error: The Error fixture.
    :type error: Error
    :param error_with_formatted_message: The Error with formatted message fixture.
    :type error_with_formatted_message: Error
    '''

    # Assert plain message formatting.
    assert error.format_message('en_US') == 'An error occurred.'

    # Assert formatted message with kwargs.
    assert error_with_formatted_message.format_message('en_US', error='test failure') == 'An error occurred: test failure'

# ** test: error_format_method_unsupported_lang
def test_error_format_method_unsupported_lang(error: Error) -> None:
    '''
    Test that Error.format_message() returns None for an unsupported language.

    :param error: The Error fixture.
    :type error: Error
    '''

    # Assert None is returned for unsupported language.
    assert error.format_message('fr_FR') is None

# ** test: error_format_response
def test_error_format_response(error: Error) -> None:
    '''
    Test that Error.format_response() returns a structured dict.

    :param error: The Error fixture.
    :type error: Error
    '''

    # Format the error response.
    response = error.format_response('en_US')

    # Assert the response structure.
    assert response['error_code'] == 'TEST_ERROR'
    assert response['name'] == 'Test Error'
    assert response['message'] == 'An error occurred.'

# ** test: error_format_response_unsupported_lang
def test_error_format_response_unsupported_lang(error: Error) -> None:
    '''
    Test that Error.format_response() returns None for an unsupported language.

    :param error: The Error fixture.
    :type error: Error
    '''

    # Assert None is returned for unsupported language.
    assert error.format_response('fr_FR') is None
