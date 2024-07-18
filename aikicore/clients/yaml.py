import os
import yaml

from ..objects.data import DataObject


def load(self, path: str, start_node: function = lambda data: data):
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

