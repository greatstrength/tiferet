"""Tiferet Configuration Repository Core Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.repos.core import ConfigurationRepository, UNSUPPORTED_CONFIG_FILE_TYPE_ID
from tiferet.utils import YamlLoader, JsonLoader
from tiferet.interfaces.core import ServiceError

# *** fixtures

# ** fixture: yaml_config_file
@pytest.fixture
def yaml_config_file(tmp_path) -> str:
    '''
    Provide a temporary YAML configuration file path.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: pathlib.Path
    :return: The YAML configuration file path.
    :rtype: str
    '''

    # Create an empty YAML configuration file.
    file_path = tmp_path / 'config.yaml'
    file_path.write_text('root: {}\n', encoding='utf-8')

    # Return the file path as a string.
    return str(file_path)

# ** fixture: json_config_file
@pytest.fixture
def json_config_file(tmp_path) -> str:
    '''
    Provide a temporary JSON configuration file path.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: pathlib.Path
    :return: The JSON configuration file path.
    :rtype: str
    '''

    # Create an empty JSON configuration file.
    file_path = tmp_path / 'config.json'
    file_path.write_text('{"root": {}}\n', encoding='utf-8')

    # Return the file path as a string.
    return str(file_path)

# *** tests

# ** test: int_unsupported_config_file_type
def test_int_unsupported_config_file_type(tmp_path) -> None:
    '''
    Test that an unsupported configuration file extension raises UNSUPPORTED_CONFIG_FILE_TYPE.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: pathlib.Path
    '''

    # Create a repository pointed at an unsupported file type.
    repo = ConfigurationRepository(str(tmp_path / 'config.txt'))

    # Resolving a loader should raise a ServiceError.
    with pytest.raises(ServiceError) as exc_info:
        repo._get_loader()

    # The error code should indicate an unsupported configuration file type.
    assert exc_info.value.error_code == UNSUPPORTED_CONFIG_FILE_TYPE_ID

# *** testers

# ** tester: test_configuration_repository
@use_tester(
    type='repo',
    target_cls=ConfigurationRepository,
    config_parameter='config_file',
    sample_data={
    },
    exists_cases=[
    ],
    get_cases=[
    ],
    list_ids=[
    ],
    delete_ids=[
    ],
)
class TestConfigurationRepository:
    '''
    Tests for ConfigurationRepository using the repo tester binder.
    '''

    # * test: new
    def test_new(self, test_ctx, yaml_config_file: str) -> None:
        '''
        Test that make_target constructs the repository with the default role.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param yaml_config_file: The YAML configuration file path.
        :type yaml_config_file: str
        '''

        # Assert construction and the default serialization role.
        test_ctx.assert_new(config_file=yaml_config_file)

    # * test: format_dispatch
    def test_format_dispatch(
            self,
            test_ctx,
            yaml_config_file: str,
            json_config_file: str,
        ) -> None:
        '''
        Test that YAML and JSON paths round-trip the same payload.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param yaml_config_file: The YAML configuration file path.
        :type yaml_config_file: str
        :param json_config_file: The JSON configuration file path.
        :type json_config_file: str
        '''

        # Assert YAML and JSON format dispatch via _save / _load.
        test_ctx.assert_format_dispatch(
            yaml_file=yaml_config_file,
            json_file=json_config_file,
        )

    # * test: get_loader_yaml
    def test_get_loader_yaml(self, test_ctx, yaml_config_file: str) -> None:
        '''
        Test that a YAML configuration file resolves to a YamlLoader.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param yaml_config_file: The YAML configuration file path.
        :type yaml_config_file: str
        '''

        # Construct the repository against the YAML path.
        repo = test_ctx.make_target(config_file=yaml_config_file)

        # The loader should be a YamlLoader.
        assert isinstance(repo._get_loader(), YamlLoader)

    # * test: get_loader_json
    def test_get_loader_json(self, test_ctx, json_config_file: str) -> None:
        '''
        Test that a JSON configuration file resolves to a JsonLoader.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param json_config_file: The JSON configuration file path.
        :type json_config_file: str
        '''

        # Construct the repository against the JSON path.
        repo = test_ctx.make_target(config_file=json_config_file)

        # The loader should be a JsonLoader.
        assert isinstance(repo._get_loader(), JsonLoader)

    # * test: load_start_node
    def test_load_start_node(self, test_ctx, yaml_config_file: str) -> None:
        '''
        Test that the start_node selector resolves nested YAML data.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param yaml_config_file: The YAML configuration file path.
        :type yaml_config_file: str
        '''

        # Construct the repository and persist a nested structure.
        repo = test_ctx.make_target(config_file=yaml_config_file)
        repo._save({
            'root': {
                'alpha': 1,
                'beta': 'two',
            },
        })

        # The start_node selector should resolve nested data.
        nested = repo._load(start_node=lambda d: d.get('root', {}))
        assert nested == {
            'alpha': 1,
            'beta': 'two',
        }
