"""Tiferet Tester Service Interface"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from ..mappers import TesterAggregate
from .core import Service

# *** interfaces

# ** interface: tester_service
class TesterService(Service):
    '''Vertical contract for declarative tester storage and retrieval.'''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''Check whether a tester exists.

        :param id: The tester identifier.
        :type id: str
        :return: True when the tester exists.
        :rtype: bool
        '''

        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str) -> TesterAggregate | None:
        '''Retrieve a tester by id.

        :param id: The tester identifier.
        :type id: str
        :return: The tester or None when absent.
        :rtype: TesterAggregate | None
        '''

        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self, type: str | None = None) -> List[TesterAggregate]:
        '''List testers, optionally filtered by type.

        :param type: The optional tester type filter.
        :type type: str | None
        :return: Matching tester aggregates.
        :rtype: List[TesterAggregate]
        '''

        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, tester: TesterAggregate) -> None:
        '''Persist a tester aggregate.

        :param tester: The tester to save.
        :type tester: TesterAggregate
        :return: None
        :rtype: None
        '''

        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''Delete a tester idempotently.

        :param id: The tester identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        raise NotImplementedError()
