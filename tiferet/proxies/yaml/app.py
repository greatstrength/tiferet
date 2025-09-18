# *** imports

# ** core
from typing import Any

# ** app
from .core import *
from ...data import DataObject
from ...data.app import AppInterfaceYamlData
from ...contracts.app import AppRepository, AppInterface


# *** proxies

# ** proxy: app_yaml_proxy
class AppYamlProxy(AppRepository, YamlConfigurationProxy):


    # * method: init
    def __init__(self, app_config_file: str):
        '''
        Initialize the YAML proxy.

        :param app_config_file: The application configuration file.
        :type app_config_file: str
        '''

        # Set the configuration file.
        super().__init__(app_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )
        
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'APP_CONFIG_LOADING_FAILED',
                f'Unable to load app configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
            )

    # * method: list_interfaces
    def list_interfaces(self) -> list[AppInterface]:
        '''
        List all app interfaces.

        :return: The list of app interfaces.
        :rtype: List[AppInterface]
        '''

        # Load the app interface data from the yaml configuration file and map it to the app interface object.
        interfaces = self.load_yaml(
            create_data=lambda data: [
                DataObject.from_data(
                    AppInterfaceYamlData,
                    id=interface_id,
                    **record
                ).map() for interface_id, record in data.items()],
            start_node=lambda data: data.get('interfaces'))

        # Return the list of app interface objects.
        return interfaces

    # * method: get_interface
    def get_interface(self, id: str) -> AppInterface:
        '''
        Get the app interface.

        :param id: The app interface id.
        :type id: str
        :return: The app interface.
        :rtype: AppInterface
        '''

        # Load the app interface data from the yaml configuration file.
        _data: AppInterface = self.load_yaml(
            create_data=lambda data: DataObject.from_data(
                AppInterfaceYamlData,
                id=id, 
                **data
            ),
            start_node=lambda data: data.get('interfaces').get(id)
        )

        # Return the app interface object.
        # If the data is None, return None.
        try:
            return _data.map()
        except AttributeError:
            return None