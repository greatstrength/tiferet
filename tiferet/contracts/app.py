# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import *

# *** contracts

# ** contract: app_attribute
class AppAttributeContract(ModelContract):
    '''
    An app dependency contract that defines the dependency attributes for an app interface.
    '''

    # * attribute: module_path
    module_path: str

    # * attribute: class_name
    class_name: str

    # * attribute: attribute_id
    attribute_id: str

    # * attribute: parameters
    parameters: Dict[str, str]

# ** contract: app_interface_contract
class AppInterfaceContract(ModelContract):
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

    # * attribute: logger_id
    logger_id: str

    # * attribute: feature_flag
    feature_flag: str

    # * attribute: data_flag
    data_flag: str

    # * attribute: attributes
    attributes: List[AppAttributeContract]

    # * attribute: constants
    constants: Dict[str, Any]

# ** interface: app_repository
class AppRepository(Repository):
    '''
    An app repository is a class that is used to get an app interface.
    '''

    # * method: get_interface
    @abstractmethod
    def get_interface(self, interface_id: str) -> AppInterfaceContract:
        '''
        Get the app interface settings by its ID.

        : param interface_id: The app interface ID.
        :type interface_id: str
        :return: The app interface settings.
        :rtype: AppInterfaceContract
        '''
        # Not implemented.
        raise NotImplementedError('get_interface method is required for AppRepository.')
    
    # * method: list_interfaces
    @abstractmethod
    def list_interfaces(self) -> List[AppInterfaceContract]:
        '''
        List all app inferface settings.

        :return: A list of app settings.
        :rtype: List[AppInterfaceContract]
        '''
        # Not implemented.
        raise NotImplementedError('list_interfaces method is required for AppRepository.')