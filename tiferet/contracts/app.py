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
    def get_interface(self, app_name: str) -> AppInterface:
        '''
        Get the app interface settings by name.

        :param app_name: The name of the app. 
        :type app_name: str
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

# ** interface: app_service
class AppService(Service):
    '''
    An app service is a class that is used to manage app interfaces.
    '''

    # * method: load_app_repository
    @abstractmethod
    def load_app_repository(self, 
        app_repo_module_path: str,
        app_repo_class_name: str,
        app_repo_params: Dict[str, Any],
        **kwargs
    ) -> AppRepository:
        '''
        Execute the command.

        :param app_repo_module_path: The application repository module path.
        :type app_repo_module_path: str
        :param app_repo_class_name: The application repository class name.
        :type app_repo_class_name: str
        :param app_repo_params: The application repository parameters.
        :type app_repo_params: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The application repository instance.
        :rtype: AppRepository
        '''
        # Not implemented.
        raise NotImplementedError('load_app_repository method is required for AppService.')
    
    # * method: load_app_instance
    @abstractmethod
    def load_app_instance(self, app_interface: AppInterface, default_attrs: List[AppAttribute]) -> Any:
        '''
        Create the app dependency injector.

        :param app_interface: The app interface.
        :type app_interface: AppInterface
        :param default_attrs: The default configured attributes for the app.
        :type default_attrs: List[AppAttribute]
        :return: The app instance.
        :rtype: Any
        '''
        # Not implemented.
        raise NotImplementedError('load_app_instance method is required for AppService.')
