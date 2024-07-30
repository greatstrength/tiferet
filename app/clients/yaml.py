
import yaml

from ..objects.data import DataObject


def load(path: str, create_data = lambda data: data, start_node = lambda data: data, **kwargs):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    data = start_node(data)
    if not data:
        return None
    return create_data(data, **kwargs)


def save(path: str, data: DataObject | dict, data_save_path: str, **kwargs):
    with open(path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Get the data save path list.
    save_path_list = data_save_path.split('.')

    # Update the yaml data.
    new_yaml_data = None
    for fragment in save_path_list[:-1]:
        if new_yaml_data is None:
            new_yaml_data = yaml_data[fragment]
        else:
            new_yaml_data = new_yaml_data[fragment]

    new_yaml_data[save_path_list[-1]] = data.to_primitive('to_data.yaml')

    # Save the updated yaml data.
    with open(path, 'w') as file:
        yaml.safe_dump(yaml_data, file)
