"""Tiferet Settings YAML Proxy Settings Tests"""

# *** imports

# ** infra
import pytest
import yaml

# ** app
from ....commands import TiferetError
from ..settings import YamlFileProxy

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

# ** fixture: yaml_file_proxy
@pytest.fixture
def yaml_file_proxy(temp_yaml_file: str) -> YamlFileProxy:
    '''
    Fixture to create an instance of the YamlFileProxy.

    :param temp_yaml_file: The YAML configuration file path.
    :type temp_yaml_file: str
    '''

    # Create and return the YamlFileProxy instance.
    return YamlFileProxy(temp_yaml_file)

# *** tests

# ** test: yaml_file_proxy_init_invalid_file
def test_yaml_file_proxy_init_invalid_file():
    '''
    Test the initialization of YamlFileProxy with an invalid file.

    This test checks that initializing the YamlFileProxy with a non-YAML file raises a TiferetError.
    '''

    # Attempt to initialize the YamlFileProxy with an invalid file name.
    with pytest.raises(TiferetError) as exc_info:
        YamlFileProxy('invalid_file.txt')

    # Verify the error message.
    assert exc_info.value.error_code == 'INVALID_YAML_FILE'
    assert 'Valid YAML file not found at path:' in str(exc_info.value)

# ** test: yaml_file_proxy_init_invalid_file
def test_yaml_file_proxy_init_invalid_path():
    '''
    Test the initialization of YamlFileProxy with an invalid file.

    This test checks that initializing the YamlFileProxy with a non-YAML file raises a TiferetError.
    '''

    # Attempt to initialize the YamlFileProxy with an invalid file name.
    with pytest.raises(TiferetError) as exc_info:
        YamlFileProxy('invalid_file.txt')

    # Verify the error message.
    assert exc_info.value.error_code == 'INVALID_YAML_FILE'
    assert 'Valid YAML file not found at path:' in str(exc_info.value)

# ** test: yaml_file_proxy_load_yaml
def test_yaml_file_proxy_load_yaml(yaml_file_proxy: YamlFileProxy):
    '''
    Test the load_yaml method of the YamlFileProxy.

    :param yaml_file_proxy: The YAML configuration proxy.
    :type yaml_file_proxy: YamlFileProxy
    '''
    
    # Load the YAML file.
    data = yaml_file_proxy.load_yaml()
    
    # Verify that the loaded data matches the expected content.
    assert data == {
        'key': 'value',
        'nested': {
            'a': 1
        }
    }

# ** test: yaml_file_proxy_load_yaml_file_not_found
def test_yaml_file_proxy_load_yaml_file_not_found(yaml_file_proxy: YamlFileProxy):
    '''
    Test the load_yaml method with a file not found error.

    :param yaml_file_proxy: The YAML configuration proxy.
    :type yaml_file_proxy: YamlFileProxy
    '''

    # Set a non-existent configuration file.
    yaml_file_proxy.yaml_file = 'non_existent_file.yml'
    
    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        yaml_file_proxy.load_yaml()
    
    # Verify the error message.
    assert exc_info.value.error_code == 'YAML_FILE_LOAD_ERROR'
    assert 'An error occurred while loading the YAML file' in str(exc_info.value)
    assert 'non_existent_file.yml' in str(exc_info.value)

# ** test: yaml_file_proxy_save_yaml
def test_yaml_file_proxy_save_yaml(yaml_file_proxy: YamlFileProxy, temp_yaml_file: str):
    '''
    Test the save_yaml method of the YamlFileProxy.

    :param yaml_file_proxy: The YAML configuration proxy.
    :type yaml_file_proxy: YamlFileProxy
    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''

    # Define new data to save.
    new_data = {
        'key': 'new_value',
        'nested': {
            'a': 2,
            'b': 3
        }
    }

    # Save the new data to the YAML file.
    yaml_file_proxy.save_yaml(new_data)

    # Load the YAML file to verify the changes.
    with open(temp_yaml_file, 'r', encoding='utf-8') as f:
        loaded_data = yaml.safe_load(f)

    # Check that the loaded data matches the new data.
    assert loaded_data == new_data

# ** test: yaml_file_proxy_save_yaml_data_yaml_path
def test_yaml_file_proxy_save_yaml_data_yaml_path(yaml_file_proxy: YamlFileProxy, temp_yaml_file: str):
    '''
    Test the save_yaml method with a specific data_yaml_path.

    :param yaml_file_proxy: The YAML configuration proxy.
    :type yaml_file_proxy: YamlFileProxy
    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''

    # Define new data to save at a specific path.
    new_data = {
        'c': 3
    }

    # Save the new data to a specific path in the YAML file.
    yaml_file_proxy.save_yaml(new_data, data_yaml_path='nested/new_nested')

    # Load the YAML file to verify the changes.
    with open(temp_yaml_file, 'r', encoding='utf-8') as f:
        loaded_data = yaml.safe_load(f)

    # Check that the loaded data has the new nested structure.
    assert loaded_data == {
        'key': 'value',
        'nested': {
            'a': 1,
            'new_nested': {'c': 3}
        }
    }

# ** test: yaml_file_proxy_save_yaml_invalid_encoding
def test_yaml_file_proxy_save_yaml_invalid_encoding(yaml_file_proxy: YamlFileProxy):
    '''
    Test the save_yaml method with an invalid encoding.

    :param yaml_file_proxy: The YAML configuration proxy.
    :type yaml_file_proxy: YamlFileProxy
    '''

    # Set an invalid encoding.
    yaml_file_proxy.encoding = 'invalid-encoding'

    # Define new data to save.
    new_data = {
        'key': 'new_value'
    }

    # Attempt to save the new data with an invalid encoding.
    with pytest.raises(TiferetError) as exc_info:
        yaml_file_proxy.save_yaml(new_data)

    # Verify the error message.
    assert exc_info.value.error_code == 'YAML_FILE_SAVE_ERROR'
    assert 'An error occurred while saving to the YAML file' in str(exc_info.value)
    assert 'invalid-encoding' in str(exc_info.value)