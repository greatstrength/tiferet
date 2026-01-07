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
from ...contracts import AppService
from ..app import GetAppInterface, AddAppInterface
from ..settings import TiferetError, Command
from ...assets.constants import COMMAND_PARAMETER_REQUIRED_ID

# *** fixtures

# ** fixture: mock_app_service
@pytest.fixture
def mock_app_service() -> AppService:
    '''
    Fixture to provide a mock AppService instance.
    '''

    service = mock.Mock(spec=AppService)
    return service

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


# *** tests

# ** test: add_app_interface_success
def test_add_app_interface_success(mock_app_service: AppService):
    '''
    Ensure AddAppInterface creates and saves a new AppInterface.
    '''

    result: AppInterface = Command.handle(
        AddAppInterface,
        dependencies={'app_service': mock_app_service},
        id='test.app',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        description='A test app interface.',
        logger_id='test_logger',
        feature_flag='test_feature',
        data_flag='test_data',
        attributes=[
            {
                'attribute_id': 'attr1',
                'module_path': 'test.module',
                'class_name': 'TestClass',
                'parameters': {'foo': 'bar'},
            }
        ],
        constants={'CONST_KEY': 'VALUE'},
    )

    assert isinstance(result, AppInterface)
    assert result.id == 'test.app'
    assert result.name == 'Test App'
    assert result.module_path == 'tiferet.contexts.app'
    assert result.class_name == 'AppInterfaceContext'
    assert result.description == 'A test app interface.'
    assert result.logger_id == 'test_logger'
    assert result.feature_flag == 'test_feature'
    assert result.data_flag == 'test_data'
    assert len(result.attributes) == 1
    attr = result.attributes[0]
    assert attr.attribute_id == 'attr1'
    assert attr.module_path == 'test.module'
    assert attr.class_name == 'TestClass'
    assert attr.parameters == {'foo': 'bar'}
    assert result.constants == {'CONST_KEY': 'VALUE'}

    # Ensure the app service was called with the new interface.
    mock_app_service.save.assert_called_once()
    saved_interface = mock_app_service.save.call_args[0][0]
    assert isinstance(saved_interface, AppInterface)
    assert saved_interface.id == 'test.app'

# ** test: add_app_interface_defaults
def test_add_app_interface_defaults(mock_app_service: AppService):
    '''
    Ensure AddAppInterface applies default flags and empty attributes/constants.
    '''

    result: AppInterface = Command.handle(
        AddAppInterface,
        dependencies={'app_service': mock_app_service},
        id='test.app',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
    )

    assert result.feature_flag == 'default'
    assert result.data_flag == 'default'
    assert result.attributes == []
    assert result.constants == {}

    mock_app_service.save.assert_called_once()


# ** test: add_app_interface_missing_required_field
def test_add_app_interface_missing_required_field(mock_app_service: AppService):
    '''
    Ensure AddAppInterface validates required parameters.
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddAppInterface,
            dependencies={'app_service': mock_app_service},
            id=' ',  # invalid
            name='Test App',
            module_path='tiferet.contexts.app',
            class_name='AppInterfaceContext',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_app_service.save.assert_not_called()

# ** test: test_get_app_interface_not_found
def test_get_app_interface_not_found(mock_app_service: AppService):
    '''
    Test the GetAppInterface command when the app interface is not found.
    
    :param get_app_interface_cmd: The GetAppInterface command instance.
    :type get_app_interface_cmd: GetAppInterface
    '''

    mock_app_service.get.return_value = None  # Simulate that the interface is not found.

    # Attempt to get an app interface that does not exist.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            GetAppInterface,
            dependencies={'app_service': mock_app_service},
            interface_id='non_existent_id',
        )
    
    # Assert that the error message contains the expected text.
    assert exc_info.value.error_code == 'APP_INTERFACE_NOT_FOUND'
    assert 'App interface with ID non_existent_id not found.' in str(exc_info.value)

# ** test: test_get_app_interface_success
def test_get_app_interface_success(mock_app_service: AppService, app_interface: AppInterface):
    '''
    Test the GetAppInterface command when the app interface is found.
    
    :param get_app_interface_cmd: The GetAppInterface command instance.
    :type get_app_interface_cmd: GetAppInterface
    :param app_interface: The mock AppInterface instance.
    :type app_interface: AppInterface
    '''

    mock_app_service.get.return_value = app_interface

    # Execute the command to get the app interface via Command.handle.
    result = Command.handle(
        GetAppInterface,
        dependencies={'app_service': mock_app_service},
        interface_id='test',
    )

    # Assert that the returned interface matches the expected app interface.
    assert result == app_interface, 'Should return the correct AppInterface instance'