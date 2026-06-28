"""Tiferet Configuration Repository Settings Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.repos.settings import ConfigurationRepository
from tiferet.utils import YamlLoader, JsonLoader
from tiferet.assets import TiferetError


# *** fixtures

# ** fixture: yaml_repo
@pytest.fixture
def yaml_repo(tmp_path) -> ConfigurationRepository:
    '''
    Provide a ConfigurationRepository backed by a temporary YAML file.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: pathlib.Path
    :return: A YAML-backed configuration repository.
    :rtype: ConfigurationRepository
    '''

    # Create an empty YAML configuration file.
    file_path = tmp_path / 'config.yaml'
    file_path.write_text('root: {}\n', encoding='utf-8')

    # Return a repository pointed at the YAML file.
    return ConfigurationRepository(str(file_path))

# ** fixture: json_repo
@pytest.fixture
def json_repo(tmp_path) -> ConfigurationRepository:
    '''
    Provide a ConfigurationRepository backed by a temporary JSON file.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: pathlib.Path
    :return: A JSON-backed configuration repository.
    :rtype: ConfigurationRepository
    '''

    # Create an empty JSON configuration file.
    file_path = tmp_path / 'config.json'
    file_path.write_text('{"root": {}}\n', encoding='utf-8')

    # Return a repository pointed at the JSON file.
    return ConfigurationRepository(str(file_path))


# *** tests

# ** test_int: default_role_is_to_data
def test_int_default_role_is_to_data(yaml_repo: ConfigurationRepository) -> None:
    '''
    Test that the configuration repository defaults to the format-agnostic 'to_data' role.

    :param yaml_repo: The YAML-backed configuration repository.
    :type yaml_repo: ConfigurationRepository
    '''

    # The default role should be 'to_data'.
    assert yaml_repo.default_role == 'to_data'

# ** test_int: get_loader_yaml
def test_int_get_loader_yaml(yaml_repo: ConfigurationRepository) -> None:
    '''
    Test that a YAML configuration file resolves to a YamlLoader.

    :param yaml_repo: The YAML-backed configuration repository.
    :type yaml_repo: ConfigurationRepository
    '''

    # Resolve the loader for the YAML file.
    loader = yaml_repo._get_loader()

    # The loader should be a YamlLoader.
    assert isinstance(loader, YamlLoader)

# ** test_int: get_loader_json
def test_int_get_loader_json(json_repo: ConfigurationRepository) -> None:
    '''
    Test that a JSON configuration file resolves to a JsonLoader.

    :param json_repo: The JSON-backed configuration repository.
    :type json_repo: ConfigurationRepository
    '''

    # Resolve the loader for the JSON file.
    loader = json_repo._get_loader()

    # The loader should be a JsonLoader.
    assert isinstance(loader, JsonLoader)

# ** test_int: load_save_round_trip_yaml
def test_int_load_save_round_trip_yaml(yaml_repo: ConfigurationRepository) -> None:
    '''
    Test that data saved to a YAML configuration file is loaded back intact.

    :param yaml_repo: The YAML-backed configuration repository.
    :type yaml_repo: ConfigurationRepository
    '''

    # Persist a sample structure.
    yaml_repo._save({'root': {'alpha': 1, 'beta': 'two'}})

    # Load the full structure back.
    data = yaml_repo._load()

    # The round-tripped data should match what was saved.
    assert data == {'root': {'alpha': 1, 'beta': 'two'}}

    # The start_node selector should resolve nested data.
    nested = yaml_repo._load(start_node=lambda d: d.get('root', {}))
    assert nested == {'alpha': 1, 'beta': 'two'}

# ** test_int: load_save_round_trip_json
def test_int_load_save_round_trip_json(json_repo: ConfigurationRepository) -> None:
    '''
    Test that data saved to a JSON configuration file is loaded back intact.

    :param json_repo: The JSON-backed configuration repository.
    :type json_repo: ConfigurationRepository
    '''

    # Persist a sample structure.
    json_repo._save({'root': {'alpha': 1, 'beta': 'two'}})

    # Load the full structure back.
    data = json_repo._load()

    # The round-tripped data should match what was saved.
    assert data == {'root': {'alpha': 1, 'beta': 'two'}}

# ** test_int: unsupported_config_file_type
def test_int_unsupported_config_file_type(tmp_path) -> None:
    '''
    Test that an unsupported configuration file extension raises UNSUPPORTED_CONFIG_FILE_TYPE.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: pathlib.Path
    '''

    # Create a repository pointed at an unsupported file type.
    repo = ConfigurationRepository(str(tmp_path / 'config.txt'))

    # Resolving a loader should raise a structured error.
    with pytest.raises(TiferetError) as exc_info:
        repo._get_loader()

    # The error code should indicate an unsupported configuration file type.
    assert exc_info.value.error_code == 'UNSUPPORTED_CONFIG_FILE_TYPE'
