"""Tiferet App JSON Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
import json

# ** app
from ....configs import TiferetError
from ....data import DataObject, AppInterfaceConfigData
from ..app import AppJsonProxy

# *** fixtures

# ** fixture: app_config_file
@pytest.fixture
def app_config_file(tmp_path) -> str:
    '''
    A fixture for the app configuration file path.

    :return: The app configuration file path.
    :rtype: str
    '''

    # Create a temporary JSON file with sample app configuration content.
    file_path = tmp_path / 'test.json'

    # Write the sample app configuration to the JSON file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'interfaces': {
                'test_app_json_proxy': {
                    'attrs': {
                        'test_attribute': {
                            'module_path': 'test_module_path',
                            'class_name': 'test_class_name'
                        }
                    },
                    'const': {
                        'test_const': 'test_const_value'
                    },
                    'name': 'Test App JSON Proxy',
                    'description': 'The context for testing the app json proxy.',
                    'feature_flag': 'test_app_json_proxy',
                    'data_flag': 'test_app_json_proxy'
                }
            }
        }, f)
    
    # Return the file path as a string.
    return str(file_path)

# ** fixture: app_json_proxy
@pytest.fixture
def app_json_proxy(app_config_file) -> AppJsonProxy:
    '''
    A fixture for the app JSON proxy.

    :param app_config_file: The app configuration file path.
    :type app_config_file: str
    :return: The app JSON proxy.
    :rtype: AppJsonProxy
    '''

    # Create and return the app JSON proxy.
    return AppJsonProxy(
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
    return 'test_app_json_proxy'


# *** tests

# ** test: app_json_proxy_load_json
def test_app_json_proxy_load_json(app_json_proxy: AppJsonProxy):
    '''
    Test the app JSON proxy load JSON method.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    '''

    # Load the JSON file.
    data = app_json_proxy.load_json()

    # Check the loaded data.
    assert data
    assert data.get('interfaces')
    assert len(data['interfaces']) > 0

# ** test: app_json_proxy_load_json_file_not_found
def test_app_json_proxy_load_json_file_not_found(app_json_proxy: AppJsonProxy):
    '''
    Test the app JSON proxy load JSON method with a file not found error.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    '''

    # Set a non-existent configuration file.
    app_json_proxy.json_file = 'non_existent_file.yml'

    # Attempt to load the JSON file.
    with pytest.raises(TiferetError) as exc_info:
        app_json_proxy.load_json()

    # Check the exception message.
    assert exc_info.value.error_code == 'APP_CONFIG_LOADING_FAILED'
    assert 'Unable to load app configuration file' in str(exc_info.value)

# ** test: app_json_proxy_list_interfaces
def test_app_json_proxy_list_interfaces(app_json_proxy: AppJsonProxy):
    '''
    Test the app JSON proxy list settings method.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    '''
    
    # List the settings.
    all_settings = app_json_proxy.list_interfaces()
    
    # Check the interfaces.
    assert all_settings
    assert len(all_settings) > 0


# ** test: app_json_proxy_get_interface
def test_app_json_proxy_get_interface(
        app_json_proxy: AppJsonProxy,
        app_id: str
    ):
    '''
    Test the app JSON proxy get settings method.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    :param app_id: The app id.
    :type app_id: str
    '''

    # Get the interface.
    interface = app_json_proxy.get_interface(app_id)

    # Check the interface.
    assert interface
    assert interface.id == 'test_app_json_proxy'
    assert interface.name == 'Test App JSON Proxy'
    assert interface.description == 'The context for testing the app json proxy.'
    assert interface.feature_flag == 'test_app_json_proxy'
    assert interface.data_flag == 'test_app_json_proxy'
    assert len(interface.attributes) == 1
    assert interface.attributes[0].attribute_id == 'test_attribute'
    assert interface.attributes[0].module_path == 'test_module_path'
    assert interface.attributes[0].class_name == 'test_class_name'
    assert interface.constants
    assert interface.constants['test_const'] == 'test_const_value'


# ** test: app_json_proxy_get_interface_not_found
def test_app_json_proxy_get_interface_not_found(app_json_proxy: AppJsonProxy):
    '''
    Test the app JSON proxy get settings method with a not found interface.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    '''

    # Get the interface.
    interface = app_json_proxy.get_interface('not_found')

    # Check the interface.
    assert not interface

# ** test: app_json_proxy_save_interface
def test_app_json_proxy_save_interface(
        app_json_proxy: AppJsonProxy
    ):
    '''
    Test the app JSON proxy save settings method.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    :param app_id: The app id.
    :type app_id: str
    '''

    # Create a new app interface to save.
    new_interface = DataObject.from_data(
        AppInterfaceConfigData,
        id='new_test_app_json_proxy',
        name='New Test App JSON Proxy',
        description='The context for testing the new app json proxy.',
        feature_flag='new_test_app_json_proxy',
        data_flag='new_test_app_json_proxy',
        attributes={
            'new_test_attribute': {
                'module_path': 'new_test_module_path',
                'class_name': 'new_test_class_name'
            }
        },
        constants={
            'new_test_const': 'new_test_const_value'
        }
    ).map()


    # Save the interface.
    app_json_proxy.save_interface(new_interface)

    # Get the updated interface.
    updated_interface = app_json_proxy.get_interface(new_interface.id)

    # Check the updated interface.
    assert updated_interface
    assert updated_interface.id == 'new_test_app_json_proxy'
    assert updated_interface.name == 'New Test App JSON Proxy'
    assert updated_interface.description == 'The context for testing the new app json proxy.'
    assert updated_interface.feature_flag == 'new_test_app_json_proxy'
    assert updated_interface.data_flag == 'new_test_app_json_proxy'
    assert len(updated_interface.attributes) == 1
    assert updated_interface.attributes[0].attribute_id == 'new_test_attribute'
    assert updated_interface.attributes[0].module_path == 'new_test_module_path'
    assert updated_interface.attributes[0].class_name == 'new_test_class_name'
    assert updated_interface.constants
    assert updated_interface.constants['new_test_const'] == 'new_test_const_value'

# ** test: app_json_proxy_delete_interface
def test_app_json_proxy_delete_interface(
        app_json_proxy: AppJsonProxy,
        app_id: str
    ):
    '''
    Test the app JSON proxy delete settings method.

    :param app_json_proxy: The app JSON proxy.
    :type app_json_proxy: AppJsonProxy
    :param app_id: The app id.
    :type app_id: str
    '''

    # Delete the interface.
    app_json_proxy.delete_interface(app_id)

    # Attempt to get the deleted interface.
    deleted_interface = app_json_proxy.get_interface(app_id)

    # Check that the interface is deleted.
    assert not deleted_interface

