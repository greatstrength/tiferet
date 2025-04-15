# *** imports 

# ** infra
import pytest

# ** app
from ..error import *


# *** fixtures

# ** fixture: error
@pytest.fixture
def error() -> Error:
    return Error.new(
        name='My Error',
        id='MY_ERROR',
        error_code='MY_ERROR',
        message=[
            ValueObject.new(
                ErrorMessage,
                lang='en_US',
                text='An error occurred.'
            )
        ]
    )


# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    return ValueObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred.'
    )


# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    return ValueObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred: {}'
    )


# ** fixture: error
@pytest.fixture
def errors(error_message) -> Error:
    return Error.new(
        name='My Error',
        message=[error_message]
    )


# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message) -> Error:
    return Error.new(
        name='MY_ERROR',
        id='MY_ERROR',
        error_code='MY_ERROR',
        message=[formatted_error_message]
    )


# *** tests

# ** test: test_error_message_new
def test_error_new(error_message):

    # Create an error message object.
    error = Error.new(
        name='My Error',
        id='MY_ERROR',
        error_code='MY_ERROR_CODE',
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'My Error'
    assert error.id == 'MY_ERROR'
    assert error.error_code == 'MY_ERROR_CODE'
    assert len(error.message) == 1
    assert error.message[0] == error_message


# ** test: test_error_new_no_error_code
def test_error_new_no_error_code(error_message):

    # Create an error message object.
    error = Error.new(
        name='My Error',
        id='MY_ERROR',
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'My Error'
    assert error.id == 'MY_ERROR'
    assert error.error_code == 'MY_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message


# ** test: test_error_new_no_id
def test_error_new_no_id(error_message):

    # Create an error message object.
    error = Error.new(
        name='My Error',
        error_code='MY_ERROR_CODE',
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'My Error'
    assert error.id == 'MY_ERROR'
    assert error.error_code == 'MY_ERROR_CODE'
    assert len(error.message) == 1
    assert error.message[0] == error_message


# ** test: test_error_new_raw_message_data
def test_error_new_raw_message_data(error_message):

    # Create an error message object.
    error = Error.new(
        name='My Error',
        id='MY_ERROR',
        error_code='MY_ERROR_CODE',
        message=[error_message.to_primitive()]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'My Error'
    assert error.id == 'MY_ERROR'
    assert error.error_code == 'MY_ERROR_CODE'
    assert len(error.message) == 1
    assert error.message[0] == error_message


# ** test: test_error_message_format
def test_error_message_format(error_message, formatted_error_message):

    # Test basic formatting
    assert error_message.format() == 'An error occurred.'
    # Test formatting with arguments
    assert formatted_error_message.format('Check for bugs.') == 'An error occurred: Check for bugs.'


# ** test: test_error_format_method
def test_error_format_method(error, error_with_formatted_message):
   
    # Test formatting with arguments
    assert error.format('en_US') == 'An error occurred.'

    # Test formatting with arguments
    assert error_with_formatted_message.format('en_US', 'Check for bugs.') == 'An error occurred: Check for bugs.'


# ** test: test_error_format_method_unsupported_lang
def test_error_format_method_unsupported_lang(error):

    # Test formatting with unsupported language
    assert error.format('fr_FR') == None
