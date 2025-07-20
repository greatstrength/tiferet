# *** imports 

# ** infra
import pytest

# ** app
from ..error import *

# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    '''
    Fixture to create a basic error message object.
    '''
    return ValueObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred.'
    )

# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    '''
    Fixture to create a formatted error message object.
    '''
    return ValueObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred: {}'
    )

# ** fixture: error
@pytest.fixture
def error(error_message) -> Error:
    '''
    Fixture to create a basic error object.
    '''
    return Error.new(
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            error_message
        ]
    )

# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message) -> Error:
    '''
    Fixture to create an error object with a formatted message.
    '''
    return Error.new(
        name='Test Formatted Error',
        error_code='TEST_FORMATTED_ERROR',
        message=[
            formatted_error_message
        ]
    )

# *** tests

# ** test: error_new_success
def test_error_new_success(error_message):
    '''
    Test successful instantiation of an Error object with explicit parameters.
    '''
    # Create an error message object.
    error = Error.new(
        id='test_error',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            ValueObject.new(
                ErrorMessage,
                lang='en_US',
                text='An error occurred.'
            )
        ]
    )

    # Check if the error message object is correctly instantiated.
    assert error.id == 'test_error'
    assert error.name == 'Test Error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message

# ** test: error_new_default_id
def test_error_new_default_id(error_message):
    '''
    Test Error instantiation with default id and error_code generation.
    '''
    # Create an error message object with no ID.
    error = Error.new(
        name='Test Error',
        error_code='TEST_ERROR',
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'Test Error'
    assert error.id == 'test_error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message

# ** test: error_new_raw_message
def test_error_new_raw_message(error_message):
    '''
    Test Error instantiation with raw message data conversion.
    '''
    # Create an error message object.
    error = Error.new(
        name='Test Error',
        error_code='TEST_ERROR',
        message=[error_message.to_primitive()]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'Test Error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message

# ** test: error_message_format_basic
def test_error_message_format_basic(error_message, formatted_error_message):
    '''
    Test basic and formatted message formatting for ErrorMessage.
    '''
    # Test basic formatting
    assert error_message.format() == 'An error occurred.'
    # Test formatting with arguments
    assert formatted_error_message.format('Check for bugs.') == 'An error occurred: Check for bugs.'

# ** test: error_format_message_basic
def test_error_format_message_basic(error, error_with_formatted_message):
    '''
    Test basic and formatted message formatting for Error.
    '''
    # Test formatting with arguments
    assert error.format_message('en_US') == 'An error occurred.'
    # Test formatting with arguments
    assert error_with_formatted_message.format_message('en_US', 'Check for bugs.') == 'An error occurred: Check for bugs.'

# ** test: error_format_message_unsupported_lang
def test_error_format_message_unsupported_lang(error):
    '''
    Test Error format_message with an unsupported language.
    '''
    # Test formatting with unsupported language
    assert error.format_message('fr_FR') is None

# ** test: error_format_response_basic
def test_error_format_response_basic(error, error_with_formatted_message):
    '''
    Test basic and formatted response formatting for Error.
    '''
    # Test formatting the error response
    response = error.format_response('en_US')
    
    # Check if the response is correctly formatted
    assert response['error_code'] == 'TEST_ERROR'
    assert response['message'] == 'An error occurred.'

    # Test formatting the error response with formatted message
    formatted_response = error_with_formatted_message.format_response('en_US', 'Check for bugs.')

    # Check if the formatted response is correctly formatted
    assert formatted_response['error_code'] == 'TEST_FORMATTED_ERROR'
    assert formatted_response['message'] == 'An error occurred: Check for bugs.'

# ** test: error_format_response_unsupported_lang
def test_error_format_response_unsupported_lang(error):
    '''
    Test Error format_response with an unsupported language.
    '''
    # Test formatting the error response with unsupported language
    response = error.format_response('fr_FR')

    # Verify that the response is None.
    assert response is None

# ** test: error_set_message_update
def test_error_set_message_update(error):
    '''
    Test updating an existing error message for a specific language.
    '''
    # Set a new message for the 'en_US' language.
    error.set_message('en_US', 'A new error occurred.')

    # Verify that the message is updated.
    assert len(error.message) == 1
    assert error.message[0].lang == 'en_US'
    assert error.message[0].text == 'A new error occurred.'

# ** test: error_set_message_new_lang
def test_error_set_message_new_lang(error):
    '''
    Test adding a new error message for a new language.
    '''
    # Set a new message for the 'fr_FR' language.
    error.set_message('fr_FR', 'Une nouvelle erreur est survenue.')

    # Verify that the new message is added.
    assert len(error.message) == 2
    assert error.message[1].lang == 'fr_FR'
    assert error.message[1].text == 'Une nouvelle erreur est survenue.'
