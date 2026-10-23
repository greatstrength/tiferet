"""Tiferet Interfaces Stage"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Dict, List

# ** app
from .core import Service

# *** interfaces

# ** interface: stage_service
class StageService(Service):
    '''
    Owns one test's temporary directory and log capture, so a phase runtime
    can give a test a place to write files and a list of emitted records
    without importing a file or logging implementation.

    Returns are plain strings, bools, and dicts. A service failure raises.
    The phase runtime turns that failure into the catalogued step error.
    '''

    # * method: arrange
    @abstractmethod
    def arrange(self) -> None:
        '''
        Create the temporary directory and attach the log capture.

        :return: None.
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: close
    @abstractmethod
    def close(self) -> None:
        '''
        Detach the capture, restore the root level, and remove the directory.

        :return: None.
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: path
    @abstractmethod
    def path(self, *parts: str) -> str:
        '''
        Join relative parts under the directory without creating anything.

        :param parts: Relative path parts. None returns the directory.
        :type parts: str
        :return: The joined path string.
        :rtype: str
        '''
        raise NotImplementedError()

    # * method: write
    @abstractmethod
    def write(self, name: str, text: str) -> str:
        '''
        Write text as utf-8 bytes to one child of the directory.

        :param name: One path segment.
        :type name: str
        :param text: The text to write.
        :type text: str
        :return: The written path string.
        :rtype: str
        '''
        raise NotImplementedError()

    # * method: read
    @abstractmethod
    def read(self, name: str) -> str:
        '''
        Read one child of the directory as utf-8 text.

        :param name: One path segment.
        :type name: str
        :return: The text.
        :rtype: str
        '''
        raise NotImplementedError()

    # * method: exists
    @abstractmethod
    def exists(self, name: str) -> bool:
        '''
        Report whether one child of the directory exists.

        :param name: One path segment.
        :type name: str
        :return: True when the child exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: records
    @abstractmethod
    def records(self) -> List[Dict[str, Any]]:
        '''
        Return the captured records as plain dicts, in emission order.

        :return: Dicts with level, message, error, and logger.
        :rtype: List[Dict[str, Any]]
        '''
        raise NotImplementedError()

    # * method: message
    @abstractmethod
    def message(self, level: str, index: int) -> str:
        '''
        Return one captured message by level name and 0-based index.

        :param level: DEBUG, INFO, WARNING, ERROR, or CRITICAL.
        :type level: str
        :param index: The 0-based index within that level.
        :type index: int
        :return: The message string.
        :rtype: str
        '''
        raise NotImplementedError()
