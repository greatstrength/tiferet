"""Tiferet DI Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..di import (
    FlaggedDependencyAggregate,
    FlaggedDependencyYamlObject,
    ServiceConfigurationAggregate,
    ServiceConfigurationYamlObject,
)
from ...domain import (
    DomainObject,
    FlaggedDependency,
)

# *** fixtures

# ** fixture: flagged_dependency_aggregate
@pytest.fixture
def flagged_dependency_aggregate() -> FlaggedDependencyAggregate:
    '''
    Provides a fixture for a FlaggedDependencyAggregate instance.

    :return: The FlaggedDependencyAggregate instance.
    :rtype: FlaggedDependencyAggregate
    '''

    # Create and return a FlaggedDependencyAggregate.
    return FlaggedDependencyAggregate.new(
        flagged_dependency_data=dict(
            module_path='tests.repos.test',
            class_name='TestRepoProxy',
            flag='test',
            parameters={'keep': 'original', 'override': 'old'},
        )
    )

# ** fixture: service_configuration_aggregate
@pytest.fixture
def service_configuration_aggregate() -> ServiceConfigurationAggregate:
    '''
    Provides a fixture for a ServiceConfigurationAggregate instance.

    :return: The ServiceConfigurationAggregate instance.
    :rtype: ServiceConfigurationAggregate
    '''

    # Create and return a ServiceConfigurationAggregate with one seeded dependency.
    return ServiceConfigurationAggregate.new(
        service_configuration_data=dict(
            id='test_repo',
            module_path='tests.repos.test',
            class_name='DefaultTestRepoProxy',
            parameters={'default_param': 'default_value'},
            dependencies=[
                DomainObject.new(
                    FlaggedDependency,
                    module_path='tests.repos.test',
                    class_name='TestRepoProxy',
                    flag='existing',
                    parameters={'param1': 'value1'},
                )
            ],
        )
    )

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

    # Check if dependencies are correctly initialized.
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
        flag='test3',
        module_path='tests.repos.test',
        class_name='TestRepoProxy3',
        parameters={'param3': 'value3'}
    )

    # Create a new data object from the model object.
    data_object = ServiceConfigurationYamlObject.from_model(model_object)

    # Assert the data object is valid.
    assert isinstance(data_object, ServiceConfigurationYamlObject)
    assert data_object.id == 'test_repo'
    assert len(data_object.dependencies) == 3

    # Check if all dependencies are of type FlaggedDependencyYamlObject.
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

    # Create a ServiceConfigurationYamlObject using the legacy 'flags' alias.
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

    # When serializing to data, dependencies should still be emitted as 'deps'.
    primitive = data_object.to_primitive(role='to_data.yaml')
    assert 'flags' not in primitive
    assert 'deps' in primitive
    assert 'flag1' in primitive['deps']

# ** test: flagged_dependency_aggregate_new
def test_flagged_dependency_aggregate_new(flagged_dependency_aggregate: FlaggedDependencyAggregate):
    '''
    Test that FlaggedDependencyAggregate.new() creates a valid aggregate.

    :param flagged_dependency_aggregate: The FlaggedDependencyAggregate instance.
    :type flagged_dependency_aggregate: FlaggedDependencyAggregate
    '''

    # Assert the aggregate is correctly instantiated.
    assert isinstance(flagged_dependency_aggregate, FlaggedDependencyAggregate)
    assert flagged_dependency_aggregate.module_path == 'tests.repos.test'
    assert flagged_dependency_aggregate.class_name == 'TestRepoProxy'
    assert flagged_dependency_aggregate.flag == 'test'
    assert flagged_dependency_aggregate.parameters == {'keep': 'original', 'override': 'old'}

# ** test: flagged_dependency_aggregate_set_parameters_clears_when_none
def test_flagged_dependency_aggregate_set_parameters_clears_when_none(
    flagged_dependency_aggregate: FlaggedDependencyAggregate,
):
    '''
    Test that set_parameters clears all parameters when called with None.

    :param flagged_dependency_aggregate: The FlaggedDependencyAggregate instance.
    :type flagged_dependency_aggregate: FlaggedDependencyAggregate
    '''

    # Call set_parameters with None to clear all parameters.
    flagged_dependency_aggregate.set_parameters(None)

    # All parameters should be cleared.
    assert flagged_dependency_aggregate.parameters == {}

# ** test: flagged_dependency_aggregate_set_parameters_merges_and_prunes_none_values
def test_flagged_dependency_aggregate_set_parameters_merges_and_prunes_none_values(
    flagged_dependency_aggregate: FlaggedDependencyAggregate,
):
    '''
    Test that set_parameters merges new values and removes keys whose value is None.

    :param flagged_dependency_aggregate: The FlaggedDependencyAggregate instance.
    :type flagged_dependency_aggregate: FlaggedDependencyAggregate
    '''

    # Merge: override existing, add new, remove by setting to None.
    flagged_dependency_aggregate.set_parameters({
        'override': 'new',
        'remove': None,
        'add': 'added',
    })

    # 'keep' preserved, 'override' updated, 'remove' pruned, 'add' added.
    assert flagged_dependency_aggregate.parameters == {
        'keep': 'original',
        'override': 'new',
        'add': 'added',
    }

# ** test: service_configuration_aggregate_new
def test_service_configuration_aggregate_new(
    service_configuration_aggregate: ServiceConfigurationAggregate,
):
    '''
    Test that ServiceConfigurationAggregate.new() creates a valid aggregate.

    :param service_configuration_aggregate: The ServiceConfigurationAggregate instance.
    :type service_configuration_aggregate: ServiceConfigurationAggregate
    '''

    # Assert the aggregate is correctly instantiated.
    assert isinstance(service_configuration_aggregate, ServiceConfigurationAggregate)
    assert service_configuration_aggregate.id == 'test_repo'
    assert service_configuration_aggregate.module_path == 'tests.repos.test'
    assert service_configuration_aggregate.class_name == 'DefaultTestRepoProxy'
    assert service_configuration_aggregate.parameters == {'default_param': 'default_value'}
    assert len(service_configuration_aggregate.dependencies) == 1

# ** test: service_configuration_aggregate_set_default_type_updates
def test_service_configuration_aggregate_set_default_type_updates(
    service_configuration_aggregate: ServiceConfigurationAggregate,
):
    '''
    Test that set_default_type updates module_path, class_name, and parameters.

    :param service_configuration_aggregate: The ServiceConfigurationAggregate instance.
    :type service_configuration_aggregate: ServiceConfigurationAggregate
    '''

    # Update the default type with new values.
    service_configuration_aggregate.set_default_type(
        module_path='updated.module',
        class_name='UpdatedClass',
        parameters={'new_param': 'new_value'},
    )

    # Assert the fields were updated correctly.
    assert service_configuration_aggregate.module_path == 'updated.module'
    assert service_configuration_aggregate.class_name == 'UpdatedClass'
    assert service_configuration_aggregate.parameters == {'new_param': 'new_value'}

# ** test: service_configuration_aggregate_set_default_type_clears_when_both_none
def test_service_configuration_aggregate_set_default_type_clears_when_both_none(
    service_configuration_aggregate: ServiceConfigurationAggregate,
):
    '''
    Test that set_default_type clears module_path, class_name, and parameters
    when both type fields are None.

    :param service_configuration_aggregate: The ServiceConfigurationAggregate instance.
    :type service_configuration_aggregate: ServiceConfigurationAggregate
    '''

    # Call with both type fields as None to clear the default type.
    service_configuration_aggregate.set_default_type(
        module_path=None,
        class_name=None,
    )

    # Both type fields and parameters should be cleared.
    assert service_configuration_aggregate.module_path is None
    assert service_configuration_aggregate.class_name is None
    assert service_configuration_aggregate.parameters == {}

# ** test: service_configuration_aggregate_set_dependency_creates_new
def test_service_configuration_aggregate_set_dependency_creates_new(
    service_configuration_aggregate: ServiceConfigurationAggregate,
):
    '''
    Test that set_dependency appends a new FlaggedDependency when the flag is not found.

    :param service_configuration_aggregate: The ServiceConfigurationAggregate instance.
    :type service_configuration_aggregate: ServiceConfigurationAggregate
    '''

    # Confirm the flag does not already exist.
    assert service_configuration_aggregate.get_dependency('new_flag') is None

    # Add a new dependency via set_dependency.
    service_configuration_aggregate.set_dependency(
        flag='new_flag',
        module_path='tests.repos.test',
        class_name='NewTestRepoProxy',
        parameters={'new_param': 'new_value'},
    )

    # Verify the dependency was created with the correct values.
    dep = service_configuration_aggregate.get_dependency('new_flag')
    assert dep is not None
    assert isinstance(dep, FlaggedDependency)
    assert dep.module_path == 'tests.repos.test'
    assert dep.class_name == 'NewTestRepoProxy'
    assert dep.parameters == {'new_param': 'new_value'}
    assert len(service_configuration_aggregate.dependencies) == 2

# ** test: service_configuration_aggregate_set_dependency_updates_existing
def test_service_configuration_aggregate_set_dependency_updates_existing(
    service_configuration_aggregate: ServiceConfigurationAggregate,
):
    '''
    Test that set_dependency updates an existing dependency in place, merging
    parameters and pruning None-valued keys.

    :param service_configuration_aggregate: The ServiceConfigurationAggregate instance.
    :type service_configuration_aggregate: ServiceConfigurationAggregate
    '''

    # Update the existing 'existing' dependency.
    service_configuration_aggregate.set_dependency(
        flag='existing',
        module_path='tests.repos.updated',
        class_name='UpdatedRepoProxy',
        parameters={'param1': None, 'param2': 'value2'},
    )

    # Verify module_path and class_name were updated.
    dep = service_configuration_aggregate.get_dependency('existing')
    assert dep.module_path == 'tests.repos.updated'
    assert dep.class_name == 'UpdatedRepoProxy'

    # 'param1' had None value so it should be removed; 'param2' should be added.
    assert dep.parameters == {'param2': 'value2'}

    # The list should still have only one dependency.
    assert len(service_configuration_aggregate.dependencies) == 1

# ** test: service_configuration_aggregate_remove_dependency
def test_service_configuration_aggregate_remove_dependency(
    service_configuration_aggregate: ServiceConfigurationAggregate,
):
    '''
    Test that remove_dependency filters out the dependency matching the given flag.

    :param service_configuration_aggregate: The ServiceConfigurationAggregate instance.
    :type service_configuration_aggregate: ServiceConfigurationAggregate
    '''

    # Confirm the dependency exists before removal.
    assert service_configuration_aggregate.get_dependency('existing') is not None

    # Remove the dependency.
    service_configuration_aggregate.remove_dependency('existing')

    # Verify it is gone and the list is empty.
    assert service_configuration_aggregate.get_dependency('existing') is None
    assert service_configuration_aggregate.dependencies == []
