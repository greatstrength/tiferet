# *** imports

# ** core
from typing import Any

# ** infra
from schematics import Model

# ** app
from ..configs import *


# *** models

# ** model: model_object
class ModelObject(Model):
    '''
    A domain model object.
    '''

    # * method: new
    @staticmethod
    def new(
        model_type: type,
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> Any:
        '''
        Initializes a new model object.

        :param model_type: The type of model object to create.
        :type model_type: type
        :param validate: True to validate the model object.
        :type validate: bool
        :param strict: True to enforce strict mode for the model object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new model object.
        :rtype: Any
        '''

        # Create a new model object.
        _object = model_type(dict(
            **kwargs
        ), strict=strict)

        # Validate if specified.
        if validate:
            _object.validate()

        # Return the new model object.
        return _object


# ** model: entity
class Entity(ModelObject):
    '''
    A domain model entity.
    '''

    # ** attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The entity unique identifier.'
        )
    )


# ** model: value_object
class ValueObject(ModelObject):
    '''
    A domain model value object.
    '''

    pass



# ** model: module_dependency
class ModuleDependency(ValueObject):
    '''
    A module dependency.
    '''

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path.'
        )
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name.'
        )
    )
