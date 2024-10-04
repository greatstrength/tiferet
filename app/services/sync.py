import typing

from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute
from ..objects.object import ObjectMethod
from ..objects.object import ObjectMethodParameter
from ..objects.object import OBJECT_TYPE_ENTITY
from ..objects.object import OBJECT_TYPE_VALUE_OBJECT
from ..objects.sync import *
from ..repositories.object import ObjectRepository


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
}


def sync_parameter_type(parameter: ObjectMethodParameter, param_obj: ModelObject = None) -> str:
    '''
    Syncs a parameter type.

    :param parameter: The parameter.
    :type parameter: ObjectMethodParameter
    :param param_obj: The parameter object.
    :type param_obj: ModelObject
    :return: The parameter type.
    :rtype: str
    '''

    # If the parameter type is a model, set the type as the model class name.
    if parameter.type == 'model' and param_obj:
        return param_obj.class_name

    # If the parameter type is not set, return 'Any'.
    if not parameter.type:
        return 'Any'

    # If the parameter is not a list, dict, or model, return the parameter type.
    if parameter.type not in ['list', 'dict', 'model']:
        return parameter.type

    # If the parameter is a list, set the type as 'List['.
    if parameter.type == 'list':
        type = f'List['

    # If the parameter is a dict, set the type as 'Dict['.
    elif parameter.type == 'dict':
        type = f'Dict['

    # If the parameter inner type is a model, use the model class name.
    if parameter.inner_type == 'model':
        type += f'{param_obj.class_name}]'

    # Otherwise, use the inner type.
    else:
        type += f'{parameter.inner_type}]'

    # Return the type.
    return type


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
    type = sync_parameter_type(parameter, param_obj)

    # Create the variable.
    parameter = Parameter.new(
        name=parameter.name,
        type=type,
        default=parameter.default,
    )

    # Return the variable.
    return parameter


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
    model_name = model.name.replace(' ','_').upper()

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
        values_list = f',\n{TAB}'.join([f'\'{choice}\'' if attribute.type == 'str' else choice for choice in attribute.choices])
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
        attributes.append(sync_model_attribute_to_code(attribute, model_object, constants))

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
