"""Tiferet App Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from ..mappers import AppInterfaceAggregate
from .settings import Service

# *** interfaces

# ** interface: app_service
class AppService(Service):
    '''
    Service interface for managing app interfaces using a repository-style API.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if an app interface exists by ID.

        :param id: The app interface identifier.
        :type id: str
        :return: True if the app interface exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for AppService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> AppInterfaceAggregate:
        '''
        Retrieve an app interface by ID.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface.
        :rtype: AppInterfaceAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get method is required for AppService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[AppInterfaceAggregate]:
        '''
        List all app interfaces.

        :return: A list of app interfaces.
        :rtype: List[AppInterfaceAggregate]
        '''
        # Not implemented.
        raise NotImplementedError('list method is required for AppService.')

    # * method: save
    @abstractmethod
    def save(self, interface: AppInterfaceAggregate) -> None:
        '''
        Save or update an app interface.

        :param interface: The app interface to save.
        :type interface: AppInterfaceAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save method is required for AppService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an app interface by ID. This operation should be idempotent.

        :param id: The app interface identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete method is required for AppService.')
