"""Tiferet App Commands Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...models import (
    ModelObject,
    AppInterface,
    AppAttribute,
)
from ...contracts import AppService
from ..app import GetAppInterface, AddAppInterface
from ..settings import TiferetError, Command

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

# ** fixture: get_app_interface_cmd
@pytest.fixture
def get_app_interface_cmd(app_service):
    '''
    Fixture to create an instance of GetAppInterface command.
    
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :return: An instance of GetAppInterface.
    :rtype: GetAppInterface
    '''
    # Create an instance of GetAppInterface with the mock app service.
    return GetAppInterface(app_service=app_service)

# ** fixture: app_service
@pytest.fixture
def app_service(app_interface):
    '''
    Fixture to create a mock AppService instance.

    :param app_interface: The mock AppInterface instance used as the default return value.
    :type app_interface: AppInterface
    :return: A mock instance of AppService.
    :rtype: AppService
    '''

    # Create a mock AppService instance configured to return the app_interface.
    service = mock.Mock(spec=AppService)
    service.get.return_value = app_interface
    return service

# *** tests

# ** test: test_get_app_interface_not_found
def test_get_app_interface_not_found(app_service, get_app_interface_cmd):
    '''
    Test the GetAppInterface command when the app interface is not found.
    
    :param get_app_interface_cmd: The GetAppInterface command instance.
    :type get_app_interface_cmd: GetAppInterface
    '''

    # Simulate that the interface is not found.
    app_service.get.return_value = None  

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

# ** test: add_app_interface_minimal_success
def test_add_app_interface_minimal_success(app_service):
    '''
    Test creating a minimal app interface using the AddAppInterface command.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Execute the command with only required parameters via Command.handle.
    interface = Command.handle(
        AddAppInterface,
        dependencies={'app_service': app_service},
        id='test.interface',
        name='Test Interface',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )

    # Assert the result is an AppInterface instance with expected defaults.
    assert isinstance(interface, AppInterface)
    assert interface.id == 'test.interface'
    assert interface.name == 'Test Interface'
    assert interface.module_path == 'tiferet.contexts.app'
    assert interface.class_name == 'AppContext'
    assert interface.description is None
    assert interface.logger_id == 'default'
    assert interface.feature_flag == 'default'
    assert interface.data_flag == 'default'
    assert interface.attributes == []
    assert interface.constants == {}

    # Assert the interface is saved via the app service.
    app_service.save.assert_called_once_with(interface)

# ** test: add_app_interface_full_parameters
def test_add_app_interface_full_parameters(app_service):
    '''
    Test creating an app interface with all parameters populated.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    attributes = [
        {
            'attribute_id': 'test_attribute',
            'module_path': 'test_module_path',
            'class_name': 'test_class_name',
            'parameters': {'test_param': 'test_value'},
        },
    ]
    constants = {
        'TEST_CONST': 'test_const_value',
    }

    # Execute the command via Command.handle with full parameters.
    interface = Command.handle(
        AddAppInterface,
        dependencies={'app_service': app_service},
        id='test.interface',
        name='Test Interface',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        description='The test interface.',
        logger_id='custom_logger',
        feature_flag='feature_flag_value',
        data_flag='data_flag_value',
        attributes=attributes,
        constants=constants,
    )

    # Core fields.
    assert interface.id == 'test.interface'
    assert interface.name == 'Test Interface'
    assert interface.module_path == 'tiferet.contexts.app'
    assert interface.class_name == 'AppContext'
    assert interface.description == 'The test interface.'

    # Flags and logger.
    assert interface.logger_id == 'custom_logger'
    assert interface.feature_flag == 'feature_flag_value'
    assert interface.data_flag == 'data_flag_value'

    # Attributes should be materialized as AppAttribute models.
    assert len(interface.attributes) == 1
    attr = interface.attributes[0]
    assert isinstance(attr, AppAttribute)
    assert attr.attribute_id == 'test_attribute'
    assert attr.module_path == 'test_module_path'
    assert attr.class_name == 'test_class_name'
    assert attr.parameters == {'test_param': 'test_value'}

    # Constants should be preserved.
    assert interface.constants == {'TEST_CONST': 'test_const_value'}

    # Assert the interface is saved via the app service.
    app_service.save.assert_called_once_with(interface)

# ** test: add_app_interface_missing_required_fields
@pytest.mark.parametrize('missing_param', ['id', 'name', 'module_path', 'class_name'])
def test_add_app_interface_missing_required_fields(missing_param, app_service):
    '''
    Test that missing required parameters raise COMMAND_PARAMETER_REQUIRED.

    :param missing_param: The parameter name to omit.
    :type missing_param: str
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    kwargs = dict(
        id='test.interface',
        name='Test Interface',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )
    kwargs[missing_param] = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            AddAppInterface,
            dependencies={'app_service': app_service},
            **kwargs,
        )

    # Verify the error code and that the missing parameter is mentioned.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED'
    assert missing_param in str(exc_info.value)

# ** test: add_app_interface_default_fallbacks
def test_add_app_interface_default_fallbacks(app_service):
    '''
    Test that falsy logger_id, feature_flag, and data_flag values fall back to 'default'.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Execute the command with explicit falsy values for flags.
    interface = Command.handle(
        AddAppInterface,
        dependencies={'app_service': app_service},
        id='test.interface',
        name='Test Interface',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        logger_id='',
        feature_flag='',
        data_flag='',
    )

    # All flags should be normalized to 'default'.
    assert interface.logger_id == 'default'
    assert interface.feature_flag == 'default'
    assert interface.data_flag == 'default'

    # Assert the interface is saved via the app service.
    app_service.save.assert_called_once_with(interface)
