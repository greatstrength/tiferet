# *** imports

# ** infra
import pytest

# ** app
from ..app import *


# *** fixtures

# ** fixture: app_dependency_yaml_data
@pytest.fixture
def app_dependency_yaml_data():
    return DataObject.from_data(
        AppDependencyYamlData,
        attribute_id='test_attr',
        module_path='tests.repos.test',
        class_name='TestProxy'
    )


# ** fixture: app_interface_yaml_data_raw
@pytest.fixture
def app_interface_yaml_data_raw():
    return dict(
        id='test_interface',
        name='Test Interface',
        data_flag='test_flag',
        app_context=dict(
            module_path='tests.contexts.test',
            class_name='TestContext'
        )
    )


# ** fixture: app_interface_yaml_data_raw_with_constants
@pytest.fixture
def app_interface_yaml_data_raw_with_constants():
    return dict(
        id='test_interface',
        name='Test Interface',
        data_flag='test_flag',
        app_context=dict(
            module_path='tests.contexts.test',
            class_name='TestContext'
        ),
        constants=dict(
            container_config_file='app/configs/container_2.yml',
        )
    )


# ** fixture: app_interface_yaml_data
@pytest.fixture
def app_interface_yaml_data():
    return AppInterfaceYamlData.from_data(
        id='test_interface',
        name='Test Interface',
        data_flag='test_flag',
        app_context=dict(
            module_path='tests.contexts.test',
            class_name='TestContext'
        )
    )


# *** tests

# ** test: test_app_interface_yaml_data_from_data
def test_app_interface_yaml_data_from_data(app_interface_yaml_data_raw):

    # Convert the raw data to an app interface yaml data object.
    app_interface_yaml_data = AppInterfaceYamlData.from_data(**app_interface_yaml_data_raw)
    
    # Assert the app interface yaml data is valid.
    assert app_interface_yaml_data.id == 'test_interface'
    assert app_interface_yaml_data.name == 'Test Interface'
    assert app_interface_yaml_data.data_flag == 'test_flag'
    assert len(app_interface_yaml_data.dependencies) == 7
    assert app_interface_yaml_data.constants == CONSTANTS_DEFAULT


# ** test: test_app_interface_yaml_data_from_data_with_constants
def test_app_interface_yaml_data_from_data_with_constants(app_interface_yaml_data_raw_with_constants):

    # Convert the raw data to an app interface yaml data object.
    app_interface_yaml_data = AppInterfaceYamlData.from_data(**app_interface_yaml_data_raw_with_constants)
    
    # Assert the app interface yaml data is valid.
    assert app_interface_yaml_data.id == 'test_interface'
    assert app_interface_yaml_data.name == 'Test Interface'
    assert app_interface_yaml_data.data_flag == 'test_flag'
    assert len(app_interface_yaml_data.dependencies) == 7
    assert len(app_interface_yaml_data.constants) == 3
    assert app_interface_yaml_data.constants.get('container_config_file') == 'app/configs/container_2.yml'


# ** test: test_app_interface_yaml_data_map
def test_app_interface_yaml_data_map(app_interface_yaml_data):

    # Map the app interface yaml data to an app interface object.
    mapped_interface = app_interface_yaml_data.map()

    # Assert the mapped app interface is valid.
    assert isinstance(mapped_interface, AppInterface)
    assert mapped_interface.id == app_interface_yaml_data.id
    assert mapped_interface.name == app_interface_yaml_data.name
    assert mapped_interface.data_flag == app_interface_yaml_data.data_flag
    assert mapped_interface.name == 'Test Interface'
    assert mapped_interface.constants == CONSTANTS_DEFAULT

    # Assert the dependencies are valid.
    assert len(mapped_interface.dependencies) == 7
    for dep in mapped_interface.dependencies:
        assert isinstance(dep, AppDependency)
