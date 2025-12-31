"""Tests for the Container Configuration Repository"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
import pytest
import yaml

# ** app
from ....data import DataObject, ContainerAttributeConfigData
from ..container import ContainerConfigurationRepository

# *** constants

# ** constant: container_service_id
CONTAINER_SERVICE_ID = 'container_service'

# ** constant: container_data
CONTAINER_DATA = {
    'attrs': {
        CONTAINER_SERVICE_ID: {
            'module_path': 'tiferet.repos.config.container',
            'class_name': 'ContainerConfigurationRepository',
            'deps': {}
        }
    },
    'const': {
        'sample_const': 'sample_value'
    }
}

# *** fixtures

# ** fixture: container_config_file
@pytest.fixture
def container_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the container YAML configuration file.

    :return: The container YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample container configuration content.
    file_path = tmp_path / 'test_container.yaml'
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(CONTAINER_DATA, yaml_file)

    # Return the string file
    return str(file_path)

# ** fixture: container_config_repo
@pytest.fixture
def container_config_repo(container_config_file: str) -> ContainerConfigurationRepository:
    '''
    Fixture to provide a ContainerConfigurationRepository instance.

    :param container_config_file: The container YAML configuration file path.
    :type container_config_file: str
    :return: The ContainerConfigurationRepository instance.
    :rtype: ContainerConfigurationRepository
    '''

    # Create and return the ContainerConfigurationRepository instance.
    return ContainerConfigurationRepository(
        container_config_file=container_config_file,
        encoding='utf-8'
    )

# *** tests

# ** test: container_configuration_repository_attribute_exists
def test_attribute_exists(container_config_repo: ContainerConfigurationRepository):
    '''
    Test the attribute_exists method of the ContainerConfigurationRepository.

    :param container_config_repo: The ContainerConfigurationRepository instance.
    :type container_config_repo: ContainerConfigurationRepository
    '''

    # Check if the container service attribute exists.
    assert container_config_repo.attribute_exists(CONTAINER_SERVICE_ID) is True

    # Check for a non-existing attribute.
    assert container_config_repo.attribute_exists('non_existing_attr') is False

# ** test: container_configuration_repository_get_attribute
def test_get_attribute(container_config_repo: ContainerConfigurationRepository):
    '''
    Test the get_attribute method of the ContainerConfigurationRepository.

    :param container_config_repo: The ContainerConfigurationRepository instance.
    :type container_config_repo: ContainerConfigurationRepository
    '''

    # Get the container service attribute.
    attribute = container_config_repo.get_attribute(CONTAINER_SERVICE_ID)

    # Verify the attribute properties.
    assert attribute.id == CONTAINER_SERVICE_ID
    assert attribute.module_path == 'tiferet.repos.config.container'
    assert attribute.class_name == 'ContainerConfigurationRepository'
    assert attribute.dependencies == []

    # Get a container attribute that does not exist and expect None.
    non_existing_attribute = container_config_repo.get_attribute('non_existing_attr')
    assert not non_existing_attribute

# ** test: container_configuration_repository_list_all
def test_list_all(container_config_repo: ContainerConfigurationRepository):
    '''
    Test the list_all method of the ContainerConfigurationRepository.

    :param container_config_repo: The ContainerConfigurationRepository instance.
    :type container_config_repo: ContainerConfigurationRepository
    '''

    # List all container attributes and constants.
    attributes, constants = container_config_repo.list_all()

    # Verify the attributes list.
    assert len(attributes) == 1
    assert attributes[0].id == CONTAINER_SERVICE_ID

    # Verify the constants dictionary.
    assert 'sample_const' in constants
    assert constants['sample_const'] == 'sample_value'