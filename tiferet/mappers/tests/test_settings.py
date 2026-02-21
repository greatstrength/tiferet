"""Mapper Settings Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...domain import (
    DomainObject,
    StringType,
)
from ..settings import Aggregate, TransferObject
from ...assets import TiferetError

# *** fixtures

# ** fixture: test_aggregate
@pytest.fixture
def test_aggregate() -> type:
    '''
    Provides a fixture for a test Aggregate class.
    
    :return: The Aggregate subclass.
    :rtype: type
    '''
    
    class TestAggregate(Aggregate):
        '''
        A test Aggregate for testing purposes.
        '''
        
        id = StringType(
            required=True,
            metadata=dict(
                description='The unique identifier.'
            )
        )
        
        name = StringType(
            required=True,
            metadata=dict(
                description='The name of the aggregate.'
            )
        )
    
    return TestAggregate

# ** fixture: mock_model
@pytest.fixture
def mock_model() -> DomainObject:
    '''
    Provides a fixture for a mocked DomainObject instance.
    
    :return: The mocked DomainObject instance.
    :rtype: DomainObject
    '''
    
    # Create a mocked DomainObject instance.
    model = mock.Mock(spec=DomainObject)
    model.to_primitive.return_value = {
        'id': 'test_id',
        'name': 'Test Model'
    }
    model.validate.return_value = None
    
    # Return the mocked model.
    return model

# ** fixture: test_data_object
@pytest.fixture
def test_data_object() -> TransferObject:
    '''
    Provides a fixture for a TransferObject instance.
    
    :return: The TransferObject instance.
    :rtype: TransferObject
    '''
    
    class TestDataObject(TransferObject):
        '''
        A test TransferObject for testing purposes.
        '''

        class Options:
            '''
            Options for the test TransferObject.
            '''

            serialize_when_none = False
            roles = {
                'to_data': TransferObject.allow('id', 'name'),
                'to_model': TransferObject.allow('id', 'name')
            }
        
        id = StringType(
            required=True,
            metadata=dict(
                description='The unique identifier for the data object.'
            )
        )

        name = StringType(
            required=True,
            metadata=dict(
                description='The name of the data object.'
            )
        )

    return TestDataObject

# *** tests

# ** test: aggregate_new
def test_aggregate_new(test_aggregate: type):
    '''
    Test the Aggregate.new factory method.
    
    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''
    
    # Create a new aggregate instance.
    aggregate = Aggregate.new(
        test_aggregate,
        id='test_id',
        name='Test Aggregate'
    )
    
    # Assert the aggregate is correctly instantiated.
    assert isinstance(aggregate, test_aggregate)
    assert aggregate.id == 'test_id'
    assert aggregate.name == 'Test Aggregate'

# ** test: aggregate_new_no_validation
def test_aggregate_new_no_validation(test_aggregate: type):
    '''
    Test the Aggregate.new factory method without validation.
    
    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''
    
    # Create a new aggregate instance without validation.
    aggregate = Aggregate.new(
        test_aggregate,
        validate=False,
        id='test_id',
        name='Test Aggregate'
    )
    
    # Assert the aggregate is correctly instantiated.
    assert isinstance(aggregate, test_aggregate)
    assert aggregate.id == 'test_id'
    assert aggregate.name == 'Test Aggregate'

# ** test: aggregate_new_not_strict
def test_aggregate_new_not_strict(test_aggregate: type):
    '''
    Test the Aggregate.new factory method with strict=False.
    
    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''
    
    # Create a new aggregate instance in non-strict mode.
    aggregate = Aggregate.new(
        test_aggregate,
        strict=False,
        id='test_id',
        name='Test Aggregate',
        extra_field='ignored'
    )
    
    # Assert the aggregate is correctly instantiated.
    assert isinstance(aggregate, test_aggregate)
    assert aggregate.id == 'test_id'
    assert aggregate.name == 'Test Aggregate'

# ** test: aggregate_set_attribute_success
def test_aggregate_set_attribute_success(test_aggregate: type):
    '''
    Test setting a valid attribute on an Aggregate instance.
    
    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''
    
    # Create an aggregate instance.
    aggregate = Aggregate.new(
        test_aggregate,
        id='test_id',
        name='Original Name'
    )
    
    # Update the name attribute.
    aggregate.set_attribute('name', 'Updated Name')
    
    # Assert the attribute was updated.
    assert aggregate.name == 'Updated Name'

# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid(test_aggregate: type):
    '''
    Test setting an invalid attribute raises TiferetError.
    
    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''
    
    # Create an aggregate instance.
    aggregate = Aggregate.new(
        test_aggregate,
        id='test_id',
        name='Test Name'
    )
    
    # Attempt to set an invalid attribute.
    with pytest.raises(TiferetError) as exc_info:
        aggregate.set_attribute('invalid_attribute', 'value')
    
    # Assert the correct error is raised.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'

# ** test: data_object_from_data
def test_data_object_from_data(test_data_object: type):
    '''
    Test the creation of a TransferObject from a dictionary.

    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''
    
    # Create a TransferObject from data.
    data_object = TransferObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )
    
    # Assert the attributes are correctly set.
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Data'}

# ** test: transfer_object_from_model
def test_transfer_object_from_model(mock_model, test_data_object):
    '''
    Test the creation of a TransferObject from a DomainObject.
    
    :param mock_model: The mocked DomainObject instance.
    :type mock_model: DomainObject
    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''
    
    # Create a TransferObject from the model.
    data_object = TransferObject.from_model(
        test_data_object,
        mock_model
    )
    
    # Assert the data object is valid.
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Model'}

# ** test: transfer_object_from_model_with_kwargs
def test_transfer_object_from_model_with_kwargs(mock_model, test_data_object):
    '''
    Test the creation of a TransferObject from a DomainObject with additional keyword arguments.
    
    :param mock_model: The mocked DomainObject instance.
    :type mock_model: DomainObject
    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''
    
    # Create a TransferObject from the model with additional attributes.
    data_object = TransferObject.from_model(
        test_data_object,
        mock_model,
        name='Overridden Name',
    )
    
    # Assert the data object is valid and includes the extra attribute.
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Overridden Name'}
    

# ** test: data_object_map_custom_new
def test_transfer_object_map_custom_new(test_data_object: type):
    '''
    Test mapping a TransferObject to a DomainObject with a custom new method.
    
    :param test_data_object: The TransferObject subclass type.
    :type test_data_object: type
    '''
    
    # Create a TransferObject instance.
    data_object = TransferObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )

    # Mock a DomainObject class with a custom new method.
    mock_model_type = mock.Mock()
    mock_model_instance = mock.Mock(spec=DomainObject)
    mock_model_instance.validate.return_value = None
    mock_model_type.new.return_value = mock_model_instance
    
    # Map the DataObject to the model.
    result = data_object.map(type=mock_model_type, role='to_model', validate=True)
    
    # Assert the mapped object is valid.
    assert result == mock_model_instance
    mock_model_type.new.assert_called_once_with(id='test_id', name='Test Data', strict=False)
    mock_model_instance.validate.assert_called_once()

# ** test: data_object_map_fallback_new
def test_data_object_map_fallback_new(test_data_object: type):
    '''
    Test mapping a DataObject to a DomainObject using the fallback DomainObject.new.
    
    :param test_data_object: The DataObject subclass type.
    :type test_data_object: type
    '''

    # Create a TransferObject instance.
    data_object = TransferObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )
    
    # Mock a DomainObject class without a custom new method.
    mock_model_type = mock.Mock()
    mock_model_type.new.side_effect = AttributeError
    mock_aggregate_instance = mock.Mock(spec=Aggregate)
    mock_aggregate_instance.validate.return_value = None
    with mock.patch.object(Aggregate, 'new', return_value=mock_aggregate_instance) as mock_new:
        result = data_object.map(type=mock_model_type, role='to_model', validate=True)
    
    # Assert the mapped object is valid.
    assert result == mock_aggregate_instance
    mock_new.assert_called_once_with(mock_model_type, id='test_id', name='Test Data', strict=False)
    mock_aggregate_instance.validate.assert_called_once()

# ** test: data_object_allow_with_args
def test_data_object_allow_with_args():
    '''
    Test the allow method with specific fields.
    '''
    
    # Create a whitelist transform with fields.
    transform = TransferObject.allow('id', 'name')
    
    # Assert the transform is a whitelist.
    from schematics.transforms import Role
    assert isinstance(transform, Role)
    assert transform.fields == set(['id', 'name'])
    assert transform.function.__name__ == 'whitelist'

# ** test: data_object_allow_no_args
def test_data_object_allow_no_args():
    '''
    Test the allow method with no arguments.
    '''
    
    # Create a wholelist transform with no fields.
    transform = TransferObject.allow()
    
    # Assert the transform is a wholelist.
    from schematics.transforms import Role
    assert isinstance(transform, Role)
    assert transform.fields == set()
    assert transform.function.__name__ == 'wholelist'

# ** test: data_object_deny
def test_data_object_deny():
    '''
    Test the deny method with specific fields.
    '''
    
    # Create a blacklist transform with fields.
    transform = TransferObject.deny('id', 'name')
    
    # Assert the transform is a blacklist.
    from schematics.transforms import Role
    assert isinstance(transform, Role)
    assert transform.fields == set(['id', 'name'])
    assert transform.function.__name__ == 'blacklist'
