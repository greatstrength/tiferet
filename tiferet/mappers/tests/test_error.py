"""Tiferet Error Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..error import (
    ErrorYamlObject,
    ErrorAggregate,
    ErrorMessageYamlObject,
)
from ...entities import (
    Error,
    ErrorMessage,
)

# *** fixtures

# ** fixture: error_yaml_object
@pytest.fixture
def error_yaml_object() -> ErrorYamlObject:
    '''
    Provides an error YAML object fixture.

    :return: The error YAML object instance.
    :rtype: ErrorYamlObject
    '''

    # Create and return an error YAML object.
    return TransferObject.from_data(
        ErrorYamlObject,
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
def test_error_data_from_data(error_yaml_object: ErrorYamlObject):
    '''
    Test the creation of error data from a dictionary.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Assert the error data is an instance of ErrorData.
    assert error_yaml_object.name == 'TEST_ERROR'
    assert error_yaml_object.error_code == 'TEST_ERROR'
    assert len(error_yaml_object.message) == 1
    assert error_yaml_object.message[0].lang == 'en'
    assert error_yaml_object.message[0].text == 'Test error message.'

# ** test: error_data_to_primitive_to_data_yaml
def test_error_data_to_primitive_to_data_yaml(error_yaml_object : ErrorYamlObject):
    '''
    Test the conversion of error data to a primitive dictionary.

    :param error_data: The error data object.
    :type error_data: ErrorData
    '''

    # Convert the error data to a primitive.
    primitive = error_yaml_object.to_primitive('to_data.yaml')

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
def test_error_data_map(error_yaml_object : ErrorYamlObject):
    '''
    Test the mapping of error YAML object to an error aggregate.

    :param error_yaml_object: The error YAML object.
    :type error_yaml_object: ErrorYamlObject
    '''

    # Map the error data to an error aggregate.
    error = error_yaml_object.map()

    # Assert the error is an instance of ErrorAggregate.
    assert isinstance(error, ErrorAggregate)
    assert error.id == error_yaml_object.id
    assert error.name == error_yaml_object.name
    assert error.error_code == error_yaml_object.error_code
    assert len(error.message) == 1
    assert isinstance(error.message[0], ErrorMessage)

    # Assert the error message attributes.
    error_message = error.message[0]
    assert error_message.lang == 'en'
    assert error_message.text == 'Test error message.'


# ** test: error_yaml_object_from_model
def test_error_yaml_object_from_model():
    '''
    Test creating an ErrorYamlObject from an Error model.
    '''

    # Create an error model.
    from ...entities import ModelObject
    error = Error.new(
        id='test_error',
        name='Test Error',
        message=[
            {'lang': 'en', 'text': 'Test message'},
            {'lang': 'es', 'text': 'Mensaje de prueba'}
        ]
    )

    # Create YAML object from model.
    yaml_object = ErrorYamlObject.from_model(error)

    # Assert the YAML object is valid.
    assert isinstance(yaml_object, ErrorYamlObject)
    assert yaml_object.id == 'test_error'
    assert yaml_object.name == 'Test Error'
    assert len(yaml_object.message) == 2
    assert all(isinstance(msg, ErrorMessageYamlObject) for msg in yaml_object.message)


# ** test: error_aggregate_new
def test_error_aggregate_new():
    '''
    Test creating a new ErrorAggregate.
    '''

    # Create an error aggregate.
    error_data = dict(
        id='test_error',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            {'lang': 'en', 'text': 'Test message'}
        ]
    )

    aggregate = ErrorAggregate.new(**error_data)

    # Assert the aggregate is valid.
    assert isinstance(aggregate, ErrorAggregate)
    assert aggregate.id == 'test_error'
    assert aggregate.name == 'Test Error'
    assert len(aggregate.message) == 1


# ** test: error_aggregate_set_message
def test_error_aggregate_set_message():
    '''
    Test setting a message on an ErrorAggregate.
    '''

    # Create an error aggregate.
    error_data = dict(
        id='test_error',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[]
    )

    aggregate = ErrorAggregate.new(**error_data)

    # Set a message.
    aggregate.set_message('en', 'New test message')

    # Assert the message was set.
    assert len(aggregate.message) == 1
    assert aggregate.message[0].lang == 'en'
    assert aggregate.message[0].text == 'New test message'

    # Update the message.
    aggregate.set_message('en', 'Updated message')

    # Assert the message was updated (not added).
    assert len(aggregate.message) == 1
    assert aggregate.message[0].text == 'Updated message'


# ** test: error_aggregate_remove_message
def test_error_aggregate_remove_message():
    '''
    Test removing a message from an ErrorAggregate.
    '''

    # Create an error aggregate with messages.
    error_data = dict(
        id='test_error',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            {'lang': 'en', 'text': 'English message'},
            {'lang': 'es', 'text': 'Spanish message'}
        ]
    )

    aggregate = ErrorAggregate.new(**error_data)

    # Remove one message.
    aggregate.remove_message('en')

    # Assert only one message remains.
    assert len(aggregate.message) == 1
    assert aggregate.message[0].lang == 'es'
