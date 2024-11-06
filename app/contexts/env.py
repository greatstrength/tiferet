# *** imports

# ** core
from typing import Tuple

# ** app
from ..configs import *
from ..contexts.app import AppInterfaceContext
from ..contexts.container import ContainerContext
from ..repositories.app import AppRepository
from ..services.container import import_dependency
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
        container, app_context = self.load_app_context(interface_id)

        # Run the app context.
        app_context.run(
            interface_id=interface_id, 
            container=container, 
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
    def load_app_context(self, interface_id: str) -> Tuple[ContainerContext, AppInterfaceContext]:
        '''
        Load the app context.

        :param container: The app container.
        :type container: AppContainer
        :return: The app context.
        :rtype: AppContext
        '''

        # Get the app container.
        container: ContainerContext = self.containers[interface_id]

        # Load the app context.
        app_context = container.get_dependency('app_interface_context')

        # Return the app context.
        return container, app_context
