from ...objects.object import ModelObject
from ...objects.object import ObjectAttribute
from ...objects.sync import Class
from ...services.sync import *
from ..mocks import MockObjectRepository
from ..test_data import *


def test_get_model_attribute_type():

    # Loop through the model attribute types.
    for type, variable_type in MODEL_ATTRIBUTE_TYPES.items():

        # Get the model attribute type.
        model_attribute_type = get_model_attribute_type(variable_type)

        # Assert the model attribute type is correct.
        assert model_attribute_type == type


def test_sync_parameter_to_code_any():

    # Get the parameter.
    param = sync_parameter_to_code(MODEL_OBJ_PARAM_ANY, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'component'
    assert param.type == 'Any'
    assert param.description == 'The component to add.'


def test_sync_parameter_to_code_non_compound():

    # Get the parameter.
    type = sync_parameter_to_code(MODEL_OBJ_PARAM_MODEL, MockObjectRepository())

    # Assert the parameter is correct.
    assert type.name == 'attribute'
    assert type.type == 'str'
    assert type.description == 'The attribute to add.'


def test_sync_parameter_to_code_list():

    # Get the parameter.
    param = sync_parameter_to_code(MODEL_OBJ_PARAM_LIST, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'choices'
    assert param.type == 'List[str]'
    assert param.description == 'The choices for the attribute value.'


def test_sync_parameter_to_code_dict():

    # Get the parameter.
    param = sync_parameter_to_code(MODEL_OBJ_PARAM_DICT, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'metadata'
    assert param.type == 'Dict[str, str]'
    assert param.description == 'The metadata for the attribute.'


def test_sync_parameter_to_code_model_compound():

    # Create object repository with a model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the parameter.
    param = sync_parameter_to_code(MODEL_OBJ_ATTR_MODEL_LIST, object_repo)

    # Assert the parameter is correct.
    assert param.name == 'attributes'
    assert param.type == 'List[Attribute]'
    assert param.description == 'The attributes to add to the object.'


def test_sync_parameter_to_code_model():

    # Create object repository with a model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the parameter.
    param = sync_parameter_to_code(MODEL_OBJ_MET_PARAM_MODEL, object_repo)

    # Assert the parameter is correct.
    assert param.name == 'attribute'
    assert param.type == 'Attribute'
    assert param.description == 'The attribute to add.'


def test_sync_model_code_block_to_code():

    # Get the code block.
    sync_code_block = sync_model_code_block_to_code(MODEL_OBJ_MET_CODE_BLOCK)

    # Assert the code block is correct.
    assert sync_code_block.comments[0] == 'Add the attribute to the object.'
    assert sync_code_block.lines[0] == 'self.attributes.append(attribute)'


def test_sync_model_code_block_to_code_multiple_lines():

    # Get the code block.
    sync_code_block = sync_model_code_block_to_code(MODEL_OBJ_MET_CODE_BLOCK_MULTILINE)

    # Assert the code block is correct.
    assert sync_code_block.comments[0] == 'Validate and return the model object.'
    assert sync_code_block.lines[0] == 'model_obj.validate()'
    assert sync_code_block.lines[1] == 'return model_obj'


def test_sync_model_method_to_code():

    # Create a mock object repository.
    object_repo = MockObjectRepository([
        MODEL_OBJ_ENTITY,
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the method.
    sync_method = sync_model_method_to_code(MODEL_OBJ_MET_STATE, object_repo)

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


def test_sync_model_attribute_to_code():

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(MODEL_OBJ_ATTR_BOOL, MODEL_OBJ_VALUE_OBJECT)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'required'
    assert sync_attribute.value == 't.BooleanType(\n    metadata=dict(\n        description=\'Whether the attribute is required.\',\n    ),\n)'


def test_sync_model_attribute_to_code_required():

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(
        attribute=MODEL_OBJ_ATTR_REQUIRED, 
        model=MODEL_OBJ_ENTITY,
        constants=[],
    )

    # Assert the attribute is correct.
    assert sync_attribute.name == 'name'
    assert sync_attribute.value == 't.StringType(\n    required=True,\n    metadata=dict(\n        description=\'The name of the object.\',\n    ),\n)'


def test_sync_model_attribute_to_code_default():

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(MODEL_OBJ_ATTR_DEFAULT, MODEL_OBJ_VALUE_OBJECT, constants)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'description'
    assert sync_attribute.value == 't.StringType(\n    default=ATTRIBUTE_DESCRIPTION_DEFAULT,\n    metadata=dict(\n        description=\'The description of the object.\',\n    ),\n)'
    assert constants[0].name == 'ATTRIBUTE_DESCRIPTION_DEFAULT'
    assert constants[0].value == "'The object.'"


def test_sync_model_attribute_to_code_default_bool():

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(MODEL_OBJ_ATTR_BOOL_DEFAULT, MODEL_OBJ_VALUE_OBJECT, constants)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'pass_on_error'
    assert sync_attribute.value == 't.BooleanType(\n    default=ATTRIBUTE_PASS_ON_ERROR_DEFAULT,\n    metadata=dict(\n        description=\'Whether to pass on error.\',\n    ),\n)'
    assert constants[0].name == 'ATTRIBUTE_PASS_ON_ERROR_DEFAULT'
    assert constants[0].value == 'False'


def test_sync_model_attribute_to_code_choices():

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(MODEL_OBJ_ATTR_CHOICES, MODEL_OBJ_ENTITY, constants)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'type'
    assert sync_attribute.value == 't.StringType(\n    choices=OBJECT_TYPE_CHOICES,\n    metadata=dict(\n        description=\'The type of the object.\',\n    ),\n)'
    assert constants[0].name == 'OBJECT_TYPE_CHOICES'
    assert constants[0].value == "[\n    'entity',\n    'value_object',\n    'context',\n]"


def test_sync_model_attribute_to_code_default_and_choices():

    # Create an attribute.
    attribute = MODEL_OBJ_ATTR_CHOICES
    attribute.default = 'entity'

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(attribute, MODEL_OBJ_ENTITY, constants)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'type'
    assert sync_attribute.value == 't.StringType(\n    default=OBJECT_TYPE_DEFAULT,\n    choices=OBJECT_TYPE_CHOICES,\n    metadata=dict(\n        description=\'The type of the object.\',\n    ),\n)'
    assert constants[0].name == 'OBJECT_TYPE_DEFAULT'
    assert constants[0].value == "'entity'"
    assert constants[1].name == 'OBJECT_TYPE_CHOICES'
    assert constants[1].value == "[\n    'entity',\n    'value_object',\n    'context',\n]"


def test_sync_model_attribute_to_code_model():

    # Create a mock object repository with the Type model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_CORE
    ])

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(MODEL_OBJ_ATTR_MODEL, MODEL_OBJ_CORE, object_repo)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'type'
    assert sync_attribute.value == 't.ModelType(\n    Type,\n    metadata=dict(\n        description=\'The object type.\',\n    ),\n)'

def test_sync_model_attribute_to_code_list():

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(MODEL_OBJ_ATTR_LIST, MODEL_OBJ_ENTITY)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'choices'
    assert sync_attribute.value == 't.ListType(\n    t.StringType(),\n    metadata=dict(\n        description=\'The choices for the attribute value.\',\n    ),\n)'

def test_sync_code_to_model():

    # Get the model object.
    model_object = sync_code_to_model('object', SYNC_CLASS_EMPTY, MockObjectRepository())

    # Assert the model object is correct.
    assert model_object.name == 'Object'
    assert model_object.group_id == 'object'
    assert model_object.class_name == 'Object'
    assert model_object.type == 'entity'
    assert model_object.description == 'An object.'