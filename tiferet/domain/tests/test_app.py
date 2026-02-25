"""Tiferet App Model Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..app import (
    DomainObject,
    AppAttribute,
    AppInterface,
)

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
    return DomainObject.new(
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
    return DomainObject.new(
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

