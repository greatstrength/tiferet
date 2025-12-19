"""Tiferet App JSON Proxy"""

# *** imports

# ** core
from typing import (
    List,
    Any,
    Callable
)

# ** app
from ...commands import RaiseError
from ...data import (
    DataObject,
    AppInterfaceConfigData,
    AppAttributeConfigData
)
from ...contracts import AppInterfaceContract, AppRepository
from .settings import JsonFileProxy

# *** proxies

# ** proxy: app_json_proxy
class AppJsonProxy(AppRepository, JsonFileProxy):
    '''
    JSON proxy for application configurations.
    '''

    # * method: init
    def __init__(self, app_config_file: str):
        '''
        Initialize the JSON proxy.

        :param app_config_file: The application configuration file.
        :type app_config_file: str
        '''

        # Set the configuration file.
        super().__init__(app_config_file)

    # * method: load_json
    def load_json(
            self, 
            start_node: Callable = lambda data: data,
            data_factory: Callable = lambda data: data
        ) -> Any:
        '''
        Load data from the JSON configuration file.

        :param start_node: The starting node in the JSON file.
        :type start_node: str
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the JSON file contents using the json config proxy.
        try:
            return super().load_json(
                start_node=start_node,
                data_factory=data_factory
            )

        # Handle any exceptions that occur during loading.
        except Exception as e:
            RaiseError.execute(
                'APP_CONFIG_LOADING_FAILED',
                f'Unable to load app configuration file {self.json_file}: {e}.',
                json_file=self.json_file,
                exception=str(e)
            )

    # * method: list_interfaces
    def list_interfaces(self) -> List[AppInterfaceContract]:
        '''
        List all interface configurations from the JSON configuration file.

        :return: A list of AppInterfaceContract instances.
        :rtype: List[AppInterfaceContract]
        '''

        # Load the interface configurations using the load_json method.
        interfaces = self.load_json(
            data_factory=lambda data: [
                DataObject.from_data(
                    AppInterfaceConfigData,
                    id=interface_id,
                    **interface_data
                ).map() for interface_id, interface_data in data.items()
            ],
            start_node=lambda data: data.get('interfaces', [])
        )

        # Return the list of app interface objects.
        return interfaces
    
    # * method: get_interface
    def get_interface(self, id: str) -> AppInterfaceContract:
        '''
        Get a specific interface configuration by its ID.

        :param id: The ID of the interface to retrieve.
        :type id: str
        :return: An instance of AppInterfaceContract.
        :rtype: AppInterfaceContract
        '''

        # Load the app interface data from the json configuration file.
        interface_data = self.load_json(
            start_node=lambda data: data.get('interfaces').get(id, None)
        )

        # If the interface data is empty, return None.
        if not interface_data:
            return None

        # Return the app interface object.
        return DataObject.from_data(
            AppInterfaceConfigData,
            id=id,
            **interface_data
        ).map()
    
        # * method: save_interface
    def save_interface(self, interface: AppInterfaceContract):
        '''
        Save the app interface to the YAML configuration file.

        :param interface: The app interface to save.
        :type interface: AppInterfaceContract
        '''

        # Create the attribute data for the app interface from the app interface contract.
        attributes = {
            attr.attribute_id: DataObject.from_model(
                AppAttributeConfigData,
                model=attr
            ) for attr in interface.attributes
        }

        # Convert the app interface object to a DataObject.
        interface_data = DataObject.from_model(
            AppInterfaceConfigData,
            model=interface,
            attributes=attributes
        )

        # Save the app interface data to the YAML configuration file.
        self.save_json(
            data=interface_data.to_primitive(self.default_role),
            data_json_path=f'interfaces.{interface.id}'
        )

    # * method: delete_interface
    def delete_interface(self, interface_id: str):
        '''
        Delete the app interface from the YAML configuration file.

        :param interface_id: The unique identifier for the app interface to delete.
        :type interface_id: str
        '''

        # Delete the app interface data from the YAML configuration file.
        interfaces_data = self.load_json(
            start_node=lambda data: data.get('interfaces', {})
        )

        # Pop the interface from the interfaces data regardless of whether it exists or not to ensure it is deleted.
        interfaces_data.pop(interface_id, None)

        # Save the updated interfaces data back to the YAML configuration file.
        self.save_json(
            data=interfaces_data,
            data_json_path='interfaces'
        )