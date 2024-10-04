from typing import List, Dict, Any

from ..objects.data import ModelData

def load(path: str, map_to_data: lambda data: data, **kwargs):
    
    # Load the data from the file.
    # Return None if the file is not found.
    # Return the data if the file is found but the data is None.
    try:
        with open(path, 'r') as file:
            data = file.read()
        if not data:
            return None
    except FileNotFoundError:
        return None
    
    # Map the data to the data object.
    return map_to_data(data, **kwargs)


def save(path: str, data: ModelData | List[str], **kwargs):
    with open(path, 'w') as file:
        if isinstance(data, ModelData):
            data = data.to_primitive('to_data.python')
        file.write(data)