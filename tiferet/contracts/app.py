"""Tiferet App Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import (
    List,
    Dict,
    Any
)

# ** app
from .settings import (
    ModelContract,
    Repository,
    Service
)

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

    # * attribute: parameters
    parameters: Dict[str, str]

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

    # * attribute: logger_id
    logger_id: str

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
    An app repository is a class that is used to manage app interfaces.
    '''

    # * method: get_interface
    @abstractmethod
    def get_interface(self, interface_id: str) -> AppInterface:
        '''
        Get the app interface settings by name.

        :param interface_id: The unique identifier for the app interface.
        :type interface_id: str
        :return: The app interface.
        :rtype: AppInterface
        '''
        # Not implemented.
        raise NotImplementedError('get_interface method is required for AppRepository.')

    # * method: list_interfaces
    @abstractmethod
    def list_interfaces(self) -> List[AppInterface]:
        '''
        List all app inferface settings.

        :return: A list of app settings.
        :rtype: List[AppInterface]
        '''
        # Not implemented.
        raise NotImplementedError('list_interfaces method is required for AppRepository.')
    
    # * method: save_interface
    def save_interface(self, interface: AppInterface):
        '''
        Save the app interface settings.

        :param interface: The app interface to save.
        :type interface: AppInterfaceContract
        '''
        # Not implemented.
        raise NotImplementedError('save_interface method is required for AppRepository.')
    
    # * method: delete_interface
    def delete_interface(self, interface_id: str):
        '''
        Delete the app interface settings by name.

        :param interface_id: The unique identifier for the app interface to delete.
        :type interface_id: str
        '''
        # Not implemented.
        raise NotImplementedError('delete_interface method is required for AppRepository.')

# ** interface: app_service
class AppService(Service):
    '''
    App service interface that mirrors AppRepository but with shorter method
    names, providing a service-level abstraction for managing app interfaces.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if the app interface exists.

        :param id: The unique identifier for the app interface.
        :type id: str
        :return: True if the app interface exists, False otherwise.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for AppService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> AppInterface:
        '''
        Get the app interface by its unique identifier.

        :param id: The unique identifier for the app interface.
        :type id: str
        :return: The app interface, or None if not found.
        :rtype: AppInterface
        '''
        raise NotImplementedError('get method is required for AppService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[AppInterface]:
        '''
        List all app interfaces.

        :return: A list of app interfaces.
        :rtype: List[AppInterface]
        '''
        raise NotImplementedError('list method is required for AppService.')

    # * method: save
    @abstractmethod
    def save(self, interface: AppInterface) -> None:
        '''
        Save the app interface settings.

        :param interface: The app interface to save.
        :type interface: AppInterface
        '''
        raise NotImplementedError('save method is required for AppService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete the app interface settings by its unique identifier.

        :param id: The unique identifier for the app interface to delete.
        :type id: str
        '''
        raise NotImplementedError('delete method is required for AppService.')

