# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import *


# *** contracts

# ** contract: app_settings
class AppSettings(ModelContract):
    '''
    An app settings contract is a class that defines the settings for an app instance.
    '''

    class AppDependency(ModelContract):
        '''
        An app dependency contract is a class that defines the dependencies for an app instance.
        '''

        # * attribute: module_path
        module_path: str

        # * attribute: class_name
        class_name: str

        # * attribute: attribute_id
        attribute_id: str

    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: description
    description: str

    # * attribute: feature_flag
    feature_flag: str

    # * attribute: data_flag
    data_flag: str

    # * attribute: dependencies
    dependencies: List[AppDependency]

    # * attribute: constants
    constants: Dict[str, Any]


# ** interface: app_repository
class AppRepository(Repository):
    '''
    An app repository is a class that is used to get an app interface.
    '''

    # * method: get_settings
    @abstractmethod
    def get_settings(self, app_name: str) -> AppSettings:
        '''
        Get the app instance settings by name.

        :param app_name: The name of the app. 
        :type app_name: str
        :return: The app interface.
        :rtype: AppInterface
        '''
        # Not implemented.
        raise NotImplementedError()
    
    # * method: list_settings
    @abstractmethod
    def list_settings(self) -> list[AppSettings]:
        '''
        List all app instance settings.

        :return: A list of app settings.
        :rtype: list[AppSettings]
        '''
        # Not implemented.
        raise NotImplementedError()