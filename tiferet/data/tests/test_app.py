# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ...configs.tests.test_app import *


# *** fixtures

# ** fixture: app_interface_yaml_data
@pytest.fixture
def app_interface_yaml_data():

    return DataObject.from_data(
        AppInterfaceYamlData,
        **TEST_APP_INTERFACE_YAML_DATA,
    )


# *** tests

# ** test: test_app_interface_yaml_data_map
def test_app_interface_yaml_data_map(app_interface_yaml_data):

    # Map the app interface yaml data to an app interface object.
    mapped_interface = app_interface_yaml_data.map()

    # Assert the mapped app interface is valid.
    assert isinstance(mapped_interface, AppInterface)
    assert mapped_interface.id == app_interface_yaml_data.id
    assert mapped_interface.name == app_interface_yaml_data.name
    assert mapped_interface.data_flag == app_interface_yaml_data.data_flag

    # Assert the mapped app interface has the correct dependencies.
    assert len(mapped_interface.dependencies) == 1
    dep = mapped_interface.dependencies[0]
    assert isinstance(dep, AppDependency)
    assert dep.module_path == app_interface_yaml_data.app_context.module_path
    assert dep.class_name == app_interface_yaml_data.app_context.class_name

