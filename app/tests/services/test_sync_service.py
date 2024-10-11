from ...objects.object import ModelObject
from ...objects.object import ObjectMethod
from ...objects.object import ObjectMethodParameter
from ...objects.object import ObjectMethodCodeBlock
from ...objects.sync import Class
from ...objects.sync import Parameter
from ...services.sync import sync_parameter_to_code
from ...services.sync import sync_model_code_block_to_code
from ...services.sync import get_model_attribute_type
from ...services.sync import sync_model_method_to_code
from ...services.sync import sync_code_to_model
from ..mocks import MockObjectRepository


def test_get_model_attribute_type():

    # Set the variable type as t.StringType.
    variable_type = 't.StringType'

    # Get the model attribute type.
    model_attribute_type = get_model_attribute_type(variable_type)

    # Assert the model attribute type is correct.
    assert model_attribute_type == 'str'


def test_sync_parameter_to_code_any():

    # Create an object method parameter with no type.
    parameter = ObjectMethodParameter.new(
        name='attribute',
        type='any',
        description='The attribute to add.',
    )

    # Get the parameter.
    param = sync_parameter_to_code(parameter, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'attribute'
    assert param.type == 'Any'
    assert param.description == 'The attribute to add.'


def test_sync_parameter_to_code_non_compound():

    # Create an object method parameter with a string type.
    parameter = ObjectMethodParameter.new(
        name='attribute',
        type='str',
        description='The attribute to add.',
    )

    # Get the parameter.
    type = sync_parameter_to_code(parameter, MockObjectRepository())

    # Assert the parameter is correct.
    assert type.name == 'attribute'
    assert type.type == 'str'
    assert type.description == 'The attribute to add.'


def test_sync_parameter_to_code_list():

    # Create an object method parameter with a list type.
    parameter = ObjectMethodParameter.new(
        name='choices',
        type='list',
        inner_type='str',
        description='The choices for the attribute value.',
    )

    # Get the parameter.
    param = sync_parameter_to_code(parameter, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'choices'
    assert param.type == 'List[str]'
    assert param.description == 'The choices for the attribute value.'


def test_sync_parameter_to_code_dict():

    # Create an object method parameter with a dict type.
    parameter = ObjectMethodParameter.new(
        name='metadata',
        type='dict',
        inner_type='str',
        description='The metadata for the attribute.',
    )

    # Get the parameter.
    param = sync_parameter_to_code(parameter, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'metadata'
    assert param.type == 'Dict[str, str]'
    assert param.description == 'The metadata for the attribute.'


def test_sync_parameter_to_code_model_compound():

    # Create an object method parameter with a model type.
    parameter = ObjectMethodParameter.new(
        name='attributes',
        type='list',
        inner_type='model',
        type_object_id='attribute',
        description='The attributes to add in bulk.',
    )

    # Create object repository with a model object.
    object_repo = MockObjectRepository([
        ModelObject.new(
            name='Attribute',
            type='value_object',
            group_id='object',
            description='An attribute.',
        )]
    )

    # Get the parameter.
    param = sync_parameter_to_code(parameter, object_repo)

    # Assert the parameter is correct.
    assert param.name == 'attributes'
    assert param.type == 'List[Attribute]'
    assert param.description == 'The attributes to add in bulk.'


def test_sync_parameter_to_code_model():

    # Create an object method parameter with a model type.
    parameter = ObjectMethodParameter.new(
        name='attribute',
        type='model',
        type_object_id='attribute',
        description='The attribute to add.',
    )

    # Create object repository with a model object.
    object_repo = MockObjectRepository([
        ModelObject.new(
            name='Attribute',
            type='value_object',
            group_id='object',
            description='An attribute.',
        )]
    )

    # Get the parameter.
    param = sync_parameter_to_code(parameter, object_repo)

    # Assert the parameter is correct.
    assert param.name == 'attribute'
    assert param.type == 'Attribute'
    assert param.description == 'The attribute to add.'


def test_sync_model_code_block_to_code():

    # Create a code block.
    code_block = ObjectMethodCodeBlock.new(
        comments='Add the attribute to the object.',
        lines='self.attributes.append(attribute)',
    )

    # Get the code block.
    sync_code_block = sync_model_code_block_to_code(code_block)

    # Assert the code block is correct.
    assert sync_code_block.comments[0] == 'Add the attribute to the object.'
    assert sync_code_block.lines[0] == 'self.attributes.append(attribute)'


def test_sync_model_code_block_to_code_multiple_lines():

    # Create a code block.
    code_block = ObjectMethodCodeBlock.new(
        comments='Add the attribute to the object.',
        lines='self.attributes.append(attribute)/n/self.attributes.append(attribute)',
    )

    # Get the code block.
    sync_code_block = sync_model_code_block_to_code(code_block)

    # Assert the code block is correct.
    assert sync_code_block.comments[0] == 'Add the attribute to the object.'
    assert sync_code_block.lines[0] == 'self.attributes.append(attribute)'
    assert sync_code_block.lines[1] == 'self.attributes.append(attribute)'


def test_sync_model_method_to_code():

    # Create a mock object repository.
    object_repo = MockObjectRepository([
        ModelObject.new(
            name='Attribute',
            type='value_object',
            group_id='object',
            description='An attribute.',
        )
    ])

    # Create a method with parameters.
    method = ObjectMethod.new(
        name='add_attribute',
        type='state',
        description='Adds an attribute to the object.',
        is_class_method=True,
        parameters=[
            ObjectMethodParameter.new(
                name='attribute',
                type='model',
                type_object_id='attribute',
                description='The attribute to add.',
            )
        ],
        code_block=[
            ObjectMethodCodeBlock.new(
                comments='Add the attribute to the object.',
                lines='self.attributes.append(attribute)',
            )
        ],
    )

    # Get the method.
    sync_method = sync_model_method_to_code(method, object_repo)

    # Assert the method is correct.
    assert sync_method.name == 'add_attribute'
    assert sync_method.description == 'Adds an attribute to the object.'
    assert sync_method.is_class_method == True
    assert len(sync_method.parameters) == 1
    assert sync_method.parameters[0].name == 'attribute'
    assert sync_method.parameters[0].type == 'Attribute'
    assert sync_method.parameters[0].description == 'The attribute to add.'
    assert len(sync_method.code_block) == 1
    assert sync_method.code_block[0].comments[0] == 'Add the attribute to the object.'
    assert sync_method.code_block[0].lines[0] == 'self.attributes.append(attribute)'


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