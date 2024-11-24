# *** imports

# ** infra
import pytest

# ** app1
from . import *


# *** fixtures

# ** fixture: container_dependency_yaml_data
@pytest.fixture
def container_dependency_yaml_data():
    return ContainerDependencyYamlData.from_data(
        module_path='tests.repos.test',
        class_name='TestRepoProxy',
        flag='test',
        parameters=dict(
            test_param='test_value'
        )
    )

@pytest.fixture
def container_attribute_yaml_data():
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

# ** fixture: container_dependency_model
@pytest.fixture
def container_dependency_model(container_dependency_yaml_data):
    model = container_dependency_yaml_data.map()
    model.class_name = 'TestRepoProxy2'
    model.parameters = {'test_param2': 'test_value2'}
    return model


# *** tests

# ** test: test_container_dependency_yaml_data_from_data
def test_container_dependency_yaml_data_from_data(container_dependency_yaml_data):
    
    # Check if the data is correctly initialized.
    assert container_dependency_yaml_data.module_path == 'tests.repos.test'
    assert container_dependency_yaml_data.class_name == 'TestRepoProxy'
    assert container_dependency_yaml_data.flag == 'test'
    assert container_dependency_yaml_data.parameters == {'test_param': 'test_value'}


# ** test: test_container_dependency_yaml_data_map
def test_container_dependency_yaml_data_map(container_dependency_yaml_data):
    
    # Map the data to a container dependency object.
    mapped_dep = container_dependency_yaml_data.map()
   
    # Check if the mapped object is of the correct type.
    assert isinstance(mapped_dep, ContainerDependency)
    assert mapped_dep.module_path == 'tests.repos.test'
    assert mapped_dep.class_name == 'TestRepoProxy'
    assert mapped_dep.flag == 'test'
    assert mapped_dep.parameters == {'test_param': 'test_value'}


# ** test: test_container_dependency_yaml_data_from_model
def test_container_dependency_yaml_data_from_model(container_dependency_model):

    # Create a new data object from the model object.
    data_from_model = ContainerDependencyYamlData.from_model(container_dependency_model)

    # Check if the data object is correctly initialized.
    assert isinstance(data_from_model, ContainerDependencyYamlData)
    assert data_from_model.module_path == container_dependency_model.module_path
    assert data_from_model.class_name == container_dependency_model.class_name
    assert data_from_model.flag == container_dependency_model.flag
    assert data_from_model.parameters == container_dependency_model.parameters


# ** test: test_container_attribute_yaml_data_from_data
def test_container_attribute_yaml_data_from_data(container_attribute_yaml_data):

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

    # Map the data to a container attribute object.
    mapped_attr = container_attribute_yaml_data.map()
    assert isinstance(mapped_attr, ContainerAttribute)
    assert mapped_attr.id == 'test_repo'
    assert mapped_attr.type == 'data'
    assert len(mapped_attr.dependencies) == 2

    # Check if all dependencies are of type ContainerDependency
    for dep in mapped_attr.dependencies:
        assert isinstance(dep, ContainerDependency)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]


# ** test: test_container_attribute_yaml_data_from_model
def test_container_attribute_yaml_data_from_model(container_attribute_yaml_data):
    
    # Create a new model object from the fixture.
    model_object = container_attribute_yaml_data.map()

    # Update the model object with a new dependency.
    new_dep = ContainerDependency.new(
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
        assert isinstance(dep, ContainerDependencyYamlData)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2', 'TestRepoProxy3']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}, {'param3': 'value3'}]