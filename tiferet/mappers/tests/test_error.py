"""Tiferet Error Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import TransferObject
from ..error import (
    ErrorAggregate,
    ErrorYamlObject,
    ErrorMessageYamlObject,
)
from ...domain import (
    DomainObject,
    Error,
    ErrorMessage,
)
from .settings import AggregateTestBase, TransferObjectTestBase

# *** tests

# ** test: TestErrorAggregate
class TestErrorAggregate(AggregateTestBase):
    '''
    Tests for the ErrorAggregate mapper using the aggregate test harness.
    '''

    # * attribute: aggregate_cls
    aggregate_cls = ErrorAggregate

    # * attribute: sample_data
    sample_data = dict(
        id='test_error',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            {'lang': 'en', 'text': 'Test error message.'},
        ],
    )

    # * attribute: equality_fields
    equality_fields = ['id', 'name', 'error_code']

    # * attribute: set_attribute_params
    set_attribute_params = [
        ('name', 'Updated Error Name', None),
        ('description', 'Updated description', None),
        ('invalid_attribute', 'value', 'INVALID_MODEL_ATTRIBUTE'),
    ]

    # * method: test_rename
    def test_rename(self, aggregate: ErrorAggregate):
        '''
        Test renaming an error via ErrorAggregate.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Rename the error.
        aggregate.rename('Renamed Error')

        # Assert the name was updated.
        assert aggregate.name == 'Renamed Error'

    # * method: test_set_message_new
    def test_set_message_new(self, aggregate: ErrorAggregate):
        '''
        Test adding a new language message on an ErrorAggregate.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Add a new language message.
        aggregate.set_message('es', 'Mensaje de error de prueba.')

        # Assert the message was added alongside the existing one.
        assert len(aggregate.message) == 2
        es_msg = next(m for m in aggregate.message if m.lang == 'es')
        assert es_msg.text == 'Mensaje de error de prueba.'

    # * method: test_set_message_update
    def test_set_message_update(self, aggregate: ErrorAggregate):
        '''
        Test updating an existing message on an ErrorAggregate.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Update the existing English message.
        aggregate.set_message('en', 'Updated message.')

        # Assert the message was updated (not added).
        assert len(aggregate.message) == 1
        assert aggregate.message[0].text == 'Updated message.'

    # * method: test_remove_message
    def test_remove_message(self):
        '''
        Test removing a message from an ErrorAggregate with multiple messages.
        '''

        # Create an aggregate with two messages.
        aggregate = ErrorAggregate.new(
            id='test_error',
            name='Test Error',
            error_code='TEST_ERROR',
            message=[
                {'lang': 'en', 'text': 'English message'},
                {'lang': 'es', 'text': 'Spanish message'},
            ],
        )

        # Remove the English message.
        aggregate.remove_message('en')

        # Assert only the Spanish message remains.
        assert len(aggregate.message) == 1
        assert aggregate.message[0].lang == 'es'

    # * method: test_remove_message_nonexistent
    def test_remove_message_nonexistent(self, aggregate: ErrorAggregate):
        '''
        Test that removing a non-existent language message is a no-op.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Capture the original message count.
        original_count = len(aggregate.message)

        # Remove a non-existent language.
        aggregate.remove_message('fr')

        # Assert the message list is unchanged.
        assert len(aggregate.message) == original_count


# ** test: TestErrorYamlObject
class TestErrorYamlObject(TransferObjectTestBase):
    '''
    Tests for the ErrorYamlObject mapper using the transfer object test harness.
    '''

    # * attribute: transfer_cls
    transfer_cls = ErrorYamlObject

    # * attribute: aggregate_cls
    aggregate_cls = ErrorAggregate

    # * attribute: sample_data
    sample_data = dict(
        id='TEST_ERROR',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            {'lang': 'en', 'text': 'Test error message.'},
        ],
    )

    # * attribute: aggregate_sample_data
    aggregate_sample_data = dict(
        id='TEST_ERROR',
        name='Test Error',
        error_code='TEST_ERROR',
        message=[
            {'lang': 'en', 'text': 'Test error message.'},
        ],
    )

    # * attribute: equality_fields
    equality_fields = ['id', 'name', 'error_code']

    # * method: test_from_data
    def test_from_data(self):
        '''
        Test that from_data() initializes all fields correctly,
        including nested ErrorMessageYamlObject instances.
        '''

        # Create a transfer object from YAML-format sample data.
        yaml_obj = TransferObject.from_data(self.transfer_cls, **self.sample_data)

        # Assert scalar attributes.
        assert isinstance(yaml_obj, ErrorYamlObject)
        assert yaml_obj.id == 'TEST_ERROR'
        assert yaml_obj.name == 'Test Error'
        assert yaml_obj.error_code == 'TEST_ERROR'

        # Assert nested messages are ErrorMessageYamlObject instances.
        assert len(yaml_obj.message) == 1
        assert isinstance(yaml_obj.message[0], ErrorMessageYamlObject)
        assert yaml_obj.message[0].lang == 'en'
        assert yaml_obj.message[0].text == 'Test error message.'

    # * method: test_to_primitive_to_data_yaml
    def test_to_primitive_to_data_yaml(self):
        '''
        Test that to_primitive('to_data.yaml') excludes the id field
        and serializes messages correctly.
        '''

        # Create a transfer object from sample data.
        yaml_obj = TransferObject.from_data(self.transfer_cls, **self.sample_data)

        # Convert to primitive for YAML serialization.
        primitive = yaml_obj.to_primitive('to_data.yaml')

        # Assert id is excluded by the to_data.yaml role.
        assert isinstance(primitive, dict)
        assert 'id' not in primitive

        # Assert the remaining values are correct.
        assert primitive.get('name') == 'Test Error'
        assert primitive.get('error_code') == 'TEST_ERROR'
        assert len(primitive.get('message')) == 1
        assert primitive['message'][0]['lang'] == 'en'
        assert primitive['message'][0]['text'] == 'Test error message.'

    # * method: test_map_messages
    def test_map_messages(self):
        '''
        Test that map() produces ErrorMessage domain objects in the message list.
        '''

        # Create a transfer object from sample data and map to aggregate.
        yaml_obj = TransferObject.from_data(self.transfer_cls, **self.sample_data)
        mapped = yaml_obj.map()

        # Assert the messages are ErrorMessage instances with correct fields.
        assert len(mapped.message) == 1
        assert isinstance(mapped.message[0], ErrorMessage)
        assert mapped.message[0].lang == 'en'
        assert mapped.message[0].text == 'Test error message.'

    # * method: test_from_model_messages
    def test_from_model_messages(self, aggregate: ErrorAggregate):
        '''
        Test that from_model() converts message list to ErrorMessageYamlObject instances.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Convert the aggregate to a transfer object.
        yaml_obj = self.transfer_cls.from_model(aggregate)

        # Assert all messages are ErrorMessageYamlObject instances.
        assert len(yaml_obj.message) == 1
        assert all(isinstance(msg, ErrorMessageYamlObject) for msg in yaml_obj.message)
        assert yaml_obj.message[0].lang == 'en'
        assert yaml_obj.message[0].text == 'Test error message.'

    # * method: test_round_trip_messages
    def test_round_trip_messages(self, aggregate: ErrorAggregate):
        '''
        Test that round-trip preserves message content field-by-field.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Convert aggregate to transfer object and back.
        yaml_obj = self.transfer_cls.from_model(aggregate)
        round_tripped = yaml_obj.map()

        # Assert messages match field-by-field.
        assert len(round_tripped.message) == len(aggregate.message)
        for orig, rt in zip(aggregate.message, round_tripped.message):
            assert rt.lang == orig.lang
            assert rt.text == orig.text

    # * method: test_from_model_via_error_new
    def test_from_model_via_error_new(self):
        '''
        Test from_model() using an Error created via the Error.new() factory,
        including multilingual messages.
        '''

        # Create an error model via the factory method.
        error = Error.new(
            id='from_factory',
            name='Factory Error',
            message=[
                {'lang': 'en', 'text': 'English message'},
                {'lang': 'es', 'text': 'Mensaje en español'},
            ],
        )

        # Create a YAML object from the model.
        yaml_obj = ErrorYamlObject.from_model(error)

        # Assert the YAML object is valid with both messages.
        assert isinstance(yaml_obj, ErrorYamlObject)
        assert yaml_obj.id == 'from_factory'
        assert yaml_obj.name == 'Factory Error'
        assert len(yaml_obj.message) == 2
        assert all(isinstance(msg, ErrorMessageYamlObject) for msg in yaml_obj.message)


# ** test: error_message_yaml_object_map
def test_error_message_yaml_object_map():
    '''
    Test mapping an ErrorMessageYamlObject to an ErrorMessage domain object.
    '''

    # Create an ErrorMessageYamlObject from data.
    yaml_obj = TransferObject.from_data(
        ErrorMessageYamlObject,
        lang='en',
        text='Test error message.',
    )

    # Map to an ErrorMessage.
    mapped = yaml_obj.map()

    # Assert the mapped object is an ErrorMessage with correct fields.
    assert isinstance(mapped, ErrorMessage)
    assert mapped.lang == 'en'
    assert mapped.text == 'Test error message.'


# ** test: error_message_yaml_object_from_model
def test_error_message_yaml_object_from_model():
    '''
    Test creating an ErrorMessageYamlObject from an ErrorMessage model.
    '''

    # Create an ErrorMessage domain object.
    error_message = DomainObject.new(
        ErrorMessage,
        lang='es',
        text='Mensaje de error.',
    )

    # Create a YAML object from the model.
    yaml_obj = ErrorMessageYamlObject.from_model(error_message)

    # Assert the YAML object is valid.
    assert isinstance(yaml_obj, ErrorMessageYamlObject)
    assert yaml_obj.lang == 'es'
    assert yaml_obj.text == 'Mensaje de error.'
