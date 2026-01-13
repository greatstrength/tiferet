"""Tiferet App Model Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...models import (
    ModelObject,
    AppAttribute,
    AppInterface,
)
from ...commands.static import TiferetError

# *** fixtures

# ** fixture: app_attribute
@pytest.fixture
def app_attribute() -> AppAttribute:
    '''
    Fixture for the container service attribute.

    :return: The container service attribute.
    :rtype: AppAttribute
    '''

    # Create a container service attribute.
    return ModelObject.new(
        AppAttribute,
        attribute_id='test_attribute',
        module_path='test_module_path',
        class_name='test_class_name',
    )

# ** fixture: app_interface
@pytest.fixture
def app_interface(app_attribute: AppAttribute) -> AppInterface:
    '''
    Fixture for the app interface.

    :param app_attribute: The app attribute to include in the app interface.
    :type app_attribute: AppAttribute
    :return: The app interface.
    :rtype: AppInterface
    '''

    # Create the app interface.
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
            app_attribute,
        ],
    )

# *** tests

# ** test: app_interface_get_attribute
def test_app_interface_get_attribute(app_interface: AppInterface):
    '''
    Test the get_attribute method of the app interface.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Get the app dependency.
    app_dependency = app_interface.get_attribute('test_attribute')

    # Assert the app dependency is valid.
    assert app_dependency.module_path == 'test_module_path'
    assert app_dependency.class_name == 'test_class_name'

# ** test: app_interface_get_attribute_invalid
def test_app_interface_get_attribute_invalid(app_interface: AppInterface):
    '''
    Test the get_attribute method of the app interface with an invalid attribute ID.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Assert the app dependency is invalid.
    assert app_interface.get_attribute('invalid') is None

# ** test: app_interface_set_attribute_valid_updates
def test_app_interface_set_attribute_valid_updates(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute successfully updates supported attributes and validates the model.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Update multiple supported attributes.
    app_interface.set_attribute('name', 'Updated App')
    app_interface.set_attribute('description', 'Updated description')
    app_interface.set_attribute('logger_id', 'updated_logger')
    app_interface.set_attribute('feature_flag', 'updated_feature')
    app_interface.set_attribute('data_flag', 'updated_data')

    # Assert that the attributes were updated.
    assert app_interface.name == 'Updated App'
    assert app_interface.description == 'Updated description'
    assert app_interface.logger_id == 'updated_logger'
    assert app_interface.feature_flag == 'updated_feature'
    assert app_interface.data_flag == 'updated_data'


# ** test: app_interface_set_attribute_invalid_name
def test_app_interface_set_attribute_invalid_name(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute rejects an unsupported attribute name.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Attempt to update an unsupported attribute and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface.set_attribute('invalid_attribute', 'value')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'
    assert exc_info.value.kwargs.get('attribute') == 'invalid_attribute'


# ** test: app_interface_set_attribute_invalid_module_path
def test_app_interface_set_attribute_invalid_module_path(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute enforces non-empty string for module_path.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Attempt to set an empty module_path and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface.set_attribute('module_path', '')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_APP_INTERFACE_TYPE'
    assert exc_info.value.kwargs.get('attribute') == 'module_path'


# ** test: app_interface_set_attribute_invalid_class_name
def test_app_interface_set_attribute_invalid_class_name(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute enforces non-empty string for class_name.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Attempt to set an empty class_name and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface.set_attribute('class_name', '   ')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_APP_INTERFACE_TYPE'
    assert exc_info.value.kwargs.get('attribute') == 'class_name'


# ** test: app_interface_set_attribute_uses_validate
def test_app_interface_set_attribute_uses_validate(app_interface: AppInterface, monkeypatch) -> None:
    '''
    Test that set_attribute calls validate after updating the attribute.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: Any
    '''

    called = {'value': False}

    def fake_validate() -> None:
        called['value'] = True

    # Patch validate to track calls.
    monkeypatch.setattr(app_interface, 'validate', fake_validate)

    # Perform an update.
    app_interface.set_attribute('name', 'Validated App')

    # Ensure validate was called.
    assert called['value'] is True
