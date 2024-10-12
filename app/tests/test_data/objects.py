from ...objects import *


MODEL_OBJ_ATTR_BOOL = ObjectAttribute.new(
    name='required',
    type='bool',
    description='Whether the attribute is required.',
)

MODEL_OBJ_ATTR_BOOL_DEFAULT = ObjectAttribute.new(
    name='Pass on Error',
    type='bool',
    description='Whether to pass on error.',
    default='False',
)

MODEL_OBJ_ATTR_REQUIRED = ObjectAttribute.new(
    name='name',
    type='str',
    description='The name of the object.',
    required=True,
)

MODEL_OBJ_ATTR_DEFAULT = ObjectAttribute.new(
    name='description',
    type='str',
    description='The description of the object.',
    default='The object.',
)

MODEL_OBJ_ATTR_CHOICES = ObjectAttribute.new(
    name='type',
    type='str',
    description='The type of the object.',
    choices=['entity', 'value_object', 'context'],
)

MODEL_OBJ_PARAM_ANY = ObjectMethodParameter.new(
        name='component',
        type='any',
        description='The component to add.',
    )

MODEL_OBJ_PARAM_MODEL = ObjectMethodParameter.new(
    name='attribute',
    type='str',
    description='The attribute to add.',
)

MODEL_OBJ_PARAM_LIST = ObjectMethodParameter.new(
    name='choices',
    type='list',
    inner_type='str',
    description='The choices for the attribute value.',
)

MODEL_OBJ_PARAM_DICT = ObjectMethodParameter.new(
    name='metadata',
    type='dict',
    inner_type='str',
    description='The metadata for the attribute.',
)

MODEL_OBJ_ATTR_MODEL_LIST = ObjectMethodParameter.new(
    name='attributes',
    type='list',
    inner_type='model',
    type_object_id='attribute',
    description='The attributes to add to the object.',
)

MODEL_OBJ_ENTITY = ModelObject.new(
    name='Object',
    type='entity',
    group_id='model',
    description='The object.',
    attributes=[
        MODEL_OBJ_ATTR_REQUIRED,
    ]
)

MODEL_OBJ_MET_PARAM_MODEL = ObjectMethodParameter.new(
    name='attribute',
    type='model',
    type_object_id='attribute',
    description='The attribute to add.'
)

MODEL_OBJ_MET_CODE_BLOCK = ObjectMethodCodeBlock.new(
    comments='Add the attribute to the object.',
    lines='self.attributes.append(attribute)',
)

MODEL_OBJ_MET_CODE_BLOCK_MULTILINE = ObjectMethodCodeBlock.new(

        comments='Validate and return the model object.',
        lines='model_obj.validate()/n/return model_obj'
)

MODEL_OBJ_MET_STATE = ObjectMethod.new(
    name='add_attribute',
    type='state',
    description='Adds an attribute to the object.',
    is_class_method=True,
    parameters = [
        MODEL_OBJ_MET_PARAM_MODEL
    ],
    code_block=[
        ObjectMethodCodeBlock.new(
            comments='Add the attribute to the object.',
            lines='self.attributes.append(attribute)',
        )
    ]
)

MODEL_OBJ_VALUE_OBJECT = ModelObject.new(
    name='Attribute',
    type='value_object',
    group_id='object',
    description='An attribute.',
)

SYNC_CLASS_EMPTY = Class.new(
    name='Object',
    description='An object.',
    base_classes=['Entity'],
)

ATTRIBUTE_MODEL_OBJECT = ModelObject.new(
    name='Attribute',
    group_id='model',
    description='The attribute object.',
    attributes=[
        ObjectAttribute.new(
            name='Name',
            type='str',
            description='The name of the attribute.',
            required=True,
        ),
    ]
)

CONTEXT_MODEL_OBJECT = ModelObject.new(
    name='Context',
    group_id='context',
    description='The context object.',
    attributes=[
        ObjectAttribute.new(
            name='Name',
            type='str',
            description='The name of the context.',
            required=True,
        ),
        ObjectAttribute.new(
            name='Group ID',
            type='str',
            description='The group ID of the context.',
            required=True,
        ),
        ObjectAttribute.new(
            name='Description',
            type='str',
            description='The description of the context.',
            required=False,
        ),
    ],
    methods=[
        ObjectMethod.new(
            name='Add Attribute',
            type='state',
            description='Adds an attribute to the context.',
            parameters=[
                ObjectMethodParameter.new(
                    name='attribute',
                    type='model',
                    required=True,
                    description='The attribute object.',
                    type_object_id='attribute',
                )
            ],
        )
    ]
)