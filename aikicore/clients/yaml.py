import yaml

def load(path: str, start_node: function = lambda data: data):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
        return start_node(data)
    
def save(path: str, data: dict):
    with open(path, 'w') as file:
        yaml.safe_dump(data, file)