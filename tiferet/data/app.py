# *** imports

# ** core
from typing import Dict

# ** app
from ..configs import *
from ..domain import DataObject
from ..domain.app import AppDependency, AppInterface


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

# *** data

# ** data: app_dependency_yaml_data
class AppDependencyYamlData(AppDependency, DataObject):
    '''
    A YAML data representation of an app dependency object.
    '''

    # * attribute: attribute_id
    attribute_id = StringType(
        metadata=dict(
            description='The attribute id for the application dependency.'
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

    # * method: from_data
    @staticmethod
    def from_data(**kwargs) -> 'AppDependencyYamlData':
        '''
        Initializes a new YAML representation of an AppDependency object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppDependencyData object.
        :rtype: AppDependencyData
        '''

        # Create a new AppDependencyData object.
        return super(AppDependencyYamlData, AppDependencyYamlData).from_data(
            AppDependencyYamlData,
            **kwargs
        )

    # * method: new
    @staticmethod
    def from_data(**kwargs) -> 'AppDependencyYamlData':
        '''
        Initializes a new YAML representation of an AppDependency object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppDependencyData object.
        :rtype: AppDependencyData
        '''

        # Create a new AppDependencyData object.
        return super(AppDependencyYamlData, AppDependencyYamlData).from_data(
            AppDependencyYamlData,
            **kwargs
        )

    # * method: map
    def map(self, **kwargs) -> AppDependency:
        '''
        Maps the app dependency data to an app dependency object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app dependency object.
        :rtype: AppDependency
        '''

        # Map the app dependency data.
        return super().map(AppDependency, **kwargs)


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
            'to_model': DataObject.deny('app_context', 'container_context', 'feature_context', 'error_context', 'feature_repo', 'container_repo', 'error_repo'),
            'to_data': DataObject.deny('id')
        }

    # attribute: app_context
    app_context = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The application context dependency.'
        ),
    )

    # * attribute: feature_context
    feature_context = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The feature context dependency.'
        ),
    )

    # * attribute: container_context
    container_context = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The container context dependency.'
        ),
    )

    # * attribute: error_context
    error_context = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The error context dependency.'
        ),
    )

    # * attribute: feature_repo
    feature_repo = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The feature repository dependency.'
        ),
    )

    # * attribute: container_repo
    container_repo = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The container repository dependency.'
        ),
    )

    # * attribute: error_repo
    error_repo = ModelType(
        AppDependencyYamlData,
        required=True,
        metadata=dict(
            description='The error repository dependency.'
        ),
    )

    # * method: new
    @staticmethod
    def from_data(app_context: Dict[str, str],
        **kwargs) -> 'AppInterfaceYamlData':
        '''
        Initializes a new YAML representation of an AppInterface object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterfaceData object.
        :rtype: AppInterfaceData
        '''

        # Add the app context to the dependencies.
        dependencies = dict(
            app_context=AppDependencyYamlData.from_data(
                attribute_id='app_context',
                **app_context
            )
        )

        # Going through the default dependencies...
        for key, value in CONTEXT_LIST_DEFAULT.items():
            
            # If the key is in the kwargs, add it and continue.
            if key in kwargs:
                dependencies[key] = AppDependencyYamlData.from_data(
                    attribute_id=key,
                    **kwargs.pop(key)) # Pop the key to avoid duplication.
                continue
            
            # Otherwise, add the default value.
            dependencies[key] = AppDependencyYamlData.from_data(
                attribute_id=key,
                **value)

        # Create a new AppInterfaceData object.
        return super(AppInterfaceYamlData, AppInterfaceYamlData).from_data(
            AppInterfaceYamlData,
            **dependencies,
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

        # Format and map the dependencies.
        dependencies = [
            self.app_context.map(),
            self.container_context.map(),
            self.feature_context.map(),
            self.error_context.map(),
            self.feature_repo.map(),
            self.container_repo.map(),
            self.error_repo.map(),
        ]

        # Map the app interface data.
        return super().map(AppInterface,
            dependencies=dependencies,
            **self.to_primitive('to_model'),
            **kwargs
        )
