# *** imports

# ** core
from typing import Tuple

# ** app
from ..configs import *
from ..contexts.app import AppInterfaceContext
from ..contexts.container import ContainerContext


# *** contexts

# ** context: environment_context
class EnvironmentContext(Model):
    '''
    An environment context is a class that is used to create and run the app interface context.
    '''

    # * attribute: containers
    containers = DictType(
        ModelType(ContainerContext),
        default={},
        metadata=dict(
            description='The container contexts keyed by app interface.'
        ),
    )

    # * method: init
    def __init__(self, interface_id: str, app_config: str, container_config: str, **kwargs):
        '''
        Initialize the environment context.

        :param env_base_key: The base key for the environment variables.
        :type env_base_key: str
        '''

        # Load the container contexts.
        self.load_containers(**kwargs)

        # Load the app context.
        container, app_context = self.load_app_context(interface_id)

        # Run the app context.
        app_context.run(container=container, **kwargs)

    # * method: load_containers
    def load_containers(self, **kwargs):
        '''
        Load the container contexts by app interface.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        pass
    
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
