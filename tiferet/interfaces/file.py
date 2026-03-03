"""Tiferet Interfaces File"""

# *** imports

# ** core
from abc import abstractmethod
from typing import IO, Any

# ** app
from .settings import Service

# *** interfaces

# ** interface: file_service
class FileService(Service):
    '''
    Service contract for low-level file stream operations.
    '''

    # * method: open_file
    @abstractmethod
    def open_file(self, path: str, mode: str = 'r', encoding: str | None = None, **kwargs) -> IO[Any]:
        '''
        Open a file stream.

        :param path: File system path.
        :type path: str
        :param mode: File open mode (r, w, a, etc.).
        :type mode: str
        :param encoding: Text encoding (for text modes).
        :type encoding: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Open file object.
        :rtype: IO[Any]
        '''
        raise NotImplementedError()

    # * method: close_file
    @abstractmethod
    def close_file(self, file: IO[Any]) -> None:
        '''
        Safely close an open file stream.

        :param file: The open file object to close.
        :type file: IO[Any]
        '''
        raise NotImplementedError()

    # * method: __enter__
    @abstractmethod
    def __enter__(self) -> 'FileService':
        '''
        Enter the runtime context for this file service.

        :return: The file service instance.
        :rtype: FileService
        '''
        raise NotImplementedError()

    # * method: __exit__
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        '''
        Exit the runtime context, ensuring resources are released.

        :param exc_type: The exception type, if any.
        :type exc_type: type | None
        :param exc_val: The exception value, if any.
        :type exc_val: BaseException | None
        :param exc_tb: The traceback, if any.
        :type exc_tb: object | None
        '''
        raise NotImplementedError()
