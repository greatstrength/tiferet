#** imp

import typing

from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute
from ..objects.object import ObjectMethod
from ..objects.object import ObjectMethodParameter
from ..objects.object import ObjectMethodCodeBlock
from ..objects.object import OBJECT_TYPE_ENTITY
from ..objects.object import OBJECT_TYPE_VALUE_OBJECT
from ..objects.object import METHOD_PARAMETER_INNER_TYPE_CHOICES
from ..objects.sync import Class
from ..objects.sync import Function
from ..objects.sync import Parameter
from ..objects.sync import Variable
from ..objects.sync import Module
from ..objects.sync import Import
from ..objects.sync import CodeBlock
from ..objects.sync import MODULE_TYPE_OBJECTS
from ..objects.sync import TAB
from ..repositories.object import ObjectRepository

#** con

MODEL_ATTRIBUTE_TYPES = {
    'str': 't.StringType',
    'int': 't.IntType',
    'float': 't.FloatType',
    'bool': 't.BooleanType',
    'date': 't.DateType',
    'datetime': 't.DateTimeType',
    'list': 't.ListType',
    'dict': 't.DictType',
    'model': 't.ModelType',
} #/

#** fun

def get_model_attribute_type(varable_type: str) -> str:
    '''
    Gets the model attribute type.

    :param varable_type: The variable type.
    :type varable_type: str
    :return: The model attribute type.
    :rtype: str
    '''

    # Map on the model attribute types.
    for k, v in MODEL_ATTRIBUTE_TYPES.items():
        if v == varable_type:
            return k 


def sync_parameter_to_code(parameter: ObjectMethodParameter, object_repo: ObjectRepository) -> Parameter:
    '''
    Syncs a parameter to code.

    :param parameter: The parameter.
    :type parameter: ObjectMethodParameter
    :param object_repo: The object repository.
    :type object_repo: ObjectRepository
    :return: The parameter.
    :rtype: Parameter
    '''

    # Get the parameter object.
    param_obj = object_repo.get(parameter.type_object_id)

    # Sync the parameter type.
    type = ''.join([
        # If the parameter is not an any, list, dict, model, return the parameter type.
        parameter.type if parameter.type not in ['any', 'list', 'dict', 'model'] else '',
        # If the parameter type is not set, return 'Any'.
        'Any' if parameter.type == 'any' else '',
        # If the parameter is a list, set the type as 'List['.
        'List[' if parameter.type == 'list' else '',
        # If the parameter is a dict, set the type as 'Dict['.
        'Dict[str, ' if parameter.type == 'dict' else '',
        # If the parameter inner type is a model, use the model class name.
        f'{param_obj.class_name}]' if parameter.inner_type == 'model' else '',
        # Otherwise, use the inner type.
        f'{parameter.inner_type}]' if parameter.inner_type and parameter.inner_type != 'model' else '',
        # If the parameter type is a model, set the type as the model class name.
        param_obj.class_name if parameter.type == 'model' else '',
    ])

    # Create and return the parameter.
    return Parameter.new(
        name=parameter.name,
        type=type,
        default=parameter.default,
        description=parameter.description
    )


def sync_model_method_to_code(method: ObjectMethod, object_repo: ObjectRepository) -> Function:
    '''
    Syncs a method to code.

    :param method: The method.
    :type method: ObjectMethod
    :param object_repo: The object repository.
    :type object_repo: ObjectRepository
    :return: The function.
    :rtype: Function
    '''

    # Create the parameters.
    parameters = [sync_parameter_to_code(
        param, object_repo) for param in method.parameters]

    # Create the function.
    function = Function.new(
        name=method.name,
        description=method.description,
        parameters=parameters,
        return_type=method.return_type,
        return_description=method.return_description,
        code_block=method.code_block
    )

    # Return the function.
    return function


def sync_model_attribute_to_code(attribute: ObjectAttribute, model: ModelObject, constants: typing.List[Variable] = []) -> Variable:
    '''
    Syncs an attribute to code.

    :param attribute: The attribute.
    :type attribute: ObjectAttribute
    :param model: The model object.
    :type model: ModelObject
    :param constants: The constants.
    :type constants: List[Variable]
    :return: The variable.
    :rtype: Variable
    '''

    # Set the value and model name.
    value = []
    model_name = model.name.replace(' ', '_').upper()

    # Map on the attribute type for non-compound types.
    if attribute.type in ['str', 'int', 'float', 'bool', 'date', 'datetime']:
        value.append(f'{MODEL_ATTRIBUTE_TYPES[attribute.type]}(')

    # Check if the attribute is required.
    if attribute.required:
        value.append(f'\n{TAB}required=True,')

    # Check if there is a default value.
    if attribute.default:
        variable = Variable.new(
            name=f'{model_name}_{attribute.name.upper()}_DEFAULT',
            value=f'\'{attribute.default}\'' if attribute.type == 'str' else attribute.default
        )
        constants.append(variable)
        value.append(f'\n{TAB}default={variable.name},')

    # Add the choices and constants if choices are provided.
    if attribute.choices:
        values_list = f',\n{TAB}'.join(
            [f'\'{choice}\'' if attribute.type == 'str' else choice for choice in attribute.choices])
        variable = Variable.new(
            name=f'{model_name}_{attribute.name.upper()}_CHOICES',
            value=f'[\n{TAB}{values_list}\n]'
        )
        constants.append(variable)
        value.append(f'\n{TAB}choices={variable.name},')

    # Add the metadata with the description.
    value.append(f'\n{TAB}metadata=dict(')
    value.append(f'\n{TAB*2}description=\'{attribute.description}\',')
    value.append(f'\n{TAB}),')
    value.append('\n)')

    # Create the variable.
    variable = Variable.new(
        name=attribute.name,
        value=''.join(value)
    )

    # Return the variable.
    return variable


def sync_model_to_code(model_object: ModelObject, object_repo: ObjectRepository, base_model: ModelObject = None, constants: typing.List[Variable] = []) -> tuple:
    '''
    Syncs a model object to code.

    :param model_object: The model object.
    :type model_object: ModelObject
    :param base_model: The base model object.
    :type base_model: ModelObject
    :return: The class.
    :rtype
    '''

    # Format the base classes as a list.
    base_classes = []

    # If the base model exists...
    if base_model:

        # Add the base model class name to the base classes.
        base_classes.append(base_model.class_name)

    # If the model object has no base classes...
    if not base_classes:

        # Set the base class name to Entity if the object type is 'entity'.
        if model_object.type == OBJECT_TYPE_ENTITY:
            base_classes.append('Entity')

        # Set the base class name to ValueObject if the object type is 'value_object'.
        elif model_object.type == OBJECT_TYPE_VALUE_OBJECT:
            base_classes.append('ValueObject')

    # Create the class attributes.
    attributes = []
    methods = []
    constants = []

    # Map on the model object attributes.
    for attribute in model_object.attributes:

        # Sync the attribute to code.
        attributes.append(sync_model_attribute_to_code(
            attribute, model_object, constants))

    # Map on the model object methods.
    for method in model_object.methods:

        # Sync the method to code.
        methods.append(sync_model_method_to_code(method, object_repo))

    # Create the class.
    _class = Class.new(
        name=model_object.class_name,
        description=model_object.description,
        base_classes=base_classes,
        attributes=attributes,
        methods=methods
    )

    # Return the class and constants.
    return _class, constants


def sync_code_to_attribute(variable: Variable, object_repo: ObjectRepository, constants: typing.List[Variable] = []) -> ObjectAttribute:
    '''
    Syncs class attribute code into a model object attribute.
    '''

    # Set the attribute type.
    type = 'str'
    inner_type = None
    type_object_id = None
    required = False
    default = None
    choices = []

    # Map the attribute type.
    type = get_model_attribute_type(variable.value.split('(')[0])

    # Split and format the settings.
    settings = '('.join(variable.value.split('(')[1:]).strip()
    settings = settings.replace('\n', '').replace(
        TAB, ' ').replace('\'', '').split(', ')
    for setting in settings:
        if type in ['list', 'dict'] and 't.' in setting:
            inner_type = get_model_attribute_type(setting)
        elif 'required=True' in setting:
            required = True
        elif 'default=' in setting:
            default = setting.split('=')[1]
            const = next((constant for constant in constants if constant.name == default), None)
            default = const.value.strip('\'') if const else default
        elif 'choices=' in setting:
            const = next((constant for constant in constants if constant.name == setting.split('=')[1]), None)
            choices = const.value.strip('[').strip(']').replace(TAB, '').replace('\n', '').split(',') if const else setting.split('=')[1]
            if type == 'str':
                choices = [choice.strip('\'') for choice in choices]
        elif 'metadata=' in setting:
            setting = setting.replace('metadata=dict(', '').replace(')', '')
            description = setting.split('=')[1].strip()
        elif type == 'model' and 't.' not in setting:
            type_object_id = object_repo.get(class_name=setting).id

    # Create the model object attribute.
    return ObjectAttribute.new(
        name=variable.name,
        description=description,
        type=type,
        inner_type=inner_type,
        type_object_id=type_object_id,
        required=required,
        default=default,
        choices=choices
    )


def sync_code_to_parameter(parameter: Parameter, object_repo: ObjectRepository) -> ObjectMethodParameter:
    '''
    Syncs class parameter code into a model object parameter.
    
    :param parameter: The parameter.
    :type parameter: Parameter
    :param object_repo: The object repository.
    :type object_repo: ObjectRepository
    :return: The model object parameter.
    :rtype: ObjectMethodParameter
    '''

    # Set the parameter type.
    type = 'str'
    inner_type = None
    type_object_id = None
    required = False

    # Map on the parameter type for non-compound types.
    if 'List' in parameter.type:
        type = 'list'
        inner_type = parameter.type[12:-1]
    elif 'Dict' in parameter.type:
        type = 'dict'
        inner_type = parameter.type[12:-1].split(',')[1]
    elif parameter.type not in ['str', 'int', 'float', 'bool', 'date', 'datetime', 'type']:
        type = 'model'
        type_object_id = object_repo.get(class_name=parameter.type).id
    else:
        type = parameter.type

    # Set the type object id if the inner type is a model.
    if inner_type and inner_type not in METHOD_PARAMETER_INNER_TYPE_CHOICES:
        type_object_id = object_repo.get(class_name=inner_type).id
        inner_type = 'model'

    # Set required to true if the default value is not set.
    if not parameter.default:
        required = True

    # Create the model object parameter.
    return ObjectMethodParameter.new(
        name=parameter.name,
        description=parameter.description,
        type=type,
        inner_type=inner_type,
        type_object_id=type_object_id,
        required=required,
        default=parameter.default
    )


def sync_code_to_code_block(code_block: CodeBlock) -> ObjectMethodCodeBlock:
    '''
    Syncs class code block code into a model object code block.
    '''

    # Format the code block lines.
    lines = '/n/'.join(code_block.lines).replace(TAB,
                                                 '/t/') if code_block.lines else None

    # Create the model object code block.
    return ObjectMethodCodeBlock.new(
        comments='/n/'.join(code_block.comments) if code_block.comments else None,
        lines=lines
    )


def sync_code_to_method(function: Function, object_repo: ObjectRepository, constants: typing.List[Variable] = []) -> ObjectMethod:
    '''
    Syncs class method code into a model object method.

    :param function: The function.
    :type function: Function
    :param object_repo: The object repository.
    :type object_repo: ObjectRepository
    :param constants: The constants.
    :type constants: List[Variable]
    :return: The model object method.
    :rtype: ObjectMethod
    '''

    # Check to see if the return type is a model.
    return_type = None
    return_inner_type = None
    return_type_object_id = None

    # If the return type is a standard type...
    if function.return_type in ['str', 'int', 'float', 'bool', 'date', 'datetime']:
        return_type = function.return_type
    elif function.return_type and 'List[' in function.return_type:
        return_type = 'list'
        return_inner_type = function.return_type[5:-1]
    elif function.return_type and 'Dict[' in function.return_type:
        return_type = 'dict'
        return_inner_type = function.return_type[5:-1].split(',')[1]
    elif function.return_type and function.return_type not in ['str', 'int', 'float', 'bool', 'date', 'datetime']:
        return_type = 'model'
        return_type_object_id = object_repo.get(
            class_name=function.return_type).id

    return ObjectMethod.new(
        name=function.name,
        type='factory' if function.is_static_method else 'state',
        description=function.description,
        parameters=[sync_code_to_parameter(
            param, object_repo) for param in function.parameters if not param.is_kwargs],
        return_type=return_type,
        return_inner_type=return_inner_type,
        return_type_object_id=return_type_object_id,
        return_description=function.return_description,
        code_block=[sync_code_to_code_block(
            code_block) for code_block in function.code_block]
    )


def sync_code_to_model(group_id: str, _class: Class, object_repo: ObjectRepository, constants: typing.List[Variable] = []) -> ModelObject:
    '''
    Syncs code to a model object.

    :param group_id: The context group id.
    :type group_id: str
    :param _class: The class.
    :type _class: Class
    :param object_repo: The object repository.
    :type object_repo: ObjectRepository
    :param constants: The constants.
    :type constants: List[Variable]
    :return: The model object.
    :rtype: ModelObject
    '''

    # Import the regular expression module.
    # Reformat the class name.
    import re
    name = re.findall('[A-Z][^A-Z]*', _class.name)
    name = ' '.join(name).title()

    # Create the model object attributes from the class attributes.
    attributes = [sync_code_to_attribute(
        attribute, object_repo, constants) for attribute in _class.attributes]

    # Create the model object methods from the class methods.
    methods = [sync_code_to_method(method, object_repo, constants)
               for method in _class.methods]

    # Set the model object type.
    base_type_id = None
    type = OBJECT_TYPE_ENTITY if 'Entity' in _class.base_classes else None
    if not type:
        type = OBJECT_TYPE_VALUE_OBJECT if 'ValueObject' in _class.base_classes else None
    if not type:
        type = 'model' if 'Model' in _class.base_classes else None
    if not type:
        for base_class in _class.base_classes:
            base_class = object_repo.get(class_name=base_class)
            type = base_class.type
            base_type_id = base_class.id
            if type:
                break

    # Create the model object.
    model = ModelObject.new(
        name=name,
        group_id=group_id,
        class_name=_class.name,
        type=type,
        description=_class.description,
        base_type_id=base_type_id,
        attributes=attributes,
        methods=methods
    )

    # Return the model object.
    return model


def create_module(type: str, name: str) -> Module:
    '''
    Create a new module.

    :param type: The module type.
    :type type: str
    :param name: The module name.
    :type name: str
    :return: The module.
    :rtype: Module
    '''

    # If the module type is an object...
    if type == MODULE_TYPE_OBJECTS:

        # Create new module imports.
        imports = [
            Import(dict(
                type='core',
                import_module='typing'
            )),
            Import(dict(
                type='infra',
                from_module='schematics',
                import_module='Model'
            )),
            Import(dict(
                type='infra',
                from_module='schematics',
                import_module='types',
                alias='t'
            )),
            Import(dict(
                type='app',
                from_module='..objects.object',
                import_module='Entity'
            )),
            Import(dict(
                type='app',
                from_module='..objects.object',
                import_module='ValueObject'
            ))]

    # Create the module.
    module = Module.new(
        imports=imports,
        type=type,
        id=name
    )

    # Return the module.
    return module
