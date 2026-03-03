"""Tests for the DI Configuration Repository"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
import pytest
import yaml

# ** app
from ...mappers import TransferObject
from ...mappers.di import ServiceConfigurationYamlObject
from ..di import DIYamlRepository

# *** constants

# ** constant: di_service_id
DI_SERVICE_ID = 'di_service'

# ** constant: di_data
DI_DATA = {
    'services': {
        DI_SERVICE_ID: {
            'module_path': 'tiferet.repos.di',
            'class_name': 'DIYamlRepository',
            'deps': {}
        }
    },
    'const': {
        'sample_const': 'sample_value'
    }
}

# *** fixtures

# ** fixture: di_yaml_file
@pytest.fixture
def di_yaml_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the DI YAML configuration file.

    :return: The DI YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample DI configuration content.
    file_path = tmp_path / 'test_di.yaml'
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(DI_DATA, yaml_file)

    # Return the string file path.
    return str(file_path)

# ** fixture: di_config_repo
@pytest.fixture
def di_config_repo(di_yaml_file: str) -> DIYamlRepository:
    '''
    Fixture to provide a DIYamlRepository instance.

    :param di_yaml_file: The DI YAML configuration file path.
    :type di_yaml_file: str
    :return: The DIYamlRepository instance.
    :rtype: DIYamlRepository
    '''

    # Create and return the DIYamlRepository instance.
    return DIYamlRepository(
        di_yaml_file=di_yaml_file,
        encoding='utf-8'
    )

# *** tests

# ** test: di_configuration_repository_configuration_exists
def test_configuration_exists(di_config_repo: DIYamlRepository):
    '''
    Test the configuration_exists method of the DIYamlRepository.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # Check if the DI service configuration exists.
    assert di_config_repo.configuration_exists(DI_SERVICE_ID) is True

    # Check for a non-existing configuration.
    assert di_config_repo.configuration_exists('non_existing_config') is False

# ** test: di_configuration_repository_get_configuration
def test_get_configuration(di_config_repo: DIYamlRepository):
    '''
    Test the get_configuration method of the DIYamlRepository.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # Get the DI service configuration.
    configuration = di_config_repo.get_configuration(DI_SERVICE_ID)

    # Verify the configuration properties.
    assert configuration.id == DI_SERVICE_ID
    assert configuration.module_path == 'tiferet.repos.di'
    assert configuration.class_name == 'DIYamlRepository'
    assert configuration.dependencies == []

    # Get a configuration that does not exist and expect None.
    non_existing_config = di_config_repo.get_configuration('non_existing_config')
    assert not non_existing_config

# ** test: di_configuration_repository_list_all
def test_list_all(di_config_repo: DIYamlRepository):
    '''
    Test the list_all method of the DIYamlRepository.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # List all service configurations and constants.
    configurations, constants = di_config_repo.list_all()

    # Verify the configurations list.
    assert len(configurations) == 1
    assert configurations[0].id == DI_SERVICE_ID

    # Verify the constants dictionary.
    assert 'sample_const' in constants
    assert constants['sample_const'] == 'sample_value'

# ** test: di_configuration_repository_save_configuration
def test_save_configuration(di_config_repo: DIYamlRepository):
    '''
    Test the save_configuration method of the DIYamlRepository.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # Create a new service configuration to save.
    new_configuration = TransferObject.from_data(
        ServiceConfigurationYamlObject,
        id='new_config',
        module_path='tiferet.new.module',
        class_name='NewClass',
        deps={}
    ).map()

    # Save the new service configuration.
    di_config_repo.save_configuration(new_configuration)

    # Verify that the new configuration now exists.
    assert di_config_repo.configuration_exists('new_config') is True

    # Retrieve the newly saved configuration and verify its properties.
    saved_configuration = di_config_repo.get_configuration('new_config')
    assert saved_configuration.id == 'new_config'
    assert saved_configuration.module_path == 'tiferet.new.module'
    assert saved_configuration.class_name == 'NewClass'
    assert saved_configuration.dependencies == []

# ** test: di_configuration_repository_delete_configuration
def test_delete_configuration(di_config_repo: DIYamlRepository):
    '''
    Test the delete_configuration method of the DIYamlRepository.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # Ensure the DI service configuration exists before deletion.
    assert di_config_repo.configuration_exists(DI_SERVICE_ID) is True

    # Delete the DI service configuration.
    di_config_repo.delete_configuration(DI_SERVICE_ID)

    # Verify that the configuration no longer exists.
    assert di_config_repo.configuration_exists(DI_SERVICE_ID) is False

# ** test: di_configuration_repository_save_constants
def test_save_constants(di_config_repo: DIYamlRepository):
    '''
    Test the save_constants method of the DIYamlRepository.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # Define new constants to save.
    new_constants = {
        'new_const_1': 'value_1',
        'new_const_2': 'value_2'
    }

    # Save the new constants.
    di_config_repo.save_constants(new_constants)

    # List all configurations and constants to verify the new constants were saved.
    _, constants = di_config_repo.list_all()

    # Verify the new constants exist in the saved constants.
    assert 'new_const_1' in constants
    assert constants['new_const_1'] == 'value_1'
    assert 'new_const_2' in constants
    assert constants['new_const_2'] == 'value_2'

# ** test: di_configuration_repository_save_constants_overwrite
def test_save_constants_overwrite(di_config_repo: DIYamlRepository):
    '''
    Test that the save_constants method of the DIYamlRepository overwrites existing constants.

    :param di_config_repo: The DIYamlRepository instance.
    :type di_config_repo: DIYamlRepository
    '''

    # Define initial constants to save.
    initial_constants = {
        'const_to_overwrite': 'initial_value',
        'another_const': 'another_value'
    }

    # Save the initial constants.
    di_config_repo.save_constants(initial_constants)

    # Define new constants that will overwrite one of the initial constants.
    new_constants = {
        'const_to_overwrite': 'new_value',
        'additional_const': 'additional_value'
    }

    # Save the new constants.
    di_config_repo.save_constants(new_constants)

    # List all configurations and constants to verify the constants were updated.
    _, constants = di_config_repo.list_all()

    # Verify that new constants were added and existing ones were overwritten.
    assert constants == {
        'sample_const': 'sample_value',
        'const_to_overwrite': 'new_value',
        'another_const': 'another_value',
        'additional_const': 'additional_value'
    }
