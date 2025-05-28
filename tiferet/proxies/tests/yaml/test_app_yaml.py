# *** imports

# ** infra
import pytest

# ** app
from ...app_yaml import *
from ....configs.tests.test_app import *


# *** fixtures

# ** fixture: app_config_file
@pytest.fixture
def app_config_file():
    return 'tiferet/configs/tests/test.yml'


# ** fixture: app_yaml_proxy
@pytest.fixture
def app_yaml_proxy(app_config_file):
    return AppYamlProxy(
        app_config_file=app_config_file
    )


# ** fixture: app_interface
@pytest.fixture
def app_interface():
    return ModelObject.new(
        AppSettings,
        **TEST_APP_INTERFACE,
    )


# *** tests

# ** test: app_yaml_proxy_list_settings
def test_app_yaml_proxy_list_settings(app_yaml_proxy, app_interface):
    '''
    Test the app YAML proxy list interfaces method.
    '''
    
    # List the interfaces.
    interfaces = app_yaml_proxy.list_settings()
    
    # Check the interfaces.
    assert interfaces
    assert len(interfaces) == 1
    assert interfaces[0].id == app_interface.id
    assert interfaces[0].name == app_interface.name


# ** test: app_yaml_proxy_get_settings
def test_app_yaml_proxy_get_settings(app_yaml_proxy, app_interface):
    '''
    Test the app YAML proxy get settings method.
    '''

    # Get the interface.
    interface = app_yaml_proxy.get_settings(app_interface.id)

    # Check the interface.
    assert interface
    assert interface.id == app_interface.id
    assert interface.name == app_interface.name
    assert interface.description == app_interface.description
    assert interface.feature_flag == app_interface.feature_flag
    assert interface.data_flag == app_interface.data_flag
    assert len(interface.dependencies) == 1
    assert interface.dependencies[0] == app_interface.dependencies[0]


# ** test: app_yaml_proxy_get_interface_not_found
def test_app_yaml_proxy_get_settings_not_found(app_yaml_proxy):

    # Get the interface.
    interface = app_yaml_proxy.get_settings('not_found')

    # Check the interface.
    assert not interface
