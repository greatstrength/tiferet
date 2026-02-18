"""Tiferet CLI Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from ..mappers import CliCommandAggregate
from .settings import Service

# *** interfaces

# ** interface: cli_service
class CliService(Service):
    '''
    Service interface for managing CLI commands using a repository-style API.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a CLI command exists by ID.

        :param id: The CLI command identifier.
        :type id: str
        :return: True if the CLI command exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for CliService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> CliCommandAggregate:
        '''
        Retrieve a CLI command by ID.

        :param id: The CLI command identifier.
        :type id: str
        :return: The CLI command aggregate.
        :rtype: CliCommandAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get method is required for CliService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[CliCommandAggregate]:
        '''
        List all CLI commands.

        :return: A list of CLI command aggregates.
        :rtype: List[CliCommandAggregate]
        '''
        # Not implemented.
        raise NotImplementedError('list method is required for CliService.')

    # * method: save
    @abstractmethod
    def save(self, command: CliCommandAggregate) -> None:
        '''
        Save or update a CLI command.

        :param command: The CLI command aggregate to save.
        :type command: CliCommandAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save method is required for CliService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a CLI command by ID. This operation should be idempotent.

        :param id: The CLI command identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete method is required for CliService.')
