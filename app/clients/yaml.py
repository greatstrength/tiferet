
import yaml

from ..objects.data import DataObject


def load(path: str, create_data = lambda data: data, start_node = lambda data: data, **kwargs):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
        if start_node:
            data = start_node(data)
        return create_data(data, **kwargs)


def save(path: str, data: DataObject | dict, start_node = lambda data: data):
    with open(path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    replace_node = start_node(yaml_data)
    if isinstance(data, DataObject):
        replace_node = data.map('to_data.yaml')
    else:
        replace_node = data

    with open(path, 'w') as file:
        yaml.safe_dump(yaml_data, file)

