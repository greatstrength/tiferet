# *** imports

# ** app
from ..configs import *
from ..models.app import *


# *** repository

# ** interface: app_repository
class AppRepository(ABC):
    '''
    An app repository is a class that is used to get an app interface.
    '''

    # * method: list_interfaces
    @abstractmethod
    def list_interfaces(self) -> List[AppInterface]:
        '''
        List all app interfaces.

        :return: The list of app interfaces.
        :rtype: List[AppInterface]
        '''
        # Not implemented.
        raise NotImplementedError()

    # * method: get_interface
    @abstractmethod
    def get_interface(self, id: str) -> AppInterface:
        '''
        Get the app interface.

        :param id: The app interface id.
        :type id: str
        :return: The app interface.
        :rtype: AppInterface
        '''
        # Not implemented.
        raise NotImplementedError()