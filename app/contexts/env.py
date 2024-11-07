# *** imports

# ** core
from typing import Tuple

# ** app
from ..configs import *
from ..contexts.app import AppInterfaceContext
from ..contexts.container import ContainerContext
from ..repositories.app import AppRepository
from ..services.container import import_dependency, create_injector
from ..domain.app import AppInterface


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
        self.interfaces = {interface.id: interface for interface in app_repo.list_interfaces()}

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
        return import_dependency(APP_REPO.module_path, APP_REPO.class_name)(**APP_REPO.params)

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

        # Get the dependencies for the app interface.
        dependencies = dict(
            interface_id=app_interface.id,
            feature_flag=app_interface.feature_flag,
            data_flag=app_interface.data_flag,
            **app_interface.constants
        )
        for dep in app_interface.get_dependencies():
            dependencies[dep.attribute_id] = import_dependency(dep.module_path, dep.class_name)

        # Create the injector from the dependencies, constants, and the app interface.
        injector = create_injector(
            app_interface.id
            **dependencies
        )

        # Return the app context.
        return getattr(injector, 'app_context')
