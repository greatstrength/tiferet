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
    type = sync_parameter_to_code(
        MODEL_OBJ_PARAM_MODEL, MockObjectRepository())

    # Assert the parameter is correct.
    assert type.name == 'attribute'
    assert type.type == 'str'
    assert type.description == 'The attribute to add.'


def test_sync_parameter_to_code_list():

    # Get the parameter.
    param = sync_parameter_to_code(
        MODEL_OBJ_PARAM_LIST, MockObjectRepository())

    # Assert the parameter is correct.
    assert param.name == 'choices'
    assert param.type == 'List[str]'
    assert param.description == 'The choices for the attribute value.'


def test_sync_parameter_to_code_dict():

    # Get the parameter.
    param = sync_parameter_to_code(
        MODEL_OBJ_PARAM_DICT, MockObjectRepository())

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
    sync_code_block = sync_model_code_block_to_code(
        MODEL_OBJ_MET_CODE_BLOCK_MULTILINE)

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
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_BOOL,
        MODEL_OBJ_VALUE_OBJECT,
        MockObjectRepository(),)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'required'
    assert sync_attribute.value == 't.BooleanType(\n    metadata=dict(\n        description=\'Whether the attribute is required.\',\n    ),\n)'


def test_sync_model_attribute_to_code_required():

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(
        attribute=MODEL_OBJ_ATTR_REQUIRED,
        model=MODEL_OBJ_ENTITY,
        object_repo=MockObjectRepository(),
        constants=[],)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'name'
    assert sync_attribute.value == 't.StringType(\n    required=True,\n    metadata=dict(\n        description=\'The name of the object.\',\n    ),\n)'


def test_sync_model_attribute_to_code_default():

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_DEFAULT,
        MODEL_OBJ_VALUE_OBJECT,
        MockObjectRepository(),
        constants,)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'description'
    assert sync_attribute.value == 't.StringType(\n    default=ATTRIBUTE_DESCRIPTION_DEFAULT,\n    metadata=dict(\n        description=\'The description of the object.\',\n    ),\n)'
    assert constants[0].name == 'ATTRIBUTE_DESCRIPTION_DEFAULT'
    assert constants[0].value == "'The object.'"


def test_sync_model_attribute_to_code_default_bool():

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_BOOL_DEFAULT,
        MODEL_OBJ_VALUE_OBJECT,
        MockObjectRepository(),
        constants,)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'pass_on_error'
    assert sync_attribute.value == 't.BooleanType(\n    default=ATTRIBUTE_PASS_ON_ERROR_DEFAULT,\n    metadata=dict(\n        description=\'Whether to pass on error.\',\n    ),\n)'
    assert constants[0].name == 'ATTRIBUTE_PASS_ON_ERROR_DEFAULT'
    assert constants[0].value == 'False'


def test_sync_model_attribute_to_code_choices():

    # Get the attribute with constants.
    constants = []
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_CHOICES,
        MODEL_OBJ_ENTITY,
        MockObjectRepository(),
        constants)

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
    sync_attribute = sync_model_attribute_to_code(
        attribute,
        MODEL_OBJ_ENTITY,
        MockObjectRepository(),
        constants,)

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
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_MODEL, MODEL_OBJ_CORE, object_repo)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'type'
    assert sync_attribute.value == 't.ModelType(\n    Type,\n    metadata=dict(\n        description=\'The object type.\',\n    ),\n)'


def test_sync_model_attribute_to_code_list():

    # Create the mock object repository with the core object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_CORE
    ])

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_LIST, MODEL_OBJ_ENTITY, object_repo)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'choices'
    assert sync_attribute.value == 't.ListType(\n    t.StringType(),\n    metadata=dict(\n        description=\'The choices for the attribute value.\',\n    ),\n)'


def test_sync_model_attribute_to_code_list_model():

    # Create the mock object repository with the core object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_ENTITY,
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_LIST_MODEL_INNER_TYPE, MODEL_OBJ_ENTITY, object_repo)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'attributes'
    assert sync_attribute.value == 't.ListType(\n    t.ModelType(Attribute),\n    metadata=dict(\n        description=\'The attributes for the object.\',\n    ),\n)'


def test_sync_model_attribute_to_code_dict():
    # Create a mock object repository with the entity object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_ENTITY
    ])

    # Get the attribute.
    sync_attribute = sync_model_attribute_to_code(
        MODEL_OBJ_ATTR_DICT, MODEL_OBJ_ENTITY, object_repo)

    # Assert the attribute is correct.
    assert sync_attribute.name == 'metadata'
    assert sync_attribute.value == 't.DictType(\n    t.StringType(),\n    metadata=dict(\n        description=\'The metadata for the attribute.\',\n    ),\n)'


def test_sync_model_object_to_code():

    # Create a mock object repository with the entity object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_ENTITY,
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the model.
    constants = []
    sync_class = sync_model_object_to_code(
        MODEL_OBJ_ENTITY, object_repo, constants)

    # Assert the model is correct.
    assert sync_class.name == 'Object'
    assert sync_class.base_classes == ['Entity']
    assert sync_class.description == 'An object.'
    assert len(sync_class.attributes) == 2
    assert sync_class.attributes[0].name == 'name'
    assert sync_class.attributes[0].value == 't.StringType(\n    required=True,\n    metadata=dict(\n        description=\'The name of the object.\',\n    ),\n)'
    assert sync_class.attributes[1].name == 'attributes'
    assert sync_class.attributes[1].value == 't.ListType(\n    t.ModelType(Attribute),\n    metadata=dict(\n        description=\'The attributes for the object.\',\n    ),\n)'
    assert len(sync_class.methods) == 1
    assert sync_class.methods[0].name == 'add_attribute'
    assert sync_class.methods[0].description == 'Adds an attribute to the object.'
    assert sync_class.methods[0].is_class_method == True
    assert len(sync_class.methods[0].parameters) == 1
    assert sync_class.methods[0].parameters[0].name == 'attribute'
    assert sync_class.methods[0].parameters[0].type == 'Attribute'
    assert sync_class.methods[0].parameters[0].description == 'The attribute to add.'


def test_sync_code_to_model_attribute_str_required():

    # Define the attribute as a variable object.
    variable = Variable.new(
        name='name',
        value='t.StringType(\n    required=True,\n    metadata=dict(\n        description=\'The name of the attribute.\',\n    ),\n)',
    )

    # Get the model attribute.
    model_attribute = sync_code_to_model_attribute(
        variable, MockObjectRepository())

    # Assert the model attribute is correct.
    assert model_attribute.name == 'name'
    assert model_attribute.type == 'str'
    assert model_attribute.required == True
    assert model_attribute.description == 'The name of the attribute.'


def test_sync_code_to_model_attribute_bool_default():

    # Define the attribute as a variable object.
    variable = Variable.new(
        name='pass_on_error',
        value='t.BooleanType(\n    default=ATTRIBUTE_PASS_ON_ERROR_DEFAULT,\n    metadata=dict(\n        description=\'Whether to pass on error.\',\n    ),\n)',
    )

    # Add the constant.
    constants = [
        Variable.new(
            name='ATTRIBUTE_PASS_ON_ERROR_DEFAULT',
            type='bool',
            value='False',
        )
    ]

    # Get the model attribute.
    model_attribute = sync_code_to_model_attribute(
        variable, MockObjectRepository(), constants)

    # Assert the model attribute is correct.
    assert model_attribute.name == 'pass_on_error'
    assert model_attribute.type == 'bool'
    assert model_attribute.default == 'False'
    assert model_attribute.description == 'Whether to pass on error.'


def test_sync_code_to_model_attribute_str_choices():

    # Define the attribute as a variable object.
    variable = Variable.new(
        name='type',
        value='t.StringType(\n    choices=OBJECT_TYPE_CHOICES,\n    metadata=dict(\n        description=\'The type of the object.\',\n    ),\n)',
    )

    # Add the constant.
    constants = [
        Variable.new(
            name='OBJECT_TYPE_CHOICES',
            value="[\n    'entity',\n    'value_object',\n    'context'\n]",
        )
    ]

    # Get the model attribute.
    model_attribute = sync_code_to_model_attribute(
        variable, MockObjectRepository(), constants)

    # Assert the model attribute is correct.
    assert model_attribute.name == 'type'
    assert model_attribute.type == 'str'
    assert model_attribute.choices == ['entity', 'value_object', 'context']
    assert model_attribute.description == 'The type of the object.'


def test_sync_code_to_model_attribute_list_str():

    # Define the attribute as a variable object.
    variable = Variable.new(
        name='choices',
        value='t.ListType(\n    t.StringType,\n    metadata=dict(\n        description=\'The choices for the attribute value.\',\n    ),\n)',
    )

    # Get the model attribute.
    model_attribute = sync_code_to_model_attribute(
        variable, MockObjectRepository())

    # Assert the model attribute is correct.
    assert model_attribute.name == 'choices'
    assert model_attribute.type == 'list'
    assert model_attribute.inner_type == 'str'
    assert model_attribute.description == 'The choices for the attribute value.'


def test_sync_code_to_model_attribute_model():

    # Define the attribute as a variable object.
    variable = Variable.new(
        name='type',
        value='t.ModelType(\n    Type,\n    metadata=dict(\n        description=\'The object type.\',\n    ),\n)',
    )

    # Create a mock object repository with the Type model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_CORE
    ])

    # Get the model attribute.
    model_attribute = sync_code_to_model_attribute(variable, object_repo)

    # Assert the model attribute is correct.
    assert model_attribute.name == 'type'
    assert model_attribute.type == 'model'
    assert model_attribute.type_object_id == 'type'
    assert model_attribute.description == 'The object type.'


def test_sync_code_to_model_attribute_list_model():

    # Define the attribute as a variable object.
    variable = Variable.new(
        name='attributes',
        value='t.ListType(\n    t.ModelType(Attribute),\n    metadata=dict(\n        description=\'The attributes for the object.\',\n    ),\n)',
    )

    # Create a mock object repository with the Attribute model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the model attribute.
    model_attribute = sync_code_to_model_attribute(variable, object_repo)

    # Assert the model attribute is correct.
    assert model_attribute.name == 'attributes'
    assert model_attribute.type == 'list'
    assert model_attribute.inner_type == 'model'
    assert model_attribute.type_object_id == 'attribute'
    assert model_attribute.description == 'The attributes for the object.'


def test_sync_code_to_model_parameter_required():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='id',
        type='str',
        description='The id of the object.',
    )

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(
        sync_parameter, MockObjectRepository())

    # Assert the model parameter is correct.
    assert parameter.name == 'id'
    assert parameter.type == 'str'
    assert parameter.description == 'The id of the object.'
    assert parameter.required == True


def test_sync_code_to_model_parameter_not_required():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='class_name',
        type='str',
        description='The class name.',
        default='None',
    )

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(
        sync_parameter, MockObjectRepository())

    # Assert the model parameter is correct.
    assert parameter.name == 'class_name'
    assert parameter.type == 'str'
    assert parameter.description == 'The class name.'
    assert parameter.required == False
    assert parameter.default == None


def test_sync_code_to_model_parameter_default():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='type',
        type='str',
        description='The type of the object.',
        default='entity',
    )

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(
        sync_parameter, MockObjectRepository())

    # Assert the model parameter is correct.
    assert parameter.name == 'type'
    assert parameter.type == 'str'
    assert parameter.description == 'The type of the object.'
    assert parameter.required == False
    assert parameter.default == 'entity'


def test_sync_code_to_model_parameter_list():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='choices',
        type='typing.List[str]',
        description='The choices for the attribute value.',
    )

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(
        sync_parameter, MockObjectRepository())

    # Assert the model parameter is correct.
    assert parameter.name == 'choices'
    assert parameter.type == 'list'
    assert parameter.inner_type == 'str'
    assert parameter.description == 'The choices for the attribute value.'


def test_sync_code_to_model_parameter_dict():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='metadata',
        type='typing.Dict[str, str]',
        description='The metadata for the attribute.',
    )

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(
        sync_parameter, MockObjectRepository())

    # Assert the model parameter is correct.
    assert parameter.name == 'metadata'
    assert parameter.type == 'dict'
    assert parameter.inner_type == 'str'
    assert parameter.description == 'The metadata for the attribute.'


def test_sync_code_to_model_parameter_model():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='attribute',
        type='Attribute',
        description='The attribute to add.',
    )

    # Create a mock object repository with the Attribute model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(sync_parameter, object_repo)

    # Assert the model parameter is correct.
    assert parameter.name == 'attribute'
    assert parameter.type == 'model'
    assert parameter.type_object_id == 'attribute'
    assert parameter.description == 'The attribute to add.'


def test_sync_code_to_model_parameter_list_model_inner_type():

    # Define a parameter object.
    sync_parameter = Parameter.new(
        name='attributes',
        type='typing.List[Attribute]',
        description='The attributes for the object.',
    )

    # Create a mock object repository with the Attribute model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Get the model parameter.
    parameter = sync_code_to_model_parameter(sync_parameter, object_repo)

    # Assert the model parameter is correct.
    assert parameter.name == 'attributes'
    assert parameter.type == 'list'
    assert parameter.inner_type == 'model'
    assert parameter.type_object_id == 'attribute'
    assert parameter.description == 'The attributes for the object.'


def test_sync_code_to_model_code_block():

    # Define a code block object.
    sync_code_block = CodeBlock.new(
        comments=['Add the attribute to the object.'],
        lines=['self.attributes.append(attribute)'],
    )

    # Get the model code block.
    code_block = sync_code_to_model_code_block(sync_code_block)

    # Assert the model code block is correct.
    assert code_block.comments == 'Add the attribute to the object.'
    assert code_block.lines == 'self.attributes.append(attribute)'


def test_sync_code_to_model_code_block_multiple_lines():

    # Define a code block object.
    sync_code_block = CodeBlock.new(
        comments=['Validate and return the model object.'],
        lines=['model_obj.validate()', 'return model_obj'],
    )

    # Get the model code block.
    code_block = sync_code_to_model_code_block(sync_code_block)

    # Assert the model code block is correct.
    assert code_block.comments == 'Validate and return the model object.'
    assert code_block.lines == 'model_obj.validate()/n/return model_obj'


def test_sync_code_to_model_method():

    # Create a mock object repository with the Attribute model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Define a method object.
    sync_method = Function.new(
        name='add_attribute',
        description='Adds an attribute to the object.',
        is_class_method=True,
        parameters=[
            Parameter.new(
                name='attribute',
                type='Attribute',
                description='The attribute to add.',
            )
        ],
        code_block=[
            CodeBlock.new(
                comments=['Add the attribute to the object.'],
                lines=['self.attributes.append(attribute)'],
            )
        ],
    )

    # Get the model method.
    method = sync_code_to_model_method(sync_method, object_repo)

    # Assert the model method is correct.
    assert method.name == 'add_attribute'
    assert method.description == 'Adds an attribute to the object.'
    assert len(method.parameters) == 1
    assert method.parameters[0].name == 'attribute'
    assert method.parameters[0].type == 'model'
    assert method.parameters[0].type_object_id == 'attribute'
    assert method.parameters[0].description == 'The attribute to add.'
    assert len(method.code_block) == 1
    assert method.code_block[0].comments == 'Add the attribute to the object.'
    assert method.code_block[0].lines == 'self.attributes.append(attribute)'


def test_sync_code_to_model_method_list_return_type():

    # Create a mock object repository with the Attribute model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Define a method object.
    sync_method = Function.new(
        name='list',
        return_type='List[Attribute]',
        return_description='The list of attributes.',
        description='List all attributes.',
        is_class_method=True,
    )

    # Get the model method.
    method = sync_code_to_model_method(sync_method, object_repo)

    # Assert the model method is correct.
    assert method.name == 'list'
    assert method.description == 'List all attributes.'
    assert method.return_type == 'list'
    assert method.return_inner_type == 'model'
    assert method.return_type_object_id == 'attribute'
    assert method.return_description == 'The list of attributes.'


def test_sync_code_to_model_method_dict_return_type():

    # Create a mock object repository with the Attribute model object.
    object_repo = MockObjectRepository([
        MODEL_OBJ_VALUE_OBJECT
    ])

    # Define a method object.
    sync_method = Function.new(
        name='get',
        return_type='Dict[str, Attribute]',
        return_description='The attributes as a dictionary.',
        description='Get all attributes.',
        is_class_method=True,)

    # Get the model method.
    method = sync_code_to_model_method(sync_method, object_repo)

    # Assert the model method is correct.
    assert method.name == 'get'
    assert method.description == 'Get all attributes.'
    assert method.return_type == 'dict'
    assert method.return_inner_type == 'model'
    assert method.return_type_object_id == 'attribute'
    assert method.return_description == 'The attributes as a dictionary.'


def test_sync_code_to_model():

    # Get the model object.
    model_object = sync_code_to_model_object(
        'object', SYNC_CLASS_EMPTY, MockObjectRepository())

    # Assert the model object is correct.
    assert model_object.name == 'Object'
    assert model_object.group_id == 'object'
    assert model_object.class_name == 'Object'
    assert model_object.type == 'entity'
    assert model_object.description == 'An object.'


def test_sync_code_to_model_value_object():

    # Create the attribute class object.
    attribute = Class.new(
        name='Attribute',
        description='An attribute.',
        base_classes=['ValueObject'],
        attributes=[
            Variable.new(
                name='name',
                value='t.StringType(\n    required=True,\n    metadata=dict(\n        description=\'The name of the attribute.\',\n    ),\n)',
            ),
        ],
        methods=[],
    )

    # Get the model object.
    model_object = sync_code_to_model_object(
        'object', attribute, MockObjectRepository())

    # Assert the model object is correct.
    assert model_object.name == 'Attribute'
    assert model_object.group_id == 'object'
    assert model_object.class_name == 'Attribute'
    assert model_object.type == 'value_object'
    assert model_object.description == 'An attribute.'
    assert len(model_object.attributes) == 1
    assert model_object.attributes[0].name == 'name'
    assert model_object.attributes[0].type == 'str'
    assert model_object.attributes[0].required == True
    assert model_object.attributes[0].description == 'The name of the attribute.'
