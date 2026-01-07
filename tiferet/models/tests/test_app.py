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
from ...commands.settings import const

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
        parameters={
            'param1': 'value1',
            'param2': 'value2',
        },
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
    assert app_dependency.attribute_id == 'test_attribute'
    assert app_dependency.parameters
    assert app_dependency.parameters['param1'] == 'value1'
    assert app_dependency.parameters['param2'] == 'value2'

# ** test: app_interface_get_attribute_invalid
def test_app_interface_get_attribute_invalid(app_interface: AppInterface):
    '''
    Test the get_attribute method of the app interface with an invalid attribute ID.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Assert the app dependency is invalid.
    assert app_interface.get_attribute('invalid') is None

def test_app_interface_add_attribute(app_interface):

    # Add a new attribute.
    app_interface.add_attribute(
        module_path='new_module_path',
        class_name='NewClassName',
        attribute_id='new_attribute',
        parameters={
            'new_param1': 'new_value1',
            'new_param2': 'new_value2',
        },
    )

    # Get the new attribute.
    new_attribute = app_interface.get_attribute('new_attribute')

    # Assert the new attribute is valid.
    assert new_attribute is not None
    assert new_attribute.module_path == 'new_module_path'
    assert new_attribute.class_name == 'NewClassName'
    assert new_attribute.attribute_id == 'new_attribute'
    assert new_attribute.parameters
    assert new_attribute.parameters['new_param1'] == 'new_value1'
    assert new_attribute.parameters['new_param2'] == 'new_value2'

# ** test: app_interface_set_attribute_valid
def test_app_interface_set_attribute_valid(app_interface: AppInterface):
    '''
    Test that set_attribute successfully updates supported scalar attributes and validates the model.
    '''

    # Update the name attribute.
    app_interface.set_attribute('name', 'Updated App Name')
    assert app_interface.name == 'Updated App Name'

    # Update the description attribute.
    app_interface.set_attribute('description', 'Updated description')
    assert app_interface.description == 'Updated description'

    # Update logger_id and flags.
    app_interface.set_attribute('logger_id', 'custom_logger')
    app_interface.set_attribute('feature_flag', 'custom_feature')
    app_interface.set_attribute('data_flag', 'custom_data')

    assert app_interface.logger_id == 'custom_logger'
    assert app_interface.feature_flag == 'custom_feature'
    assert app_interface.data_flag == 'custom_data'

# ** test: app_interface_set_attribute_invalid_name
def test_app_interface_set_attribute_invalid_name(app_interface: AppInterface):
    '''
    Test that set_attribute rejects unsupported attribute names.
    '''

    from ...assets import TiferetError

    with pytest.raises(TiferetError) as excinfo:
        app_interface.set_attribute('invalid_attr', 'value')

    error = excinfo.value
    assert error.error_code == const.INVALID_MODEL_ATTRIBUTE_ID
    assert error.kwargs.get('attribute') == 'invalid_attr'

# ** test: app_interface_set_attribute_empty_module_or_class
def test_app_interface_set_attribute_empty_module_or_class(app_interface: AppInterface):
    '''
    Test that set_attribute rejects empty values for module_path and class_name.
    '''

    from ...assets import TiferetError

    # Empty module_path.
    with pytest.raises(TiferetError) as excinfo_module:
        app_interface.set_attribute('module_path', ' ')

    assert excinfo_module.value.error_code == const.INVALID_APP_INTERFACE_TYPE_ID

    # Empty class_name.
    with pytest.raises(TiferetError) as excinfo_class:
        app_interface.set_attribute('class_name', '')

    assert excinfo_class.value.error_code == const.INVALID_APP_INTERFACE_TYPE_ID
