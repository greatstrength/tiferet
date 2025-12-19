"""Tiferet Error Models Tests"""

# *** imports 

# ** infra
import pytest

# ** app
from ..error import (
    ModelObject,
    Error,
    ErrorMessage
)

# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    '''
    Fixture to create a basic error message object.

    :return: The ErrorMessage instance.
    :rtype: ErrorMessage
    '''

    # Create the error message object.
    return ModelObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred.'
    )

# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    '''
    Fixture to create a formatted error message object.

    :return: The ErrorMessage instance.
    :rtype: ErrorMessage
    '''

    # Create the formatted error message object.
    return ModelObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred: {error}'
    )

# ** fixture: error
@pytest.fixture
def error(error_message: ErrorMessage) -> Error:
    '''
    Fixture to create a basic error object.

    :param error_message: The error message to associate with the error.
    :type error_message: ErrorMessage
    :return: The Error instance.
    :rtype: Error
    '''

    # Create the error object.
    return Error.new(
        id='TEST_ERROR',
        name='Test Error',
        message=[
            error_message
        ]
    )

# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message: ErrorMessage) -> Error:
    '''
    Fixture to create an error object with a formatted message.

    :param formatted_error_message: The formatted error message to associate with the error.
    :type formatted_error_message: ErrorMessage
    :return: The Error instance.
    :rtype: Error
    '''

    # Create the error object.
    return Error.new(
        id='TEST_FORMATTED_ERROR',
        name='Test Formatted Error',
        message=[
            formatted_error_message
        ]
    )

# *** tests

# ** test: error_new
def test_error_new(error: Error, error_message: ErrorMessage):
    '''
    Test creating a new error message object with raw message data.

    :param error: The error to test.
    :type error: Error
    :param error_message: The error message to test.
    :type error_message: ErrorMessage
    '''

    # Check if the error message object is correctly instantiated.
    assert error.id == 'TEST_ERROR'
    assert error.name == 'Test Error'
    assert len(error.message) == 1
    assert error.message[0] == error_message

# ** test: error_message_format
def test_error_message_format(
        error_message: ErrorMessage,
        formatted_error_message: ErrorMessage
    ):
    '''
    Test the format method of an error message.

    :param error_message: The basic error message to test.
    :type error_message: ErrorMessage
    :param formatted_error_message: The formatted error message to test.
    :type formatted_error_message: ErrorMessage
    '''

    # Test basic formatting
    assert error_message.format() == 'An error occurred.'
    # Test formatting with arguments
    assert formatted_error_message.format(error='Check for bugs.') == 'An error occurred: Check for bugs.'

# ** test: error_format_method
def test_error_format_method(
        error: Error,
        error_with_formatted_message: Error
    ):
    '''
    Test the format method of an error.

    :param error: The basic error to test.
    :type error: Error
    :param error_with_formatted_message: The error with a formatted message to test.
    :type error_with_formatted_message: Error
    '''

    # Test formatting with arguments
    assert error.format_message('en_US') == 'An error occurred.'

    # Test formatting with arguments
    assert error_with_formatted_message.format_message('en_US', error='Check for bugs.') == 'An error occurred: Check for bugs.'

# ** test: error_format_method_unsupported_lang
def test_error_format_method_unsupported_lang(error: Error):
    '''
    Test the format method of an error with an unsupported language.

    :param error: The basic error to test.
    :type error: Error
    '''

    # Test formatting with unsupported language
    assert error.format_message('fr_FR') == None

# ** test: error_format_response
def test_error_format_response(
        error: Error,
        error_with_formatted_message: Error
    ):
    '''
    Test the format_response method of an error.

    :param error: The basic error to test.
    :type error: Error
    :param error_with_formatted_message: The error with a formatted message to test.
    :type error_with_formatted_message: Error
    '''

    # Test formatting the error response
    response = error.format_response('en_US')

    # Check if the response is correctly formatted
    assert response['error_code'] == 'TEST_ERROR'
    assert response['message'] == 'An error occurred.'

    # Test formatting the error response with formatted message
    formatted_response = error_with_formatted_message.format_response('en_US', error='Check for bugs.')

    # Check if the formatted response is correctly formatted
    assert formatted_response['error_code'] == 'TEST_FORMATTED_ERROR'
    assert formatted_response['message'] == 'An error occurred: Check for bugs.'

# ** test: error_format_response_unsupported_lang
def test_error_format_response_unsupported_lang(error: Error):
    '''
    Test the format_response method of an error with an unsupported language.

    :param error: The basic error to test.
    :type error: Error
    '''

# ** test: error_format_response_unsupported_lang
def test_error_format_response_unsupported_lang(error: Error):
    '''
    Test the format_response method of an error with an unsupported language.

    :param error: The basic error to test.
    :type error: Error
    '''

    # Test formatting the error response with unsupported language
    response = error.format_response('fr_FR')

    # Verify that the response is None.
    assert not response

# ** test: error_set_message
def test_error_set_message(error: Error):
    '''
    Test setting a new error message for a specific language.

    :param error: The error to test.
    :type error: Error
    '''

    # Set a new message for the 'en_US' language.
    error.set_message('en_US', 'A new error occurred.')

    # Verify that the message is updated.
    assert len(error.message) == 1
    assert error.message[0].lang == 'en_US'
    assert error.message[0].text == 'A new error occurred.'

# ** test: error_set_message_new_lang
def test_error_set_message_new_lang(error: Error):
    '''
    Test setting a new error message for a new language.

    :param error: The error to test.
    :type error: Error
    '''

    # Set a new message for the 'fr_FR' language.
    error.set_message('fr_FR', 'Une nouvelle erreur est survenue.')

    # Verify that the new message is added.
    assert len(error.message) == 2
    assert error.message[1].lang == 'fr_FR'
    assert error.message[1].text == 'Une nouvelle erreur est survenue.'