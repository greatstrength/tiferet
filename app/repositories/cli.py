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

    def __init__(self, base_path: str):
        self.base_path = base_path

    def get(self, interface_id: str) -> CliInterface:
        data: CliInterfaceData = yaml_client.load(
            self.base_path, 
            create_data=lambda data: CliInterfaceData.new(interface_id, data),
            start_node=lambda data: data.get('interfaces').get(interface_id))
        return data.map('to_object.yaml')

    def save(self, interface: CliInterface):
        data = yaml_client.load(self.base_path)
        data['interfaces'][interface.id] = CliInterfaceData(interface).map('to_data.yaml')
