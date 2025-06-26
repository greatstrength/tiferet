# *** imports

# ** infra
import pytest

# ** app
from ...models.app import *


# *** fixtures

# ** fixture: app_attribute
@pytest.fixture
def app_attribute():
    '''
    Fixture for the container service attribute.
    '''

    return dict(
        attribute_id='test_attribute',
        module_path='test_module_path',
        class_name='test_class_name',
    )

# ** fixture: app_interface
@pytest.fixture
def app_interface(app_attribute):

    return Entity.new(
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

# ** test: test_app_interface_get_attribute
def test_app_interface_get_attribute(app_interface):

    # Get the app dependency.
    app_dependency = app_interface.get_attribute('test_attribute')

    # Assert the app dependency is valid.
    assert app_dependency.module_path == 'test_module_path'
    assert app_dependency.class_name == 'test_class_name'


# ** test: test_app_interface_get_attribute_invalid
def test_app_interface_get_attribute_invalid(app_interface):

    # Assert the app dependency is invalid.
    assert app_interface.get_attribute('invalid') is None