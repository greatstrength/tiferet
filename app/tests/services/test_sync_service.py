from ...objects.object import ModelObject
from ...objects.object import ObjectMethodParameter
from ...objects.sync import Class
from ...objects.sync import Parameter
from ...services.sync import sync_parameter_type
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


def test_sync_parameter_type_any():

    # Create an object method parameter with no type.
    parameter = ObjectMethodParameter.new(
        name='attribute',
        type='any',
        description='The attribute to add.',
    )

    # Get the parameter type.
    type = sync_parameter_type(parameter)

    # Assert the parameter type is correct.
    assert type == 'Any'


def test_sync_parameter_type_non_compound():

    # Create an object method parameter with a string type.
    parameter = ObjectMethodParameter.new(
        name='attribute',
        type='str',
        description='The attribute to add.',
    )

    # Get the parameter type.
    type = sync_parameter_type(parameter)

    # Assert the parameter type is correct.
    assert type == 'str'


def test_sync_parameter_type_list():

    # Create an object method parameter with a list type.
    parameter = ObjectMethodParameter.new(
        name='choices',
        type='list',
        inner_type='str',
        description='The choices for the attribute value.',
    )

    # Get the parameter type.
    type = sync_parameter_type(parameter)

    # Assert the parameter type is correct.
    assert type == 'List[str]'


def test_sync_parameter_type_dict():

    # Create an object method parameter with a dict type.
    parameter = ObjectMethodParameter.new(
        name='metadata',
        type='dict',
        inner_type='str',
        description='The metadata for the attribute.',
    )

    # Get the parameter type.
    type = sync_parameter_type(parameter)

    # Assert the parameter type is correct.
    assert type == 'Dict[str, str]'


def test_sync_parameter_type_model():

    # Create an object method parameter with a model type.
    parameter = ObjectMethodParameter.new(
        name='attribute',
        type='model',
        type_object_id='attribute',
        description='The attribute to add.',
    )

    # Create the model object for the attribute.
    model_obj = ModelObject.new(
        name='Attribute',
        type='value_object',
        group_id='object',
        description='An attribute.',
    )

    # Get the parameter type.
    type = sync_parameter_type(parameter, model_obj)

    # Assert the parameter type is correct.
    assert type == 'Attribute'


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