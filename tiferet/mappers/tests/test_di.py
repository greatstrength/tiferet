"""Tiferet DI Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..di import (
    ServiceConfigurationYamlObject,
    ServiceConfigurationAggregate,
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

# ** fixture: service_configuration_yaml_object
@pytest.fixture
def service_configuration_yaml_object() -> ServiceConfigurationYamlObject:
    '''
    Provides a fixture for ServiceConfiguration YAML object.

    :return: The ServiceConfigurationYamlObject instance.
    :rtype: ServiceConfigurationYamlObject
    '''

    # Create and return a ServiceConfigurationYamlObject.
    return TransferObject.from_data(
        ServiceConfigurationYamlObject,
        id='test_repo',
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

# ** test: service_configuration_yaml_object_to_primitive_to_data_yaml
def test_service_configuration_yaml_object_to_primitive_to_data_yaml(service_configuration_yaml_object: ServiceConfigurationYamlObject):
    '''
    Test that the ServiceConfigurationYamlObject can be serialized to primitive data for YAML.

    :param service_configuration_yaml_object: The ServiceConfigurationYamlObject instance.
    :type service_configuration_yaml_object: ServiceConfigurationYamlObject
    '''

    # Serialize the data to primitive format for YAML.
    primitive_data = service_configuration_yaml_object.to_primitive(role='to_data.yaml')

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
    Test that the FlaggedDependencyYamlObject can be initialized from data.

    :param flagged_dependency_yaml_object: The FlaggedDependencyYamlObject instance.
    :type flagged_dependency_yaml_object: FlaggedDependencyYamlObject
    '''

    # Check if the data is correctly initialized.
    assert flagged_dependency_yaml_object.module_path == 'tests.repos.test'
    assert flagged_dependency_yaml_object.class_name == 'TestRepoProxy'
    assert flagged_dependency_yaml_object.flag == 'test'
    assert flagged_dependency_yaml_object.parameters == {'test_param': 'test_value'}

# ** test: flagged_dependency_yaml_data_map
def test_flagged_dependency_yaml_data_map(flagged_dependency_yaml_object: FlaggedDependencyYamlObject):
    '''
    Test that the FlaggedDependencyYamlObject can be mapped to a FlaggedDependency object.

    :param flagged_dependency_yaml_object: The FlaggedDependencyYamlObject instance.
    :type flagged_dependency_yaml_object: FlaggedDependencyYamlObject
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
    Test that the FlaggedDependencyYamlObject can be created from a model object.

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

# ** test: service_configuration_yaml_data_from_data
def test_service_configuration_yaml_data_from_data(service_configuration_yaml_object: ServiceConfigurationYamlObject):
    '''
    Test that the ServiceConfigurationYamlObject can be initialized from data.

    :param service_configuration_yaml_object: The ServiceConfigurationYamlObject instance.
    :type service_configuration_yaml_object: ServiceConfigurationYamlObject
    '''

    # Check if the data is correctly initialized.
    assert service_configuration_yaml_object.id == 'test_repo'
    assert len(service_configuration_yaml_object.dependencies) == 2

    # Check if dependencies are correctly initialized
    for flag, dep in service_configuration_yaml_object.dependencies.items():
        assert flag in ['test', 'test2']
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}]

# ** test: service_configuration_yaml_data_map
def test_service_configuration_yaml_data_map(service_configuration_yaml_object: ServiceConfigurationYamlObject):
    '''
    Test that the ServiceConfigurationYamlObject can be mapped to a ServiceConfiguration aggregate.

    :param service_configuration_yaml_object: The ServiceConfigurationYamlObject instance.
    :type service_configuration_yaml_object: ServiceConfigurationYamlObject
    '''

    # Map the data to a service configuration aggregate.
    mapped_attr = service_configuration_yaml_object.map()

    # Assert the mapped object is valid.
    assert isinstance(mapped_attr, ServiceConfigurationAggregate)
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

# ** test: service_configuration_yaml_data_from_model
def test_service_configuration_yaml_data_from_model(service_configuration_yaml_object: ServiceConfigurationYamlObject):
    '''
    Test that the ServiceConfigurationYamlObject can be created from a model object.

    :param service_configuration_yaml_object: The ServiceConfigurationYamlObject instance.
    :type service_configuration_yaml_object: ServiceConfigurationYamlObject
    '''

    # Create a new model object from the fixture.
    model_object = service_configuration_yaml_object.map()
    
    # Add another dependency to the model object.
    model_object.set_dependency(
        flag = 'test3',
        module_path = 'tests.repos.test',
        class_name = 'TestRepoProxy3',
        parameters = {'param3': 'value3'}
    )
    
    # Create a new data object from the model object.
    data_object = ServiceConfigurationYamlObject.from_model(model_object)
    
    # Assert the data object is valid.
    assert isinstance(data_object, ServiceConfigurationYamlObject)
    assert data_object.id == 'test_repo'
    assert len(data_object.dependencies) == 3

    # Check if all dependencies are of type FlaggedDependencyYamlObject
    for dep in data_object.dependencies.values():
        assert isinstance(dep, FlaggedDependencyYamlObject)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name in ['TestRepoProxy', 'TestRepoProxy2', 'TestRepoProxy3']
        assert dep.parameters in [{'test_param': 'test_value'}, {'param2': 'value2'}, {'param3': 'value3'}]


# ** test: service_configuration_yaml_data_flags_alias_round_trip
def test_service_configuration_yaml_data_flags_alias_round_trip() -> None:
    '''
    Test that the ``flags`` alias for dependencies is accepted on input and
    that dependencies are still serialized under ``deps``.
    '''

    data_object = TransferObject.from_data(
        ServiceConfigurationYamlObject,
        id='test_repo_flags',
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
    assert isinstance(data_object, ServiceConfigurationYamlObject)
    assert 'flag1' in data_object.dependencies
    assert isinstance(data_object.dependencies['flag1'], FlaggedDependencyYamlObject)

    # When serializing to data, dependencies should still be emitted as ``deps``.
    primitive = data_object.to_primitive(role='to_data.yaml')
    assert 'flags' not in primitive
    assert 'deps' in primitive
    assert 'flag1' in primitive['deps']
