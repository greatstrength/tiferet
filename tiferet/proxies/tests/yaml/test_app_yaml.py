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


# ** fixture: app_settings
@pytest.fixture
def app_settings():
    settings = ModelObject.new(
        AppSettings,
        **TEST_APP_SETTINGS,
    )

    # Set the test_app_yaml_proxy id.
    settings.id = 'test_app_yaml_proxy'
    settings.name = 'Test App YAML Proxy'
    settings.description = 'The context for testing the app yaml proxy.'
    settings.feature_flag = 'test_app_yaml_proxy'
    settings.data_flag = 'test_app_yaml_proxy'

    # Return the settings.
    return settings


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
def test_app_yaml_proxy_get_settings(app_yaml_proxy, app_settings):
    '''
    Test the app YAML proxy get settings method.
    '''

    # Get the interface.
    settings = app_yaml_proxy.get_settings(app_settings.id)

    # Check the interface.
    assert settings
    assert settings.id == app_settings.id
    assert settings.name == app_settings.name
    assert settings.description == app_settings.description
    assert settings.feature_flag == app_settings.feature_flag
    assert settings.data_flag == app_settings.data_flag
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
