from typing import List, Dict, Any

from ..objects.object import ModelObject
from ..objects.object import OBJECT_TYPE_ENTITY
from ..objects.object import OBJECT_TYPE_VALUE_OBJECT
from ..objects.sync import Class
from ..objects.sync import Module
from ..objects.sync import MODULE_TYPE_OBJECTS
from ..objects.sync import Import


def sync_model_to_code(model_object: ModelObject, base_model: ModelObject = None) -> Class:
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

    # Create the class.
    _class = Class.new(
        name=model_object.class_name,
        description=model_object.description,
        base_classes=base_classes
    )

    # Return the class.
    return _class
    

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
        imports = [Import(dict(
            type='core',
            from_module='typing',
            import_module='List, Dict, Any'
        )),
        Import(dict(
            type='app',
            from_module='..objects.object',
            import_module='Entity'
        )),]

    # Create the module.
    module = Module.new(
        imports=imports,
        type=type,
        id=name
    )

    # Return the module.
    return module