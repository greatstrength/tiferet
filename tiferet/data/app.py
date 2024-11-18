# *** imports

# ** core
from typing import Dict

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
            dict(**kwargs),
            strict=False,
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
        default=AppDependencyYamlData.new(
            attribute_id='feature_context',
            module_path='tiferet.contexts.feature',
            class_name='FeatureContext',
        ),
        metadata=dict(
            description='The feature context dependency.'
        ),
    )

    # * attribute: container_context
    container_context = ModelType(
        AppDependencyYamlData,
        required=True,
        default=AppDependencyYamlData.new(
            attribute_id='container_context',
            module_path='tiferet.contexts.container',
            class_name='ContainerContext',
        ),
        metadata=dict(
            description='The container context dependency.'
        ),
    )

    # * attribute: error_context
    error_context = ModelType(
        AppDependencyYamlData,
        required=True,
        default=AppDependencyYamlData.new(
            attribute_id='error_context',
            module_path='tiferet.contexts.error',
            class_name='ErrorContext',
        ),
        metadata=dict(
            description='The error context dependency.'
        ),
    )

    # * attribute: feature_repo
    feature_repo = ModelType(
        AppDependencyYamlData,
        required=True,
        default=AppDependencyYamlData.new(
            attribute_id='feature_repo',
            module_path='tiferet.repos.feature',
            class_name='FeatureRepository',
        ),
        metadata=dict(
            description='The feature repository dependency.'
        ),
    )

    # * attribute: container_repo
    container_repo = ModelType(
        AppDependencyYamlData,
        required=True,
        default=AppDependencyYamlData.new(
            attribute_id='container_repo',
            module_path='tiferet.repos.container',
            class_name='ContainerRepository',
        ),
        metadata=dict(
            description='The container repository dependency.'
        ),
    )

    # * attribute: error_repo
    error_repo = ModelType(
        AppDependencyYamlData,
        required=True,
        default=AppDependencyYamlData.new(
            attribute_id='error_repo',
            module_path='tiferet.repos.error',
            class_name='ErrorRepository',
        ),
        metadata=dict(
            description='The error repository dependency.'
        ),
    )

    # * method: new
    @staticmethod
    def new(app_context: Dict[str, str],
            container_context: Dict[str, str] = None,
            feature_context: Dict[str, str] = None,
            error_context: Dict[str, str] = None,
            feature_repo: Dict[str, str] = None,
            container_repo: Dict[str, str] = None,
            error_repo: Dict[str, str] = None,
            **kwargs) -> 'AppInterfaceYamlData':
        '''
        Initializes a new YAML representation of an AppInterface object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterfaceData object.
        :rtype: AppInterfaceData
        '''

        # Format the dependencies.
        dependencies = {}
        if app_context:
            dependencies['app_context'] = AppDependencyYamlData.new(attribute_id='app_context', **app_context)
        if container_context:
            dependencies['container_context'] = AppDependencyYamlData.new(attribute_id='container_context', **container_context)
        if feature_context:
            dependencies['feature_context'] = AppDependencyYamlData.new(attribute_id='feature_context', **feature_context)
        if error_context:
            dependencies['error_context'] = AppDependencyYamlData.new(attribute_id='error_context', **error_context)
        if feature_repo:
            dependencies['feature_repo'] = AppDependencyYamlData.new(attribute_id='feature_repo', **feature_repo)
        if container_repo:
            dependencies['container_repo'] = AppDependencyYamlData.new(attribute_id='container_repo', **container_repo)
        if error_repo:
            dependencies['error_repo'] = AppDependencyYamlData.new(attribute_id='error_repo', **error_repo)

        # Create a new AppInterfaceData object.
        data = AppInterfaceYamlData(dict(
            **dependencies,
            **kwargs),
            strict=False,
        )

        # Validate and return the new AppInterfaceData object.
        data.validate()
        return data
    
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