# *** imports

# ** app
from ..configs import *
from ..models.error import *

# *** repository

# ** interface: error_repository
class ErrorRepository(ABC):
    '''
    An interface for managing errors.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.

        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str) -> Error:
        '''
        Get the error.

        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: Error
        '''
        raise NotImplementedError()
    
    # * method: list
    @abstractmethod
    def list(self) -> List[Error]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''
        raise NotImplementedError()
    
    # * method: save
    @abstractmethod
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''
        raise NotImplementedError()