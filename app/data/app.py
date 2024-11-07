# *** imports

# ** app
from ..configs import *
from ..domain import DataObject
from ..domain.app import AppDependency, AppInterface, AppRepositoryConfiguration


# *** data

# ** data: app_dependency_yaml_data
class AppDependencyYamlData(AppDependency, DataObject):
    '''
    A YAML data representation of an app dependency object.
    '''

    class Options():
        '''
        The options for the app dependency data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data.yaml': DataObject.deny('attribute_id')
        }

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'AppDependencyYamlData':
        '''
        Initializes a new YAML representation of an AppDependency object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppDependencyData object.
        :rtype: AppDependencyData
        '''

        # Create a new AppDependencyData object.
        return AppDependencyYamlData(
            super(AppDependencyYamlData, AppDependencyYamlData).new(
                **kwargs
            )
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
            'to_model': DataObject.allow(),
            'to_data.yaml': DataObject.deny('id')
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
    def new(**kwargs) -> 'AppInterfaceYamlData':
        '''
        Initializes a new YAML representation of an AppInterface object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterfaceData object.
        :rtype: AppInterfaceData
        '''

        # Create a new AppInterfaceData object.
        return AppInterfaceYamlData(
            super(AppInterfaceYamlData, AppInterfaceYamlData).new(
                **kwargs
            )
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
        return super().map(AppInterface, **kwargs)


# ** data: app_repository_configuration_yaml_data
class AppRepositoryConfigurationYamlData(DataObject):
    '''
    A YAML data representation of an app repository configuration object.
    '''

    class Options():
        '''
        The options for the app repository configuration data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data.yaml': DataObject.allow()
        }

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'AppRepositoryConfigurationYamlData':
        '''
        Initializes a new YAML representation of an AppRepositoryConfiguration object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppRepositoryConfigurationData object.
        :rtype: AppRepositoryConfigurationData
        '''

        # Create a new AppRepositoryConfigurationData object.
        return AppRepositoryConfigurationYamlData(
            super(AppRepositoryConfigurationYamlData, AppRepositoryConfigurationYamlData).new(
                **kwargs
            )
        )
    
    # * method: map
    def map(self, **kwargs) -> AppRepositoryConfiguration:
        '''
        Maps the app repository configuration data to an app repository configuration object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app repository configuration object.
        :rtype: AppRepositoryConfiguration
        '''

        # Map the app repository configuration data.
        return super().map(AppRepositoryConfiguration, **kwargs)