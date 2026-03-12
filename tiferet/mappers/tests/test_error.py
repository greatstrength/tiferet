"""Tiferet Error Mapper Tests"""

# *** imports

# ** app
from ...domain import (
    DomainObject,
    Error,
    ErrorMessage,
)
from ...events import a
from ..settings import TransferObject
from ..error import (
    ErrorAggregate,
    ErrorYamlObject,
    ErrorMessageYamlObject,
)
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: error_sample_data
ERROR_SAMPLE_DATA = {
    'id': 'TEST_ERROR',
    'name': 'TEST_ERROR',
    'error_code': 'TEST_ERROR',
    'message': [
        {'lang': 'en', 'text': 'Test error message.'},
    ],
}

# ** constant: error_equality_fields
ERROR_EQUALITY_FIELDS = ['id', 'name', 'error_code']


# *** classes

# ** class: TestErrorAggregate
class TestErrorAggregate(AggregateTestBase):
    '''
    Tests for ErrorAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = ErrorAggregate

    sample_data = ERROR_SAMPLE_DATA

    equality_fields = ERROR_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name', 'Updated Error', None),
        ('description', 'A new description', None),
        # invalid
        ('invalid_attribute', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''
        Test that rename() updates the error name.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Rename the error.
        aggregate.rename('Renamed Error')

        # Assert the name was updated.
        assert aggregate.name == 'Renamed Error'

    # ** test: set_message_new
    def test_set_message_new(self, aggregate):
        '''
        Test that set_message() adds a new language message alongside existing ones.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Add a new Spanish message.
        aggregate.set_message('es', 'Mensaje de error de prueba.')

        # Assert both messages exist.
        assert len(aggregate.message) == 2
        assert aggregate.message[1].lang == 'es'
        assert aggregate.message[1].text == 'Mensaje de error de prueba.'

    # ** test: set_message_update
    def test_set_message_update(self, aggregate):
        '''
        Test that set_message() updates an existing language message in-place (no duplication).

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Update the existing English message.
        aggregate.set_message('en', 'Updated message')

        # Assert only one message exists and it was updated.
        assert len(aggregate.message) == 1
        assert aggregate.message[0].text == 'Updated message'

    # ** test: remove_message
    def test_remove_message(self, aggregate):
        '''
        Test that remove_message() removes a message from a multi-message aggregate.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Add a second message, then remove the first.
        aggregate.set_message('es', 'Mensaje de prueba')
        aggregate.remove_message('en')

        # Assert only the Spanish message remains.
        assert len(aggregate.message) == 1
        assert aggregate.message[0].lang == 'es'

    # ** test: remove_message_nonexistent
    def test_remove_message_nonexistent(self, aggregate):
        '''
        Test that removing a non-existent language is a no-op.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Record the initial count.
        initial_count = len(aggregate.message)

        # Attempt to remove a non-existent language.
        aggregate.remove_message('fr')

        # Assert the message list is unchanged.
        assert len(aggregate.message) == initial_count


# ** class: TestErrorYamlObject
class TestErrorYamlObject(TransferObjectTestBase):
    '''
    Tests for ErrorYamlObject mapping, round-trip, and nested ErrorMessageYamlObject.
    '''

    transfer_cls = ErrorYamlObject
    aggregate_cls = ErrorAggregate

    sample_data = ERROR_SAMPLE_DATA

    aggregate_sample_data = ERROR_SAMPLE_DATA

    equality_fields = ERROR_EQUALITY_FIELDS

    # *** domain-specific tests

    # ** test: from_data
    def test_from_data(self):
        '''
        Test that from_data() initializes scalar fields and nested ErrorMessageYamlObject instances.
        '''

        # Create a YAML object from sample data.
        yaml_obj = TransferObject.from_data(ErrorYamlObject, **self.sample_data)

        # Assert scalar fields.
        assert yaml_obj.name == 'TEST_ERROR'
        assert yaml_obj.error_code == 'TEST_ERROR'

        # Assert nested messages.
        assert len(yaml_obj.message) == 1
        assert isinstance(yaml_obj.message[0], ErrorMessageYamlObject)
        assert yaml_obj.message[0].lang == 'en'
        assert yaml_obj.message[0].text == 'Test error message.'

    # ** test: to_primitive_to_data_yaml
    def test_to_primitive_to_data_yaml(self):
        '''
        Test that to_primitive('to_data.yaml') excludes id and serializes messages correctly.
        '''

        # Create a YAML object and serialize.
        yaml_obj = TransferObject.from_data(ErrorYamlObject, **self.sample_data)
        primitive = yaml_obj.to_primitive('to_data.yaml')

        # Assert id is excluded.
        assert isinstance(primitive, dict)
        assert primitive.pop('id', None) is None

        # Assert remaining fields.
        assert primitive.get('name') == 'TEST_ERROR'
        assert primitive.get('error_code') == 'TEST_ERROR'
        assert len(primitive.get('message')) == 1
        assert primitive.get('message')[0].get('lang') == 'en'
        assert primitive.get('message')[0].get('text') == 'Test error message.'

    # ** test: map_messages
    def test_map_messages(self):
        '''
        Test that map() produces ErrorMessage domain objects in the message list.
        '''

        # Create YAML object and map.
        yaml_obj = TransferObject.from_data(ErrorYamlObject, **self.sample_data)
        mapped = yaml_obj.map()

        # Assert messages are ErrorMessage instances.
        assert len(mapped.message) == 1
        assert isinstance(mapped.message[0], ErrorMessage)
        assert mapped.message[0].lang == 'en'
        assert mapped.message[0].text == 'Test error message.'

    # ** test: from_model_messages
    def test_from_model_messages(self, aggregate):
        '''
        Test that from_model() converts messages to ErrorMessageYamlObject instances.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Convert aggregate to YAML object.
        yaml_obj = ErrorYamlObject.from_model(aggregate)

        # Assert messages are ErrorMessageYamlObject instances.
        assert len(yaml_obj.message) == 1
        assert all(isinstance(msg, ErrorMessageYamlObject) for msg in yaml_obj.message)

    # ** test: round_trip_messages
    def test_round_trip_messages(self, aggregate):
        '''
        Test that round-trip preserves message content field-by-field.

        :param aggregate: The error aggregate fixture.
        :type aggregate: ErrorAggregate
        '''

        # Round-trip: aggregate -> YAML object -> aggregate.
        yaml_obj = ErrorYamlObject.from_model(aggregate)
        round_tripped = yaml_obj.map()

        # Assert message content preserved.
        assert len(round_tripped.message) == len(aggregate.message)
        for original, restored in zip(aggregate.message, round_tripped.message):
            assert restored.lang == original.lang
            assert restored.text == original.text

    # ** test: from_model_via_error_new
    def test_from_model_via_error_new(self):
        '''
        Test that from_model() works with an Error.new() factory-created model with multilingual messages.
        '''

        # Create an Error model via the domain factory.
        error = Error.new(
            id='test_error',
            name='Test Error',
            message=[
                {'lang': 'en', 'text': 'Test message'},
                {'lang': 'es', 'text': 'Mensaje de prueba'},
            ],
        )

        # Convert to YAML object.
        yaml_obj = ErrorYamlObject.from_model(error)

        # Assert the YAML object is valid.
        assert isinstance(yaml_obj, ErrorYamlObject)
        assert yaml_obj.id == 'test_error'
        assert yaml_obj.name == 'Test Error'
        assert len(yaml_obj.message) == 2
        assert all(isinstance(msg, ErrorMessageYamlObject) for msg in yaml_obj.message)


# *** standalone tests

# ** test: error_message_yaml_object_map
def test_error_message_yaml_object_map():
    '''
    Test that ErrorMessageYamlObject maps to an ErrorMessage domain object.
    '''

    # Create from data and map.
    yaml_obj = TransferObject.from_data(
        ErrorMessageYamlObject,
        lang='en',
        text='Test message',
    )
    msg = yaml_obj.map()

    # Assert the mapped domain object.
    assert isinstance(msg, ErrorMessage)
    assert msg.lang == 'en'
    assert msg.text == 'Test message'


# ** test: error_message_yaml_object_from_model
def test_error_message_yaml_object_from_model():
    '''
    Test that ErrorMessageYamlObject can be created from an ErrorMessage domain object.
    '''

    # Create an ErrorMessage via DomainObject.new.
    model = DomainObject.new(
        ErrorMessage,
        lang='es',
        text='Mensaje de prueba',
    )

    # Convert to YAML object.
    yaml_obj = ErrorMessageYamlObject.from_model(model)

    # Assert the YAML object fields.
    assert isinstance(yaml_obj, ErrorMessageYamlObject)
    assert yaml_obj.lang == 'es'
    assert yaml_obj.text == 'Mensaje de prueba'
