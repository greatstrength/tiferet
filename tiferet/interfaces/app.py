"""Tiferet Interfaces App"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from ..mappers import AppSessionAggregate
from .core import Service

# *** interfaces

# ** interface: app_service
class AppService(Service):
    '''
    Service interface for managing app interface configurations.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if an app session exists by ID.

        :param id: The app session identifier.
        :type id: str
        :return: True if the app session exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for AppService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> AppSessionAggregate:
        '''
        Retrieve an app session by ID.

        :param id: The app session identifier.
        :type id: str
        :return: The app session aggregate.
        :rtype: AppSessionAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get method is required for AppService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[AppSessionAggregate]:
        '''
        List all app sessions.

        :return: A list of app session aggregates.
        :rtype: List[AppSessionAggregate]
        '''
        # Not implemented.
        raise NotImplementedError('list method is required for AppService.')

    # * method: save
    @abstractmethod
    def save(self, session: AppSessionAggregate) -> None:
        '''
        Save or update an app session.

        :param session: The app session aggregate to save.
        :type session: AppSessionAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save method is required for AppService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an app session by ID. This operation should be idempotent.

        :param id: The app session identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete method is required for AppService.')
