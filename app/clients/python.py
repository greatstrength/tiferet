from typing import List, Dict, Any

from ..objects.data import ModelData

def load(path: str, map_to_data: lambda data: data, **kwargs):
    
    # Load the data from the file.
    try:
        with open(path, 'r') as file:
            data = file.read().split('\n')

    # Return None if the file is not found.
    except FileNotFoundError:
        return None
    
    if data == None:
        return None
    
    return map_to_data(data, **kwargs)


def save(path: str, data: ModelData | List[str], **kwargs):
    with open(path, 'w') as file:
        if isinstance(data, ModelData):
            data = data.to_primitive('to_data.python')
        file.write('\n'.join(data))