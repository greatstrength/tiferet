"""Tiferet App YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest

# ** app
from ....configs import TiferetError
from ..app import AppYamlProxy

# *** fixtures

# ** fixture: app_config_file
@pytest.fixture
def app_config_file() -> str:
    '''
    A fixture for the app configuration file path.

    :return: The app configuration file path.
    :rtype: str
    '''

    # Return the app configuration file path.
    return 'tiferet/configs/tests/test.yml'

# ** fixture: app_yaml_proxy
@pytest.fixture
def app_yaml_proxy(app_config_file) -> AppYamlProxy:
    '''
    A fixture for the app YAML proxy.

    :param app_config_file: The app configuration file path.
    :type app_config_file: str
    :return: The app YAML proxy.
    :rtype: AppYamlProxy
    '''

    # Create and return the app YAML proxy.
    return AppYamlProxy(
        app_config_file=app_config_file
    )

# ** fixture: app_id
@pytest.fixture
def app_id() -> str:
    '''
    A fixture for the app id.

    :return: The app id.
    :rtype: str
    '''

    # Return the app id.
    return 'test_app_yaml_proxy'


# *** tests

# ** test: app_yaml_proxy_load_yaml
def test_app_yaml_proxy_load_yaml(app_yaml_proxy: AppYamlProxy):
    '''
    Test the app YAML proxy load YAML method.

    :param app_yaml_proxy: The app YAML proxy.
    :type app_yaml_proxy: AppYamlProxy
    '''

    # Load the YAML file.
    data = app_yaml_proxy.load_yaml()

    # Check the loaded data.
    assert data
    assert data.get('interfaces')
    assert len(data['interfaces']) > 0

# ** test: app_yaml_proxy_load_yaml_file_not_found
def test_app_yaml_proxy_load_yaml_file_not_found(app_yaml_proxy: AppYamlProxy):
    '''
    Test the app YAML proxy load YAML method with a file not found error.

    :param app_yaml_proxy: The app YAML proxy.
    :type app_yaml_proxy: AppYamlProxy
    '''

    # Set a non-existent configuration file.
    app_yaml_proxy.config_file = 'non_existent_file.yml'

    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        app_yaml_proxy.load_yaml()

    # Check the exception message.
    assert exc_info.value.error_code == 'APP_CONFIG_LOADING_FAILED'
    assert 'Unable to load app configuration file' in str(exc_info.value)

# ** test: app_yaml_proxy_list_interfaces
def test_app_yaml_proxy_list_interfaces(app_yaml_proxy: AppYamlProxy):
    '''
    Test the app YAML proxy list settings method.

    :param app_yaml_proxy: The app YAML proxy.
    :type app_yaml_proxy: AppYamlProxy
    '''
    
    # List the settings.
    all_settings = app_yaml_proxy.list_interfaces()
    
    # Check the interfaces.
    assert all_settings
    assert len(all_settings) > 0


# ** test: app_yaml_proxy_get_interface
def test_app_yaml_proxy_get_interface(
        app_yaml_proxy: AppYamlProxy,
        app_id: str
    ):
    '''
    Test the app YAML proxy get settings method.

    :param app_yaml_proxy: The app YAML proxy.
    :type app_yaml_proxy: AppYamlProxy
    :param app_id: The app id.
    :type app_id: str
    '''

    # Get the interface.
    interface = app_yaml_proxy.get_interface(app_id)

    # Check the interface.
    assert interface
    assert interface.id == 'test_app_yaml_proxy'
    assert interface.name == 'Test App YAML Proxy'
    assert interface.description == 'The context for testing the app yaml proxy.'
    assert interface.feature_flag == 'test_app_yaml_proxy'
    assert interface.data_flag == 'test_app_yaml_proxy'
    assert len(interface.attributes) == 1
    assert interface.attributes[0].attribute_id == 'test_attribute'
    assert interface.attributes[0].module_path == 'test_module_path'
    assert interface.attributes[0].class_name == 'test_class_name'
    assert interface.constants
    assert interface.constants['test_const'] == 'test_const_value'


# ** test: app_yaml_proxy_get_interface_not_found
def test_app_yaml_proxy_get_interface_not_found(app_yaml_proxy: AppYamlProxy):
    '''
    Test the app YAML proxy get settings method with a not found interface.

    :param app_yaml_proxy: The app YAML proxy.
    :type app_yaml_proxy: AppYamlProxy
    '''

    # Get the interface.
    interface = app_yaml_proxy.get_interface('not_found')

    # Check the interface.
    assert not interface