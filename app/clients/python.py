from typing import List, Dict, Any

from ..objects.data import ModelData

def load(path: str, map_to_data: lambda data: data, **kwargs):
    with open(path, 'r') as file:
        data = file.readlines()
    if data == None:
        return None
    return map_to_data(data, **kwargs)


def save(path: str, data: ModelData | List[str], **kwargs):
    with open(path, 'w') as file:
        if isinstance(data, ModelData):
            data = data.to_primitive('to_data.python')
        file.write(data)