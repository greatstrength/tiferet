"""Tiferet YAML Middleware Tests"""

# *** imports

# ** infra
import pytest
import yaml

# ** app
from ..yaml import (
    YamlLoaderMiddleware, 
    TiferetError,
    const
)

# *** fixtures

# ** fixture: temp_yaml_file
@pytest.fixture
def temp_yaml_file(tmp_path):
    '''
    Fixture to create a temporary YAML file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created temporary YAML file.
    :rtype: str
    '''
    
    # Create a temporary YAML file with sample content.
    file_path = tmp_path / 'test.yaml'
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({
            'key': 'value', 
            'nested': {
                'a': 1
            }
        }, f)
    
    # Return the file path as a string.
    return str(file_path)

# *** tests

# ** test: yaml_loader_middleware_init_invalid_file
def test_yaml_loader_middleware_init_invalid_file():
    '''
    Test initialization of YamlLoaderMiddleware with an invalid YAML file path.
    '''

    yaml_loader_middleware = YamlLoaderMiddleware(path='invalid_file.txt')
    
    # Attempt to initialize with an invalid file path and verify that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        yaml_loader_middleware.open_file()
    
    # Verify the exception message.
    assert exc_info.value.error_code == const.INVALID_YAML_FILE_ID
    assert 'is not a valid YAML file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('path') == 'invalid_file.txt'

# ** test: yaml_loader_middleware_load
def test_yaml_loader_middleware_load(temp_yaml_file: str):
    '''
    Test successful loading of a YAML file using YamlLoaderMiddleware.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Load the YAML content.
    with YamlLoaderMiddleware(path=temp_yaml_file) as yaml_r:
        content = yaml_r.load()
    
    # Verify the loaded content.
    assert isinstance(content, dict)
    assert content == {'key': 'value', 'nested': {'a': 1}}
    
    # Verify the file is closed after loading.
    assert yaml_r.file is None

# ** test: yaml_loader_middleware_load_start_node
def test_yaml_loader_middleware_load_start_node(temp_yaml_file: str):
    '''
    Test loading a YAML file with a custom start node using YamlLoaderMiddleware.
    
    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''

    # Define a custom start node function to extract a specific part of the YAML content.
    def start_node(data):
        return data.get('nested', {})
    
    # Load the YAML content using the custom start node.
    with YamlLoaderMiddleware(path=temp_yaml_file) as yaml_r:
        content = yaml_r.load(start_node=start_node)

    # Verify the loaded content is the nested dictionary.
    assert isinstance(content, dict)
    assert content == {'a': 1}

    # Verify the file is closed after loading.
    assert yaml_r.file is None

# ** test: yaml_loader_middleware_save
def test_yaml_loader_middleware_save(temp_yaml_file: str):
    '''
    Test successful saving of a dictionary to a YAML file using YamlLoaderMiddleware.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Data to save.
    data = {'new_key': 'new_value', 'nested': {'b': 2}}
    
    # Save the data to the YAML file.
    with YamlLoaderMiddleware(path=temp_yaml_file, mode='w') as yaml_w:
        yaml_w.save(data)
    
    # Verify the file content.
    with open(temp_yaml_file, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
    assert content == data
    
    # Verify the file is closed after saving.
    assert yaml_w.file is None

# ** test: yaml_loader_middleware_save_data_yaml_path
def test_yaml_loader_middleware_save_data_yaml_path(temp_yaml_file: str):
    '''
    Test saving a dictionary to a specific path in a YAML file using YamlLoaderMiddleware.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Data to save.
    data = {'c': 3}
    
    # Save the data to a specific path in the YAML file.
    with YamlLoaderMiddleware(path=temp_yaml_file, mode='w') as yaml_w:
        yaml_w.save(data, data_path='nested/new_nested')
    
    # Load the YAML content to verify the update.
    with open(temp_yaml_file, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
 
    # Verify the updated content.
    assert isinstance(content, dict)
    assert content == {
        'key': 'value',
        'nested': {
            'a': 1,
            'new_nested': {'c': 3}
        }
    }
    
    # Verify the file is closed after saving and that the cache data is cleared.
    assert yaml_w.file is None
    assert yaml_w.cache_data is None