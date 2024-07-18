import os
import yaml

from ..objects.data import DataObject


class YamlClient(object):

    def __init__(self, base_path: str):
        if not base_path:
            base_path = os.getcwd()
        self.base_path = base_path

    def load(self, start_node: function = lambda data: data):
        with open(self.base_path, 'r') as file:
            data = yaml.safe_load(file)
            return start_node(data)

    def save(self, data: DataObject, start_node: function = lambda data: data):
        with open(self.base_path, 'r') as file:
            yaml_data = yaml.safe_load(file)

        replace_node = start_node(yaml_data)
        replace_node = data.to_primitive('to_data.yaml')

        with open(self.base_path, 'w') as file:
            yaml.safe_dump(yaml_data, file)

