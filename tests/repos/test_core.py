"""Tiferet Configuration Repository Core Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.core import ServiceError
from tiferet.repos.core import (
    ConfigurationRepository,
    UNSUPPORTED_CONFIG_FILE_TYPE_ID,
)
from tiferet.utils import YamlLoader, JsonLoader

# *** testers

# ** tester: test_configuration_repository
@use_tester(
    type='repo',
    target_cls=ConfigurationRepository,
    config_parameter='config_file',
)
class TestConfigurationRepository:
    '''ConfigurationRepository construction, format dispatch, and loader selection.'''

    # * test: new
    def test_new(self, test_ctx, tmp_path) -> None:
        '''Verify repository construction and default_role.'''

        file_path = tmp_path / 'config.yaml'
        file_path.write_text('root: {}\n', encoding='utf-8')
        test_ctx.assert_new(config_file=str(file_path))

    # * test: format_dispatch
    def test_format_dispatch(self, test_ctx, tmp_path) -> None:
        '''Verify YAML and JSON payload round-trip.'''

        yaml_file = tmp_path / 'dispatch.yaml'
        json_file = tmp_path / 'dispatch.json'
        yaml_file.write_text('root: {}\n', encoding='utf-8')
        json_file.write_text('{"root": {}}\n', encoding='utf-8')
        test_ctx.assert_format_dispatch(str(yaml_file), str(json_file))

    # * test: get_loader_yaml
    def test_get_loader_yaml(self, test_ctx, tmp_path) -> None:
        '''Test that a YAML configuration file resolves to a YamlLoader.'''

        file_path = tmp_path / 'config.yaml'
        file_path.write_text('root: {}\n', encoding='utf-8')
        repo = test_ctx.make_target(config_file=str(file_path))
        loader = repo._get_loader()

        assert isinstance(loader, YamlLoader)

    # * test: get_loader_json
    def test_get_loader_json(self, test_ctx, tmp_path) -> None:
        '''Test that a JSON configuration file resolves to a JsonLoader.'''

        file_path = tmp_path / 'config.json'
        file_path.write_text('{"root": {}}\n', encoding='utf-8')
        repo = test_ctx.make_target(config_file=str(file_path))
        loader = repo._get_loader()

        assert isinstance(loader, JsonLoader)

    # * test: load_save_round_trip_yaml_start_node
    def test_load_save_round_trip_yaml_start_node(self, test_ctx, tmp_path) -> None:
        '''Test that YAML start_node selects nested data after a save.'''

        file_path = tmp_path / 'config.yaml'
        file_path.write_text('root: {}\n', encoding='utf-8')
        repo = test_ctx.make_target(config_file=str(file_path))
        repo._save({'root': {'alpha': 1, 'beta': 'two'}})

        nested = repo._load(start_node=lambda d: d.get('root', {}))
        assert nested == {'alpha': 1, 'beta': 'two'}

    # * test: unsupported_config_file_type
    def test_unsupported_config_file_type(self, test_ctx, tmp_path) -> None:
        '''Test that an unsupported configuration file extension raises ServiceError.'''

        repo = test_ctx.make_target(config_file=str(tmp_path / 'config.txt'))

        with pytest.raises(ServiceError) as exc_info:
            repo._get_loader()

        assert exc_info.value.error_code == UNSUPPORTED_CONFIG_FILE_TYPE_ID
        assert exc_info.value.class_name == 'ConfigurationRepository'
        assert exc_info.value.target_method == '_get_loader'
