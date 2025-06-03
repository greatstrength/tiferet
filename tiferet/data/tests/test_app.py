# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ...configs.tests.test_app import *


# *** fixtures

# ** fixture: app_settings_yaml_data
@pytest.fixture
def app_settings_yaml_data():

    return DataObject.from_data(
        AppSettingsYamlData,
        **TEST_APP_SETTINGS_YAML_DATA,
    )


# *** tests

# ** test: test_app_settings_yaml_data_map
def test_app_settings_yaml_data_map(app_settings_yaml_data):

    # Map the app interface yaml data to an app interface object.
    app_settings = app_settings_yaml_data.map()

    # Assert the mapped app interface is valid.
    assert isinstance(app_settings, AppSettings)
    assert app_settings.id == app_settings_yaml_data.id
    assert app_settings.name == app_settings_yaml_data.name
    assert app_settings.data_flag == app_settings_yaml_data.data_flag

    # Assert the mapped app interface has the correct dependencies.
    assert len(app_settings.dependencies) == 2
    dep = next(dep for dep in app_settings.dependencies if dep.attribute_id == 'app_context')
    assert isinstance(dep, AppDependency)
    assert dep.module_path == app_settings_yaml_data.app_context.module_path
    assert dep.class_name == app_settings_yaml_data.app_context.class_name

    # Assert that the mapped app dependency contains the correct parameters.
    dep = next(dep for dep in app_settings.dependencies if dep.attribute_id == 'container_service')
    assert isinstance(dep, AppDependency)
    for param in dep.parameters:
        assert param in ['container_id', 'container_name']

    # Assert that the constants are correctly set.
    assert app_settings.constants
    assert app_settings.constants['test_const'] == '123'

