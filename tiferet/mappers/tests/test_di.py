"""Tiferet DI Mapper Tests"""

# *** imports

# ** app
from ...domain import DomainObject, FlaggedDependency
from ...events import a
from ..settings import TransferObject
from ..di import (
    FlaggedDependencyAggregate,
    FlaggedDependencyYamlObject,
    ServiceConfigurationAggregate,
    ServiceConfigurationYamlObject,
)
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: flagged_dep_aggregate_sample_data
FLAGGED_DEP_AGGREGATE_SAMPLE_DATA = {
    'module_path': 'tests.repos.test',
    'class_name': 'TestRepoProxy',
    'flag': 'test',
    'parameters': {'keep': 'original', 'override': 'old'},
}

# ** constant: flagged_dep_equality_fields
FLAGGED_DEP_EQUALITY_FIELDS = [
    'module_path',
    'class_name',
    'flag',
    'parameters',
]

# ** constant: svc_config_aggregate_sample_data
SVC_CONFIG_AGGREGATE_SAMPLE_DATA = {
    'id': 'test_repo',
    'module_path': 'tests.repos.test',
    'class_name': 'DefaultTestRepoProxy',
    'parameters': {'default_param': 'default_value'},
    'dependencies': [
        {
            'module_path': 'tests.repos.test',
            'class_name': 'TestRepoProxy',
            'flag': 'existing',
            'parameters': {'param1': 'value1'},
        },
    ],
}

# ** constant: svc_config_equality_fields
SVC_CONFIG_EQUALITY_FIELDS = [
    'id',
    'module_path',
    'class_name',
    'parameters',
    'dependencies',
]

# ** constant: dep_tuple
def DEP_TUPLE(d):
    '''
    Normalize a single dependency (dict or domain object) into a comparable tuple.
    '''

    if isinstance(d, dict):
        return (
            d['flag'],
            d['module_path'],
            d['class_name'],
            tuple(sorted(d.get('parameters', {}).items())),
        )
    return (
        d.flag,
        d.module_path,
        d.class_name,
        tuple(sorted((d.parameters or {}).items())),
    )

# ** constant: svc_config_field_normalizers
SVC_CONFIG_FIELD_NORMALIZERS = {
    'dependencies': lambda deps: tuple(sorted(DEP_TUPLE(d) for d in (deps or []))),
}


# *** classes

# ** class: TestFlaggedDependencyAggregate
class TestFlaggedDependencyAggregate(AggregateTestBase):
    '''
    Tests for FlaggedDependencyAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = FlaggedDependencyAggregate

    sample_data = FLAGGED_DEP_AGGREGATE_SAMPLE_DATA

    equality_fields = FLAGGED_DEP_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('module_path', 'new.module.path', None),
        ('class_name',  'NewClassName',    None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FlaggedDependencyAggregate:
        '''
        Override to use FlaggedDependencyAggregate.new(flagged_dependency_data=...) signature.
        '''

        # Create an aggregate using the custom factory.
        return FlaggedDependencyAggregate.new(
            flagged_dependency_data=(data if data is not None else self.sample_data).copy()
        )

    # *** domain-specific mutation tests

    # ** test: set_parameters_clears_when_none
    def test_set_parameters_clears_when_none(self, aggregate):
        '''
        Test that set_parameters clears all parameters when called with None.
        '''

        # Call set_parameters with None to clear all parameters.
        aggregate.set_parameters(None)

        # All parameters should be cleared.
        assert aggregate.parameters == {}

    # ** test: set_parameters_merges_and_prunes_none_values
    def test_set_parameters_merges_and_prunes_none_values(self, aggregate):
        '''
        Test that set_parameters merges new values and removes keys whose value is None.
        '''

        # Merge: override existing, add new, remove by setting to None.
        aggregate.set_parameters({
            'override': 'new',
            'remove': None,
            'add': 'added',
        })

        # 'keep' preserved, 'override' updated, 'remove' pruned, 'add' added.
        assert aggregate.parameters == {
            'keep': 'original',
            'override': 'new',
            'add': 'added',
        }


# ** class: TestServiceConfigurationAggregate
class TestServiceConfigurationAggregate(AggregateTestBase):
    '''
    Tests for ServiceConfigurationAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = ServiceConfigurationAggregate

    sample_data = SVC_CONFIG_AGGREGATE_SAMPLE_DATA

    equality_fields = SVC_CONFIG_EQUALITY_FIELDS

    field_normalizers = SVC_CONFIG_FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name',         'Updated Service', None),
        ('module_path',  'updated.module',  None),
        ('class_name',   'UpdatedClass',    None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> ServiceConfigurationAggregate:
        '''
        Override to use ServiceConfigurationAggregate.new(service_configuration_data=...) signature.
        '''

        # Create an aggregate using the custom factory.
        return ServiceConfigurationAggregate.new(
            service_configuration_data=(data if data is not None else self.sample_data).copy()
        )

    # *** domain-specific mutation tests

    # ** test: set_default_type_updates
    def test_set_default_type_updates(self, aggregate):
        '''
        Test that set_default_type updates module_path, class_name, and parameters.
        '''

        # Update the default type with new values.
        aggregate.set_default_type(
            module_path='updated.module',
            class_name='UpdatedClass',
            parameters={'new_param': 'new_value'},
        )

        # Assert the fields were updated correctly.
        assert aggregate.module_path == 'updated.module'
        assert aggregate.class_name == 'UpdatedClass'
        assert aggregate.parameters == {'new_param': 'new_value'}

    # ** test: set_default_type_clears_when_both_none
    def test_set_default_type_clears_when_both_none(self, aggregate):
        '''
        Test that set_default_type clears module_path, class_name, and parameters
        when both type fields are None.
        '''

        # Call with both type fields as None to clear the default type.
        aggregate.set_default_type(
            module_path=None,
            class_name=None,
        )

        # Both type fields and parameters should be cleared.
        assert aggregate.module_path is None
        assert aggregate.class_name is None
        assert aggregate.parameters == {}

    # ** test: set_dependency_creates_new
    def test_set_dependency_creates_new(self, aggregate):
        '''
        Test that set_dependency appends a new FlaggedDependency when the flag is not found.
        '''

        # Confirm the flag does not already exist.
        assert aggregate.get_dependency('new_flag') is None

        # Add a new dependency via set_dependency.
        aggregate.set_dependency(
            flag='new_flag',
            module_path='tests.repos.test',
            class_name='NewTestRepoProxy',
            parameters={'new_param': 'new_value'},
        )

        # Verify the dependency was created with the correct values.
        dep = aggregate.get_dependency('new_flag')
        assert dep is not None
        assert isinstance(dep, FlaggedDependency)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name == 'NewTestRepoProxy'
        assert dep.parameters == {'new_param': 'new_value'}
        assert len(aggregate.dependencies) == 2

    # ** test: set_dependency_updates_existing
    def test_set_dependency_updates_existing(self, aggregate):
        '''
        Test that set_dependency updates an existing dependency in place, merging
        parameters and pruning None-valued keys.
        '''

        # Update the existing 'existing' dependency.
        aggregate.set_dependency(
            flag='existing',
            module_path='tests.repos.updated',
            class_name='UpdatedRepoProxy',
            parameters={'param1': None, 'param2': 'value2'},
        )

        # Verify module_path and class_name were updated.
        dep = aggregate.get_dependency('existing')
        assert dep.module_path == 'tests.repos.updated'
        assert dep.class_name == 'UpdatedRepoProxy'

        # 'param1' had None value so it should be removed; 'param2' should be added.
        assert dep.parameters == {'param2': 'value2'}

        # The list should still have only one dependency.
        assert len(aggregate.dependencies) == 1

    # ** test: remove_dependency
    def test_remove_dependency(self, aggregate):
        '''
        Test that remove_dependency filters out the dependency matching the given flag.
        '''

        # Confirm the dependency exists before removal.
        assert aggregate.get_dependency('existing') is not None

        # Remove the dependency.
        aggregate.remove_dependency('existing')

        # Verify it is gone and the list is empty.
        assert aggregate.get_dependency('existing') is None
        assert aggregate.dependencies == []

    # ** test: remove_dependency_missing_flag_is_noop
    def test_remove_dependency_missing_flag_is_noop(self, aggregate):
        '''
        Test that remove_dependency with an unmatched flag leaves the list unchanged.
        '''

        # Record the initial count.
        initial_count = len(aggregate.dependencies)

        # Attempt to remove a non-existent flag.
        aggregate.remove_dependency('nonexistent')

        # The list should be unchanged.
        assert len(aggregate.dependencies) == initial_count


# ** class: TestServiceConfigurationYamlObject
class TestServiceConfigurationYamlObject(TransferObjectTestBase):
    '''
    Tests for ServiceConfigurationYamlObject mapping, round-trip, and nested FlaggedDependencyYamlObject.
    '''

    transfer_cls = ServiceConfigurationYamlObject
    aggregate_cls = ServiceConfigurationAggregate

    # YAML-format sample data (dependencies as dict keyed by flag).
    sample_data = {
        'id': 'test_repo',
        'module_path': 'tests.repos.test',
        'class_name': 'DefaultTestRepoProxy',
        'deps': {
            'test': {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy',
                'params': {'test_param': 'test_value'},
            },
            'test2': {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy2',
                'params': {'param2': 'value2'},
            },
        },
        'params': {
            'test_param': 'test_value',
            'param0': 'value0',
        },
    }

    # Aggregate-format expected data (dependencies as list, defaults filled in).
    aggregate_sample_data = {
        'id': 'test_repo',
        'module_path': 'tests.repos.test',
        'class_name': 'DefaultTestRepoProxy',
        'parameters': {'test_param': 'test_value', 'param0': 'value0'},
        'dependencies': [
            {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy',
                'flag': 'test',
                'parameters': {'test_param': 'test_value'},
            },
            {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy2',
                'flag': 'test2',
                'parameters': {'param2': 'value2'},
            },
        ],
    }

    equality_fields = SVC_CONFIG_EQUALITY_FIELDS

    field_normalizers = SVC_CONFIG_FIELD_NORMALIZERS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> ServiceConfigurationAggregate:
        '''
        Override to use ServiceConfigurationAggregate.new(service_configuration_data=...) signature.
        '''

        # Create an aggregate using the custom factory.
        return ServiceConfigurationAggregate.new(
            service_configuration_data=(data if data is not None else self.aggregate_sample_data).copy()
        )

    # *** domain-specific tests

    # ** test: to_primitive_to_data_yaml
    def test_to_primitive_to_data_yaml(self):
        '''
        Test that ServiceConfigurationYamlObject serializes correctly to YAML primitive format.
        '''

        # Create a YAML object from sample data.
        yaml_obj = TransferObject.from_data(
            ServiceConfigurationYamlObject,
            **self.sample_data,
        )

        # Serialize to primitive format for YAML.
        primitive = yaml_obj.to_primitive(role='to_data.yaml')

        # Verify id is excluded and the remaining structure is correct.
        assert isinstance(primitive, dict)
        assert 'id' not in primitive
        assert primitive == {
            'module_path': 'tests.repos.test',
            'class_name': 'DefaultTestRepoProxy',
            'deps': {
                'test': {
                    'module_path': 'tests.repos.test',
                    'class_name': 'TestRepoProxy',
                    'params': {'test_param': 'test_value'},
                },
                'test2': {
                    'module_path': 'tests.repos.test',
                    'class_name': 'TestRepoProxy2',
                    'params': {'param2': 'value2'},
                },
            },
            'params': {
                'test_param': 'test_value',
                'param0': 'value0',
            },
        }

    # ** test: to_model_role_excludes_dependencies_and_parameters
    def test_to_model_role_excludes_dependencies_and_parameters(self):
        '''
        Test that the to_model role excludes dependencies and parameters.
        '''

        # Create YAML object.
        yaml_obj = TransferObject.from_data(
            ServiceConfigurationYamlObject,
            **self.sample_data,
        )
        primitive = yaml_obj.to_primitive('to_model')

        # Verify excluded fields.
        assert 'dependencies' not in primitive
        assert 'parameters' not in primitive
        assert primitive['id'] == 'test_repo'
        assert primitive['module_path'] == 'tests.repos.test'
        assert primitive['class_name'] == 'DefaultTestRepoProxy'

    # ** test: flags_alias_round_trip
    def test_flags_alias_round_trip(self):
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

    # ** test: from_model_with_added_dependency
    def test_from_model_with_added_dependency(self):
        '''
        Test that from_model correctly converts an aggregate with added dependencies.
        '''

        # Create an aggregate and add a third dependency.
        aggregate = self.make_aggregate()
        aggregate.set_dependency(
            flag='test3',
            module_path='tests.repos.test',
            class_name='TestRepoProxy3',
            parameters={'param3': 'value3'},
        )

        # Convert to YAML object.
        data_object = ServiceConfigurationYamlObject.from_model(aggregate)

        # Verify the YAML object has all three dependencies.
        assert isinstance(data_object, ServiceConfigurationYamlObject)
        assert data_object.id == 'test_repo'
        assert len(data_object.dependencies) == 3

        # All dependencies should be FlaggedDependencyYamlObject instances.
        for dep in data_object.dependencies.values():
            assert isinstance(dep, FlaggedDependencyYamlObject)

    # *** child mapper: FlaggedDependencyYamlObject

    # ** constant: flagged_dep_sample_data
    flagged_dep_sample_data = {
        'module_path': 'tests.repos.test',
        'class_name': 'TestRepoProxy',
        'flag': 'test',
        'params': {'test_param': 'test_value'},
    }

    # ** test: flagged_dependency_yaml_map_basic
    def test_flagged_dependency_yaml_map_basic(self):
        '''
        Test mapping a FlaggedDependencyYamlObject to a FlaggedDependency.
        '''

        # Create a YAML object and map it.
        yaml_obj = TransferObject.from_data(
            FlaggedDependencyYamlObject,
            **self.flagged_dep_sample_data,
        )
        dep = yaml_obj.map()

        # Verify the mapped entity.
        assert isinstance(dep, FlaggedDependency)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name == 'TestRepoProxy'
        assert dep.flag == 'test'
        assert dep.parameters == {'test_param': 'test_value'}

    # ** test: flagged_dependency_yaml_aliasing_params
    def test_flagged_dependency_yaml_aliasing_params(self):
        '''
        Test that the "params" serialized_name alias is correctly deserialized.
        '''

        # Create YAML object using the 'params' alias.
        yaml_obj = TransferObject.from_data(
            FlaggedDependencyYamlObject,
            module_path='alias.test.mod',
            class_name='AliasImpl',
            flag='aliased',
            params={'alias_key': 'value'},
        )
        dep = yaml_obj.map()

        # Verify aliased parameters were deserialized correctly.
        assert dep.parameters == {'alias_key': 'value'}

    # ** test: flagged_dependency_yaml_from_model
    def test_flagged_dependency_yaml_from_model(self):
        '''
        Test that FlaggedDependencyYamlObject can be created from a FlaggedDependency model.
        '''

        # Create a FlaggedDependency model.
        model = DomainObject.new(
            FlaggedDependency,
            module_path='tests.repos.test',
            class_name='TestRepoProxy2',
            flag='test',
            parameters={'test_param2': 'test_value2'},
        )

        # Create a YAML object from the model.
        yaml_obj = FlaggedDependencyYamlObject.from_model(model)

        # Verify the YAML object has the correct values.
        assert isinstance(yaml_obj, FlaggedDependencyYamlObject)
        assert yaml_obj.module_path == model.module_path
        assert yaml_obj.class_name == model.class_name
        assert yaml_obj.flag == model.flag
        assert yaml_obj.parameters == model.parameters

    # ** test: flagged_dependency_yaml_roles_to_data_yaml_excludes_flag
    def test_flagged_dependency_yaml_roles_to_data_yaml_excludes_flag(self):
        '''
        Test that to_data.yaml role excludes the flag field.
        '''

        # Create a YAML object.
        yaml_obj = TransferObject.from_data(
            FlaggedDependencyYamlObject,
            **self.flagged_dep_sample_data,
        )

        # Serialize with to_data.yaml role.
        primitive = yaml_obj.to_primitive('to_data.yaml')

        # Flag should be excluded; other fields present.
        assert 'flag' not in primitive
        assert primitive['module_path'] == 'tests.repos.test'
        assert primitive['class_name'] == 'TestRepoProxy'

    # ** test: flagged_dependency_yaml_round_trip_via_parent
    def test_flagged_dependency_yaml_round_trip_via_parent(self, aggregate):
        '''
        Test that dependencies are preserved through the parent ServiceConfigurationYamlObject round-trip.
        '''

        # Convert aggregate to YAML object and back.
        yaml_top = ServiceConfigurationYamlObject.from_model(aggregate)
        round_tripped = yaml_top.map()

        # Verify dependencies list preserved using nested helper.
        self.assert_nested_list_matches(
            round_tripped.dependencies,
            aggregate.dependencies,
            key_field='flag',
            compare_fields=['module_path', 'class_name', 'parameters'],
        )
