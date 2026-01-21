"""Tiferet App Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ....data import (
    DataObject,
    AppInterfaceConfigData,
)
from ..app import AppConfigurationRepository


# *** constants

# ** constant: test_app_id
TEST_APP_ID = 'test.app'

# ** constant: another_app_id
ANOTHER_APP_ID = 'another.app'

# ** constant: app_data
APP_DATA: Dict[str, Dict] = {
    'interfaces': {
        TEST_APP_ID: {
            'name': 'Test App',
            'description': 'A test app interface.',
            'module': 'tiferet.apps.test',
            'class': 'TestApp',
            'attrs': {},
            'const': {},
        },
        ANOTHER_APP_ID: {
            'name': 'Another App',
            'description': 'Another test app interface.',
            'module': 'tiferet.apps.another',
            'class': 'AnotherApp',
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
    Fixture to provide the path to the app YAML configuration file.

    :return: The app YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample app configuration content.
    file_path = tmp_path / 'test_app.yaml'

    # Write the sample app configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(APP_DATA, yaml_file)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: app_config_repo
@pytest.fixture
def app_config_repo(app_config_file: str) -> AppConfigurationRepository:
    '''
    Fixture to create an instance of the App Configuration Repository.

    :param app_config_file: The app YAML configuration file path.
    :type app_config_file: str
    :return: An instance of AppConfigurationRepository.
    :rtype: AppConfigurationRepository
    '''

    # Create and return the AppConfigurationRepository instance.
    return AppConfigurationRepository(app_config_file)

# *** tests

# ** test_int: app_config_repo_exists
def test_int_app_config_repo_exists(
        app_config_repo: AppConfigurationRepository,
    ) -> None:
    '''
    Test the exists method of the AppConfigurationRepository.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    # Check if the app interfaces exist.
    assert app_config_repo.exists(TEST_APP_ID)
    assert app_config_repo.exists(ANOTHER_APP_ID)
    assert not app_config_repo.exists('missing.app')

# ** test_int: app_config_repo_get
def test_int_app_config_repo_get(
        app_config_repo: AppConfigurationRepository,
    ) -> None:
    '''
    Test the get method of the AppConfigurationRepository.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    # Get app interfaces by id.
    app = app_config_repo.get(TEST_APP_ID)
    another_app = app_config_repo.get(ANOTHER_APP_ID)

    # Check the first app interface.
    assert app
    assert app.id == TEST_APP_ID
    assert app.name == 'Test App'
    assert app.module_path == 'tiferet.apps.test'
    assert app.class_name == 'TestApp'

    # Check the second app interface.
    assert another_app
    assert another_app.id == ANOTHER_APP_ID
    assert another_app.name == 'Another App'
    assert another_app.module_path == 'tiferet.apps.another'
    assert another_app.class_name == 'AnotherApp'

# ** test_int: app_config_repo_get_not_found
def test_int_app_config_repo_get_not_found(
        app_config_repo: AppConfigurationRepository,
    ) -> None:
    '''
    Test the get method of the AppConfigurationRepository for a non-existent app interface.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    # Attempt to get a non-existent app interface.
    app = app_config_repo.get('missing.app')

    # Check that the app interface is None.
    assert not app

# ** test_int: app_config_repo_list
def test_int_app_config_repo_list(
        app_config_repo: AppConfigurationRepository,
    ) -> None:
    '''
    Test the list method of the AppConfigurationRepository for all app interfaces.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    # List all app interfaces.
    interfaces = app_config_repo.list()

    # Check the interfaces.
    assert interfaces
    assert len(interfaces) == 2
    interface_ids = [interface.id for interface in interfaces]
    assert TEST_APP_ID in interface_ids
    assert ANOTHER_APP_ID in interface_ids

# ** test_int: app_config_repo_save
def test_int_app_config_repo_save(
        app_config_repo: AppConfigurationRepository,
    ) -> None:
    '''
    Test the save method of the AppConfigurationRepository.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    # Create constant for new test app interface.
    new_app_id = 'new.app'

    # Create new app interface config data and map to a model.
    app = DataObject.from_data(
        AppInterfaceConfigData,
        id=new_app_id,
        name='New App',
        description='A new test app interface.',
        module_path='tiferet.apps.new',
        class_name='NewApp',
        attributes={},
        constants={},
    ).map()

    # Save the new app interface.
    app_config_repo.save(app)

    # Reload the app interface to verify it was saved.
    new_app = app_config_repo.get(new_app_id)

    # Check the new app interface.
    assert new_app
    assert new_app.id == new_app_id
    assert new_app.name == 'New App'
    assert new_app.module_path == 'tiferet.apps.new'
    assert new_app.class_name == 'NewApp'

# ** test_int: app_config_repo_delete
def test_int_app_config_repo_delete(
        app_config_repo: AppConfigurationRepository,
    ) -> None:
    '''
    Test the delete method of the AppConfigurationRepository.

    :param app_config_repo: The app configuration repository.
    :type app_config_repo: AppConfigurationRepository
    '''

    # Delete an existing app interface.
    app_config_repo.delete(ANOTHER_APP_ID)

    # Attempt to get the deleted app interface.
    deleted_app = app_config_repo.get(ANOTHER_APP_ID)

    # Check that the app interface is None.
    assert not deleted_app

    # Ensure that deleting a non-existent app interface is idempotent.
    app_config_repo.delete('missing.app')
