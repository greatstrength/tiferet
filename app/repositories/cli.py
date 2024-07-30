from typing import List

from ..objects.cli import CliInterface
from ..data.cli import CliInterfaceData
from ..clients import yaml as yaml_client


class CliInterfaceRepository(object):

    def get(self, interface_id: str) -> CliInterface:
        raise NotImplementedError()

    def save(self, interface: CliInterface):
        raise NotImplementedError


class YamlRepository(CliInterfaceRepository):

    base_path: str

    def __init__(self, interface_yaml_base_path: str):

        # Set the base path.
        self.base_path = interface_yaml_base_path

    def get(self, interface_id: str) -> CliInterface:

        # Load the interface data from the yaml configuration file.
        data: CliInterfaceData = yaml_client.load(
            self.base_path, 
            create_data=lambda data: CliInterfaceData.from_yaml_data(interface_id, data),
            start_node=lambda data: data.get('interfaces').get(interface_id))
        
        # Return the interface object.
        return data.map('to_object.yaml')

    def save(self, interface: CliInterface):
        
        # Create updated interface data.
        interface_data = CliInterfaceData.new(**interface.to_primitive())

        # Update the interface data.
        yaml_client.save(
            path=self.base_path, 
            data=interface_data,
            data_save_path=f'interfaces.{interface.id}',
        )

        # Return the updated interface object.
        return interface_data.map('to_object.yaml')
