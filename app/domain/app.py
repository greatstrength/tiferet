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
            **kwargs
        )

# ** model: app_interface
class AppInterface(ValueObject):
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

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(AppDependency),
        required=True,
        default=[],
        metadata=dict(
            description='The application dependencies.'
        ),
    )

    # * attribute: constants
    constants = DictType(
        StringType,
        default={},
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


# ** model: app_repository_configuration
class AppRepositoryConfiguration(ModuleDependency):
    '''
    The import configuration for the application repository.
    '''

    # * attribute: module_path
    module_path = StringType(
        required=True,
        default='app.repositories.app',
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
        return super(AppRepositoryConfiguration, AppRepositoryConfiguration).new(
            AppRepositoryConfiguration,
            **kwargs
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