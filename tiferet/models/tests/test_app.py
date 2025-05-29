# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ...configs.app import *
from ...configs.tests.test_app import *


# *** fixtures

# ** fixture: app_settings
@pytest.fixture
def app_settings():

    return Entity.new(
        AppSettings,
        **TEST_APP_SETTINGS,
    )


# *** tests

# ** test: test_app_settings_get_dependency
def test_app_settings_get_dependency(app_settings):

    # Get the app dependency.
    app_dependency = app_settings.get_dependency('app_context')

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == DEFAULT_APP_CONTEXT_DEPENDENCY.get('attribute_id')
    assert app_dependency.module_path == DEFAULT_APP_CONTEXT_DEPENDENCY.get('module_path')
    assert app_dependency.class_name == DEFAULT_APP_CONTEXT_DEPENDENCY.get('class_name')


# ** test: test_app_settings_get_dependency_invalid
def test_app_settings_get_dependency_invalid(app_settings):

    # Assert the app dependency is invalid.
    assert app_settings.get_dependency('invalid') is None
