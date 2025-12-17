"""Tiferet App Commands Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...models import (
    ModelObject,
    AppInterface,
    AppAttribute
)
from ...contracts import AppRepository
from ..app import GetAppInterface, TiferetError

# *** fixtures

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