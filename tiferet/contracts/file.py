"""Tiferet File Contract"""

# *** imports

# ** core
from abc import abstractmethod

# ** app
from .settings import Service

# *** contracts

# ** contract: file_service
class FileService(Service):
    '''
    Abstract contract for low-level file stream management.
    '''

    # * method: open_file
    @abstractmethod
    def open_file(self):
        '''
        Open the file stream with configured path, mode, and encoding.
        '''
        
        raise NotImplementedError('The open_file method must be implemented by the file service.')

    # * method: close_file
    @abstractmethod
    def close_file(self):
        '''
        Close the file stream if open.
        '''
        
        raise NotImplementedError('The close_file method must be implemented by the file service.')