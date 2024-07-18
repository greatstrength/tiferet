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
        data = yaml_client.load(self.base_path, lambda data: data.get(interface_id))
        return CliInterfaceData(data).map('to_object.yaml', interface_id)

    def save_interface(self, interface: CliInterface):
        data = yaml_client.load(self.base_path)
        data['interfaces'][interface.id] = CliInterfaceData(interface).map('to_data.yaml')
