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


# ** model: data_object
class DataObject(Model):
    '''
    A data representation object.
    '''

    # ** method: map
    def map(self,
            type: ModelObject,
            role: str = 'to_model',
            validate: bool = True,
            **kwargs
            ) -> ModelObject:
        '''
        Maps the model data to a model object.

        :param type: The type of model object to map to.
        :type type: type
        :param role: The role for the mapping.
        :type role: str
        :param validate: True to validate the model object.
        :type validate: bool
        :param kwargs: Additional keyword arguments for mapping.
        :type kwargs: dict
        :return: A new model object.
        :rtype: ModelObject
        '''

        # Get primitive of the model data and merge with the keyword arguments.
        # Give priority to the keyword arguments.
        _data = self.to_primitive(role=role)
        for key, value in kwargs.items():
            _data[key] = value

        # Map the data object to a model object.
        _object = type.new(**_data, strict=False)

        # Validate if specified.
        if validate:
            _object.validate()

        # Return the model data.
        return _object

    # ** method: from_model
    @staticmethod
    def from_model(
        data: 'DataObject',
        model: ModelObject,
        validate: bool = True,
        **kwargs
    ) -> 'DataObject':
        '''
        Initializes a new data object from a model object.

        :param model: The type of model object to map from.
        :type model: type
        :param data: The data object to map from.
        :type data: DataObject
        :param validate: True to validate the data object.
        :type validate: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new data object.
        :rtype: DataObject
        '''

        # Create a new data object.
        obj = data(dict(
            **model.to_primitive(),
            **kwargs
        ), strict=False)

        # Validate the data object if specified.
        if validate:
            obj.validate()

        # Return the data object.
        return obj

    @staticmethod
    def from_data(
        data: type,
        **kwargs
    ) -> 'DataObject':
        '''
        Initializes a new data object from a dictionary.

        :param data: The type of data object to map from.
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new data object.
        :rtype: DataObject
        '''

        # Create a new data object.
        return data(dict(**kwargs), strict=False)

    # ** method: allow
    @staticmethod
    def allow(*args) -> Any:

        # Create a whitelist transform.
        # Create a wholelist transform if no arguments are specified.
        from schematics.transforms import whitelist, wholelist
        if args:
            return whitelist(*args)
        return wholelist()

    # ** method: deny
    @staticmethod
    def deny(*args) -> Any:

        # Create a blacklist transform.
        from schematics.transforms import blacklist
        return blacklist(*args)


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
