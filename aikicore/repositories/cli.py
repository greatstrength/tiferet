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
        return self.client.load(CliInterfaceData, interface_id)

    def save_interface(self, interface: CliInterface):
        self.client.save(interface, CliInterfaceData)
