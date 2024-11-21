# *** imports 

# ** infra
import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message():
    return ErrorMessage.new(
        lang='en_US',
        text='An error occurred.'
    )


# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message():
    return ErrorMessage.new(
        lang='en_US',
        text='An error occurred: {}'
    )


# ** fixture: error
@pytest.fixture
def error(error_message):
    return Error.new(
        name='My Error',
        message=[error_message]
    )


# ** fixture: error_with_multiple_messages
@pytest.fixture
def error_with_multiple_messages():
    return Error.new(
        name='Multi Language Error',
        message=[
            ErrorMessage.new(lang='en_US', text='An error occurred.'),
            ErrorMessage.new(lang='fr_FR', text='Une erreur est survenue.')
        ]
    )


# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message):
    return Error.new(
        name='Formatted Error',
        message=[
            formatted_error_message
        ]
    )


# ** fixture: errror_with_custom_id_and_code
@pytest.fixture
def error_with_custom_id_and_code():
    return Error.new(
        name='Custom Error',
        id='CUSTOM_ERROR',
        error_code='CUSTOM_ERR',
        message=[ErrorMessage.new(lang='en_US', text='An error occurred.')]
    )


# *** tests

# ** test: test_error_message_new
def test_error_message_new(error_message):

    # Check if the ErrorMessage is correctly instantiated
    assert error_message.lang == 'en_US'
    assert error_message.text == 'An error occurred.'


# ** test: test_error_message_format
def test_error_message_format(error_message, formatted_error_message):

    # Test basic formatting
    assert error_message.format() == 'An error occurred.'
    # Test formatting with arguments
    assert formatted_error_message.format('Check for bugs.') == 'An error occurred: Check for bugs.'


# ** test: test_error_new
def test_error_new(error):

    # Check if the Error object is correctly instantiated
    assert error.name == 'MY_ERROR'
    assert error.id == 'MY_ERROR'
    assert error.error_code == 'MY_ERROR'
    assert len(error.message) == 1
    assert error.message[0].lang == 'en_US'


# ** test: test_error_format_method
def test_error_format_method(error, error_with_formatted_message):
   
    # Test formatting with arguments
    assert error.format('en_US') == 'An error occurred.'

    # Test formatting with arguments
    assert error_with_formatted_message.format('en_US', 'Check for bugs.') == 'An error occurred: Check for bugs.'


# ** test: test_error_id_and_code_customization
def test_error_id_and_code_customization(error_with_custom_id_and_code):
    
   # Check if the custom ID and error code are set correctly
    assert error_with_custom_id_and_code.name == 'CUSTOM_ERROR'
    assert error_with_custom_id_and_code.id == 'CUSTOM_ERROR'
    assert error_with_custom_id_and_code.error_code == 'CUSTOM_ERR'
