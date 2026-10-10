"""Tiferet Interfaces Check"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any

# ** app
from .core import Service

# *** interfaces

# ** interface: check_service
class CheckService(Service):
    '''
    Answers one verification during a check, so a phase event can swap the
    comparison without seeing the module, the node, or the failure pool.

    The return is a mismatch or ``None``. The event raises the catalogued
    error. This service does not.
    '''

    # * method: equal
    @abstractmethod
    def equal(self, actual: Any, expected: Any) -> str | None:
        '''
        Compare two values, including a structural compare.

        :param actual: The value under check.
        :type actual: Any
        :param expected: The expected value.
        :type expected: Any
        :return: A mismatch, or None when the values match.
        :rtype: str | None
        '''
        raise NotImplementedError()

    # * method: codes
    @abstractmethod
    def codes(self, actual: str, expected: str) -> str | None:
        '''
        Compare two error-code strings.

        :param actual: The code that was read.
        :type actual: str
        :param expected: The code that was required.
        :type expected: str
        :return: A mismatch, or None when the codes match.
        :rtype: str | None
        '''
        raise NotImplementedError()

    # * method: role_dump
    @abstractmethod
    def role_dump(self, dumped: Any, exclude: Any) -> str | None:
        '''
        Compare a dump to an exclude set.

        :param dumped: The dumped mapping.
        :type dumped: Any
        :param exclude: Names that must be absent from the dump.
        :type exclude: Any
        :return: A mismatch, or None when every excluded name is absent.
        :rtype: str | None
        '''
        raise NotImplementedError()

    # * method: mapper_contract
    @abstractmethod
    def mapper_contract(self, exclude: Any, source: Any) -> str | None:
        '''
        Run the mapper protocol and return one mismatch or None.

        :param exclude: Names the to_data role excludes. Compared as a set.
        :type exclude: Any
        :param source: The domain source ``from_model`` copies. Already built.
        :type source: Any
        :return: A mismatch, or None when the protocol holds.
        :rtype: str | None
        '''
        raise NotImplementedError()
