# *** imports

# ** infra
import pytest

# ** app
from ...app_yaml import *


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

# ** fixture: app_id
@pytest.fixture
def app_id():
    return 'test_app_yaml_proxy'


# *** tests

# ** test: app_yaml_proxy_list_settings
def test_app_yaml_proxy_list_settings(app_yaml_proxy, app_settings):
    '''
    Test the app YAML proxy list settings method.
    '''
    
    # List the settings.
    all_settings = app_yaml_proxy.list_settings()
    
    # Check the interfaces.
    assert all_settings
    assert len(all_settings) > 0


# ** test: app_yaml_proxy_get_settings
def test_app_yaml_proxy_get_settings(app_yaml_proxy, app_id):
    '''
    Test the app YAML proxy get settings method.
    '''

    # Get the interface.s
    settings = app_yaml_proxy.get_settings(app_id)

    # Check the interface.
    assert settings
    assert settings.id == 'test_app_yaml_proxy'
    assert settings.name == 'Test App YAML Proxy'
    assert settings.description == 'The context for testing the app yaml proxy.'
    assert settings.feature_flag == 'test_app_yaml_proxy'
    assert settings.data_flag == 'test_app_yaml_proxy'
    assert len(settings.attributes) == 1
    assert settings.attributes[0].attribute_id == 'test_attribute'
    assert settings.attributes[0].module_path == 'test_module_path'
    assert settings.attributes[0].class_name == 'test_class_name'
    assert settings.constants
    assert settings.constants['test_const'] == 'test_const_value'


# ** test: app_yaml_proxy_get_interface_not_found
def test_app_yaml_proxy_get_settings_not_found(app_yaml_proxy):

    # Get the interface.
    interface = app_yaml_proxy.get_settings('not_found')

    # Check the interface.
    assert not interface
