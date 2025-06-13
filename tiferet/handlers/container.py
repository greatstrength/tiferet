# *** imports

# ** core
from typing import Any, Dict

# ** infra
from dependencies import Injector

# ** app
from ..contracts.container import ContainerService


# *** handlers

# ** handler: dependency_injector_handler
class DependencyInjectorHandler(ContainerService):
    '''
    Dependency handler for managing container dependencies for app initialization.
    '''

    _injectors: Dict[str, Any] = {}


    # * method: get_dependency
    def get_dependency(self, app_id: str, type: str, attribute_id: str, dependencies: Dict[str, Any] = {}) -> Any:
        '''
        Get a dependency by its attribute ID.

        :param attribute_id: The ID of the attribute to retrieve.
        :type attribute_id: str
        :return: The dependency object.
        :rtype: Any
        '''

        # Retrieve the injector from the container repository.
        injector = self.cache.get(f'{app_id}.{type}')

        # If the injector is not found, create a new one.
        if injector is None:
            injector = self.create_injector(app_id, dependencies)
            self.cache.set(f'{app_id}.app', injector)

        # Return the dependency from the injector.
        return getattr(injector, attribute_id, None)
    
    # * method: create_injector
    def create_injector(self, app_id: str, type: str, dependencies: Dict[str, Any] = {}) -> Any:
        '''
        Create an injector object with the given dependencies.

        :param app_id: The application instance ID.
        :type app_id: str
        :param dependencies: The dependencies.
        :type dependencies: dict
        :return: The injector object.
        :rtype: Any
        '''

        # Create the injector with the application ID and dependencies.
        return Injector(f'{app_id}.{type}', app_id=app_id, **dependencies)
