"""Tiferet Error Data Object Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..error import  ErrorConfigData

# *** fixtures

# ** fixture: error_config_data
@pytest.fixture
def error_config_data() -> ErrorConfigData:
    '''
    Provides an error data fixture.

    :param error_message: The error message instance.
    :type error_message: ErrorMessage
    :return: The error data instance.
    :rtype: ErrorData
    '''

    # Create and return an error data object.
    return ErrorConfigData.from_data(
        id='TEST_ERROR',
        name='TEST_ERROR',
        error_code='TEST_ERROR',
        message=[{
            'lang': 'en',
            'text': 'Test error message.'
        }]
    )

# *** tests

# ** test: error_data_from_data
def test_error_data_from_data(error_config_data: ErrorConfigData):
    '''
    Test the creation of error data from a dictionary.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Assert the error data is an instance of ErrorData.
    assert error_config_data.name == 'TEST_ERROR'
    assert error_config_data.error_code == 'TEST_ERROR'
    assert len(error_config_data.message) == 1
    assert error_config_data.message[0].lang == 'en'
    assert error_config_data.message[0].text == 'Test error message.'

# ** test: error_data_to_primitive_to_data_yaml
def test_error_data_to_primitive_to_data_yaml(error_config_data : ErrorConfigData):
    '''
    Test the conversion of error data to a primitive dictionary.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Convert the error data to a primitive.
    primitive = error_config_data.to_primitive('to_data.yaml')

    # Assert the primitive is a dictionary.
    assert isinstance(primitive, dict)

    # Assert the primitive values are correct.
    assert primitive.pop('id', None) is None
    assert primitive.get('name') == 'TEST_ERROR'
    assert primitive.get('error_code') == 'TEST_ERROR'
    assert len(primitive.get('message')) == 1
    assert primitive.get('message')[0].get('lang') == 'en'
    assert primitive.get('message')[0].get('text') == 'Test error message.'

# ** test: error_data_map
def test_error_data_map(error_config_data : ErrorConfigData):
    '''
    Test the mapping of error data to an error object.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Map the error data to an error object.
    error = error_config_data.map()

    # Assert the error is an instance of Error.
    assert error.id == error_config_data.id
    assert error.name == error_config_data.name
    assert error.error_code == error_config_data.error_code
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