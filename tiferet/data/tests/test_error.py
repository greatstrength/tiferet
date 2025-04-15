# *** imports

# ** infra
import pytest

# ** app
from ..error import *


# *** fixtures

# ** fixture: error_yaml_data
@pytest.fixture
def error_yaml_data():
    '''
    Fixture for creating an error data object.
    '''
    
    # Return the error data.
    return DataObject.from_data(
        ErrorYamlData,
        id='MY_ERROR',
        name='My Error',
        error_code='MY_ERROR',
        message=[
            dict(
                lang='en_US',
                text='This is a test error message.'
            )
        ]
    )


# ** fixture: error_message_yaml_data
@pytest.fixture
def error_message_yaml_data():
    '''
    Fixture for creating an error message data object.
    '''
    
    # Return the error message data.
    return DataObject.from_data(
        ErrorMessageYamlData,
        lang='en_US',
        text='This is a test error message.'
    )


# *** tests

# ** test: test_error_yaml_data_map
def test_error_yaml_data_map(error_yaml_data):
    '''
    Test the error data mapping.
    '''
    
    # Map the error data to an error object.
    error = error_yaml_data.map(Error)
    
    # Assert the error type.
    assert isinstance(error, Error)
    
    # Assert the error attributes.
    assert len(error.message) == 1
    assert isinstance(error.message[0], ErrorMessage)
    
    # Assert the error message attributes.
    error_message = error.message[0]
    assert error_message.lang == 'en_US'
    assert error_message.text == 'This is a test error message.'


# ** test: test_error_message_yaml_data_map
def test_error_message_yaml_data_map(error_message_yaml_data):
    '''
    Test the error message data mapping.
    '''
    
    # Map the error message data to an error message object.
    error_message = error_message_yaml_data.map(ErrorMessage)
    
    # Assert the error message type.
    assert isinstance(error_message, ErrorMessage)
    
    # Assert the error message attributes.
    assert error_message.lang == 'en_US'
    assert error_message.text == 'This is a test error message.'