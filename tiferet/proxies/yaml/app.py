"""Tiferet App YAML Proxy"""

# *** imports

# ** core
from typing import (
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
from .settings import YamlFileProxy

# *** proxies

# ** proxy: app_yaml_proxy
class AppYamlProxy(AppRepository, YamlFileProxy):
    '''
    YAML proxy for application configurations.
    '''

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
    def load_yaml(
            self, 
            start_node: Callable = lambda data: data,
            data_factory: Callable = lambda data: data
        ) -> Any:
        '''
        Load data from the YAML configuration file.

        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                data_factory=data_factory
            )
        
        # Raise an error if the loading fails.
        except Exception as e:
            RaiseError.execute(
                'APP_CONFIG_LOADING_FAILED',
                f'Unable to load app configuration file {self.yaml_file}: {e}.',
                yaml_file=self.yaml_file,
                exception=str(e)
            )

    # * method: list_interfaces
    def list_interfaces(self) -> list[AppInterfaceContract]:
        '''
        List all app interfaces.

        :return: The list of app interfaces.
        :rtype: List[AppInterface]
        '''

        # Load the app interface data from the yaml configuration file and map it to the app interface object.
        interfaces = self.load_yaml(
            data_factory=lambda data: [
                DataObject.from_data(
                    AppInterfaceConfigData,
                    id=interface_id,
                    **record
                ).map() for interface_id, record in data.items()],
            start_node=lambda data: data.get('interfaces'))

        # Return the list of app interface objects.
        return interfaces

    # * method: get_interface
    def get_interface(self, id: str) -> AppInterfaceContract:
        '''
        Get the app interface.

        :param id: The app interface id.
        :type id: str
        :return: The app interface.
        :rtype: AppInterface
        '''

        # Load the app interface data from the yaml configuration file.
        interface_data: AppInterfaceContract = self.load_yaml(
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
        self.save_yaml(
            data=interface_data.to_primitive('to_data.yaml'),
            data_yaml_path=f'interfaces/{interface.id}'
        )

    # * method: delete_interface
    def delete_interface(self, interface_id: str):
        '''
        Delete the app interface from the YAML configuration file.

        :param interface_id: The unique identifier for the app interface to delete.
        :type interface_id: str
        '''

        # Delete the app interface data from the YAML configuration file.
        interfaces_data = self.load_yaml(
            start_node=lambda data: data.get('interfaces', {})
        )

        # Pop the interface from the interfaces data regardless of whether it exists or not to ensure it is deleted.
        interfaces_data.pop(interface_id, None)

        # Save the updated interfaces data back to the YAML configuration file.
        self.save_yaml(
            data=interfaces_data,
            data_yaml_path='interfaces'
        )