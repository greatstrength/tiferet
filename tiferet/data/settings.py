# *** imports

# ** core
from typing import Any

# ** app
from ..contracts.settings import ModelContract
from ..models.settings import *


# *** constants

# ** constant: default_module_path
DEFAULT_MODULE_PATH = 'tiferet.contexts.app'

# ** constant: default_class_name
DEFAULT_CLASS_NAME = 'AppInterfaceContext'


# *** classes

# ** class: data_object
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
            ) -> ModelContract:
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
        :return: A new model object as a contract.
        :rtype: ModelContract
        '''

        # Get primitive of the model data and merge with the keyword arguments.
        # Give priority to the keyword arguments.
        _data = self.to_primitive(role=role)
        for key, value in kwargs.items():
            _data[key] = value

        # Map the data object to a model object.
        # Attempt to create a new model object with a custom factory method.
        # If the factory method does not exist, employ the standard method.
        try:
            _object = type.new(**_data, strict=False)
        except Exception:
            _object = ModelObject.new(type, **_data, strict=False)

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

    # ** method: from_data
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
        '''
        Creates a whitelist transform for data mapping.

        :param args: Fields to allow in the transform.
        :type args: tuple
        :return: The whitelist transform.
        :rtype: Any
        '''

        # Create a whitelist transform.
        # Create a wholelist transform if no arguments are specified.
        from schematics.transforms import whitelist, wholelist
        if args:
            return whitelist(*args)
        return wholelist()

    # ** method: deny
    @staticmethod
    def deny(*args) -> Any:
        '''
        Creates a blacklist transform for data mapping.

        :param args: Fields to deny in the transform.
        :type args: tuple
        :return: The blacklist transform.
        :rtype: Any
        '''

        # Create a blacklist transform.
        from schematics.transforms import blacklist
        return blacklist(*args)