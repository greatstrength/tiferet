from ...objects.sync import Class
from ...services.sync import get_model_attribute_type
from ...services.sync import sync_code_to_model
from ..mocks import MockObjectRepository


def test_get_model_attribute_type():

    # Set the variable type as t.StringType.
    variable_type = 't.StringType'

    # Get the model attribute type.
    model_attribute_type = get_model_attribute_type(variable_type)

    # Assert the model attribute type is correct.
    assert model_attribute_type == 'str'


def test_sync_code_to_model():

    # Create a mock ObjectRepository.
    object_repo = MockObjectRepository()
    
    # Create a Class object with no attributes or methods.
    _class = Class.new(
        name='ModelObject',
        description='A model object.',
        base_classes=['Entity'],
    )

    # Get the model object.
    model_object = sync_code_to_model('object', _class, object_repo)

    # Assert the model object is correct.
    assert model_object.name == 'Model Object'
    assert model_object.group_id == 'object'
    assert model_object.class_name == 'ModelObject'
    assert model_object.type == 'entity'
    assert model_object.description == 'A model object.'