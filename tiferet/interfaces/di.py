"""Tiferet DI Interfaces"""

# *** imports

# ** core
from abc import abstractmethod
from typing import (
    List,
    Dict,
    Tuple,
    Any
)

# ** app
from ..mappers.di import (
    ServiceConfigurationAggregate,
)
from .settings import Service

# *** interfaces

# ** interface: di_service
class DIService(Service):
    '''
    Service interface for managing service configurations and constants.
    '''

    # * method: configuration_exists
    @abstractmethod
    def configuration_exists(self, id: str) -> bool:
        '''
        Check if a service configuration exists by ID.

        :param id: The service configuration identifier.
        :type id: str
        :return: True if the service configuration exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('configuration_exists method is required for DIService.')

    # * method: get_configuration
    @abstractmethod
    def get_configuration(self, configuration_id: str, flag: str = None) -> ServiceConfigurationAggregate:
        '''
        Retrieve a service configuration by ID, optionally filtered by flag.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flag: Optional flag to filter the configuration.
        :type flag: str
        :return: The service configuration aggregate.
        :rtype: ServiceConfigurationAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get_configuration method is required for DIService.')

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ServiceConfigurationAggregate], Dict[str, str]]:
        '''
        List all service configurations and constants.

        :return: A tuple containing a list of service configuration aggregates and a dictionary of constants.
        :rtype: Tuple[List[ServiceConfigurationAggregate], Dict[str, str]]
        '''
        # Not implemented.
        raise NotImplementedError('list_all method is required for DIService.')

    # * method: save_configuration
    @abstractmethod
    def save_configuration(self, configuration: ServiceConfigurationAggregate) -> None:
        '''
        Save or update a service configuration.

        :param configuration: The service configuration aggregate to save.
        :type configuration: ServiceConfigurationAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_configuration method is required for DIService.')

    # * method: delete_configuration
    @abstractmethod
    def delete_configuration(self, configuration_id: str) -> None:
        '''
        Delete a service configuration by ID. This operation should be idempotent.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete_configuration method is required for DIService.')

    # * method: save_constants
    @abstractmethod
    def save_constants(self, constants: Dict[str, Any] = {}) -> None:
        '''
        Save or update constants.

        :param constants: The constants to save.
        :type constants: Dict[str, Any]
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_constants method is required for DIService.')
