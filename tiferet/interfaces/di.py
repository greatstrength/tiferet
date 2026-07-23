"""Tiferet Interfaces DI"""

# *** imports

# ** core
from abc import abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

# ** app
from ..mappers.di import ServiceRegistrationAggregate
from .core import Service

# *** interfaces

# ** interface: di_service
class DIService(Service):
    '''
    Service interface for managing service registrations and constants.
    '''

    # * method: registration_exists
    @abstractmethod
    def registration_exists(self, id: str) -> bool:
        '''
        Check if a service registration exists by ID.

        :param id: The service registration identifier.
        :type id: str
        :return: True if the service registration exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('registration_exists method is required for DIService.')

    # * method: get_registration
    @abstractmethod
    def get_registration(self, registration_id: str, flag: str = None) -> ServiceRegistrationAggregate:
        '''
        Retrieve a service registration by ID, optionally filtered by flag.

        :param registration_id: The service registration identifier.
        :type registration_id: str
        :param flag: Optional flag to filter the registration.
        :type flag: str
        :return: The service registration aggregate.
        :rtype: ServiceRegistrationAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get_registration method is required for DIService.')

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ServiceRegistrationAggregate], Dict[str, str]]:
        '''
        List all service registrations and constants.

        :return: A tuple containing a list of service registration aggregates and a dictionary of constants.
        :rtype: Tuple[List[ServiceRegistrationAggregate], Dict[str, str]]
        '''
        # Not implemented.
        raise NotImplementedError('list_all method is required for DIService.')

    # * method: save_registration
    @abstractmethod
    def save_registration(self, registration: ServiceRegistrationAggregate) -> None:
        '''
        Save or update a service registration.

        :param registration: The service registration aggregate to save.
        :type registration: ServiceRegistrationAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_registration method is required for DIService.')

    # * method: delete_registration
    @abstractmethod
    def delete_registration(self, registration_id: str) -> None:
        '''
        Delete a service registration by ID. This operation should be idempotent.

        :param registration_id: The service registration identifier.
        :type registration_id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete_registration method is required for DIService.')

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
