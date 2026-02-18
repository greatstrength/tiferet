"""Tiferet YAML Utility Tests"""

# *** imports

# ** infra
import pytest
import yaml

# ** app
from ..yaml import YamlLoader, TiferetError, a

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

# ** test: yaml_loader_init_invalid_file
def test_yaml_loader_init_invalid_file():
    '''
    Test initialization of YamlLoader with an invalid YAML file path.
    '''

    yaml_loader = YamlLoader(path='invalid_file.txt')
    
    # Attempt to initialize with an invalid file path and verify that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        yaml_loader.open_file()
    
    # Verify the exception message.
    assert exc_info.value.error_code == a.const.INVALID_YAML_FILE_ID
    assert 'is not a valid YAML file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('path') == 'invalid_file.txt'

# ** test: yaml_loader_load
def test_yaml_loader_load(temp_yaml_file: str):
    '''
    Test successful loading of a YAML file using YamlLoader.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Load the YAML content.
    with YamlLoader(path=temp_yaml_file) as yaml_r:
        content = yaml_r.load()
    
    # Verify the loaded content.
    assert isinstance(content, dict)
    assert content == {'key': 'value', 'nested': {'a': 1}}
    
    # Verify the file is closed after loading.
    assert yaml_r.file is None

# ** test: yaml_loader_load_start_node
def test_yaml_loader_load_start_node(temp_yaml_file: str):
    '''
    Test loading a YAML file with a custom start node using YamlLoader.
    
    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''

    # Define a custom start node function to extract a specific part of the YAML content.
    def start_node(data):
        return data.get('nested', {})
    
    # Load the YAML content using the custom start node.
    with YamlLoader(path=temp_yaml_file) as yaml_r:
        content = yaml_r.load(start_node=start_node)

    # Verify the loaded content is the nested dictionary.
    assert isinstance(content, dict)
    assert content == {'a': 1}

    # Verify the file is closed after loading.
    assert yaml_r.file is None

# ** test: yaml_loader_load_data_factory
def test_yaml_loader_load_data_factory(temp_yaml_file: str):
    '''
    Test loading a YAML file with a custom data factory using YamlLoader.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Define a custom data factory to transform the loaded YAML data.
    def data_factory(data):
        return {k.upper(): v for k, v in data.items()}
    
    # Load the YAML content using the custom data factory.
    with YamlLoader(path=temp_yaml_file) as yaml_r:
        content = yaml_r.load(data_factory=data_factory)
    
    # Verify the transformed content.
    assert isinstance(content, dict)
    assert content == {'KEY': 'value', 'NESTED': {'a': 1}}
    
    # Verify the file is closed after loading.
    assert yaml_r.file is None

# ** test: yaml_loader_save
def test_yaml_loader_save(temp_yaml_file: str):
    '''
    Test successful saving of a dictionary to a YAML file using YamlLoader.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Data to save.
    data = {'new_key': 'new_value', 'nested': {'b': 2}}
    
    # Save the data to the YAML file.
    with YamlLoader(path=temp_yaml_file, mode='w') as yaml_w:
        yaml_w.save(data)
    
    # Verify the file content.
    with open(temp_yaml_file, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
    assert content == data
    
    # Verify the file is closed after saving.
    assert yaml_w.file is None

# ** test: yaml_loader_save_data_yaml_path
def test_yaml_loader_save_data_yaml_path(temp_yaml_file: str):
    '''
    Test saving a dictionary to a specific path in a YAML file using YamlLoader.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''
    
    # Data to save.
    data = {'c': 3}
    
    # Save the data to a specific path in the YAML file.
    with YamlLoader(path=temp_yaml_file, mode='w') as yaml_w:
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

# ** test: verify_yaml_file_success
def test_verify_yaml_file_success(temp_yaml_file: str):
    '''
    Test successful verification of a YAML file.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: str
    '''

    # Verify the YAML file exists and is valid.
    verified_path = YamlLoader.verify_yaml_file(temp_yaml_file)

    # Verify the returned path matches the input.
    assert verified_path == temp_yaml_file

# ** test: verify_yaml_file_with_default_path
def test_verify_yaml_file_with_default_path(tmp_path):
    '''
    Test verification of a YAML file with default path.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a YAML file in a subdirectory.
    subdir = tmp_path / 'configs'
    subdir.mkdir()
    yaml_file = subdir / 'config.yaml'
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump({'test': 'data'}, f)

    # Verify using just the filename and default path.
    verified_path = YamlLoader.verify_yaml_file('config.yaml', default_path=str(subdir))

    # Verify the returned path is the full path.
    assert verified_path == str(yaml_file)

# ** test: verify_yaml_file_not_found
def test_verify_yaml_file_not_found():
    '''
    Test verification of a non-existent YAML file.
    '''

    # Attempt to verify a non-existent file.
    with pytest.raises(TiferetError) as exc_info:
        YamlLoader.verify_yaml_file('nonexistent.yaml')

    # Verify the error code.
    assert exc_info.value.error_code == a.const.YAML_FILE_NOT_FOUND_ID
    assert 'not found' in str(exc_info.value).lower()

# ** test: verify_yaml_file_invalid_extension
def test_verify_yaml_file_invalid_extension(tmp_path):
    '''
    Test verification of a file with invalid YAML extension.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a file with invalid extension.
    invalid_file = tmp_path / 'config.txt'
    with open(invalid_file, 'w', encoding='utf-8') as f:
        f.write('test: data\n')

    # Attempt to verify the invalid file.
    with pytest.raises(TiferetError) as exc_info:
        YamlLoader.verify_yaml_file(str(invalid_file))

    # Verify the error code.
    assert exc_info.value.error_code == a.const.INVALID_YAML_FILE_ID
    assert 'not a valid YAML file' in str(exc_info.value)
