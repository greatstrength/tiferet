"""Tiferet JSON Proxy Settings Tests"""

# *** imports

# ** infra
import pytest
import json

# ** app
from ....assets import TiferetError
from ..settings import JsonFileProxy

# *** fixtures

# ** fixture: temp_json_file
@pytest.fixture
def temp_json_file(tmp_path) -> str:
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
            }
        }, f)
    
    # Return the file path as a string.
    return str(file_path)

# ** fixture: json_file_proxy
@pytest.fixture
def json_file_proxy(temp_json_file: str) -> JsonFileProxy:
    '''
    Fixture to create an instance of the JsonFileProxy.

    :param temp_json_file: The JSON configuration file path.
    :type temp_json_file: str
    '''

    # Create and return the JsonFileProxy instance.
    return JsonFileProxy(temp_json_file)

# *** tests
# ** test: json_file_proxy_init_invalid_file
def test_json_file_proxy_init_invalid_file():
    '''
    Test the initialization of JsonFileProxy with an invalid file.

    This test checks that initializing the JsonFileProxy with a non-JSON file raises a TiferetError.
    '''

    # Attempt to initialize the JsonFileProxy with an invalid file and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        JsonFileProxy('invalid_file.txt')

    # Verify that the error code and message are as expected.
    assert exc_info.value.error_code == 'INVALID_JSON_FILE'
    assert 'File is not a valid JSON file:' in str(exc_info.value)
    assert exc_info.value.kwargs.get('json_file') == 'invalid_file.txt'

# ** test: json_file_proxy_load_json
def test_json_file_proxy_load_json(json_file_proxy: JsonFileProxy):
    '''
    Test the load_json method of the JsonFileProxy.

    This test verifies that the load_json method correctly loads data from a JSON file.
    '''

    # Load the JSON data using the proxy.
    loaded_data = json_file_proxy.load_json()

    # Verify that the loaded data matches the expected content.
    assert loaded_data == {
        'key': 'value',
        'nested': {
            'a': 1
        }
    }

# ** test: json_file_proxy_load_json_file_not_found
def test_json_file_proxy_load_json_file_not_found():
    '''
    Test the load_json method of the JsonFileProxy when the JSON file does not exist.

    This test checks that attempting to load a non-existent JSON file raises a TiferetError.
    '''

    # Create a JsonFileProxy instance with a non-existent file path.
    json_proxy = JsonFileProxy('non_existent_file.json')

    # Attempt to load the JSON data and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        json_proxy.load_json()

    # Verify that the error code indicates a file not found error.
    assert exc_info.value.error_code == 'JSON_FILE_LOAD_ERROR'
    assert 'An error occurred while loading the JSON file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('json_file') == 'non_existent_file.json'

# ** test: json_file_proxy_save_json
def test_json_file_proxy_save_json(json_file_proxy: JsonFileProxy, temp_json_file: str):
    '''
    Test the save_json method of the JsonFileProxy.

    This test verifies that the save_json method correctly saves data to a JSON file.
    '''

    # Define the data to be saved.
    data_to_save = {
        'new_key': 'new_value',
        'nested': {
            'b': 2
        }
    }

    # Save the data using the proxy.
    json_file_proxy.save_json(data=data_to_save,)

    # Load the saved data directly from the file to verify.
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)

    # Verify that the saved data matches the original data.
    assert saved_data == data_to_save

# ** test: json_file_proxy_save_json_data_json_path
def test_json_file_proxy_save_json_data_json_path(json_file_proxy: JsonFileProxy, temp_json_file: str):
    '''
    Test the save_json method of the JsonFileProxy with a specific JSON path.

    This test verifies that the save_json method correctly saves data to a specified path within the JSON file.
    '''

    # Define the data to be saved at a specific JSON path.
    data_to_save = {
        'b': 2,
        'c': 3
    }

    # Save the data to the 'nested' path in the JSON file.
    json_file_proxy.save_json(data=data_to_save, data_json_path='nested.new_nested')

    # Load the updated data directly from the file to verify.
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)

    # Verify that the updated data matches the expected structure.
    assert updated_data == {
        'key': 'value',
        'nested': {
            'a': 1,
            'new_nested': {
                'b': 2,
                'c': 3
            }
        }
    }

# ** test: json_file_proxy_save_json_invalid_encoding
def test_json_file_proxy_save_json_invalid_encoding(json_file_proxy: JsonFileProxy):
    '''
    Test the save_json method of the JsonFileProxy with an invalid encoding.

    This test checks that attempting to save data with an invalid encoding raises a TiferetError.
    '''

    # Define the data to be saved.
    data_to_save = {
        'key': 'value'
    }

    # Temporarily set an invalid encoding.
    json_file_proxy.encoding = 'invalid-encoding'

    # Attempt to save the data and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        json_file_proxy.save_json(data=data_to_save)

    # Verify that the error code indicates a JSON file save error.
    assert exc_info.value.error_code == 'JSON_FILE_SAVE_ERROR'
    assert 'An error occurred while saving to the JSON file' in str(exc_info.value)