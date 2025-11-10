"""Tiferet JSON Middleware Tests"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from ..json import JsonLoaderMiddleware

# *** fixtures

# ** fixture: temp_json_file
@pytest.fixture
def temp_json_file(tmp_path):
    '''
    Fixture to create a temporary JSON file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created temporary JSON file.
    :rtype: str
    '''

    # Create a temporary JSON file with sample content.
    file_path = tmp_path / 'test.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'key': 'value', 
            'nested': {
                'a': 1
            },
            'list': [{
                'b': 2
            }]
        }, f)
    
    # Return the file path as a string.
    return str(file_path)

# *** tests

# ** test: json_loader_middleware_load_json
def test_json_loader_middleware_load_json(temp_json_file: str):
    '''
    Test successful loading of a JSON file using JsonLoaderMiddleware.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: str
    '''
    
    # Load the JSON content.
    with JsonLoaderMiddleware(path=temp_json_file) as json_r:
        content = json_r.load_json()
    
    # Verify the loaded content.
    assert isinstance(content, dict)
    assert content == {'key': 'value', 'nested': {'a': 1}, 'list': [{'b': 2}]}
    
    # Verify the file is closed after loading.
    assert json_r.file is None

# ** test: json_loader_middleware_load_json_start_node
def test_json_loader_middleware_load_json_start_node(temp_json_file: str):
    '''
    Test loading a JSON file with a custom start node using JsonLoaderMiddleware.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: str
    '''
    
    # Define a custom start node function to extract nested data.
    def start_node(data):
        return data.get('nested', {})
    
    # Load the JSON content using the custom start node.
    with JsonLoaderMiddleware(path=temp_json_file) as json_r:
        content = json_r.load_json(start_node=start_node)
    
    # Verify the loaded content is the nested dictionary.
    assert isinstance(content, dict)
    assert content == {'a': 1}
    
    # Verify the file is closed after loading.
    assert json_r.file is None

# ** test: json_loader_middleware_parse_json_path
def test_json_loader_middleware_parse_json_path(temp_json_file: str):
    '''
    Test parsing a JSON path to extract specific data from a JSON file using JsonLoaderMiddleware.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: str
    '''
    
    # Load the JSON content and parse a JSON path.
    with JsonLoaderMiddleware(path=temp_json_file, mode='w') as json_w:
        path = json_w.parse_json_path('list[0].b')
    
    # Verify the parsed path is correct.
    assert path == ['list', 0, 'b']

# ** test: json_loader_middleware_save_json
def test_json_loader_middleware_save_json(temp_json_file: str):
    '''
    Test saving a dictionary to a JSON file using JsonLoaderMiddleware.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: str
    '''
    
    # Data to save.
    data = {'new_key': 'new_value', 'nested': {'b': 2}, 'list': [{'c': 3}]}
    
    # Save the data to the JSON file.
    with JsonLoaderMiddleware(path=temp_json_file, mode='w') as json_w:
        json_w.save_json(data)
    
    # Load the JSON content to verify the update.
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
 
    # Verify the updated content.
    assert isinstance(content, dict)
    assert content == data

    # Verify the file is closed after saving and that the cache data is cleared.
    assert json_w.file is None
    assert json_w.cache_data is None

# ** test: json_loader_middleware_save_json_data_json_path
def test_json_loader_middleware_save_json_data_json_path(temp_json_file: str):
    '''
    Test saving a dictionary to a specific path in a JSON file using JsonLoaderMiddleware.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: str
    '''
    
    # Data to save.
    data = {'c': 3}
    
    # Save the data to a specific path in the JSON file.
    with JsonLoaderMiddleware(path=temp_json_file, mode='w') as json_w:
        json_w.save_json(data, data_json_path='nested.new_nested')
    
    # Load the JSON content to verify the update.
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
 
    # Verify the updated content.
    assert isinstance(content, dict)
    assert content == {
        'key': 'value',
        'nested': {
            'a': 1,
            'new_nested': {'c': 3},
        },
        'list': [{
            'b': 2
        }]
    }

    # Verify the file is closed after saving and that the cache data is cleared.
    assert json_w.file is None
    assert json_w.cache_data is None

# ** test: json_loader_middleware_save_json_data_json_path_list
def test_json_loader_middleware_save_json_data_json_path_list(temp_json_file: str):
    '''
    Test saving a dictionary to a specific path in a JSON file using JsonLoaderMiddleware with a list path.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: str
    '''
    
    # Data to save.
    data = {'d': 4}
    
    # Save the data to a specific path in the JSON file using a list for the path.
    with JsonLoaderMiddleware(path=temp_json_file, mode='w') as json_w:
        json_w.save_json(data, data_json_path='list[0]')
    
    # Load the JSON content to verify the update.
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
 
    # Verify the updated content.
    assert isinstance(content, dict)
    assert content == {
        'key': 'value',
        'nested': {
            'a': 1,
        },
        'list': [{
            'd': 4
        }]
    }

    # Verify the file is closed after saving and that the cache data is cleared.
    assert json_w.file is None
    assert json_w.cache_data is None