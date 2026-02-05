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
from ..app import (
    GetAppInterface,
    AddAppInterface,
    ListAppInterfaces,
    UpdateAppInterface,
    SetAppConstants,
    SetServiceDependency,
    RemoveServiceDependency,
    RemoveAppInterface,
)
from ..settings import TiferetError, Command, a

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

# ** fixture: list_app_interfaces_cmd
@pytest.fixture
def list_app_interfaces_cmd(app_service):
    '''
    Fixture to create an instance of ListAppInterfaces command.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :return: An instance of ListAppInterfaces.
    :rtype: ListAppInterfaces
    '''

    # Create an instance of ListAppInterfaces with the mock app service.
    return ListAppInterfaces(app_service=app_service)

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
    assert exc_info.value.error_code == a.const.APP_INTERFACE_NOT_FOUND_ID
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

# ** test: list_app_interfaces_empty
def test_list_app_interfaces_empty(app_service):
    '''
    Test that ListAppInterfaces returns an empty list when no interfaces are configured.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Configure the service to return an empty list.
    app_service.list.return_value = []

    # Execute the command via Command.handle.
    result = Command.handle(
        ListAppInterfaces,
        dependencies={'app_service': app_service},
    )

    # Assert that an empty list is returned and the service was called.
    assert result == []
    app_service.list.assert_called_once_with()


# ** test: set_service_dependency_creates_new_attribute
def test_set_service_dependency_creates_new_attribute(app_service, app_interface):
    '''
    Test that SetServiceDependency creates a new dependency attribute when it does not exist.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Ensure no attribute with the target id exists initially.
    assert app_interface.get_attribute('new_dependency') is None

    # Execute the command via Command.handle.
    result = Command.handle(
        SetServiceDependency,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        attribute_id='new_dependency',
        module_path='new.module.path',
        class_name='NewClass',
        parameters={'param1': 'value1'},
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # A new attribute should be created with the provided values.
    new_attr = app_interface.get_attribute('new_dependency')
    assert new_attr is not None
    assert new_attr.module_path == 'new.module.path'
    assert new_attr.class_name == 'NewClass'
    assert new_attr.parameters == {'param1': 'value1'}

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)


# ** test: set_service_dependency_updates_existing_attribute_and_merges_parameters
def test_set_service_dependency_updates_existing_attribute_and_merges_parameters(
    app_service, app_interface
):
    '''
    Test that SetServiceDependency updates an existing dependency and merges parameters.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Precondition: existing attribute from fixture.
    existing_attr = app_interface.get_attribute('test_attribute')
    existing_attr.parameters = {'keep': 'value', 'override': 'old', 'remove': 'to_be_removed'}

    # Execute the command via Command.handle with updated fields and parameters.
    result = Command.handle(
        SetServiceDependency,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        attribute_id='test_attribute',
        module_path='updated.module.path',
        class_name='UpdatedClass',
        parameters={
            'override': 'new',
            'remove': None,
            'new_param': 'new_value',
        },
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # Attribute should be updated.
    updated_attr = app_interface.get_attribute('test_attribute')
    assert updated_attr.module_path == 'updated.module.path'
    assert updated_attr.class_name == 'UpdatedClass'
    # Parameters merged: keep preserved, override updated, remove dropped, new_param added.
    assert updated_attr.parameters == {
        'keep': 'value',
        'override': 'new',
        'new_param': 'new_value',
    }

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)


# ** test: set_service_dependency_parameters_none_clears_existing
def test_set_service_dependency_parameters_none_clears_existing(app_service, app_interface):
    '''
    Test that passing parameters=None clears existing parameters on the attribute.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Precondition: existing attribute has parameters.
    existing_attr = app_interface.get_attribute('test_attribute')
    existing_attr.parameters = {'key': 'value'}

    # Execute the command with parameters set to None.
    result = Command.handle(
        SetServiceDependency,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        attribute_id='test_attribute',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        parameters=None,
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # Parameters should be cleared.
    cleared_attr = app_interface.get_attribute('test_attribute')
    assert cleared_attr.parameters == {}

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)


# ** test: set_service_dependency_missing_required_parameters
@pytest.mark.parametrize('missing_param', ['id', 'attribute_id', 'module_path', 'class_name'])
def test_set_service_dependency_missing_required_parameters(missing_param, app_service):
    '''
    Test that missing required parameters raise COMMAND_PARAMETER_REQUIRED.

    :param missing_param: The parameter name to omit.
    :type missing_param: str
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    kwargs = dict(
        id='test.interface',
        attribute_id='dep',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )
    kwargs[missing_param] = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            SetServiceDependency,
            dependencies={'app_service': app_service},
            **kwargs,
        )

    # Verify the error code and that the missing parameter is mentioned.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert missing_param in str(exc_info.value)


# ** test: set_service_dependency_interface_not_found
def test_set_service_dependency_interface_not_found(app_service):
    '''
    Test that SetServiceDependency raises APP_INTERFACE_NOT_FOUND when the interface does not exist.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Simulate missing interface.
    app_service.get.return_value = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            SetServiceDependency,
            dependencies={'app_service': app_service},
            id='missing.interface',
            attribute_id='dep',
            module_path='tiferet.contexts.app',
            class_name='AppContext',
        )

    # Verify error code and message.
    assert exc_info.value.error_code == a.const.APP_INTERFACE_NOT_FOUND_ID
    assert 'App interface with ID missing.interface not found.' in str(exc_info.value)

# ** test: list_app_interfaces_multiple
def test_list_app_interfaces_multiple(app_service, app_interface):
    '''
    Test that ListAppInterfaces returns multiple interfaces when configured.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The mock AppInterface instance.
    :type app_interface: AppInterface
    '''

    # Configure the service to return multiple interfaces.
    another_interface = ModelObject.new(
        AppInterface,
        id='other',
        name='Other App',
        module_path='tiferet.contexts.app',
        class_name='OtherAppContext',
    )
    app_service.list.return_value = [app_interface, another_interface]

    # Execute the command via Command.handle.
    result = Command.handle(
        ListAppInterfaces,
        dependencies={'app_service': app_service},
    )

    # Assert that the returned list matches the configured interfaces.
    assert result == [app_interface, another_interface]
    app_service.list.assert_called_once_with()

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
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
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

# ** test: update_app_interface_success_supported_attributes
@pytest.mark.parametrize(
    'attribute,new_value',
    [
        ('name', 'Updated Name'),
        ('description', 'Updated description'),
        ('module_path', 'updated.module.path'),
        ('class_name', 'UpdatedClass'),
        ('logger_id', 'updated_logger'),
        ('feature_flag', 'updated_feature_flag'),
        ('data_flag', 'updated_data_flag'),
    ],
)

def test_update_app_interface_success_supported_attributes(
    app_service, app_interface, attribute, new_value
):
    '''
    Test updating each supported scalar attribute via UpdateAppInterface.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        UpdateAppInterface,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        attribute=attribute,
        value=new_value,
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # The attribute on the interface should be updated.
    assert getattr(app_interface, attribute) == new_value

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)

# ** test: update_app_interface_missing_required_parameters
@pytest.mark.parametrize('missing_param', ['id', 'attribute'])
def test_update_app_interface_missing_required_parameters(missing_param, app_service):
    '''
    Test that missing required parameters raise COMMAND_PARAMETER_REQUIRED.

    :param missing_param: The parameter name to omit.
    :type missing_param: str
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    kwargs = dict(
        id='test.interface',
        attribute='name',
        value='Updated Name',
    )
    kwargs[missing_param] = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            UpdateAppInterface,
            dependencies={'app_service': app_service},
            **kwargs,
        )

    # Verify the error code and that the missing parameter is mentioned.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert missing_param in str(exc_info.value)

# ** test: update_app_interface_interface_not_found
def test_update_app_interface_interface_not_found(app_service):
    '''
    Test that UpdateAppInterface raises APP_INTERFACE_NOT_FOUND when the interface does not exist.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Simulate missing interface.
    app_service.get.return_value = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            UpdateAppInterface,
            dependencies={'app_service': app_service},
            id='missing.interface',
            attribute='name',
            value='Updated Name',
        )

    # Verify error code and message.
    assert exc_info.value.error_code == a.const.APP_INTERFACE_NOT_FOUND_ID
    assert 'App interface with ID missing.interface not found.' in str(exc_info.value)

# ** test: update_app_interface_invalid_attribute_raises_model_error
def test_update_app_interface_invalid_attribute_raises_model_error(
    app_service, app_interface
):
    '''
    Test that an invalid attribute name is validated by the AppInterface model.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Execute the command with an unsupported attribute name.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            UpdateAppInterface,
            dependencies={'app_service': app_service},
            id=app_interface.id,
            attribute='invalid_attribute',
            value='value',
        )

    # The underlying model validation should raise INVALID_MODEL_ATTRIBUTE.
    assert exc_info.value.error_code == a.const.INVALID_MODEL_ATTRIBUTE_ID
    app_service.save.assert_not_called()

# ** test: update_app_interface_invalid_type_attributes_empty_value
@pytest.mark.parametrize('attribute', ['module_path', 'class_name'])
def test_update_app_interface_invalid_type_attributes_empty_value(
    attribute, app_service, app_interface
):
    '''
    Test that empty values for module_path or class_name are rejected by the model.

    :param attribute: The attribute name under test.
    :type attribute: str
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Execute the command with an empty value for a type-constrained attribute.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            UpdateAppInterface,
            dependencies={'app_service': app_service},
            id=app_interface.id,
            attribute=attribute,
            value='',
        )

    # The underlying model validation should raise INVALID_APP_INTERFACE_TYPE.
    assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
    app_service.save.assert_not_called()

# ** test: set_app_constants_full_clear
def test_set_app_constants_full_clear(app_service, app_interface):
    '''
    Test that SetAppConstants clears all constants when constants=None.
    '''

    # Seed existing constants on the interface.
    app_interface.constants = {
        'EXISTING': 'value',
        'OTHER': 'other_value',
    }

    # Execute the command via Command.handle with constants=None.
    result = Command.handle(
        SetAppConstants,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        constants=None,
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # All constants should be cleared.
    assert app_interface.constants == {}

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)

# ** test: set_app_constants_merge_override_and_remove
def test_set_app_constants_merge_override_and_remove(app_service, app_interface):
    '''
    Test that SetAppConstants merges constants, overrides values, and removes None-valued keys.
    '''

    # Seed existing constants.
    app_interface.constants = {
        'KEEP': 'keep_value',
        'OVERRIDE': 'old',
        'REMOVE': 'to_be_removed',
    }

    # Execute the command with mixed updates.
    result = Command.handle(
        SetAppConstants,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        constants={
            'OVERRIDE': 'new',
            'REMOVE': None,
            'ADD': 'added',
        },
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # Constants should be merged/updated with None-valued keys removed.
    assert app_interface.constants == {
        'KEEP': 'keep_value',
        'OVERRIDE': 'new',
        'ADD': 'added',
    }

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)

# ** test: set_app_constants_add_new_constants
def test_set_app_constants_add_new_constants(app_service, app_interface):
    '''
    Test that SetAppConstants adds new constants when none exist.
    '''

    # Precondition: no constants defined.
    assert app_interface.constants == {}

    # Execute the command with new constants.
    result = Command.handle(
        SetAppConstants,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        constants={
            'NEW_ONE': 'one',
            'NEW_TWO': 'two',
        },
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # All new constants should be present.
    assert app_interface.constants == {
        'NEW_ONE': 'one',
        'NEW_TWO': 'two',
    }

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)

# ** test: set_app_constants_missing_or_empty_id
@pytest.mark.parametrize('invalid_id', [None, ''])
def test_set_app_constants_missing_or_empty_id(invalid_id, app_service):
    '''
    Test that missing or empty id raises COMMAND_PARAMETER_REQUIRED.
    '''

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            SetAppConstants,
            dependencies={'app_service': app_service},
            id=invalid_id,
            constants={'KEY': 'VALUE'},
        )

    # Verify the error code and that the id parameter is mentioned.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert 'id' in str(exc_info.value)
    app_service.save.assert_not_called()

# ** test: set_app_constants_interface_not_found
def test_set_app_constants_interface_not_found(app_service):
    '''
    Test that SetAppConstants raises APP_INTERFACE_NOT_FOUND when the interface does not exist.
    '''

    # Simulate missing interface.
    app_service.get.return_value = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            SetAppConstants,
            dependencies={'app_service': app_service},
            id='missing.interface',
            constants={'KEY': 'VALUE'},
        )

    # Verify error code and message.
    assert exc_info.value.error_code == a.const.APP_INTERFACE_NOT_FOUND_ID
    assert 'App interface with ID missing.interface not found.' in str(exc_info.value)

# ** test: remove_service_dependency_removes_existing_attribute
def test_remove_service_dependency_removes_existing_attribute(app_service, app_interface):
    '''
    Test that RemoveServiceDependency removes an existing dependency attribute.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Precondition: the attribute exists on the interface.
    existing_attr = app_interface.get_attribute('test_attribute')
    assert existing_attr is not None
    initial_count = len(app_interface.attributes)

    # Execute the command via Command.handle.
    result = Command.handle(
        RemoveServiceDependency,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        attribute_id='test_attribute',
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # The attribute should be removed and the list size decreased by one.
    assert app_interface.get_attribute('test_attribute') is None
    assert len(app_interface.attributes) == initial_count - 1

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)

# ** test: remove_service_dependency_missing_attribute_is_idempotent
def test_remove_service_dependency_missing_attribute_is_idempotent(app_service, app_interface):
    '''
    Test that removing a non-existent dependency attribute is idempotent and succeeds.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    :param app_interface: The AppInterface instance returned by the service.
    :type app_interface: AppInterface
    '''

    # Precondition: no attribute with the given id exists.
    assert app_interface.get_attribute('missing_attribute') is None
    initial_count = len(app_interface.attributes)

    # Execute the command via Command.handle.
    result = Command.handle(
        RemoveServiceDependency,
        dependencies={'app_service': app_service},
        id=app_interface.id,
        attribute_id='missing_attribute',
    )

    # Command should return the interface id.
    assert result == app_interface.id

    # Attributes list should remain unchanged and still not contain the attribute.
    assert app_interface.get_attribute('missing_attribute') is None
    assert len(app_interface.attributes) == initial_count

    # The updated interface should be saved.
    app_service.save.assert_called_once_with(app_interface)

# ** test: remove_service_dependency_interface_not_found
def test_remove_service_dependency_interface_not_found(app_service):
    '''
    Test that RemoveServiceDependency raises APP_INTERFACE_NOT_FOUND when the interface does not exist.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Simulate missing interface.
    app_service.get.return_value = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            RemoveServiceDependency,
            dependencies={'app_service': app_service},
            id='missing.interface',
            attribute_id='dep',
        )

    # Verify error code and message.
    assert exc_info.value.error_code == a.const.APP_INTERFACE_NOT_FOUND_ID
    assert 'App interface with ID missing.interface not found.' in str(exc_info.value)


# ** test: remove_service_dependency_missing_required_parameters
@pytest.mark.parametrize('missing_param', ['id', 'attribute_id'])
def test_remove_service_dependency_missing_required_parameters(missing_param, app_service):
    '''
    Test that missing required parameters raise COMMAND_PARAMETER_REQUIRED.

    :param missing_param: The parameter name to omit.
    :type missing_param: str
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    kwargs = dict(
        id='test.interface',
        attribute_id='dep',
    )
    kwargs[missing_param] = None

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            RemoveServiceDependency,
            dependencies={'app_service': app_service},
            **kwargs,
        )

    # Verify the error code and that the missing parameter is mentioned.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert missing_param in str(exc_info.value)

# ** test: remove_app_interface_success_existing
def test_remove_app_interface_success_existing(app_service):
    '''
    Test that RemoveAppInterface deletes an existing app interface and returns the ID.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Execute the command via Command.handle for an existing interface.
    result = Command.handle(
        RemoveAppInterface,
        dependencies={'app_service': app_service},
        id='existing.interface',
    )

    # Command should return the interface id and delegate deletion to the service.
    assert result == 'existing.interface'
    app_service.delete.assert_called_once_with('existing.interface')

# ** test: remove_app_interface_success_missing_is_idempotent
def test_remove_app_interface_success_missing_is_idempotent(app_service):
    '''
    Test that removing a non-existent interface is idempotent and still succeeds.

    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Execute the command via Command.handle for a missing interface.
    result = Command.handle(
        RemoveAppInterface,
        dependencies={'app_service': app_service},
        id='missing.interface',
    )

    # Command should return the interface id and still call delete exactly once.
    assert result == 'missing.interface'
    app_service.delete.assert_called_once_with('missing.interface')

# ** test: remove_app_interface_missing_or_empty_id
@pytest.mark.parametrize('invalid_id', [None, ''])
def test_remove_app_interface_missing_or_empty_id(invalid_id, app_service):
    '''
    Test that missing or empty id raises COMMAND_PARAMETER_REQUIRED.

    :param invalid_id: The invalid id value to use.
    :type invalid_id: str | None
    :param app_service: The mock AppService instance.
    :type app_service: AppService
    '''

    # Execute the command and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            RemoveAppInterface,
            dependencies={'app_service': app_service},
            id=invalid_id,
        )

    # Verify the error code and that the id parameter is mentioned.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert 'id' in str(exc_info.value)
    app_service.delete.assert_not_called()
