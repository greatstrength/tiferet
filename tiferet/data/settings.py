# *** imports

# ** app
from ..models.settings import *


# *** constants

# ** constant: app_dependency_default
FEATURE_CONTEXT_DEFAULT = dict(
    module_path='tiferet.contexts.feature',
    class_name='FeatureContext',
) 

# * constant: app_dependency_default
CONTAINER_CONTEXT_DEFAULT = dict(
    module_path='tiferet.contexts.container',
    class_name='ContainerContext',
)

ERROR_CONTEXT_DEFAULT = dict(
    module_path='tiferet.contexts.error',
    class_name='ErrorContext',
)

FEATURE_PROXY_DEFAULT = dict(
    module_path='tiferet.proxies.feature_yaml',
    class_name='FeatureYamlProxy',
)

CONTAINER_PROXY_DEFAULT = dict(
    module_path='tiferet.proxies.container_yaml',
    class_name='ContainerYamlProxy',
)

ERROR_PROXY_DEFAULT = dict(
    module_path='tiferet.proxies.error_yaml',
    class_name='ErrorYamlProxy',
)

# ** constant: context_list_default
CONTEXT_LIST_DEFAULT = {
    'feature_context': FEATURE_CONTEXT_DEFAULT,
    'container_context': CONTAINER_CONTEXT_DEFAULT,
    'error_context': ERROR_CONTEXT_DEFAULT,
    'feature_repo': FEATURE_PROXY_DEFAULT,
    'container_repo': CONTAINER_PROXY_DEFAULT,
    'error_repo': ERROR_PROXY_DEFAULT,
}

# ** constant: constants_default
CONSTANTS_DEFAULT = dict(
    container_config_file='app/configs/container.yml',
    feature_config_file='app/configs/features.yml',
    error_config_file='app/configs/errors.yml',
)


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