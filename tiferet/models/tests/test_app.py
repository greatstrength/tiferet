# *** imports

# ** infra
import pytest

# ** app
from ..app import *


# *** fixtures

# ** fixture: container_service_attribute
@pytest.fixture
def container_service_attribute():
    '''
    Fixture for the container service attribute.
    '''

    return dict(
        attribute_id='container_service',
        module_path='tiferet.handlers.container',
        class_name='DependencyHandler',
    )

# ** fixture: app_settings
@pytest.fixture
def app_settings(container_service_attribute):

    return Entity.new(
        AppSettings,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        description='The test app.',
        feature_flag='test',
        data_flag='test',
        attributes=[
            container_service_attribute,
        ],
    )


# *** tests

# ** test: test_app_settings_get_attribute
def test_app_settings_get_attribute(app_settings):

    # Get the app dependency.
    app_dependency = app_settings.get_attribute('container_service')

    # Assert the app dependency is valid.
    assert app_dependency.module_path == 'tiferet.handlers.container'
    assert app_dependency.class_name == 'DependencyHandler'


# ** test: test_app_settings_get_attribute_invalid
def test_app_settings_get_attribute_invalid(app_settings):

    # Assert the app dependency is invalid.
    assert app_settings.get_attribute('invalid') is None
