# *** imports

# ** infra
import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: app_dependency_yaml_data
@pytest.fixture
def app_dependency_yaml_data():
    return AppDependencyYamlData.from_data(
        attribute_id='test_attr',
        module_path='tests.repos.test',
        class_name='TestProxy'
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


# ** fixture: app_interface_yaml_data_custom_dependencies
@pytest.fixture
def app_interface_yaml_data_custom_dependencies():
    return AppInterfaceYamlData.from_data(
        id='custom_interface',
        name='Custom Interface',
        data_flag='custom_flag',
        app_context=dict(
            module_path='custom.module',
            class_name='CustomClass'
        ),
        container_context=dict(
            module_path='custom.container',
            class_name='ContainerClass'
        )
    )


# *** tests

# ** test: test_app_dependency_yaml_data_from_data
def test_app_dependency_yaml_data_from_data(app_dependency_yaml_data):
    
    # Assert the app dependency yaml data is valid.
    assert app_dependency_yaml_data.attribute_id == 'test_attr'
    assert app_dependency_yaml_data.module_path == 'tests.repos.test'
    assert app_dependency_yaml_data.class_name == 'TestProxy'


# ** test: test_app_dependency_yaml_data_map
def test_app_dependency_yaml_data_map(app_dependency_yaml_data):

    # Map the app dependency yaml data.
    mapped_dep = app_dependency_yaml_data.map()
    assert isinstance(mapped_dep, AppDependency)
    assert mapped_dep.attribute_id == 'test_attr'
    assert mapped_dep.module_path == 'tests.repos.test'
    assert mapped_dep.class_name == 'TestProxy'


# ** test: test_app_interface_yaml_data_from_data
def test_app_interface_yaml_data_from_data(app_interface_yaml_data):
    
    # Assert the app interface yaml data is valid.
    assert isinstance(app_interface_yaml_data.app_context,
                      AppDependencyYamlData)
    assert app_interface_yaml_data.app_context.attribute_id == 'app_context'
    assert app_interface_yaml_data.feature_context.attribute_id == 'feature_context'
    assert app_interface_yaml_data.container_context.attribute_id == 'container_context'
    assert app_interface_yaml_data.error_context.attribute_id == 'error_context'
    assert app_interface_yaml_data.feature_repo.attribute_id == 'feature_repo'
    assert app_interface_yaml_data.container_repo.attribute_id == 'container_repo'
    assert app_interface_yaml_data.error_repo.attribute_id == 'error_repo'


# ** test: test_app_interface_yaml_data_map
def test_app_interface_yaml_data_map(app_interface_yaml_data):

    mapped_interface = app_interface_yaml_data.map()
    assert isinstance(mapped_interface, AppInterface)
    assert len(mapped_interface.dependencies) == 7
    # Check if all dependencies are of type AppDependency
    for dep in mapped_interface.dependencies:
        assert isinstance(dep, AppDependency)


# ** test: test_app_interface_yaml_data_custom_dependencies
def test_app_interface_yaml_data_custom_dependencies(app_interface_yaml_data_custom_dependencies):

    # Assert the custom app interface yaml data is valid.
    assert app_interface_yaml_data_custom_dependencies.app_context.module_path == 'custom.module'
    assert app_interface_yaml_data_custom_dependencies.container_context.module_path == 'custom.container'
