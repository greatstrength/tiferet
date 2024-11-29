# *** imports

# ** core
from typing import List, Dict

# ** infra

# ** app
from . import *
from ...repos.container import YamlProxy as ContainerYamlProxy


# *** fixtures

# ** fixture: test_container_yaml_proxy
@pytest.fixture
def test_container_yaml_proxy():
    return ContainerYamlProxy(TEST_CONFIG_FILE_PATH)


# *** tests

# ** test: container_yaml_proxy_list_all
def test_container_yaml_proxy_list_all(test_container_yaml_proxy, test_repo_container_attribute):

    # List all the container attributes.
    container_attributes, constants = test_container_yaml_proxy.list_all()

    # Verify Constants
    assert constants.get('config_file') == 'tiferet/configs/tests/test.yml'

    # Check the container attributes.
    assert container_attributes
    assert len(container_attributes) == 1
    assert container_attributes[0].id == test_repo_container_attribute.id
    assert container_attributes[0].type == test_repo_container_attribute.type
    assert len(container_attributes[0].dependencies) == len(test_repo_container_attribute.dependencies)


# ** test: container_yaml_proxy_get_attribute
def test_container_yaml_proxy_get_attribute(test_container_yaml_proxy, test_repo_container_attribute):

    # Get the container attribute.
    container_attribute = test_container_yaml_proxy.get_attribute(test_repo_container_attribute.id, test_repo_container_attribute.type)

    # Check the container attribute.
    assert container_attribute
    assert container_attribute.id == test_repo_container_attribute.id
    assert container_attribute.type == test_repo_container_attribute.type
    assert len(container_attribute.dependencies) == len(test_repo_container_attribute.dependencies)


# ** test: container_yaml_proxy_get_attribute_not_found_or_wrong_type
def test_container_yaml_proxy_get_attribute_not_found_or_wrong_type(test_container_yaml_proxy, test_repo_container_attribute):

    # Get the container attribute with the wrong id or type.
    container_attribute_not_found = test_container_yaml_proxy.get_attribute('not_found', test_repo_container_attribute.type)
    container_attribute_wrong_type = test_container_yaml_proxy.get_attribute(test_repo_container_attribute.id, 'invalid')

    # Check the container attribute is not found.
    assert not container_attribute_not_found
    assert not container_attribute_wrong_type
