"""Tiferet Container YAML Proxy Tests Exports"""

# *** imports

# ** core
import os

# ** infra
import pytest

# ** app
from ....commands import TiferetError
from ....models import (
    ContainerAttribute,
    FlaggedDependency,
    ModelObject
)
from ..container import ContainerYamlProxy

# *** fixtures

# ** fixture: read_config_file_path
@pytest.fixture
def read_config_file_path() -> str:
    '''
    A fixture for the container configuration file path.

    :return: The container configuration file path.
    :rtype: str
    '''

    # Return the container configuration file path.
    return 'tiferet/configs/tests/test.yml'


# ** fixture: container_attribute
@pytest.fixture
def container_attribute() -> ContainerAttribute:
    '''
    A fixture for a basic ContainerAttribute instance.
    
    :return: The ContainerAttribute instance.
    :rtype: ContainerAttribute
    '''
    
    return ModelObject.new(
        ContainerAttribute,
        id='test_container',
        module_path='tiferet.containers.tests',
        class_name='TestContainer',
        dependencies=[
            ModelObject.new(
                FlaggedDependency,
                module_path='tiferet.proxies.tests',
                class_name='TestProxy',
                flag='test',
                parameters={'param1': 'value1'}
            )
        ]
    )


# ** fixture: container_yaml_proxy
@pytest.fixture
def container_yaml_proxy(read_config_file_path: str) -> ContainerYamlProxy:
    '''
    A fixture for the container YAML proxy.

    :param read_config_file_path: The container configuration file path.
    :type read_config_file_path: str
    :return: The container YAML proxy.
    :rtype: ContainerYamlProxy
    '''

    # Create and return the container YAML proxy.
    return ContainerYamlProxy(read_config_file_path)


# *** tests

# ** test: container_yaml_proxy_load_yaml
def test_container_yaml_proxy_load_yaml(container_yaml_proxy: ContainerYamlProxy):
    '''
    Test the load_yaml method of the ContainerYamlProxy.

    :param container_yaml_proxy: The container YAML proxy.
    :type container_yaml_proxy: ContainerYamlProxy
    '''

    # Load the YAML file.
    data = container_yaml_proxy.load_yaml()

    # Check the loaded data.
    assert data
    assert data.get('attrs')
    assert len(data['attrs']) > 0
    assert data.get('const')
    assert isinstance(data['const'], dict)


# ** test: container_yaml_proxy_load_yaml_file_not_found
def test_container_yaml_proxy_load_yaml_file_not_found(container_yaml_proxy: ContainerYamlProxy):
    '''
    Test the load_yaml method with a file not found error.

    :param container_yaml_proxy: The container YAML proxy.
    :type container_yaml_proxy: ContainerYamlProxy
    '''

    # Set a non-existent configuration file.
    container_yaml_proxy.config_file = 'non_existent_file.yml'

    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        container_yaml_proxy.load_yaml()

    # Verify the error message.
    assert exc_info.value.error_code == 'CONTAINER_CONFIG_LOADING_FAILED'
    assert 'Unable to load container configuration file' in str(exc_info.value)


# ** test: container_yaml_proxy_list_all_empty
def test_container_yaml_proxy_list_all_empty(container_yaml_proxy: ContainerYamlProxy):
    '''
    Test the list_all method with an empty configuration.

    :param container_yaml_proxy: The container YAML proxy.
    :type container_yaml_proxy: ContainerYamlProxy
    '''

    # Create new config file with no container attributess.
    file_path = 'tiferet/configs/tests/test_empty.yml'
    with open(file_path, 'w') as f:
        f.write('attrs:\n')
        f.write('const:\n')

    # Replace the config file path in the proxy.
    container_yaml_proxy.config_file = file_path

    # List all the container attributes.
    container_attributes, constants = container_yaml_proxy.list_all()

    # Verify that the attributes is an empty list and constants is an empty dict.
    assert container_attributes == []
    assert constants == {}

    # Clean up the empty config file.
    os.remove(file_path)


# ** test: container_yaml_proxy_list_all
def test_container_yaml_proxy_list_all(
        container_yaml_proxy: ContainerYamlProxy,
        container_attribute: ContainerAttribute
    ):
    '''
    Test the list_all method of the ContainerYamlProxy.

    :param container_yaml_proxy: The container YAML proxy.
    :type container_yaml_proxy: ContainerYamlProxy
    :param container_attribute: The container attribute fixture.
    :type container_attribute: ContainerAttribute
    '''

    # List all the container attributes.
    container_attributes, constants = container_yaml_proxy.list_all()

    # Verify Constants
    assert constants.get('config_file') == 'tiferet/configs/tests/test.yml'

    # Check the container attributes.
    assert container_attributes
    assert len(container_attributes) == 1
    assert container_attributes[0].id == container_attribute.id
    assert container_attributes[0].module_path == container_attribute.module_path
    assert container_attributes[0].class_name == container_attribute.class_name
    assert len(container_attributes[0].dependencies) == len(container_attribute.dependencies)

    # Check the dependencies.
    for i, dependency in enumerate(container_attributes[0].dependencies):
        assert dependency.module_path == container_attribute.dependencies[i].module_path
        assert dependency.class_name == container_attribute.dependencies[i].class_name
        assert dependency.flag == container_attribute.dependencies[i].flag
        assert dependency.parameters == container_attribute.dependencies[i].parameters


# ** test: container_yaml_proxy_get_attribute
def test_container_yaml_proxy_get_attribute(
        container_yaml_proxy: ContainerYamlProxy,
        container_attribute: ContainerAttribute
    ):
    '''
    Test the get_attribute method of the ContainerYamlProxy.

    :param container_yaml_proxy: The container YAML proxy.
    :type container_yaml_proxy: ContainerYamlProxy
    :param container_attribute: The container attribute fixture.
    :type container_attribute: ContainerAttribute
    '''

    # Get the container attribute.
    test_container_attribute = container_yaml_proxy.get_attribute(container_attribute.id)

    # Check the container attribute.
    assert test_container_attribute
    assert test_container_attribute.id == container_attribute.id
    assert test_container_attribute.module_path == container_attribute.module_path
    assert test_container_attribute.class_name == container_attribute.class_name
    assert len(test_container_attribute.dependencies) == len(container_attribute.dependencies)

    # Check the dependencies.
    for i, dependency in enumerate(test_container_attribute.dependencies):
        assert dependency.module_path == container_attribute.dependencies[i].module_path
        assert dependency.class_name == container_attribute.dependencies[i].class_name
        assert dependency.flag == container_attribute.dependencies[i].flag
        assert dependency.parameters == container_attribute.dependencies[i].parameters