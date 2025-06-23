# *** imports

# ** infra
import pytest

# ** app1
from ..container import *
from ...models.container import *


# *** fixtures

# ** fixture: flagged_dependency_yaml_data
@pytest.fixture
def flagged_dependency_yaml_data():
    """Fixture to create a FlaggedDependencyYamlData instance for testing."""

    return FlaggedDependencyYamlData.from_data(
        module_path='tests.repos.test',
        class_name='TestRepoProxy',
        flag='test',
        parameters=dict(
            test_param='test_value'
        )
    )

@pytest.fixture
def container_attribute_yaml_data():
    """Fixture to create a ContainerAttributeYamlData instance for testing."""

    return ContainerAttributeYamlData.from_data(
        id='test_repo',
        type='data',
        deps=dict(
            test=dict(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                parameters={'test_param': 'test_value'}
            ),
            test2=dict(
                module_path='tests.repos.test',
                class_name='TestRepoProxy2',
                parameters={'param2': 'value2'}
            )
        )
    )

# ** fixture: flagged_dependency_model
@pytest.fixture
def flagged_dependency_model(flagged_dependency_yaml_data):
    model = flagged_dependency_yaml_data.map()
    model.class_name = 'TestRepoProxy2'
    model.parameters = {'test_param2': 'test_value2'}
    return model


# *** tests

# ** test: test_flagged_dependency_yaml_data_from_data
def test_flagged_dependency_yaml_data_from_data(flagged_dependency_yaml_data):
    """Test that the FlaggedDependencyYamlData can be initialized from data."""

    # Check if the data is correctly initialized.
    assert flagged_dependency_yaml_data.module_path == 'tests.repos.test'
    assert flagged_dependency_yaml_data.class_name == 'TestRepoProxy'
    assert flagged_dependency_yaml_data.flag == 'test'
    assert flagged_dependency_yaml_data.parameters == {'test_param': 'test_value'}


# ** test: test_flagged_dependency_yaml_data_map
def test_flagged_dependency_yaml_data_map(flagged_dependency_yaml_data):
    """Test that the FlaggedDependencyYamlData can be mapped to a FlaggedDependency object."""
    
    # Map the data to a flagged dependency object.
    mapped_dep = flagged_dependency_yaml_data.map()
   
    # Check if the mapped object is of the correct type.
    assert isinstance(mapped_dep, FlaggedDependency)
    assert mapped_dep.module_path == 'tests.repos.test'
    assert mapped_dep.class_name == 'TestRepoProxy'
    assert mapped_dep.flag == 'test'
    assert mapped_dep.parameters == {'test_param': 'test_value'}


# ** test: test_flagged_dependency_yaml_data_from_model
def test_flagged_dependency_yaml_data_from_model(flagged_dependency_model):
    """Test that the FlaggedDependencyYamlData can be created from a model object."""

    # Create a new data object from the model object.
    data_from_model = FlaggedDependencyYamlData.from_model(flagged_dependency_model)

    # Check if the data object is correctly initialized.
    assert isinstance(data_from_model, FlaggedDependencyYamlData)
    assert data_from_model.module_path == flagged_dependency_model.module_path
    assert data_from_model.class_name == flagged_dependency_model.class_name
    assert data_from_model.flag == flagged_dependency_model.flag
    assert data_from_model.parameters == flagged_dependency_model.parameters


# ** test: test_container_attribute_yaml_data_from_data
def test_container_attribute_yaml_data_from_data(container_attribute_yaml_data):
    """Test that the ContainerAttributeYamlData can be initialized from data."""

    # Check if the data is correctly initialized.
    assert container_attribute_yaml_data.id == 'test_repo'
    assert container_attribute_yaml_data.type == 'data'
    assert len(container_attribute_yaml_data.dependencies) == 2
    
    # Check if dependencies are correctly initialized
    for flag, dep in container_attribute_yaml_data.dependencies.items():
        assert flag in ['test', 'test2']
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]


# ** test: test_container_attribute_yaml_data_map
def test_container_attribute_yaml_data_map(container_attribute_yaml_data):
    """Test that the ContainerAttributeYamlData can be mapped to a ContainerAttribute object."""

    # Map the data to a container attribute object.
    mapped_attr = container_attribute_yaml_data.map()
    assert isinstance(mapped_attr, ContainerAttribute)
    assert mapped_attr.id == 'test_repo'
    assert mapped_attr.type == 'data'
    assert len(mapped_attr.dependencies) == 2

    # Check if all dependencies are of type ContainerDependency
    for dep in mapped_attr.dependencies:
        assert isinstance(dep, FlaggedDependency)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]


# ** test: test_container_attribute_yaml_data_from_model
def test_container_attribute_yaml_data_from_model(container_attribute_yaml_data):
    """Test that the ContainerAttributeYamlData can be created from a model object."""
    
    # Create a new model object from the fixture.
    model_object = container_attribute_yaml_data.map()

    # Update the model object with a new dependency.
    new_dep = ModelObject.new(
        FlaggedDependency,
        module_path='tests.repos.test',
        class_name='TestRepoProxy3',
        flag='test3',
        parameters={'param3': 'value3'}
    )
    model_object.set_dependency(new_dep)

    # Create a new data object from the model object.
    data_object = ContainerAttributeYamlData.from_model(model_object)

    # Assert the data object is valid.
    assert isinstance(data_object, ContainerAttributeYamlData)
    assert data_object.id == 'test_repo'
    assert data_object.type == 'data'
    assert len(data_object.dependencies) == 3

    # Check if all dependencies are of type ContainerDependencyYamlData
    for flag, dep in data_object.dependencies.items():
        assert isinstance(dep, FlaggedDependencyYamlData)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2', 'TestRepoProxy3']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}, {'param3': 'value3'}]