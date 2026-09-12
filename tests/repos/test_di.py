"""Tiferet DI Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet import use_tester
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
    sample_data={
    },
    equality_fields=[
        'id',
        'name',
    ],
    exists_cases=[
    ],
    get_cases=[
    ],
    list_ids=[
    ],
    delete_ids=[
    ],
)
class TestDIConfigRepository:
    '''
    Tests for DIConfigRepository using the repo tester binder.
    '''

    # * test: registration_exists
    def test_registration_exists(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the registration_exists method of the DIConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # Check if the service configurations exist.
        assert repo.registration_exists(DI_SERVICE_ID)
        assert repo.registration_exists(ANOTHER_SERVICE_ID)
        assert not repo.registration_exists('missing_service')

    # * test: get_registration
    def test_get_registration(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the get_registration method of the DIConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # Get service configurations by id.
        config = repo.get_registration(DI_SERVICE_ID)
        another_config = repo.get_registration(ANOTHER_SERVICE_ID)

        # Check the first service configuration.
        assert config
        assert config.id == DI_SERVICE_ID
        assert config.name == 'DI Service'
        assert config.module_path == 'tiferet.services.di'
        assert config.class_name == 'DIServiceImpl'
        assert config.parameters.get('config_file') == 'app/configs/di.yml'
        assert len(config.dependencies) == 1
        assert config.dependencies[0].flag == 'yaml'

        # Check the second service configuration.
        assert another_config
        assert another_config.id == ANOTHER_SERVICE_ID
        assert another_config.name == 'Another Service'
        assert another_config.module_path == 'tiferet.services.another'
        assert another_config.class_name == 'AnotherServiceImpl'

    # * test: get_registration_not_found
    def test_get_registration_not_found(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the get_registration method of the DIConfigRepository for a missing id.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # Attempt to get a non-existent service configuration.
        config = repo.get_registration('missing_service')

        # Check that the configuration is None.
        assert not config

    # * test: list_all
    def test_list_all(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the list_all method of the DIConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # List all service configurations and constants.
        configurations, constants = repo.list_all()

        # Check the configurations.
        assert configurations
        assert len(configurations) == 2
        config_ids = [config.id for config in configurations]
        assert DI_SERVICE_ID in config_ids
        assert ANOTHER_SERVICE_ID in config_ids

        # Check the constants.
        assert constants
        assert constants.get('sample_const') == 'sample_value'

    # * test: save_registration
    def test_save_registration(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the save_registration method of the DIConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # Create constant for new service configuration.
        new_service_id = 'new_service'

        # Create new service configuration data and map to an aggregate.
        config = ServiceRegistrationConfigObject.model_validate(dict(
            id=new_service_id,
            name='New Service',
            module_path='tiferet.services.new',
            class_name='NewServiceImpl',
        )).map()

        # Save the new service configuration.
        repo.save_registration(config)

        # Reload the service configuration to verify it was saved.
        new_config = repo.get_registration(new_service_id)

        # Check the new service configuration.
        assert new_config
        assert new_config.id == new_service_id
        assert new_config.name == 'New Service'
        assert new_config.module_path == 'tiferet.services.new'
        assert new_config.class_name == 'NewServiceImpl'

    # * test: delete_registration
    def test_delete_registration(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the delete_registration method of the DIConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # Delete an existing service configuration.
        repo.delete_registration(ANOTHER_SERVICE_ID)

        # Attempt to get the deleted service configuration.
        deleted_config = repo.get_registration(ANOTHER_SERVICE_ID)

        # Check that the service configuration is None.
        assert not deleted_config

        # Ensure that deleting a non-existent service configuration is idempotent.
        repo.delete_registration('missing_service')

    # * test: save_constants
    def test_save_constants(self, test_ctx, di_config_file: str) -> None:
        '''
        Test the save_constants method of the DIConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param di_config_file: The DI YAML configuration file path.
        :type di_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=di_config_file)

        # Save new constants.
        repo.save_constants({'new_const': 'new_value'})

        # Reload and verify the constants were saved alongside existing ones.
        _, constants = repo.list_all()

        # Check that both old and new constants exist.
        assert constants.get('sample_const') == 'sample_value'
        assert constants.get('new_const') == 'new_value'
