"""Tiferet DI Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID, FlaggedDependency
from tiferet.mappers.di import (
    FlaggedDependencyAggregate,
    FlaggedDependencyConfigObject,
    ServiceRegistrationAggregate,
    ServiceRegistrationConfigObject,
)
from tiferet.blueprints.tester import use_tester

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

# ** constant: test_service_registration_config_object_sample_data
TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_SAMPLE_DATA = {
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

# ** constant: test_service_registration_config_object_aggregate_sample_data
TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA = {
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

# *** testers

# ** tester: test_flagged_dependency_aggregate
@use_tester(
    type='aggregate',
    target_cls=FlaggedDependencyAggregate,
    sample_data=FLAGGED_DEP_AGGREGATE_SAMPLE_DATA,
    equality_fields=FLAGGED_DEP_EQUALITY_FIELDS,
    set_attribute_params=[
        ('module_path', 'new.module.path', None),
        ('class_name', 'NewClassName', None),
        ('invalid_attr', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
class TestFlaggedDependencyAggregate:
    '''
    Tests for FlaggedDependencyAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * test: new
    def test_new(self, test_ctx):
        '''Verify aggregate construction against declared expected data.'''

        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''Verify declared set_attribute cases.'''

        test_ctx.assert_set_attribute()

    aggregate_cls = FlaggedDependencyAggregate

    sample_data = FLAGGED_DEP_AGGREGATE_SAMPLE_DATA

    equality_fields = FLAGGED_DEP_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('module_path', 'new.module.path', None),
        ('class_name',  'NewClassName',    None),
        # invalid
        ('invalid_attr', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * test: set_parameters_clears_when_none
    def test_set_parameters_clears_when_none(self, test_ctx):
        '''
        Test that set_parameters clears all parameters when called with None.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Call set_parameters with None to clear all parameters.
        aggregate.set_parameters(None)

        # All parameters should be cleared.
        assert aggregate.parameters == {}

    # * test: set_parameters_merges_and_prunes_none_values
    def test_set_parameters_merges_and_prunes_none_values(self, test_ctx):
        '''
        Test that set_parameters merges new values and removes keys whose value is None.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

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

# ** tester: test_service_registration_aggregate
@use_tester(
    type='aggregate',
    target_cls=ServiceRegistrationAggregate,
    sample_data=SVC_CONFIG_AGGREGATE_SAMPLE_DATA,
    equality_fields=SVC_CONFIG_EQUALITY_FIELDS,
    field_normalizers=SVC_CONFIG_FIELD_NORMALIZERS,
    set_attribute_params=[
        ('name', 'Updated Service', None),
        ('module_path', 'updated.module', None),
        ('class_name', 'UpdatedClass', None),
        ('invalid_attr', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
class TestServiceRegistrationAggregate:
    '''
    Tests for ServiceRegistrationAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * test: new
    def test_new(self, test_ctx):
        '''Verify aggregate construction against declared expected data.'''

        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''Verify declared set_attribute cases.'''

        test_ctx.assert_set_attribute()

    aggregate_cls = ServiceRegistrationAggregate

    sample_data = SVC_CONFIG_AGGREGATE_SAMPLE_DATA

    equality_fields = SVC_CONFIG_EQUALITY_FIELDS

    field_normalizers = SVC_CONFIG_FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name',         'Updated Service', None),
        ('module_path',  'updated.module',  None),
        ('class_name',   'UpdatedClass',    None),
        # invalid
        ('invalid_attr', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * test: set_default_type_updates
    def test_set_default_type_updates(self, test_ctx):
        '''
        Test that set_default_type updates module_path, class_name, and parameters.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

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

    # * test: set_default_type_clears_when_both_none
    def test_set_default_type_clears_when_both_none(self, test_ctx):
        '''
        Test that set_default_type clears module_path, class_name, and parameters
        when both type fields are None.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Call with both type fields as None to clear the default type.
        aggregate.set_default_type(
            module_path=None,
            class_name=None,
        )

        # Both type fields and parameters should be cleared.
        assert aggregate.module_path is None
        assert aggregate.class_name is None
        assert aggregate.parameters == {}

    # * test: set_dependency_creates_new
    def test_set_dependency_creates_new(self, test_ctx):
        '''
        Test that set_dependency appends a new FlaggedDependency when the flag is not found.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

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

    # * test: set_dependency_updates_existing
    def test_set_dependency_updates_existing(self, test_ctx):
        '''
        Test that set_dependency updates an existing dependency in place, merging
        parameters and pruning None-valued keys.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

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

    # * test: remove_dependency
    def test_remove_dependency(self, test_ctx):
        '''
        Test that remove_dependency filters out the dependency matching the given flag.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Confirm the dependency exists before removal.
        assert aggregate.get_dependency('existing') is not None

        # Remove the dependency.
        aggregate.remove_dependency('existing')

        # Verify it is gone and the list is empty.
        assert aggregate.get_dependency('existing') is None
        assert aggregate.dependencies == []

    # * test: remove_dependency_missing_flag_is_noop
    def test_remove_dependency_missing_flag_is_noop(self, test_ctx):
        '''
        Test that remove_dependency with an unmatched flag leaves the list unchanged.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Record the initial count.
        initial_count = len(aggregate.dependencies)

        # Attempt to remove a non-existent flag.
        aggregate.remove_dependency('nonexistent')

        # The list should be unchanged.
        assert len(aggregate.dependencies) == initial_count

# ** tester: test_service_registration_config_object
@use_tester(
    type='transfer_object',
    target_cls=ServiceRegistrationConfigObject,
    aggregate_cls=ServiceRegistrationAggregate,
    sample_data=TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_SAMPLE_DATA,
    aggregate_sample_data=TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA,
    equality_fields=SVC_CONFIG_EQUALITY_FIELDS,
    field_normalizers=SVC_CONFIG_FIELD_NORMALIZERS,
)
class TestServiceRegistrationConfigObject:
    '''
    Tests for ServiceRegistrationConfigObject mapping, round-trip, and nested FlaggedDependencyConfigObject.
    '''

    # * test: map
    def test_map(self, test_ctx):
        '''Verify transfer construction and mapping to the declared aggregate.'''

        test_ctx.assert_map()

    # * test: from_model
    def test_from_model(self, test_ctx):
        '''Verify aggregate conversion to the declared transfer-object type.'''

        test_ctx.assert_from_model()

    # * test: round_trip
    def test_round_trip(self, test_ctx):
        '''Verify aggregate conversion through the transfer object and back.'''

        test_ctx.assert_round_trip()

    transfer_cls = ServiceRegistrationConfigObject
    aggregate_cls = ServiceRegistrationAggregate

    # YAML-format sample data (dependencies as dict keyed by flag).
    sample_data = TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_SAMPLE_DATA

    # Aggregate-format expected data (dependencies as list, defaults filled in).
    aggregate_sample_data = TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA

    equality_fields = SVC_CONFIG_EQUALITY_FIELDS

    field_normalizers = SVC_CONFIG_FIELD_NORMALIZERS

    # * test: to_primitive_to_data
    def test_to_primitive_to_data(self):
        '''
        Test that ServiceRegistrationConfigObject serializes correctly to YAML primitive format.
        '''

        # Create a YAML object from sample data.
        yaml_obj = ServiceRegistrationConfigObject.model_validate(self.sample_data)

        # Serialize to primitive format for YAML.
        primitive = yaml_obj.to_primitive(role='to_data')

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

    # * test: to_model_role_excludes_dependencies_and_parameters
    def test_to_model_role_excludes_dependencies_and_parameters(self):
        '''
        Test that the to_model role excludes dependencies and parameters.
        '''

        # Create YAML object.
        yaml_obj = ServiceRegistrationConfigObject.model_validate(self.sample_data)
        primitive = yaml_obj.to_primitive('to_model')

        # Verify excluded fields.
        assert 'dependencies' not in primitive
        assert 'parameters' not in primitive
        assert primitive['id'] == 'test_repo'
        assert primitive['module_path'] == 'tests.repos.test'
        assert primitive['class_name'] == 'DefaultTestRepoProxy'

    # * test: flags_alias_round_trip
    def test_flags_alias_round_trip(self):
        '''
        Test that the ``flags`` alias for dependencies is accepted on input and
        that dependencies are still serialized under ``deps``.
        '''

        # Create a ServiceRegistrationConfigObject using the legacy 'flags' alias.
        data_object = ServiceRegistrationConfigObject.model_validate(dict(
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
        ))

        # The alias should populate the dependencies mapping keyed by flag.
        assert isinstance(data_object, ServiceRegistrationConfigObject)
        assert 'flag1' in data_object.dependencies
        assert isinstance(data_object.dependencies['flag1'], FlaggedDependencyConfigObject)

        # When serializing to data, dependencies should still be emitted as 'deps'.
        primitive = data_object.to_primitive(role='to_data')
        assert 'flags' not in primitive
        assert 'deps' in primitive
        assert 'flag1' in primitive['deps']

    # * test: from_model_with_added_dependency
    def test_from_model_with_added_dependency(self, test_ctx):
        '''
        Test that from_model correctly converts an aggregate with added dependencies.
        '''

        target = test_ctx.make_target()

        # Create an aggregate and add a third dependency.
        aggregate = target
        aggregate.set_dependency(
            flag='test3',
            module_path='tests.repos.test',
            class_name='TestRepoProxy3',
            parameters={'param3': 'value3'},
        )

        # Convert to YAML object.
        data_object = ServiceRegistrationConfigObject.from_model(aggregate)

        # Verify the YAML object has all three dependencies.
        assert isinstance(data_object, ServiceRegistrationConfigObject)
        assert data_object.id == 'test_repo'
        assert len(data_object.dependencies) == 3

        # All dependencies should be FlaggedDependencyConfigObject instances.
        for dep in data_object.dependencies.values():
            assert isinstance(dep, FlaggedDependencyConfigObject)

    # ** constant: flagged_dep_sample_data
    flagged_dep_sample_data = {
        'module_path': 'tests.repos.test',
        'class_name': 'TestRepoProxy',
        'flag': 'test',
        'params': {'test_param': 'test_value'},
    }

    # * test: flagged_dependency_yaml_map_basic
    def test_flagged_dependency_yaml_map_basic(self):
        '''
        Test mapping a FlaggedDependencyConfigObject to a FlaggedDependency.
        '''

        # Create a YAML object and map it.
        yaml_obj = FlaggedDependencyConfigObject.model_validate(self.flagged_dep_sample_data)
        dep = yaml_obj.map()

        # Verify the mapped entity.
        assert isinstance(dep, FlaggedDependency)
        assert dep.module_path == 'tests.repos.test'
        assert dep.class_name == 'TestRepoProxy'
        assert dep.flag == 'test'
        assert dep.parameters == {'test_param': 'test_value'}

    # * test: flagged_dependency_yaml_aliasing_params
    def test_flagged_dependency_yaml_aliasing_params(self):
        '''
        Test that the "params" serialized_name alias is correctly deserialized.
        '''

        # Create YAML object using the 'params' alias.
        yaml_obj = FlaggedDependencyConfigObject.model_validate(dict(
            module_path='alias.test.mod',
            class_name='AliasImpl',
            flag='aliased',
            params={'alias_key': 'value'},
        ))
        dep = yaml_obj.map()

        # Verify aliased parameters were deserialized correctly.
        assert dep.parameters == {'alias_key': 'value'}

    # * test: flagged_dependency_yaml_from_model
    def test_flagged_dependency_yaml_from_model(self):
        '''
        Test that FlaggedDependencyConfigObject can be created from a FlaggedDependency model.
        '''

        # Create a FlaggedDependency model.
        model = FlaggedDependency(module_path='tests.repos.test',
            class_name='TestRepoProxy2',
            flag='test',
            parameters={'test_param2': 'test_value2'},
        )

        # Create a YAML object from the model.
        yaml_obj = FlaggedDependencyConfigObject.from_model(model)

        # Verify the YAML object has the correct values.
        assert isinstance(yaml_obj, FlaggedDependencyConfigObject)
        assert yaml_obj.module_path == model.module_path
        assert yaml_obj.class_name == model.class_name
        assert yaml_obj.flag == model.flag
        assert yaml_obj.parameters == model.parameters

    # * test: flagged_dependency_yaml_roles_to_data_excludes_flag
    def test_flagged_dependency_yaml_roles_to_data_excludes_flag(self):
        '''
        Test that to_data role excludes the flag field.
        '''

        # Create a YAML object.
        yaml_obj = FlaggedDependencyConfigObject.model_validate(self.flagged_dep_sample_data)

        # Serialize with to_data role.
        primitive = yaml_obj.to_primitive('to_data')

        # Flag should be excluded; other fields present.
        assert 'flag' not in primitive
        assert primitive['module_path'] == 'tests.repos.test'
        assert primitive['class_name'] == 'TestRepoProxy'

    # * test: flagged_dependency_yaml_round_trip_via_parent
    def test_flagged_dependency_yaml_round_trip_via_parent(self, test_ctx):
        '''
        Test that dependencies are preserved through the parent ServiceRegistrationConfigObject round-trip.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Convert aggregate to YAML object and back.
        yaml_top = ServiceRegistrationConfigObject.from_model(aggregate)
        round_tripped = yaml_top.map()

        # Verify every dependency's identity and implementation fields are preserved.
        assert len(round_tripped.dependencies) == len(aggregate.dependencies)
        for actual, expected in zip(round_tripped.dependencies, aggregate.dependencies):
            assert actual.flag == expected.flag
            assert actual.module_path == expected.module_path
            assert actual.class_name == expected.class_name
            assert actual.parameters == expected.parameters
