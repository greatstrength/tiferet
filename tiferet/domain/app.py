# *** imports

# ** app
from ..configs import *
from ..domain import *


# *** models

# ** model: app_dependency
class AppDependency(ModuleDependency):

    # * attribute: attribute_id
    attribute_id = StringType(
        required=True,
        metadata=dict(
            description='The attribute id for the application dependency.'
        ),
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'AppDependency':
        '''
        Initializes a new AppDependency object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppDependency object.
        :rtype: AppDependency
        '''

        # Create and return a new AppDependency object.
        return AppDependency(
            super(AppDependency, AppDependency).new(**kwargs),
            strict=False,
        )

# ** model: app_interface
class AppInterface(Entity):
    '''
    The base application interface object.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the application interface.'
        ),
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the application interface.'
        ),
    )

    # attribute: feature_flag
    feature_flag = StringType(
        required=True,
        metadata=dict(
            description='The feature flag.'
        ),
    )

    # attribute: data_flag
    data_flag = StringType(
        required=True,
        metadata=dict(
            description='The data flag.'
        ),
    )

    # * attribute: app_context
    app_context = ModelType(
        AppDependency,
        required=True,
        metadata=dict(
            description='The application context dependency.'
        ),
    )

    # * attribute: feature_context
    feature_context = ModelType(
        AppDependency,
        required=True,
        default=AppDependency.new(
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
        AppDependency,
        required=True,
        default=AppDependency.new(
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
        AppDependency,
        required=True,
        default=AppDependency.new(
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
        AppDependency,
        required=True,
        default=AppDependency.new(
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
        AppDependency,
        required=True,
        default=AppDependency.new(
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
        AppDependency,
        required=True,
        default=AppDependency.new(
            attribute_id='error_repo',
            module_path='tiferet.repos.error',
            class_name='ErrorRepository',
        ),
        metadata=dict(
            description='The error repository dependency.'
        ),
    )

    # * attribute: constants
    constants = DictType(
        StringType,
        default=dict(
            container_config_file='app/configs/container.yml',
            feature_config_file='app/configs/features.yml',
            error_config_file='app/configs/errors.yml',
        ),
        metadata=dict(
            description='The application dependency constants.'
        ),
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'AppInterface':
        '''
        Initializes a new AppInterface object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterface object.
        :rtype: AppInterface
        '''

        # Create and return a new AppInterface object.
        return super(AppInterface, AppInterface).new(
            AppInterface,
            **kwargs
        )
    
    # * method: list_dependencies
    def get_dependencies(self) -> list:
        '''
        Lists the dependencies for the application interface.

        :return: The list of dependencies for the application interface.
        :rtype: list
        '''

        # Return the list of dependencies for the application interface.
        return [
            self.app_context,
            self.feature_context,
            self.container_context,
            self.error_context,
            self.feature_repo,
            self.container_repo,
            self.error_repo,
        ]


# ** model: app_repository_configuration
class AppRepositoryConfiguration(ModuleDependency):
    '''
    The import configuration for the application repository.
    '''

    # * attribute: module_path
    module_path = StringType(
        required=True,
        default='tiferet.repos.app',
        metadata=dict(
            description='The module path for the application repository.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        default='YamlProxy',
        metadata=dict(
            description='The class name for the application repository.'
        ),
    )

    # * attribute: params
    params = DictType(
        StringType,
        default=dict(
            app_config_file='app/configs/app.yml',
        ),
        metadata=dict(
            description='The application repository configuration parameters.'
        ),
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'AppRepositoryConfiguration':
        '''
        Initializes a new AppRepositoryConfiguration object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppRepositoryConfiguration object.
        :rtype: AppRepositoryConfiguration
        '''

        # Create and return a new AppRepositoryConfiguration object.
        return AppRepositoryConfiguration(
            super(AppRepositoryConfiguration, AppRepositoryConfiguration).new(**kwargs),
            strict=False,
        )


# ** model: app_configuration
class AppConfiguration(Entity):
    '''
    The application configuration object.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the application.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the application.'
        )
    )

    # * attribute: app_repo
    app_repo = ModelType(AppRepositoryConfiguration,
        required=True,
        metadata=dict(
            description='The application repository configuration.'
        ),
    )

    # * attribute: interfaces
    interfaces = ListType(
        ModelType(AppInterface),
        required=True,
        default=[],
        metadata=dict(
            description='The application interfaces.'
        )
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'AppConfiguration':
        '''
        Initializes a new AppConfiguration object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppConfiguration object.
        :rtype: AppConfiguration
        '''

        # Create and return a new AppConfiguration object.
        return super(AppConfiguration, AppConfiguration).new(
            AppConfiguration,
            **kwargs
        )