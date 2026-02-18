"""Tests for the Container Configuration Repository"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
import pytest
import yaml

# ** app
from ...mappers import TransferObject, ContainerAttributeYamlObject
from ..container import ContainerYamlRepository

# *** constants

# ** constant: container_service_id
CONTAINER_SERVICE_ID = 'container_service'

# ** constant: container_data
CONTAINER_DATA = {
    'attrs': {
        CONTAINER_SERVICE_ID: {
            'module_path': 'tiferet.repos.config.container',
            'class_name': 'ContainerYamlRepository',
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
def container_config_repo(container_config_file: str) -> ContainerYamlRepository:
    '''
    Fixture to provide a ContainerYamlRepository instance.

    :param container_config_file: The container YAML configuration file path.
    :type container_config_file: str
    :return: The ContainerYamlRepository instance.
    :rtype: ContainerYamlRepository
    '''

    # Create and return the ContainerYamlRepository instance.
    return ContainerYamlRepository(
        yaml_file=container_config_file,
        encoding='utf-8'
    )

# *** tests

# ** test: container_configuration_repository_attribute_exists
def test_attribute_exists(container_config_repo: ContainerYamlRepository):
    '''
    Test the attribute_exists method of the ContainerYamlRepository.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # Check if the container service attribute exists.
    assert container_config_repo.attribute_exists(CONTAINER_SERVICE_ID) is True

    # Check for a non-existing attribute.
    assert container_config_repo.attribute_exists('non_existing_attr') is False

# ** test: container_configuration_repository_get_attribute
def test_get_attribute(container_config_repo: ContainerYamlRepository):
    '''
    Test the get_attribute method of the ContainerYamlRepository.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # Get the container service attribute.
    attribute = container_config_repo.get_attribute(CONTAINER_SERVICE_ID)

    # Verify the attribute properties.
    assert attribute.id == CONTAINER_SERVICE_ID
    assert attribute.module_path == 'tiferet.repos.config.container'
    assert attribute.class_name == 'ContainerYamlRepository'
    assert attribute.dependencies == []

    # Get a container attribute that does not exist and expect None.
    non_existing_attribute = container_config_repo.get_attribute('non_existing_attr')
    assert not non_existing_attribute

# ** test: container_configuration_repository_list_all
def test_list_all(container_config_repo: ContainerYamlRepository):
    '''
    Test the list_all method of the ContainerYamlRepository.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # List all container attributes and constants.
    attributes, constants = container_config_repo.list_all()

    # Verify the attributes list.
    assert len(attributes) == 1
    assert attributes[0].id == CONTAINER_SERVICE_ID

    # Verify the constants dictionary.
    assert 'sample_const' in constants
    assert constants['sample_const'] == 'sample_value'

# ** test: container_configuration_repository_save_attribute
def test_save_attribute(container_config_repo: ContainerYamlRepository):
    '''
    Test the save_attribute method of the ContainerYamlRepository.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # Create a new container attribute to save.
    new_attribute = TransferObject.from_data(
        ContainerAttributeYamlObject,
        id='new_attr',
        module_path='tiferet.new.module',
        class_name='NewClass',
        deps={}
    ).map()

    # Save the new container attribute.
    container_config_repo.save_attribute(new_attribute)

    # Verify that the new attribute now exists.
    assert container_config_repo.attribute_exists('new_attr') is True

    # Retrieve the newly saved attribute and verify its properties.
    saved_attribute = container_config_repo.get_attribute('new_attr')
    assert saved_attribute.id == 'new_attr'
    assert saved_attribute.module_path == 'tiferet.new.module'
    assert saved_attribute.class_name == 'NewClass'
    assert saved_attribute.dependencies == []

# ** test: container_configuration_repository_delete_attribute
def test_delete_attribute(container_config_repo: ContainerYamlRepository):
    '''
    Test the delete_attribute method of the ContainerYamlRepository.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # Ensure the container service attribute exists before deletion.
    assert container_config_repo.attribute_exists(CONTAINER_SERVICE_ID) is True

    # Delete the container service attribute.
    container_config_repo.delete_attribute(CONTAINER_SERVICE_ID)

    # Verify that the attribute no longer exists.
    assert container_config_repo.attribute_exists(CONTAINER_SERVICE_ID) is False

# ** test: container_configuration_repository_save_constants
def test_save_constants(container_config_repo: ContainerYamlRepository):
    '''
    Test the save_constants method of the ContainerYamlRepository.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # Define new constants to save.
    new_constants = {
        'new_const_1': 'value_1',
        'new_const_2': 'value_2'
    }

    # Save the new constants.
    container_config_repo.save_constants(new_constants)

    # List all attributes and constants to verify the new constants were saved.
    _, constants = container_config_repo.list_all()

    # Verify the new constants exist in the saved constants.
    assert 'new_const_1' in constants
    assert constants['new_const_1'] == 'value_1'
    assert 'new_const_2' in constants
    assert constants['new_const_2'] == 'value_2'

# ** test: container_configuration_repository_save_constants_overwrite
def test_save_constants_overwrite(container_config_repo: ContainerYamlRepository):
    '''
    Test that the save_constants method of the ContainerYamlRepository overwrites existing constants.

    :param container_config_repo: The ContainerYamlRepository instance.
    :type container_config_repo: ContainerYamlRepository
    '''

    # Define initial constants to save.
    initial_constants = {
        'const_to_overwrite': 'initial_value',
        'another_const': 'another_value'
    }

    # Save the initial constants.
    container_config_repo.save_constants(initial_constants)

    # Define new constants that will overwrite one of the initial constants.
    new_constants = {
        'const_to_overwrite': 'new_value',
        'additional_const': 'additional_value'
    }

    # Save the new constants.
    container_config_repo.save_constants(new_constants)

    # List all attributes and constants to verify the constants were updated.
    _, constants = container_config_repo.list_all()

    # Verify that new constants were added and existing ones were overwritten.
    assert constants == {
        'sample_const': 'sample_value',
        'const_to_overwrite': 'new_value',
        'another_const': 'another_value',
        'additional_const': 'additional_value'
    }