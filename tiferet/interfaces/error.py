"""Tiferet Error Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from ..mappers import ErrorAggregate
from .settings import Service

# *** interfaces

# ** interface: error_service
class ErrorService(Service):
    '''
    Service interface for managing error objects using a repository-style API.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if an error exists by ID.

        :param id: The error identifier.
        :type id: str
        :return: True if the error exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for ErrorService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> ErrorAggregate:
        '''
        Retrieve an error by ID.

        :param id: The error identifier.
        :type id: str
        :return: The error aggregate.
        :rtype: ErrorAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get method is required for ErrorService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[ErrorAggregate]:
        '''
        List all errors.

        :return: A list of error aggregates.
        :rtype: List[ErrorAggregate]
        '''
        # Not implemented.
        raise NotImplementedError('list method is required for ErrorService.')

    # * method: save
    @abstractmethod
    def save(self, error: ErrorAggregate) -> None:
        '''
        Save or update an error.

        :param error: The error aggregate to save.
        :type error: ErrorAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save method is required for ErrorService.')
    
    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an error by ID. This operation should be idempotent.

        :param id: The error identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete method is required for ErrorService.')
