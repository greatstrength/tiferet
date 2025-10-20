"""Tiferet Error Data Transfer Object Tests"""

# *** imports

# ** infra 
import pytest

# ** app
from ...models import (
    ModelObject,
    ErrorMessage,
)
from ..error import (
    ErrorData,
)

# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    '''
    Provides an error message data fixture.

    :return: The error message instance.
    :rtype: ErrorMessage
    '''

    # Create and return an error message object.
    return ModelObject.new(
        ErrorMessage,
        lang='en',
        text='Test error message.'
    )

# ** fixture: error_data
@pytest.fixture
def error_data(error_message: ErrorMessage) -> ErrorData:
    '''
    Provides an error data fixture.

    :param error_message: The error message instance.
    :type error_message: ErrorMessage
    :return: The error data instance.
    :rtype: ErrorData
    '''

    # Create and return an error data object.
    return ErrorData.from_data(
        id='TEST_ERROR',
        name='TEST_ERROR',
        error_code='TEST_ERROR',
        message=[error_message]
    )

# *** tests

# ** test: error_data_from_data
def test_error_data_from_data(error_data: ErrorData):
    '''
    Test the creation of error data from a dictionary.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Assert the error data is an instance of ErrorData.
    assert error_data.name == 'TEST_ERROR'
    assert error_data.error_code == 'TEST_ERROR'
    assert len(error_data.message) == 1
    assert error_data.message[0].lang == 'en'
    assert error_data.message[0].text == 'Test error message.'

# ** test: error_data_to_primitive
def test_error_data_to_primitive(error_data : ErrorData):
    '''
    Test the conversion of error data to a primitive dictionary.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Convert the error data to a primitive.
    primitive = error_data.to_primitive('to_data')

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
def test_error_data_map(error_data : ErrorData):
    '''
    Test the mapping of error data to an error object.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Map the error data to an error object.
    error = error_data.map()

    # Assert the error is an instance of Error.
    assert error.id == error_data.id
    assert error.name == error_data.name
    assert error.error_code == error_data.error_code
    assert len(error.message) == 1
    assert error.message[0].lang == 'en'
    assert error.message[0].text == 'Test error message.'