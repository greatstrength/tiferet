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
        return super(AppDependency, AppDependency).new(
            AppDependency,
            **kwargs,
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
        default='core',
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

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(AppDependency),
        required=True,
        default=[],
        metadata=dict(
            description='The application interface dependencies.'
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
    
    # * method: get_dependency
    def get_dependency(self, attribute_id: str) -> AppDependency:
        '''
        Get the dependency by attribute id.

        :param attribute_id: The attribute id of the dependency.
        :type attribute_id: str
        :return: The dependency.
        :rtype: AppDependency
        '''

        # Get the dependency by attribute id.
        return next((dep for dep in self.dependencies if dep.attribute_id == attribute_id), None)
    

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
            super(AppRepositoryConfiguration, AppRepositoryConfiguration).new(
                AppRepositoryConfiguration,
                **kwargs),
            strict=False,
        )
