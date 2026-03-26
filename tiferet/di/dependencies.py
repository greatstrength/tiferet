"""Dependencies DI Service Provider"""

# *** imports

# ** core
from typing import Any, Dict

# ** infra
from dependencies import Injector
from dependencies.exceptions import DependencyError

# ** app
from ..events import RaiseError
from .settings import ServiceProvider


# *** classes

# ** class: dependencies_service_provider
class DependenciesServiceProvider(ServiceProvider):
    '''
    A service provider for managing app context dependencies via the
    dependencies library injector.
    '''

    # * attribute: services
    services: Dict[str, type]

    # * attribute: injector
    injector: type

    # * attribute: _name
    _name: str

    # * init
    def __init__(self, services: Dict[str, type] = None, name: str = 'TiferetInjector'):
        '''
        Initialize the dependencies service provider.

        :param services: Initial service ID-to-type mapping.
        :type services: Dict[str, type]
        :param name: Name used for the internal injector class.
        :type name: str
        '''

        # Store the name and services, then build the injector.
        self._name = name
        self.services = services or {}
        self.build_injector()

    # * method: new (static)
    @staticmethod
    def new(name: str, dependencies: Dict[str, type]) -> 'DependenciesServiceProvider':
        '''
        Create a new service provider instance with the given dependencies.

        :param name: The name of the service provider.
        :type name: str
        :param dependencies: The dependencies to include in the service provider.
        :type dependencies: Dict[str, type]
        :return: A new service provider instance.
        :rtype: DependenciesServiceProvider
        '''

        # Return a new provider instance pre-populated with the given dependencies.
        return DependenciesServiceProvider(services=dependencies, name=name)

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        '''
        Add a service dependency to the service provider.

        :param service_id: The ID of the service to add.
        :type service_id: str
        :param service_type: The type of the service to add.
        :type service_type: type
        '''

        # Add the service to the services dictionary and rebuild the injector.
        self.services[service_id] = service_type
        self.build_injector()

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        '''
        Add multiple service dependencies to the service provider.

        :param services: A dictionary of service IDs and their corresponding types.
        :type services: Dict[str, type]
        '''

        # Merge the given services and rebuild the injector.
        self.services.update(services)
        self.build_injector()

    # * method: add_constants
    def add_constants(self, constants: Dict[str, Any]):
        '''
        Add constant dependencies to the service provider.

        :param constants: A dictionary of constant names and their corresponding values.
        :type constants: Dict[str, Any]
        '''

        # Merge the constants into the services dictionary and rebuild the injector.
        self.services.update(constants)
        self.build_injector()

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        '''
        Get a service dependency by its ID.

        :param service_id: The service ID.
        :type service_id: str
        :return: The resolved service dependency instance.
        :rtype: Any
        '''

        # If no services have been registered the injector is None — raise immediately.
        if self.injector is None:
            RaiseError.execute(
                'INVALID_DEPENDENCY_ERROR',
                f'Dependency {service_id} could not be resolved: no services are registered.',
                dependency_name=service_id,
                exception='No services registered in the service provider.',
            )

        # Attempt to retrieve the resolved service from the injector.
        try:
            return getattr(self.injector, service_id)

        # If the dependency does not exist or cannot be resolved, raise an error.
        except (DependencyError, AttributeError) as e:
            RaiseError.execute(
                'INVALID_DEPENDENCY_ERROR',
                f'Dependency {service_id} could not be resolved: {str(e)}',
                dependency_name=service_id,
                exception=str(e)
            )

    # * method: remove_service
    def remove_service(self, service_id: str):
        '''
        Remove a service dependency from the service provider.

        :param service_id: The service ID to remove.
        :type service_id: str
        '''

        # Remove the service from the services dictionary and rebuild the injector.
        if service_id in self.services:
            del self.services[service_id]
            self.build_injector()

    # * method: build_injector
    def build_injector(self):
        '''
        Rebuild the internal injector from the current services dictionary.
        The injector is set to None when no services are registered, as the
        dependencies library requires a non-empty scope.
        '''

        # Only build the injector when there are services to register.
        if self.services:
            self.injector = type(self._name, (Injector,), self.services)
        else:
            self.injector = None
