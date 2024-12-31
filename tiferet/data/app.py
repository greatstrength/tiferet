# *** imports

# ** app
from ..configs import *
from ..models.app import *
from .core import *


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

FEATURE_REPO_DEFAULT = dict(
    module_path='tiferet.repos.feature',
    class_name='YamlProxy',
)

CONTAINER_REPO_DEFAULT = dict(
    module_path='tiferet.repos.container',
    class_name='YamlProxy',
)

ERROR_REPO_DEFAULT = dict(
    module_path='tiferet.repos.error',
    class_name='YamlProxy',
)

# ** constant: context_list_default
CONTEXT_LIST_DEFAULT = {
    'feature_context': FEATURE_CONTEXT_DEFAULT,
    'container_context': CONTAINER_CONTEXT_DEFAULT,
    'error_context': ERROR_CONTEXT_DEFAULT,
    'feature_repo': FEATURE_REPO_DEFAULT,
    'container_repo': CONTAINER_REPO_DEFAULT,
    'error_repo': ERROR_REPO_DEFAULT,
}

# ** constant: constants_default
CONSTANTS_DEFAULT = dict(
    container_config_file='app/configs/container.yml',
    feature_config_file='app/configs/features.yml',
    error_config_file='app/configs/errors.yml',
)

# *** data

# ** data: app_dependency_yaml_data
class AppDependencyYamlData(AppDependency, DataObject):
    '''
    A YAML data representation of an app dependency object.
    '''

    # * attribute: attribute_id
    attribute_id = StringType(
        metadata=dict(
            description='The attribute id for the application dependency that is not required for assembly.'
        ),
    )

    class Options():
        '''
        The options for the app dependency data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data.yaml': DataObject.deny('attribute_id')
        }


# ** data: app_interface_yaml_data
class AppInterfaceYamlData(AppInterface, DataObject):
    '''
    A data representation of an app interface object.
    '''

    class Options():
        '''
        The options for the app interface data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('dependencies'),
            'to_data': DataObject.deny('id')
        }

    # attribute: dependencies
    dependencies = DictType(
        ModelType(AppDependencyYamlData),
        default={},
        metadata=dict(
            description='The app dependencies.'
        ),
    )

    # * method: new
    @staticmethod
    def from_data(
        app_context: Dict[str, str], 
        constants: Dict[str, str] = {},
        **kwargs
    ) -> 'AppInterfaceYamlData':
        '''
        Initializes a new YAML representation of an AppInterface object.

        :param app_context: The app context.
        :type app_context: Dict[str, str]
        :param constants: The constants.
        :type constants: Dict[str, str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterfaceData object.
        :rtype: AppInterfaceData
        '''

        # Add the app context to the dependencies.
        dependencies = dict(
            app_context=DataObject.from_data(
                AppDependencyYamlData,
                attribute_id='app_context',
                **app_context
            )
        )

        # Going through the default dependencies...
        for key, value in CONTEXT_LIST_DEFAULT.items():
            
            # If the key is in the kwargs, add it and continue.
            if key in kwargs:
                dependencies[key] = DataObject.from_data(
                    AppDependencyYamlData,
                    attribute_id=key,
                    **kwargs.pop(key)) # Pop the key to avoid duplication.
                continue
            
            # Otherwise, add the default value.
            dependencies[key] = DataObject.from_data(
                AppDependencyYamlData,
                attribute_id=key,
                **value)
            
        # Add the default constants to the contants.
        for key, value in CONSTANTS_DEFAULT.items():
            if key in constants:
                continue
            constants[key] = value

        # Create a new AppInterfaceData object.
        return DataObject.from_data(
            AppInterfaceYamlData,
            dependencies=dependencies,
            constants=constants,
            **kwargs
        )

    # * method: map
    def map(self, **kwargs) -> AppInterface:
        '''
        Maps the app interface data to an app interface object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app interface object.
        :rtype: AppInterface
        '''

        # Map the app interface data.
        return super().map(AppInterface,
            dependencies=[dep.map(AppDependency, attribute_id=key) for key, dep in self.dependencies.items()],
            **self.to_primitive('to_model'),
            **kwargs
        )
