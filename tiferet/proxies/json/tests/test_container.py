"""Tiferet Container JSON Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
import json

# ** app
from ....assets import TiferetError
from ....mappers import DataObject, ContainerAttributeConfigData
from ..container import ContainerJsonProxy

# *** fixtures

# ** fixture: container_config_file
@pytest.fixture
def container_config_file(tmp_path) -> str:
    '''
    A fixture for the container configuration file path.

    :return: The container configuration file path.
    :rtype: str
    '''

    # Create a temporary JSON file with sample container configuration content.
    file_path = tmp_path / 'test.json'

    # Write the sample container configuration to the JSON file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'attrs': {
                'test_container': {
                    'module_path': 'tiferet.containers.tests',
                    'class_name': 'TestContainer',
                    'dependencies': {
                        'test': {
                            'module_path': 'tiferet.proxies.tests',
                            'class_name': 'TestProxy',
                            'parameters': {
                                'param1': 'value1'
                            }
                        }
                    },
                }
            },
            'const': {
                'config_file': 'tiferet/configs/tests/test.yml'
            }
        }, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: container_json_proxy
@pytest.fixture
def container_json_proxy(container_config_file: str) -> ContainerJsonProxy:
    '''
    A fixture for the container JSON proxy.

    :param read_config_file_path: The container configuration file path.
    :type read_config_file_path: str
    :return: The container JSON proxy.
    :rtype: ContainerJsonProxy
    '''

    # Create and return the container JSON proxy.
    return ContainerJsonProxy(container_config_file)

# *** tests

# ** test: container_json_proxy_load_json
def test_container_json_proxy_load_json(container_json_proxy: ContainerJsonProxy):
    '''
    Test the load_json method of the ContainerJsonProxy.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    '''

    # Load the JSON file.
    data = container_json_proxy.load_json()

    # Check the loaded data.
    assert data
    assert data.get('attrs')
    assert len(data['attrs']) > 0
    assert data.get('const')
    assert isinstance(data['const'], dict)

# ** test: container_json_proxy_load_json_file_not_found
def test_container_json_proxy_load_json_file_not_found(container_json_proxy: ContainerJsonProxy):
    '''
    Test the load_json method with a file not found error.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    '''

    # Set a non-existent configuration file.
    container_json_proxy.json_file = 'non_existent_file.yml'

    # Attempt to load the JSON file.
    with pytest.raises(TiferetError) as exc_info:
        container_json_proxy.load_json()

    # Verify the error message.
    assert exc_info.value.error_code == 'CONTAINER_CONFIG_LOADING_FAILED'
    assert 'Unable to load container configuration file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('json_file') == container_json_proxy.json_file

# ** test: container_json_proxy_list_all_empty
def test_container_json_proxy_list_all_empty(container_json_proxy: ContainerJsonProxy, tmp_path):
    '''
    Test the list_all method with an empty configuration.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    :param tmp_path: The temporary path fixture.
    :type tmp_path: pathlib.Path
    '''

    # Create new config file with no container attributess.
    file_path = tmp_path / 'test_empty.json'
    with open(file_path, 'w') as f:
        json.dump({
            'attrs': {},
            'const': {}
        }, f)

    # Replace the config file path in the proxy.
    container_json_proxy.json_file = str(file_path)

    # List all the container attributes.
    container_attributes, constants = container_json_proxy.list_all()

    # Verify that the attributes is an empty list and constants is an empty dict.
    assert container_attributes == []
    assert constants == {}

# ** test: container_json_proxy_list_all
def test_container_json_proxy_list_all(
        container_json_proxy: ContainerJsonProxy
    ):
    '''
    Test the list_all method of the ContainerJsonProxy.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    :param container_attribute: The container attribute fixture.
    :type container_attribute: ContainerAttribute
    '''

    # List all the container attributes.
    container_attributes, constants = container_json_proxy.list_all()

    # Verify Constants
    assert constants.get('config_file') == 'tiferet/configs/tests/test.yml'

    # Check the container attributes.
    assert container_attributes
    assert len(container_attributes) == 1
    assert container_attributes[0].id == 'test_container'
    assert container_attributes[0].module_path == 'tiferet.containers.tests'
    assert container_attributes[0].class_name == 'TestContainer'
    assert len(container_attributes[0].dependencies) == 1


    # Check the dependencies.
    dependency = container_attributes[0].dependencies[0]
    assert dependency.module_path == 'tiferet.proxies.tests'
    assert dependency.class_name == 'TestProxy'
    assert dependency.flag == 'test'
    assert dependency.parameters == {'param1': 'value1'}

# ** test: container_json_proxy_get_attribute
def test_container_json_proxy_get_attribute(
        container_json_proxy: ContainerJsonProxy,
    ):
    '''
    Test the get_attribute method of the ContainerJsonProxy.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    :param container_attribute: The container attribute fixture.
    :type container_attribute: ContainerAttribute
    '''

    # Get the container attribute.
    test_container_attribute = container_json_proxy.get_attribute('test_container')

    # Check the container attribute.
    assert test_container_attribute
    assert test_container_attribute.id == 'test_container'
    assert test_container_attribute.module_path == 'tiferet.containers.tests'
    assert test_container_attribute.class_name == 'TestContainer'
    assert len(test_container_attribute.dependencies) == 1

    # Check the dependencies.
    dependency = test_container_attribute.dependencies[0]
    assert dependency.module_path == 'tiferet.proxies.tests'
    assert dependency.class_name == 'TestProxy'
    assert dependency.flag == 'test'
    assert dependency.parameters == {'param1': 'value1'}

# ** test: container_json_proxy_get_attribute_not_found
def test_container_json_proxy_get_attribute_not_found(
        container_json_proxy: ContainerJsonProxy,
    ):
    '''
    Test the get_attribute method of the ContainerJsonProxy for a non-existent attribute.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    '''

    # Get the container attribute.
    test_container_attribute = container_json_proxy.get_attribute('not_found')

    # Check the container attribute.
    assert not test_container_attribute

# ** test: container_json_proxy_save_attribute
def test_container_json_proxy_save_attribute(
        container_json_proxy: ContainerJsonProxy,
    ):
    '''
    Test the save_attribute method of the ContainerJsonProxy.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    '''

    # Create a new container attribute.
    new_attribute = DataObject.from_data(
        ContainerAttributeConfigData,
        id='new_container',
        module_path='tiferet.containers.new',
        class_name='NewContainer',
        deps={
            'new_flag': {
                'module_path': 'tiferet.proxies.new',
                'class_name': 'NewProxy',
                'parameters': {
                    'paramA': 'valueA'
                }
            }
        }
    ).map()

    # Save the updated container attribute.
    container_json_proxy.save_attribute(new_attribute)

    # Retrieve the saved container attribute.
    saved_attribute = container_json_proxy.get_attribute('new_container')

    # Check the saved container attribute.
    assert saved_attribute
    assert saved_attribute.id == 'new_container'
    assert saved_attribute.module_path == 'tiferet.containers.new'
    assert saved_attribute.class_name == 'NewContainer'
    assert len(saved_attribute.dependencies) == 1

    # Check the dependencies.
    dependency = saved_attribute.dependencies[0]
    assert dependency.module_path == 'tiferet.proxies.new'
    assert dependency.class_name == 'NewProxy'
    assert dependency.flag == 'new_flag'
    assert dependency.parameters == {'paramA': 'valueA'}

# ** test: container_json_proxy_delete_attribute
def test_container_json_proxy_delete_attribute(
        container_json_proxy: ContainerJsonProxy,
    ):
    '''
    Test the delete_attribute method of the ContainerJsonProxy.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    '''

    # Delete the existing container attribute.
    container_json_proxy.delete_attribute('test_container')

    # Attempt to retrieve the deleted container attribute.
    deleted_attribute = container_json_proxy.get_attribute('test_container')

    # Check that the container attribute is None.
    assert not deleted_attribute

# ** test: container_json_proxy_save_constants
def test_container_json_proxy_save_constants(
        container_json_proxy: ContainerJsonProxy,
    ):
    '''
    Test the save_constants method of the ContainerJsonProxy.

    :param container_json_proxy: The container JSON proxy.
    :type container_json_proxy: ContainerJsonProxy
    '''

    # Define new constants to save.
    new_constants = {
        'new_const1': 'value1',
        'new_const2': 'value2'
    }

    # Save the new constants.
    container_json_proxy.save_constants(new_constants)

    # List all the container attributes to retrieve the updated constants.
    _, constants = container_json_proxy.list_all()

    # Check the saved constants.
    assert constants.get('new_const1') == 'value1'
    assert constants.get('new_const2') == 'value2'