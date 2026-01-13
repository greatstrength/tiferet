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
    An app repository is a class that is used to get an app interface.
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
    Service interface for managing app interfaces using a repository-style API.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if an app interface exists by ID.

        :param id: The app interface identifier.
        :type id: str
        :return: True if the app interface exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for AppService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> AppInterface | None:
        '''
        Retrieve an app interface by ID.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface if found, otherwise None.
        :rtype: AppInterface | None
        '''
        # Not implemented.
        raise NotImplementedError('get method is required for AppService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[AppInterface]:
        '''
        List all app interfaces.

        :return: A list of app interfaces.
        :rtype: List[AppInterface]
        '''
        # Not implemented.
        raise NotImplementedError('list method is required for AppService.')

    # * method: save
    @abstractmethod
    def save(self, interface: AppInterface) -> None:
        '''
        Save or update an app interface.

        :param interface: The app interface to save.
        :type interface: AppInterface
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save method is required for AppService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an app interface by ID. This operation should be idempotent.

        :param id: The app interface identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete method is required for AppService.')
