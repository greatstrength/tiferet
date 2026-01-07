"""Tiferet App Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest
import yaml

# ** app
from ....data import DataObject, AppInterfaceConfigData
from ..app import AppConfigurationRepository

# *** constants

# ** constant: TEST_APP_ID
TEST_APP_ID = 'test_app'

# ** constant: TEST_APP_2_ID
TEST_APP_2_ID = 'test_app_2'

# ** constant: APP_DATA
APP_DATA = {
    'interfaces': {
        TEST_APP_ID: {
            'name': 'Test App',
            'description': 'First test app interface.',
            'feature_flag': 'test_feature_flag',
            'data_flag': 'test_data_flag',
            'attrs': {
                'test_attribute': {
                    'module_path': 'test.module',
                    'class_name': 'TestClass',
                    'params': {'foo': 'bar'},
                },
            },
            'const': {
                'TEST_CONST': 'VALUE',
            },
        },
        TEST_APP_2_ID: {
            'name': 'Second Test App',
            'description': 'Second test app interface.',
            'feature_flag': 'test_feature_flag_2',
            'data_flag': 'test_data_flag_2',
            'attrs': {},
            'const': {},
        },
    },
}

# *** fixtures

# ** fixture: app_config_file
@pytest.fixture
def app_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to a temporary app YAML configuration file.

    :return: The app YAML configuration file path.
    :rtype: str
    '''

    file_path = tmp_path / 'test_app.yaml'

    # Write the sample app configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(APP_DATA, f)

    return str(file_path)


# ** fixture: app_config_repo
@pytest.fixture
def app_config_repo(app_config_file: str) -> AppConfigurationRepository:
    '''
    Fixture to create an instance of the AppConfigurationRepository.

    :param app_config_file: The app YAML configuration file path.
    :type app_config_file: str
    :return: An instance of AppConfigurationRepository.
    :rtype: AppConfigurationRepository
    '''

    return AppConfigurationRepository(app_config_file)

# *** tests

# ** test_int: app_config_repo_exists

def test_int_app_config_repo_exists(app_config_repo: AppConfigurationRepository):
    '''
    Test the exists method of the AppConfigurationRepository.
    '''

    assert app_config_repo.exists(TEST_APP_ID)
    assert app_config_repo.exists(TEST_APP_2_ID)
    assert not app_config_repo.exists('missing_app')


# ** test_int: app_config_repo_get
def test_int_app_config_repo_get(app_config_repo: AppConfigurationRepository):
    '''
    Test the get method of the AppConfigurationRepository.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    interface = app_config_repo.get(TEST_APP_ID)
    interface_2 = app_config_repo.get(TEST_APP_2_ID)

    # Check first interface
    assert interface
    assert interface.id == TEST_APP_ID
    assert interface.name == 'Test App'
    assert interface.description == 'First test app interface.'
    assert interface.feature_flag == 'test_feature_flag'
    assert interface.data_flag == 'test_data_flag'
    assert len(interface.attributes) == 1
    attr = interface.attributes[0]
    assert attr.attribute_id == 'test_attribute'
    assert attr.module_path == 'test.module'
    assert attr.class_name == 'TestClass'
    assert attr.parameters == {'foo': 'bar'}
    assert interface.constants == {'TEST_CONST': 'VALUE'}

    # Check second interface
    assert interface_2
    assert interface_2.id == TEST_APP_2_ID
    assert interface_2.name == 'Second Test App'
    assert interface_2.description == 'Second test app interface.'
    assert interface_2.feature_flag == 'test_feature_flag_2'
    assert interface_2.data_flag == 'test_data_flag_2'
    assert interface_2.attributes == []
    assert interface_2.constants == {}

# ** test_int: app_config_repo_get_not_found
def test_int_app_config_repo_get_not_found(app_config_repo: AppConfigurationRepository):
    '''
    Test the get method of the AppConfigurationRepository for a non-existent interface.
    '''

    interface = app_config_repo.get('missing_app')
    assert not interface

# ** test_int: app_config_repo_list
def test_int_app_config_repo_list(app_config_repo: AppConfigurationRepository):
    '''
    Test the list method of the AppConfigurationRepository.
    '''

    interfaces = app_config_repo.list()

    assert interfaces
    assert len(interfaces) == 2
    ids = {i.id for i in interfaces}
    assert TEST_APP_ID in ids
    assert TEST_APP_2_ID in ids

# ** test_int: app_config_repo_save
def test_int_app_config_repo_save(app_config_repo: AppConfigurationRepository):
    '''
    Test the save method of the AppConfigurationRepository.
    '''

    NEW_APP_ID = 'new_test_app'

    # Build a new AppInterface using AppInterfaceConfigData mapping helper
    interface = DataObject.from_data(
        AppInterfaceConfigData,
        id=NEW_APP_ID,
        name='New Test App',
        description='New test app interface.',
        feature_flag='new_feature_flag',
        data_flag='new_data_flag',
        attrs={
            'new_attr': {
                'module_path': 'new.module',
                'class_name': 'NewClass',
                'params': {'x': 'y'},
            },
        },
        const={'NEW_CONST': 'NEW_VALUE'},
    ).map()

    app_config_repo.save(interface)

    saved = app_config_repo.get(NEW_APP_ID)

    assert saved
    assert saved.id == NEW_APP_ID
    assert saved.name == 'New Test App'
    assert saved.description == 'New test app interface.'
    assert saved.feature_flag == 'new_feature_flag'
    assert saved.data_flag == 'new_data_flag'
    assert len(saved.attributes) == 1
    s_attr = saved.attributes[0]
    assert s_attr.attribute_id == 'new_attr'
    assert s_attr.module_path == 'new.module'
    assert s_attr.class_name == 'NewClass'
    assert s_attr.parameters == {'x': 'y'}
    assert saved.constants == {'NEW_CONST': 'NEW_VALUE'}

# ** test_int: app_config_repo_delete
def test_int_app_config_repo_delete(app_config_repo: AppConfigurationRepository):
    '''
    Test the delete method of the AppConfigurationRepository.
    '''

    # Ensure the interface exists first
    assert app_config_repo.get(TEST_APP_2_ID)

    # Delete and verify it is gone
    app_config_repo.delete(TEST_APP_2_ID)
    deleted = app_config_repo.get(TEST_APP_2_ID)
    assert not deleted
