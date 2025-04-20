# *** imports 

# ** infra
import pytest

# ** app
from ..error import *
from ...configs.tests.test_error import *


# *** fixtures


# ** fixture: error_config
@pytest.fixture
def error_config():
    
    return dict(**TEST_ERROR)


# ** fixture: error
@pytest.fixture
def error(error_config) -> Error:
    
    return ModelObject.new(
        Error,
        **error_config
    )


# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    
    return ValueObject.new(
        ErrorMessage,
        **TEST_ERROR_MESSAGE
    )


# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    return ValueObject.new(
        ErrorMessage,
        **TEST_FORMATTED_ERROR_MESSAGE
    )


# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message) -> Error:
    
    return ModelObject.new(
        Error,
        **TEST_ERROR_WITH_FORMATTED_MESSAGE
    )


# *** tests

# ** test: test_error_message_new
def test_error_new(error_config, error_message):

    # Remove message from the error config.
    error_config.pop('message', None)
    
    # Create an error message object.
    error = Error.new(
        **error_config,
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'Test Error'
    assert error.id == 'test_error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message


# ** test: test_error_new_no_error_code
def test_error_new_no_error_code(error_config, error_message):

    # Remove message and error_code from the error config.
    error_config.pop('message', None)
    error_config.pop('error_code', None)

    # Create an error message object.
    error = Error.new(
        **error_config,
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'Test Error'
    assert error.id == 'test_error'
    assert error.error_code == 'TEST_ERROR'
    assert len(error.message) == 1
    assert error.message[0] == error_message


# ** test: test_error_new_no_id
def test_error_new_no_id(error_config, error_message):

    # Remove message, id, and error code from the error config.
    error_config.pop('message', None)
    error_config.pop('id', None)
    error_config.pop('error_code', None)
    
    # Create an error message object.
    error = Error.new(
        **error_config,
        message=[error_message]
    )

    # Check if the error message object is correctly instantiated.
    assert error.name == 'Test Error'
    assert error.id == 'test_error'
    assert error.error_code == 'TEST_ERROR'
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
