
import yaml

from ..objects.data import DataObject


def load(path: str, start_node = lambda data: data):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
        return start_node(data)


def save(path: str, data: DataObject, start_node = lambda data: data):
    with open(path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    replace_node = start_node(yaml_data)
    replace_node = data.to_primitive('to_data.yaml')

    with open(path, 'w') as file:
        yaml.safe_dump(yaml_data, file)

