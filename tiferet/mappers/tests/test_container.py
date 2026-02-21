"""Tiferet Container Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..container import (
    ContainerAttributeYamlObject,
    ContainerAttributeAggregate,
    FlaggedDependencyYamlObject,
)
from ...domain import (
    FlaggedDependency,
)

# *** fixtures

# ** fixture: flagged_dependency_yaml_object
@pytest.fixture
def flagged_dependency_yaml_object() -> FlaggedDependencyYamlObject:
    '''
    Provides a fixture for FlaggedDependency YAML object.

    :return: The FlaggedDependencyYamlObject instance.
    :rtype: FlaggedDependencyYamlObject
    '''

    # Create and return a FlaggedDependencyYamlObject.
    return TransferObject.from_data(
        FlaggedDependencyYamlObject,
        module_path='tests.repos.test',
        class_name='TestRepoProxy',
        flag='test',
        params=dict(
            test_param='test_value'
        )
    )

# ** fixture: container_attribute_yaml_object
@pytest.fixture
def container_attribute_yaml_object() -> ContainerAttributeYamlObject:
    '''
    Provides a fixture for ContainerAttribute YAML object.

    :return: The ContainerAttributeYamlObject instance.
    :rtype: ContainerAttributeYamlObject
    '''

    # Create and return a ContainerAttributeYamlObject.
    return TransferObject.from_data(
        ContainerAttributeYamlObject,
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
def flagged_dependency_model(flagged_dependency_yaml_object: FlaggedDependencyYamlObject):
    '''
    Fixture to create a FlaggedDependency model instance for testing.

    :param flagged_dependency_yaml_object: The FlaggedDependencyYamlObject instance.
    :type flagged_dependency_yaml_object: FlaggedDependencyYamlObject
    :return: The FlaggedDependency model instance.
    :rtype: FlaggedDependency
    '''

    # Map the YAML object to a FlaggedDependency model.
    model = flagged_dependency_yaml_object.map()
    model.class_name = 'TestRepoProxy2'
    model.parameters = {'test_param2': 'test_value2'}

    # Return the model object.
    return model

# *** tests

# ** test: container_attribute_yaml_object_to_primitive_to_data_yaml
def test_container_attribute_yaml_object_to_primitive_to_data_yaml(container_attribute_yaml_object: ContainerAttributeYamlObject):
    '''
    Test that the ContainerAttributeYamlObject can be serialized to primitive data for YAML.

    :param container_attribute_yaml_object: The ContainerAttributeYamlObject instance.
    :type container_attribute_yaml_object: ContainerAttributeYamlObject
    '''

    # Serialize the data to primitive format for YAML.
    primitive_data = container_attribute_yaml_object.to_primitive(role='to_data.yaml')

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
def test_flagged_dependency_yaml_data_from_data(flagged_dependency_yaml_object: FlaggedDependencyYamlObject):
    '''
    Test that the FlaggedDependencyYamlData can be initialized from data.

    :param flagged_dependency_yaml_data: The FlaggedDependencyYamlData instance.
    :type flagged_dependency_yaml_data: FlaggedDependencyYamlData
    '''

    # Check if the data is correctly initialized.
    assert flagged_dependency_yaml_object.module_path == 'tests.repos.test'
    assert flagged_dependency_yaml_object.class_name == 'TestRepoProxy'
    assert flagged_dependency_yaml_object.flag == 'test'
    assert flagged_dependency_yaml_object.parameters == {'test_param': 'test_value'}

# ** test: flagged_dependency_yaml_data_map
def test_flagged_dependency_yaml_data_map(flagged_dependency_yaml_object: FlaggedDependencyYamlObject):
    '''
    Test that the FlaggedDependencyYamlData can be mapped to a FlaggedDependency object.

    :param flagged_dependency_yaml_data: The FlaggedDependencyYamlData instance.
    :type flagged_dependency_yaml_data: FlaggedDependencyYamlData
    '''

    # Map the data to a flagged dependency object.
    mapped_dep = flagged_dependency_yaml_object.map()

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
    data_from_model = FlaggedDependencyYamlObject.from_model(flagged_dependency_model)
    
    # Assert the data object is valid.
    assert isinstance(data_from_model, FlaggedDependencyYamlObject)
    assert data_from_model.module_path == flagged_dependency_model.module_path
    assert data_from_model.class_name == flagged_dependency_model.class_name
    assert data_from_model.flag == flagged_dependency_model.flag
    assert data_from_model.parameters == flagged_dependency_model.parameters

# ** test: container_attribute_yaml_data_from_data
def test_container_attribute_yaml_data_from_data(container_attribute_yaml_object: ContainerAttributeYamlObject):
    '''
    Test that the ContainerAttributeYamlData can be initialized from data.

    :param container_attribute_yaml_data: The ContainerAttributeYamlData instance.
    :type container_attribute_yaml_data: ContainerAttributeYamlData
    '''

    # Check if the data is correctly initialized.
    assert container_attribute_yaml_object.id == 'test_repo'
    assert len(container_attribute_yaml_object.dependencies) == 2

    # Check if dependencies are correctly initialized
    for flag, dep in container_attribute_yaml_object.dependencies.items():
        assert flag in ['test', 'test2']
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]

# ** test: container_attribute_yaml_data_map
def test_container_attribute_yaml_data_map(container_attribute_yaml_object: ContainerAttributeYamlObject):
    '''
    Test that the ContainerAttributeYamlObject can be mapped to a ContainerAttribute aggregate.

    :param container_attribute_yaml_object: The ContainerAttributeYamlObject instance.
    :type container_attribute_yaml_object: ContainerAttributeYamlObject
    '''

    # Map the data to a container attribute aggregate.
    mapped_attr = container_attribute_yaml_object.map()

    # Assert the mapped object is valid.
    assert isinstance(mapped_attr, ContainerAttributeAggregate)
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
def test_container_attribute_yaml_data_from_model(container_attribute_yaml_object: ContainerAttributeYamlObject):
    '''
    Test that the ContainerAttributeYamlData can be created from a model object.

    :param container_attribute_yaml_data: The ContainerAttributeYamlData instance.
    :type container_attribute_yaml_data: ContainerAttributeYamlData
    '''

    # Create a new model object from the fixture.
    model_object = container_attribute_yaml_object.map()
    
    # Add another dependency to the model object.
    model_object.set_dependency(
        flag = 'test3',
        module_path = 'tests.repos.test',
        class_name = 'TestRepoProxy3',
        parameters = {'param3': 'value3'}
    )
    
    # Create a new data object from the model object.
    data_object = ContainerAttributeYamlObject.from_model(model_object)
    
    # Assert the data object is valid.
    assert isinstance(data_object, ContainerAttributeYamlObject)
    assert data_object.id == 'test_repo'
    assert len(data_object.dependencies) == 3

    # Check if all dependencies are of type ContainerDependencyYamlData
    for dep in data_object.dependencies.values():
        assert isinstance(dep, FlaggedDependencyYamlObject)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2', 'TestRepoProxy3']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}, {'param3': 'value3'}]


# ** test: container_attribute_yaml_data_flags_alias_round_trip
def test_container_attribute_yaml_data_flags_alias_round_trip() -> None:
    '''
    Test that the ``flags`` alias for dependencies is accepted on input and
    that dependencies are still serialized under ``deps``.
    '''

    data_object = TransferObject.from_data(
        ContainerAttributeYamlObject,
        id='test_repo_flags',
        type='data',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        flags=dict(
            flag1=dict(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                params={'test_param': 'test_value'},
            ),
        ),
        params=dict(
            test_param='test_value',
        ),
    )

    # The alias should populate the dependencies mapping keyed by flag.
    assert isinstance(data_object, ContainerAttributeYamlObject)
    assert 'flag1' in data_object.dependencies
    assert isinstance(data_object.dependencies['flag1'], FlaggedDependencyYamlObject)

    # When serializing to data, dependencies should still be emitted as ``deps``.
    primitive = data_object.to_primitive(role='to_data.yaml')
    assert 'flags' not in primitive
    assert 'deps' in primitive
    assert 'flag1' in primitive['deps']
