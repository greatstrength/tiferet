# *** imports

# ** infra 
import pytest

# ** app
from ..error import *


# *** fixtures

# ** fixture: error_message
@pytest.fixture
def error_message():
    '''
    Provides an error message data fixture.
    '''

    return ValueObject.new(
        ErrorMessage,
        lang='en',
        text='Test error message.'
    )


# ** fixture: error_data
@pytest.fixture
def error_data(error_message):
    '''
    Provides an error data fixture.
    '''

    return ErrorData.from_data(
        id='TEST_ERROR',
        name='TEST_ERROR',
        error_code='TEST_ERROR',
        message=[error_message]
    )


# *** tests

# ** test: error_data_from_data
def test_error_data_from_data(error_data):

    # Assert the error data is an instance of ErrorData.
    assert error_data.name == 'TEST_ERROR'
    assert error_data.error_code == 'TEST_ERROR'
    assert len(error_data.message) == 1
    assert error_data.message[0].lang == 'en'
    assert error_data.message[0].text == 'Test error message.'


# ** test: error_data_to_primitive
def test_error_data_to_primitive(error_data):

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
def test_error_data_map(error_data):

    # Map the error data to an error object.
    error = error_data.map()

    # Assert the error is an instance of Error.
    assert error.id == error_data.id
    assert error.name == error_data.name
    assert error.error_code == error_data.error_code
    assert len(error.message) == 1
    assert error.message[0].lang == 'en'
    assert error.message[0].text == 'Test error message.'