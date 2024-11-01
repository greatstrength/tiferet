# *** imports

# ** core
from typing import List, Dict, Any

# ** infra
from schematics import Model, types as t


# *** models

# ** model: model_object
class ModelObject(Model):
    '''
    A domain model object.
    '''

    # ** method: new
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
    id = t.StringType(
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
            role: str = 'to_object',
            **kwargs
            ) -> ModelObject:
        '''
        Maps the model data to a model object.

        :param type: The type of model object to map to.
        :type type: type
        :param role: The role for the mapping.
        :type role: str
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

        # Return the model data.
        return _object

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
