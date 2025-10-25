"""Tiferet App Commands Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...configs import TiferetError
from ...models import (
    ModelObject,
    AppInterface,
    AppAttribute
)
from ...contracts import AppRepository
from ..app import ImportAppRepository, GetAppInterface

# *** fixtures

# ** fixture: import_app_repo_cmd
@pytest.fixture
def import_app_repo_cmd():
    '''
    Fixture to create an instance of ImportAppRepository command.
    
    :return: An instance of ImportAppRepository.
    :rtype: ImportAppRepository
    '''
    return ImportAppRepository()


# ** app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create a mock AppInterface instance.
    
    :return: A mock instance of AppInterface.
    :rtype: AppInterface
    '''
    # Create a test AppInterface instance.
    return ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        description='The test app.',
        feature_flag='test',
        data_flag='test',
        attributes=[
            ModelObject.new(
                AppAttribute,
                attribute_id='test_attribute',
                module_path='test_module_path',
                class_name='test_class_name',
            ),
        ],
    )

# ** fixture: app_repo
@pytest.fixture
def app_repo(app_interface):
    '''
    Fixture to create a mock AppRepository instance.
    
    :return: A mock instance of AppRepository.
    :rtype: AppRepository
    '''

    # Create a mock AppRepository instance.
    app_repo = mock.Mock(spec=AppRepository)
    app_repo.config_file = 'tiferet/configs/test.yml'
    app_repo.get_interface.return_value = app_interface
    return app_repo

# ** fixture: get_app_interface_cmd
@pytest.fixture
def get_app_interface_cmd(app_repo):
    '''
    Fixture to create an instance of GetAppInterface command.
    
    :param app_repo: The mock AppRepository instance.
    :type app_repo: AppRepository
    :return: An instance of GetAppInterface.
    :rtype: GetAppInterface
    '''
    # Create an instance of GetAppInterface with the mock app repository.
    return GetAppInterface(app_repo=app_repo)

# *** tests

# ** test: test_import_app_repo_import_failed
def test_import_app_repo_import_failed(import_app_repo_cmd):
    '''
    Test the ImportAppRepository command when the import fails.
    
    :param import_app_repo_cmd: The ImportAppRepository command instance.
    :type import_app_repo_cmd: ImportAppRepository
    '''

    # Attempt to execute the command with an invalid module path.
    with pytest.raises(TiferetError) as exc_info:
        import_app_repo_cmd.execute(
            app_repo_module_path='invalid.module.path',
            app_repo_class_name='InvalidClassName'
        )
    
    # Assert that the error message contains the expected text.
    assert exc_info.value.error_code == 'APP_REPOSITORY_IMPORT_FAILED'
    assert 'Failed to import app repository' in str(exc_info.value)

# ** test: test_import_app_repo_success
def test_import_app_repo_success(import_app_repo_cmd):
    '''
    Test the ImportAppRepository command when the import is successful.
    
    :param import_app_repo_cmd: The ImportAppRepository command instance.
    :type import_app_repo_cmd: ImportAppRepository
    '''

    # Execute the command with valid parameters.
    app_repo = import_app_repo_cmd.execute(
        app_repo_module_path='tiferet.proxies.yaml.app',
        app_repo_class_name='AppYamlProxy',
        app_repo_params=dict(
            app_config_file='tiferet/configs/test.yml',
        )
    )

    # Assert that the returned instance is of type AppRepository.
    assert isinstance(app_repo, AppRepository), 'Should return an instance of AppRepository'

    # Assert that the app_config_file attribute is set correctly.
    assert hasattr(app_repo, 'config_file'), 'AppRepository should have app_config_file attribute'
    config_file = getattr(app_repo, 'config_file', None)
    assert config_file == 'tiferet/configs/test.yml', 'AppRepository should have the correct config file'

# ** test: test_get_app_interface_not_found
def test_get_app_interface_not_found(app_repo, get_app_interface_cmd):
    '''
    Test the GetAppInterface command when the app interface is not found.
    
    :param get_app_interface_cmd: The GetAppInterface command instance.
    :type get_app_interface_cmd: GetAppInterface
    '''

    app_repo.get_interface.return_value = None  # Simulate that the interface is not found.

    # Attempt to get an app interface that does not exist.
    with pytest.raises(TiferetError) as exc_info:
        get_app_interface_cmd.execute(interface_id='non_existent_id')
    
    # Assert that the error message contains the expected text.
    assert exc_info.value.error_code == 'APP_INTERFACE_NOT_FOUND'
    assert 'App interface with ID non_existent_id not found.' in str(exc_info.value)

# ** test: test_get_app_interface_success
def test_get_app_interface_success(get_app_interface_cmd, app_interface):
    '''
    Test the GetAppInterface command when the app interface is found.
    
    :param get_app_interface_cmd: The GetAppInterface command instance.
    :type get_app_interface_cmd: GetAppInterface
    :param app_interface: The mock AppInterface instance.
    :type app_interface: AppInterface
    '''

    # Execute the command to get the app interface.
    result = get_app_interface_cmd.execute(interface_id='test')

    # Assert that the returned interface matches the expected app interface.
    assert result == app_interface, 'Should return the correct AppInterface instance'