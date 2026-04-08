# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Dict, Any


# *** classes

# ** class: service_provider
class ServiceProvider(ABC):
    '''
    Service provider for app context dependencies.
    '''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service_type: type):
        '''
        Add a service dependency to the service provider.

        :param service_id: The service ID.
        :type service_id: str
        :param service_type: The type of the service dependency.
        :type service_type: type
        '''

        pass

    # * method: add_services
    @abstractmethod
    def add_services(self, services: Dict[str, type]):
        '''
        Add multiple service dependencies to the service provider.

        :param services: A dictionary of service IDs and their corresponding types.
        :type services: Dict[str, type]
        '''

        pass

    # * method: add_constants
    @abstractmethod
    def add_constants(self, constants: Dict[str, Any]):
        '''
        Add constant dependencies to the service provider.

        :param constants: A dictionary of constant names and their corresponding values.
        :type constants: Dict[str, Any]
        '''

        pass

    # * method: get_service
    @abstractmethod
    def get_service(self, service_id: str) -> Any:
        '''
        Get a service dependency by its ID.

        :param service_id: The service ID.
        :type service_id: str
        :return: The service dependency instance.
        :rtype: Any
        '''

        pass

    # * method: remove_service
    @abstractmethod
    def remove_service(self, service_id: str):
        '''
        Remove a service dependency from the service provider.

        :param service_id: The service ID.
        :type service_id: str
        '''

        pass
