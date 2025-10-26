"""Data Transfer Object Settings Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...models import (
    ModelObject,
    StringType,
)
from ..settings import DataObject

# *** fixtures

# ** fixture: mock_model
@pytest.fixture
def mock_model() -> ModelObject:
    '''
    Provides a fixture for a mocked ModelObject instance.
    
    :return: The mocked ModelObject instance.
    :rtype: ModelObject
    '''
    
    # Create a mocked ModelObject instance.
    model = mock.Mock(spec=ModelObject)
    model.to_primitive.return_value = {
        'id': 'test_id',
        'name': 'Test Model'
    }
    model.validate.return_value = None
    
    # Return the mocked model.
    return model

# ** fixture: test_data_object
@pytest.fixture
def test_data_object() -> DataObject:
    '''
    Provides a fixture for a DataObject instance.
    
    :return: The DataObject instance.
    :rtype: DataObject
    '''
    
    class TestDataObject(DataObject):
        '''
        A test DataObject for testing purposes.
        '''

        class Options:
            '''
            Options for the test DataObject.
            '''

            serialize_when_none = False
            roles = {
                'to_data': DataObject.allow('id', 'name'),
                'to_model': DataObject.allow('id', 'name')
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

# ** test: data_object_from_data
def test_data_object_from_data(test_data_object: type):
    '''
    Test the creation of a DataObject from a dictionary.

    :param test_data_object: The DataObject subclass to test.
    :type test_data_object: type
    '''
    
    # Create a DataObject from data.
    data_object = DataObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )
    
    # Assert the attributes are correctly set.
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Data'}

# ** test: data_object_from_model
def test_data_object_from_model(mock_model, test_data_object):
    '''
    Test the creation of a DataObject from a ModelObject.
    
    :param mock_model: The mocked ModelObject instance.
    :type mock_model: ModelObject
    :param test_data_object: The DataObject subclass to test.
    :type test_data_object: type
    '''
    
    # Create a DataObject from the model.
    data_object = DataObject.from_model(
        test_data_object,
        mock_model
    )
    
    # Assert the data object is valid.
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Model'}

# ** test: data_object_from_model_with_kwargs
def test_data_object_from_model_with_kwargs(mock_model, test_data_object):
    '''
    Test the creation of a DataObject from a ModelObject with additional keyword arguments.
    
    :param mock_model: The mocked ModelObject instance.
    :type mock_model: ModelObject
    :param test_data_object: The DataObject subclass to test.
    :type test_data_object: type
    '''
    
    # Create a DataObject from the model with additional attributes.
    data_object = DataObject.from_model(
        test_data_object,
        mock_model,
        name='Overridden Name',
    )
    
    # Assert the data object is valid and includes the extra attribute.
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Overridden Name'}
    

# ** test: data_object_map_custom_new
def test_data_object_map_custom_new(test_data_object: type):
    '''
    Test mapping a DataObject to a ModelObject with a custom new method.
    
    :param test_data_object: The DataObject subclass type.
    :type test_data_object: type
    '''
    
    # Create a DataObject instance.
    data_object = DataObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )

    # Mock a ModelObject class with a custom new method.
    mock_model_type = mock.Mock()
    mock_model_instance = mock.Mock(spec=ModelObject)
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
    Test mapping a DataObject to a ModelObject using the fallback ModelObject.new.
    
    :param test_data_object: The DataObject subclass type.
    :type test_data_object: type
    '''

    # Create a DataObject instance.
    data_object = DataObject.from_data(
        test_data_object,
        id='test_id',
        name='Test Data'
    )
    
    # Mock a ModelObject class without a custom new method.
    mock_model_type = mock.Mock()
    mock_model_type.new.side_effect = AttributeError
    mock_model_instance = mock.Mock(spec=ModelObject)
    mock_model_instance.validate.return_value = None
    with mock.patch('tiferet.data.settings.ModelObject.new', return_value=mock_model_instance) as mock_new:
        result = data_object.map(type=mock_model_type, role='to_model', validate=True)
    
    # Assert the mapped object is valid.
    assert result == mock_model_instance
    mock_new.assert_called_once_with(mock_model_type, id='test_id', name='Test Data', strict=False)
    mock_model_instance.validate.assert_called_once()

# ** test: data_object_allow_with_args
def test_data_object_allow_with_args():
    '''
    Test the allow method with specific fields.
    '''
    
    # Create a whitelist transform with fields.
    transform = DataObject.allow('id', 'name')
    
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
    transform = DataObject.allow()
    
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
    transform = DataObject.deny('id', 'name')
    
    # Assert the transform is a blacklist.
    from schematics.transforms import Role
    assert isinstance(transform, Role)
    assert transform.fields == set(['id', 'name'])
    assert transform.function.__name__ == 'blacklist'