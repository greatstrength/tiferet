# *** imports

# ** infra
from schematics import Model

# ** app
from .app import AppInterfaceContext
from ..services import container_service
from ..domain import *
from ..repos.app import AppRepository


# *** contexts

# ** context: environment_context
class EnvironmentContext(Model):
    '''
    An environment context is a class that is used to create and run the app interface context.
    '''

    # * attribute: interfaces
    interfaces = DictType(
        ModelType(AppInterface), 
        default={},
        metadata=dict(
            description='The app interfaces keyed by interface ID.'
        ),
    )

    # * method: init
    def __init__(self, **kwargs):
        '''
        Initialize the environment context.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Load the app repository.
        app_repo = self.load_app_repo()

        # Load the interface configuration.
        interfaces = {interface.id: interface for interface in app_repo.list_interfaces()}

        # Set the interfaces.
        super().__init__(dict(
            interfaces=interfaces,
            **kwargs
        ), strict=False)

    # * method: start
    def start(self, interface_id: str, **kwargs):
        '''
        Start the environment context.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Load the app context.
        app_context = self.load_app_context(interface_id)

        # Run the app context.
        app_context.run(
            interface_id=interface_id,
            **kwargs
        )

    # * method: load_app_repo
    def load_app_repo(self) -> AppRepository:
        '''
        Load the app interface repository.

        :return: The app repository.
        :rtype: AppRepository
        '''

        # Load the app repository configuration.
        from ..configs.app import APP_REPO

        # Return the app repository.
        return container_service.import_dependency(APP_REPO.module_path, APP_REPO.class_name)(**APP_REPO.params)

    # * method: load_app_context
    def load_app_context(self, interface_id: str) -> AppInterfaceContext:
        '''
        Load the app context.

        :param container: The app container.
        :type container: AppContainer
        :return: The app context.
        :rtype: AppContext
        '''

        # Get the app interface.
        app_interface: AppInterface = self.interfaces.get(interface_id)

        # Get the default dependencies for the app interface.
        app_context = app_interface.get_dependency('app_context')
        dependencies = dict(
            interface_id=app_interface.id,
            app_name=app_interface.name,
            feature_flag=app_interface.feature_flag,
            data_flag=app_interface.data_flag,
            app_context=container_service.import_dependency(
                **app_context.to_primitive()
            ),
            **app_interface.constants
        )

        # Import the dependencies.
        for dep in app_interface.dependencies:
            dependencies[dep.attribute_id] = container_service.import_dependency(dep.module_path, dep.class_name)

        # Create the injector from the dependencies, constants, and the app interface.
        injector = container_service.create_injector(
            app_interface.id,
            **dependencies
        )

        # Return the app context.
        return getattr(injector, 'app_context')
