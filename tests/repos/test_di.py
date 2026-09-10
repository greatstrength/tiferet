"""Tiferet DI Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.mappers import ServiceRegistrationConfigObject
from tiferet.repos.di import DIConfigRepository

# *** constants

# ** constant: di_service_id
DI_SERVICE_ID = 'di_service'

# ** constant: another_service_id
ANOTHER_SERVICE_ID = 'another_service'

# ** constant: di_data
DI_DATA: Dict[str, Dict] = {
    'services': {
        DI_SERVICE_ID: {
            'name': 'DI Service',
            'module_path': 'tiferet.services.di',
            'class_name': 'DIServiceImpl',
            'params': {
                'config_file': 'app/configs/di.yml',
            },
            'deps': {
                'yaml': {
                    'module_path': 'tiferet.repos.di',
                    'class_name': 'DIConfigRepository',
                    'params': {
                        'di_config': 'app/configs/di.yml',
                    },
                },
            },
        },
        ANOTHER_SERVICE_ID: {
            'name': 'Another Service',
            'module_path': 'tiferet.services.another',
            'class_name': 'AnotherServiceImpl',
        },
    },
    'const': {
        'sample_const': 'sample_value',
    },
}

# *** fixtures

# ** fixture: di_config_file
@pytest.fixture
def di_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the DI YAML configuration file.

    :return: The DI YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample DI configuration content.
    file_path = tmp_path / 'test_di.yaml'

    # Write the sample DI configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(DI_DATA, yaml_file)

    # Return the file path as a string.
    return str(file_path)

# *** testers

# ** tester: test_di_config_repository
@use_tester(
    type='repo',
    target_cls=DIConfigRepository,
    config_parameter='di_config',
)
class TestDIConfigRepository:
    '''DIConfigRepository construction plus bespoke registration methods.'''

    # * test: new
    def test_new(self, test_ctx, di_config_file: str) -> None:
        '''Verify repository construction and default_role.'''

        test_ctx.assert_new(config_file=di_config_file)

    # * test: format_dispatch
    def test_format_dispatch(self, test_ctx, tmp_path) -> None:
        '''Verify YAML and JSON payload round-trip.'''

        yaml_file = tmp_path / 'dispatch.yaml'
        json_file = tmp_path / 'dispatch.json'
        yaml_file.write_text('root: {}\n', encoding='utf-8')
        json_file.write_text('{"root": {}}\n', encoding='utf-8')
        test_ctx.assert_format_dispatch(str(yaml_file), str(json_file))

    # * test: registration_exists
    def test_registration_exists(self, test_ctx, di_config_file: str) -> None:
        '''Test the registration_exists method of the DIConfigRepository.'''

        repo = test_ctx.make_target(config_file=di_config_file)

        assert repo.registration_exists(DI_SERVICE_ID)
        assert repo.registration_exists(ANOTHER_SERVICE_ID)
        assert not repo.registration_exists('missing_service')

    # * test: get_registration
    def test_get_registration(self, test_ctx, di_config_file: str) -> None:
        '''Test the get_registration method of the DIConfigRepository.'''

        repo = test_ctx.make_target(config_file=di_config_file)
        config = repo.get_registration(DI_SERVICE_ID)
        another_config = repo.get_registration(ANOTHER_SERVICE_ID)

        assert config
        assert config.id == DI_SERVICE_ID
        assert config.name == 'DI Service'
        assert config.module_path == 'tiferet.services.di'
        assert config.class_name == 'DIServiceImpl'
        assert config.parameters.get('config_file') == 'app/configs/di.yml'
        assert len(config.dependencies) == 1
        assert config.dependencies[0].flag == 'yaml'

        assert another_config
        assert another_config.id == ANOTHER_SERVICE_ID
        assert another_config.name == 'Another Service'
        assert another_config.module_path == 'tiferet.services.another'
        assert another_config.class_name == 'AnotherServiceImpl'

    # * test: get_registration_not_found
    def test_get_registration_not_found(self, test_ctx, di_config_file: str) -> None:
        '''Test get_registration for a non-existent configuration.'''

        repo = test_ctx.make_target(config_file=di_config_file)
        config = repo.get_registration('missing_service')

        assert not config

    # * test: list_all
    def test_list_all(self, test_ctx, di_config_file: str) -> None:
        '''Test the list_all method of the DIConfigRepository.'''

        repo = test_ctx.make_target(config_file=di_config_file)
        configurations, constants = repo.list_all()

        assert configurations
        assert len(configurations) == 2
        config_ids = [config.id for config in configurations]
        assert DI_SERVICE_ID in config_ids
        assert ANOTHER_SERVICE_ID in config_ids

        assert constants
        assert constants.get('sample_const') == 'sample_value'

    # * test: save_registration
    def test_save_registration(self, test_ctx, di_config_file: str) -> None:
        '''Test the save_registration method of the DIConfigRepository.'''

        repo = test_ctx.make_target(config_file=di_config_file)
        new_service_id = 'new_service'
        config = ServiceRegistrationConfigObject.model_validate(dict(
            id=new_service_id,
            name='New Service',
            module_path='tiferet.services.new',
            class_name='NewServiceImpl',
        )).map()

        repo.save_registration(config)
        new_config = repo.get_registration(new_service_id)

        assert new_config
        assert new_config.id == new_service_id
        assert new_config.name == 'New Service'
        assert new_config.module_path == 'tiferet.services.new'
        assert new_config.class_name == 'NewServiceImpl'

    # * test: delete_registration
    def test_delete_registration(self, test_ctx, di_config_file: str) -> None:
        '''Test the delete_registration method of the DIConfigRepository.'''

        repo = test_ctx.make_target(config_file=di_config_file)
        repo.delete_registration(ANOTHER_SERVICE_ID)
        deleted_config = repo.get_registration(ANOTHER_SERVICE_ID)

        assert not deleted_config

        repo.delete_registration('missing_service')

    # * test: save_constants
    def test_save_constants(self, test_ctx, di_config_file: str) -> None:
        '''Test the save_constants method of the DIConfigRepository.'''

        repo = test_ctx.make_target(config_file=di_config_file)
        repo.save_constants({'new_const': 'new_value'})
        _, constants = repo.list_all()

        assert constants.get('sample_const') == 'sample_value'
        assert constants.get('new_const') == 'new_value'
