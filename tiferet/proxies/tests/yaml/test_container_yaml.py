# *** imports

# ** infra
import pytest

# ** app
from .. import *
from ....configs.tests.test_container import *
from ...container_yaml import *


# *** fixtures

# ** fixture: config_file_path
@pytest.fixture
def config_file_path():
    return 'tiferet/configs/tests/test.yml'


# ** fixture: container_attribute
@pytest.fixture
def container_attribute():
    return Entity.new(
        ContainerAttribute,
        **TEST_CONTAINER_ATTRIBUTE,
    )

# ** fixture: container_yaml_proxy
@pytest.fixture
def container_yaml_proxy(config_file_path):
    return ContainerYamlProxy(config_file_path)


# *** tests

# ** test: container_yaml_proxy_list_all
def test_container_yaml_proxy_list_all(container_yaml_proxy, container_attribute):

    # List all the container attributes.
    container_attributes, constants = container_yaml_proxy.list_all()

    # Verify Constants
    assert constants.get('config_file') == 'tiferet/configs/tests/test.yml'

    # Check the container attributes.
    assert container_attributes
    assert len(container_attributes) == 1
    assert container_attributes[0].id == container_attribute.id
    assert container_attributes[0].type == container_attribute.type
    assert len(container_attributes[0].dependencies) == len(container_attribute.dependencies)


# ** test: container_yaml_proxy_get_attribute
def test_container_yaml_proxy_get_attribute(container_yaml_proxy, container_attribute):

    # Get the container attribute.
    container_attribute = container_yaml_proxy.get_attribute(container_attribute.id, container_attribute.type)

    # Check the container attribute.
    assert container_attribute
    assert container_attribute.id == container_attribute.id
    assert container_attribute.type == container_attribute.type
    assert len(container_attribute.dependencies) == len(container_attribute.dependencies)


# ** test: container_yaml_proxy_get_attribute_not_found_or_wrong_type
def test_container_yaml_proxy_get_attribute_not_found_or_wrong_type(container_yaml_proxy, container_attribute):

    # Get the container attribute with the wrong id or type.
    container_attribute_not_found = container_yaml_proxy.get_attribute('not_found', container_attribute.type)
    container_attribute_wrong_type = container_yaml_proxy.get_attribute(container_attribute.id, 'invalid')

    # Check the container attribute is not found.
    assert not container_attribute_not_found
    assert not container_attribute_wrong_type
