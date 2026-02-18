"""Tests for Tiferet Configuration Repository Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import *

# *** fixtures

# ** fixture: config_file_repo
@pytest.fixture
def config_file_repo() -> YamlFileRepository:
    '''
    Fixture to provide an instance of YamlFileRepository.

    :return: An instance of YamlFileRepository.
    :rtype: YamlFileRepository
    '''

    # Return the YamlFileRepository instance.
    return YamlFileRepository()

# *** tests

# ** test: open_config_valid_yaml_file
def test_open_config_valid_yaml_file(tmp_path):
    '''
    Test opening a valid YAML configuration file.
    '''

    # Create a temporary YAML file.
    file_path = tmp_path / 'config.yaml'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('key: value\n')

    # Initialize the YamlFileRepository.
    config_repo = YamlFileRepository()

    # Open the YAML configuration file.
    config_service = config_repo.open_config(str(file_path), mode='r', encoding='utf-8')

    # Verify that the returned service is an instance of YamlLoaderMiddleware.
    assert isinstance(config_service, Yaml)
    assert config_repo.default_role == 'to_data.yaml'

# ** test: open_config_valid_json_file
def test_open_config_valid_json_file(tmp_path):
    '''
    Test opening a valid JSON configuration file.
    '''

    # Create a temporary JSON file.
    file_path = tmp_path / 'config.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('{"key": "value"}\n')

    # Initialize the YamlFileRepository.
    config_repo = YamlFileRepository()

    # Open the JSON configuration file.
    config_service = config_repo.open_config(str(file_path), mode='r', encoding='utf-8')

    # Verify that the returned service is an instance of JsonLoaderMiddleware.
    assert isinstance(config_service, Json)
    assert config_repo.default_role == 'to_data.json'

# ** test: open_config_unsupported_file_type
def test_open_config_unsupported_file_type(tmp_path):
    '''
    Test opening a configuration file with an unsupported file type.
    '''

    # Create a temporary TXT file.
    file_path = tmp_path / 'config.txt'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('key=value\n')

    # Initialize the YamlFileRepository.
    config_repo = YamlFileRepository()

    # Attempt to open the unsupported configuration file and verify that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        config_repo.open_config(str(file_path), mode='r', encoding='utf-8')

    # Verify the exception message.
    assert exc_info.value.error_code == const.UNSUPPORTED_CONFIG_FILE_TYPE_ID
    assert 'Unsupported configuration file type' in str(exc_info.value)
    assert exc_info.value.kwargs.get('file_extension') == '.txt'