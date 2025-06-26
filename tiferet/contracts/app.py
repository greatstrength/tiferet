# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import *


# *** contracts

# ** contract: app_attribute
class AppAttribute(ModelContract):
    '''
    An app dependency contract that defines the dependency attributes for an app interface.
    '''

    # * attribute: module_path
    module_path: str

    # * attribute: class_name
    class_name: str

    # * attribute: attribute_id
    attribute_id: str


# ** contract: app_interface
class AppInterface(ModelContract):
    '''
    An app interface settings contract that defines the settings for an app interface.
    '''

    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: module_path
    module_path: str

    # * attribute: class_name
    class_name: str

    # * attribute: description
    description: str

    # * attribute: feature_flag
    feature_flag: str

    # * attribute: data_flag
    data_flag: str

    # * attribute: attributes
    attributes: List[AppAttribute]

    # * attribute: constants
    constants: Dict[str, Any]


# ** interface: app_repository
class AppRepository(Repository):
    '''
    An app repository is a class that is used to get an app interface.
    '''

    # * method: get_interface
    @abstractmethod
    def get_interface(self, app_name: str) -> AppInterface:
        '''
        Get the app interface settings by name.

        :param app_name: The name of the app. 
        :type app_name: str
        :return: The app interface.
        :rtype: AppInterface
        '''
        # Not implemented.
        raise NotImplementedError()
    
    # * method: list_interfaces
    @abstractmethod
    def list_interfaces(self) -> List[AppInterface]:
        '''
        List all app inferface settings.

        :return: A list of app settings.
        :rtype: List[AppInterface]
        '''
        # Not implemented.
        raise NotImplementedError()