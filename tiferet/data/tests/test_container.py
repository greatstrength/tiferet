"""Tiferet Container Data Object Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...models import (
    ModelObject,
)
from ..container import (
    ContainerAttributeConfigData,
    ContainerAttribute,
    FlaggedDependencyConfigData,
    FlaggedDependency,
)

# *** fixtures

# ** fixture: flagged_dependency_config_data
@pytest.fixture
def flagged_dependency_config_data() -> FlaggedDependencyConfigData:
    '''
    Provides a fixture for FlaggedDependency YAML data.
    
    :return: The FlaggedDependencyYamlData instance.
    :rtype: FlaggedDependencyYamlData
    '''

    # Create and return a FlaggedDependencyYamlData object.
    return FlaggedDependencyConfigData.from_data(
        module_path='tests.repos.test',
        class_name='TestRepoProxy',
        flag='test',
        parameters=dict(
            test_param='test_value'
        )
    )

# ** fixture: container_attribute_config_data
@pytest.fixture
def container_attribute_config_data() -> ContainerAttributeConfigData:
    '''
    Provides a fixture for ContainerAttribute YAML data.
    
    :return: The ContainerAttributeYamlData instance.
    :rtype: ContainerAttributeYamlData
    '''
    
    # Create and return a ContainerAttributeYamlData object.
    return ContainerAttributeConfigData.from_data(
        id='test_repo',
        type='data',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        deps=dict(
            test=dict(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                params={'test_param': 'test_value'}
            ),
            test2=dict(
                module_path='tests.repos.test',
                class_name='TestRepoProxy2',
                params={'param2': 'value2'}
            )
        ),
        params=dict(
            test_param='test_value',
            param0='value0'
        )
    )

# ** fixture: flagged_dependency_model
@pytest.fixture
def flagged_dependency_model(flagged_dependency_config_data: FlaggedDependencyConfigData):
    '''
    Fixture to create a FlaggedDependency model instance for testing.

    :param flagged_dependency_yaml_data: The FlaggedDependencyYamlData instance.
    :type flagged_dependency_yaml_data: FlaggedDependencyYamlData
    :return: The FlaggedDependency model instance.
    :rtype: FlaggedDependency
    '''

    # Map the YAML data to a FlaggedDependency model object.
    model = flagged_dependency_config_data.map()
    model.class_name = 'TestRepoProxy2'
    model.parameters = {'test_param2': 'test_value2'}
    
    # Return the model object.
    return model

# *** tests

# ** test: container_attribute_config_data_to_primitive_to_data_yaml
def test_container_attribute_config_data_to_primitive_to_data_yaml(container_attribute_config_data: ContainerAttributeConfigData):
    '''
    Test that the ContainerAttributeYamlData can be serialized to primitive data for YAML.

    :param container_attribute_yaml_data: The ContainerAttributeYamlData instance.
    :type container_attribute_yaml_data: ContainerAttributeYamlData
    '''

    # Serialize the data to primitive format for YAML.
    primitive_data = container_attribute_config_data.to_primitive(role='to_data.yaml')

    # Check if the primitive data is correct.
    assert isinstance(primitive_data, dict)
    assert primitive_data == {
        'module_path': 'tests.repos.test',
        'class_name': 'DefaultTestRepoProxy',
        'deps': {
            'test': {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy',
                'params': {'test_param': 'test_value'}
            },
            'test2': {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy2',
                'params': {'param2': 'value2'}
            },
        },
        'params': {
            'test_param': 'test_value',
            'param0': 'value0'
        }
    }


# ** test: flagged_dependency_yaml_data_from_data
def test_flagged_dependency_yaml_data_from_data(flagged_dependency_config_data: FlaggedDependencyConfigData):
    '''
    Test that the FlaggedDependencyYamlData can be initialized from data.

    :param flagged_dependency_yaml_data: The FlaggedDependencyYamlData instance.
    :type flagged_dependency_yaml_data: FlaggedDependencyYamlData
    '''

    # Check if the data is correctly initialized.
    assert flagged_dependency_config_data.module_path == 'tests.repos.test'
    assert flagged_dependency_config_data.class_name == 'TestRepoProxy'
    assert flagged_dependency_config_data.flag == 'test'
    assert flagged_dependency_config_data.parameters == {'test_param': 'test_value'}

# ** test: flagged_dependency_yaml_data_map
def test_flagged_dependency_yaml_data_map(flagged_dependency_config_data: FlaggedDependencyConfigData):
    '''
    Test that the FlaggedDependencyYamlData can be mapped to a FlaggedDependency object.

    :param flagged_dependency_yaml_data: The FlaggedDependencyYamlData instance.
    :type flagged_dependency_yaml_data: FlaggedDependencyYamlData
    '''

    # Map the data to a flagged dependency object.
    mapped_dep = flagged_dependency_config_data.map()

    # Check if the mapped object is of the correct type.
    assert isinstance(mapped_dep, FlaggedDependency)
    assert mapped_dep.module_path == 'tests.repos.test'
    assert mapped_dep.class_name == 'TestRepoProxy'
    assert mapped_dep.flag == 'test'
    assert mapped_dep.parameters == {'test_param': 'test_value'}

# ** test: flagged_dependency_yaml_data_from_model
def test_flagged_dependency_yaml_data_from_model(flagged_dependency_model: FlaggedDependency):
    '''
    Test that the FlaggedDependencyYamlData can be created from a model object.

    :param flagged_dependency_model: The FlaggedDependency model instance.
    :type flagged_dependency_model: FlaggedDependency
    '''

    # Create a new data object from the model object.
    data_from_model = FlaggedDependencyConfigData.from_model(flagged_dependency_model)
    
    # Assert the data object is valid.
    assert isinstance(data_from_model, FlaggedDependencyConfigData)
    assert data_from_model.module_path == flagged_dependency_model.module_path
    assert data_from_model.class_name == flagged_dependency_model.class_name
    assert data_from_model.flag == flagged_dependency_model.flag
    assert data_from_model.parameters == flagged_dependency_model.parameters

# ** test: container_attribute_yaml_data_from_data
def test_container_attribute_yaml_data_from_data(container_attribute_config_data: ContainerAttributeConfigData):
    '''
    Test that the ContainerAttributeYamlData can be initialized from data.

    :param container_attribute_yaml_data: The ContainerAttributeYamlData instance.
    :type container_attribute_yaml_data: ContainerAttributeYamlData
    '''

    # Check if the data is correctly initialized.
    assert container_attribute_config_data.id == 'test_repo'
    assert len(container_attribute_config_data.dependencies) == 2

    # Check if dependencies are correctly initialized
    for flag, dep in container_attribute_config_data.dependencies.items():
        assert flag in ['test', 'test2']
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]

# ** test: container_attribute_yaml_data_map
def test_container_attribute_yaml_data_map(container_attribute_config_data: ContainerAttributeConfigData):
    '''
    Test that the ContainerAttributeYamlData can be mapped to a ContainerAttribute object.

    :param container_attribute_yaml_data: The ContainerAttributeYamlData instance.
    :type container_attribute_yaml_data: ContainerAttributeYamlData
    '''

    # Map the data to a container attribute object.
    mapped_attr = container_attribute_config_data.map()
    
    # Assert the mapped object is valid.
    assert isinstance(mapped_attr, ContainerAttribute)
    assert mapped_attr.id == 'test_repo'
    assert mapped_attr.module_path == 'tests.repos.test'
    assert mapped_attr.class_name == 'DefaultTestRepoProxy'
    assert mapped_attr.parameters == {'test_param': 'test_value', 'param0': 'value0'}
    assert len(mapped_attr.dependencies) == 2
    
    # Assert the dependencies are correctly mapped.
    for dep in mapped_attr.dependencies:
        assert isinstance(dep, FlaggedDependency)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]

# ** test: container_attribute_yaml_data_from_model
def test_container_attribute_yaml_data_from_model(container_attribute_config_data: ContainerAttributeConfigData):
    '''
    Test that the ContainerAttributeYamlData can be created from a model object.

    :param container_attribute_yaml_data: The ContainerAttributeYamlData instance.
    :type container_attribute_yaml_data: ContainerAttributeYamlData
    '''

    # Create a new model object from the fixture.
    model_object = container_attribute_config_data.map()
    
    # Add another dependency to the model object.
    model_object.set_dependency(
        flag = 'test3',
        module_path = 'tests.repos.test',
        class_name = 'TestRepoProxy3',
        parameters = {'param3': 'value3'}
    )
    
    # Create a new data object from the model object.
    data_object = ContainerAttributeConfigData.from_model(model_object)
    
    # Assert the data object is valid.
    assert isinstance(data_object, ContainerAttributeConfigData)
    assert data_object.id == 'test_repo'
    assert len(data_object.dependencies) == 3

    # Check if all dependencies are of type ContainerDependencyYamlData
    for dep in data_object.dependencies.values():
        assert isinstance(dep, FlaggedDependencyConfigData)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2', 'TestRepoProxy3']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}, {'param3': 'value3'}]