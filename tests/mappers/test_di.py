"""Tiferet DI Mapper Tests"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from tiferet.domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    FlaggedDependency,
    ModelError,
)
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

# *** fixtures

# ** fixture: flagged_dependency_aggregate
@pytest.fixture
def flagged_dependency_aggregate() -> FlaggedDependencyAggregate:
    '''
    Fixture for a flagged dependency aggregate with seeded parameters.

    :return: The flagged dependency aggregate.
    :rtype: FlaggedDependencyAggregate
    '''

    # Create the aggregate with keep and override parameters.
    return FlaggedDependencyAggregate(
        module_path='tests.repos.test',
        class_name='TestRepoProxy',
        flag='test',
        parameters={'keep': 'original', 'override': 'old'},
    )

# ** fixture: service_registration_aggregate
@pytest.fixture
def service_registration_aggregate() -> ServiceRegistrationAggregate:
    '''
    Fixture for a service registration aggregate with one existing dependency.

    :return: The service registration aggregate.
    :rtype: ServiceRegistrationAggregate
    '''

    # Create the aggregate with the existing dependency.
    return ServiceRegistrationAggregate(
        id='test_repo',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        parameters={'default_param': 'default_value'},
        dependencies=[
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                flag='existing',
                parameters={'param1': 'value1'},
            ),
        ],
    )

# ** fixture: overlay_registration
@pytest.fixture
def overlay_registration() -> ServiceRegistrationAggregate:
    '''
    Fixture for a service registration aggregate whose dependencies carry overlay parameters.

    :return: The service registration aggregate.
    :rtype: ServiceRegistrationAggregate
    '''

    # Create the aggregate with existing then other.
    return ServiceRegistrationAggregate(
        id='test_repo',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        parameters={'default_param': 'default_value'},
        dependencies=[
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                flag='existing',
                parameters={'keep': 'original', 'override': 'old'},
            ),
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='OtherRepoProxy',
                flag='other',
                parameters={'p': 'other'},
            ),
        ],
    )

# ** fixture: repeat_registration
@pytest.fixture
def repeat_registration() -> ServiceRegistrationAggregate:
    '''
    Fixture for a service registration aggregate with a repeated flag around another dependency.

    :return: The service registration aggregate.
    :rtype: ServiceRegistrationAggregate
    '''

    # Create the aggregate with dup_flag, other, then dup_flag again.
    return ServiceRegistrationAggregate(
        id='test_repo',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        parameters={'default_param': 'default_value'},
        dependencies=[
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='DupOne',
                flag='dup_flag',
                parameters={},
            ),
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='OtherRepoProxy',
                flag='other',
                parameters={},
            ),
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='DupTwo',
                flag='dup_flag',
                parameters={},
            ),
        ],
    )

# ** fixture: registration_for_transfer
@pytest.fixture
def registration_for_transfer() -> ServiceRegistrationAggregate:
    '''
    Fixture for a service registration aggregate with two ordered dependencies for transfer.

    :return: The service registration aggregate.
    :rtype: ServiceRegistrationAggregate
    '''

    # Create the aggregate with test then test2.
    return ServiceRegistrationAggregate(
        id='test_repo',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        parameters={'test_param': 'test_value', 'param0': 'value0'},
        dependencies=[
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                flag='test',
                parameters={'test_param': 'test_value'},
            ),
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='TestRepoProxy2',
                flag='test2',
                parameters={'param2': 'value2'},
            ),
        ],
    )

# ** fixture: reversed_registration
@pytest.fixture
def reversed_registration() -> ServiceRegistrationAggregate:
    '''
    Fixture for the transfer service registration aggregate with its dependencies reversed.

    :return: The service registration aggregate.
    :rtype: ServiceRegistrationAggregate
    '''

    # Create the aggregate with test2 then test.
    return ServiceRegistrationAggregate(
        id='test_repo',
        module_path='tests.repos.test',
        class_name='DefaultTestRepoProxy',
        parameters={'test_param': 'test_value', 'param0': 'value0'},
        dependencies=[
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='TestRepoProxy2',
                flag='test2',
                parameters={'param2': 'value2'},
            ),
            FlaggedDependency(
                module_path='tests.repos.test',
                class_name='TestRepoProxy',
                flag='test',
                parameters={'test_param': 'test_value'},
            ),
        ],
    )

# ** fixture: service_registration_config
@pytest.fixture
def service_registration_config() -> ServiceRegistrationConfigObject:
    '''
    Fixture for a service registration config object with deps keyed in declared order.

    :return: The service registration config object.
    :rtype: ServiceRegistrationConfigObject
    '''

    # Create the config object with test then test2.
    return ServiceRegistrationConfigObject.model_validate({
        'id': 'test_repo',
        'module_path': 'tests.repos.test',
        'class_name': 'DefaultTestRepoProxy',
        'params': {'test_param': 'test_value', 'param0': 'value0'},
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
    })

# ** fixture: reversed_service_registration_config
@pytest.fixture
def reversed_service_registration_config() -> ServiceRegistrationConfigObject:
    '''
    Fixture for a service registration config object with deps keyed in reverse order.

    :return: The service registration config object.
    :rtype: ServiceRegistrationConfigObject
    '''

    # Create the config object with test2 then test.
    return ServiceRegistrationConfigObject.model_validate({
        'id': 'test_repo',
        'module_path': 'tests.repos.test',
        'class_name': 'DefaultTestRepoProxy',
        'params': {'test_param': 'test_value', 'param0': 'value0'},
        'deps': {
            'test2': {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy2',
                'params': {'param2': 'value2'},
            },
            'test': {
                'module_path': 'tests.repos.test',
                'class_name': 'TestRepoProxy',
                'params': {'test_param': 'test_value'},
            },
        },
    })

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
        '''
        Verify aggregate construction against declared expected data.
        '''

        # Assert construction against the declared sample.
        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''
        Verify declared set_attribute cases.
        '''

        # Assert each declared set_attribute case.
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

    # * test: set_parameters_none_leaves_existing
    def test_set_parameters_none_leaves_existing(self, flagged_dependency_aggregate):
        '''
        Test that set_parameters leaves the existing parameters unchanged when called with None.

        :param flagged_dependency_aggregate: The seeded flagged dependency aggregate.
        :type flagged_dependency_aggregate: FlaggedDependencyAggregate
        '''

        # Call set_parameters with None.
        flagged_dependency_aggregate.set_parameters(parameters=None)

        # The seeded parameters are unchanged.
        assert flagged_dependency_aggregate.parameters == {'keep': 'original', 'override': 'old'}
        assert isinstance(flagged_dependency_aggregate.parameters, dict)
        assert list(flagged_dependency_aggregate.parameters) == ['keep', 'override']

    # * test: set_parameters_merges_and_prunes_none_values
    def test_set_parameters_merges_and_prunes_none_values(self, test_ctx):
        '''
        Test that set_parameters merges new values and removes keys whose value is None.
        '''

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

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

    # * test: set_parameters_overlay_exact
    def test_set_parameters_overlay_exact(self, flagged_dependency_aggregate):
        '''
        Test that set_parameters overlays exact keys in order and an empty overlay preserves existing entries.

        :param flagged_dependency_aggregate: The seeded flagged dependency aggregate.
        :type flagged_dependency_aggregate: FlaggedDependencyAggregate
        '''

        # Take a second fresh aggregate with the same seeded parameters.
        first = flagged_dependency_aggregate
        second = flagged_dependency_aggregate.model_copy(deep=True)

        # Apply an overlay to the first and an empty overlay to the second.
        first.set_parameters(parameters={'override': 'new', 'remove': None, 'add': 'added'})
        second.set_parameters(parameters={})

        # The first carries the exact overlay in key order.
        assert first.parameters == {'keep': 'original', 'override': 'new', 'add': 'added'}
        assert list(first.parameters) == ['keep', 'override', 'add']

        # The second keeps the original mapping.
        assert second.parameters == {'keep': 'original', 'override': 'old'}
        assert list(second.parameters) == ['keep', 'override']

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
        '''
        Verify aggregate construction against declared expected data.
        '''

        # Assert construction against the declared sample.
        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''
        Verify declared set_attribute cases.
        '''

        # Assert each declared set_attribute case.
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

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

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

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

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

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

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

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

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

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

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

        # Build a fresh aggregate from the declared sample.
        aggregate = test_ctx.make_target()

        # Record the initial count.
        initial_count = len(aggregate.dependencies)

        # Attempt to remove a non-existent flag.
        aggregate.remove_dependency('nonexistent')

        # The list should be unchanged.
        assert len(aggregate.dependencies) == initial_count

    # * test: set_dependency_none_parameters_leaves_existing
    def test_set_dependency_none_parameters_leaves_existing(self, service_registration_aggregate):
        '''
        Test that set_dependency updates type fields and leaves existing parameters unchanged for None.

        :param service_registration_aggregate: The seeded service registration aggregate.
        :type service_registration_aggregate: ServiceRegistrationAggregate
        '''

        # Update the existing dependency with None parameters.
        service_registration_aggregate.set_dependency(
            'existing',
            module_path='tests.repos.updated',
            class_name='UpdatedRepoProxy',
            parameters=None,
        )

        # The type fields are updated and the parameters are unchanged.
        dep = service_registration_aggregate.get_dependency('existing')
        assert dep.module_path == 'tests.repos.updated'
        assert dep.class_name == 'UpdatedRepoProxy'
        assert dep.parameters == {'param1': 'value1'}
        assert list(dep.parameters) == ['param1']

    # * test: set_dependency_overlay_in_place
    def test_set_dependency_overlay_in_place(self, overlay_registration):
        '''
        Test that set_dependency overlays parameters on the existing dependency instance without moving it.

        :param overlay_registration: The service registration aggregate with overlay parameters.
        :type overlay_registration: ServiceRegistrationAggregate
        '''

        # Retain the original existing dependency instance.
        existing = overlay_registration.dependencies[0]

        # Overlay the existing dependency and apply an empty overlay to the other.
        overlay_registration.set_dependency(
            'existing',
            module_path='tests.repos.updated',
            class_name='UpdatedRepoProxy',
            parameters={'override': 'new', 'remove': None, 'add': 'added'},
        )
        overlay_registration.set_dependency(
            'other',
            module_path='tests.repos.test',
            class_name='OtherRepoProxy',
            parameters={},
        )

        # The existing dependency is updated in place with the overlaid parameters.
        updated = overlay_registration.dependencies[0]
        assert updated is existing
        assert updated.module_path == 'tests.repos.updated'
        assert updated.class_name == 'UpdatedRepoProxy'
        assert updated.parameters == {'keep': 'original', 'override': 'new', 'add': 'added'}
        assert list(updated.parameters) == ['keep', 'override', 'add']

        # The empty overlay preserves the other parameters, and the order is unchanged.
        assert overlay_registration.get_dependency('other').parameters == {'p': 'other'}
        assert [dep.flag for dep in overlay_registration.dependencies] == ['existing', 'other']

    # * test: set_dependency_create_drops_none_values
    def test_set_dependency_create_drops_none_values(self, service_registration_aggregate):
        '''
        Test that set_dependency creates dependencies omitting None-valued parameters and with empty parameters for None.

        :param service_registration_aggregate: The seeded service registration aggregate.
        :type service_registration_aggregate: ServiceRegistrationAggregate
        '''

        # Create one dependency with a None-valued parameter and one with None parameters.
        service_registration_aggregate.set_dependency(
            'pruned_flag',
            module_path='tests.repos.test',
            class_name='PrunedRepoProxy',
            parameters={'p1': 'v1', 'gone': None},
        )
        service_registration_aggregate.set_dependency(
            'null_flag',
            module_path='tests.repos.test',
            class_name='NullRepoProxy',
            parameters=None,
        )

        # Verify the created dependency fields.
        pruned = service_registration_aggregate.get_dependency('pruned_flag')
        assert (pruned.flag, pruned.module_path, pruned.class_name) == ('pruned_flag', 'tests.repos.test', 'PrunedRepoProxy')
        assert pruned.parameters == {'p1': 'v1'}
        assert isinstance(pruned.parameters, dict)
        null = service_registration_aggregate.get_dependency('null_flag')
        assert (null.flag, null.module_path, null.class_name) == ('null_flag', 'tests.repos.test', 'NullRepoProxy')
        assert null.parameters == {}
        assert isinstance(null.parameters, dict)

        # The new dependencies are appended in order.
        assert [dep.flag for dep in service_registration_aggregate.dependencies] == [
            'existing',
            'pruned_flag',
            'null_flag',
        ]

    # * test: remove_dependency_drops_every_match
    def test_remove_dependency_drops_every_match(self, repeat_registration):
        '''
        Test that remove_dependency removes every dependency matching the flag.

        :param repeat_registration: The service registration aggregate with a repeated flag.
        :type repeat_registration: ServiceRegistrationAggregate
        '''

        # Remove the repeated flag.
        result = repeat_registration.remove_dependency('dup_flag')

        # Nothing is returned, and only the other dependency survives.
        assert result is None
        assert [dep.model_dump() for dep in repeat_registration.dependencies] == [
            {
                'module_path': 'tests.repos.test',
                'class_name': 'OtherRepoProxy',
                'parameters': {},
                'flag': 'other',
            },
        ]

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
        '''
        Verify transfer construction and mapping to the declared aggregate.
        '''

        # Assert map against the declared samples.
        test_ctx.assert_map()

    # * test: from_model
    def test_from_model(self, test_ctx):
        '''
        Verify aggregate conversion to the declared transfer-object type.
        '''

        # Assert from_model against the declared aggregate sample.
        test_ctx.assert_from_model()

    # * test: round_trip
    def test_round_trip(self, test_ctx):
        '''
        Verify aggregate conversion through the transfer object and back.
        '''

        # Assert the aggregate round-trip.
        test_ctx.assert_round_trip()

    transfer_cls = ServiceRegistrationConfigObject

    aggregate_cls = ServiceRegistrationAggregate

    sample_data = TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_SAMPLE_DATA

    aggregate_sample_data = TEST_SERVICE_REGISTRATION_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA

    equality_fields = SVC_CONFIG_EQUALITY_FIELDS

    field_normalizers = SVC_CONFIG_FIELD_NORMALIZERS

    # * attribute: flagged_dep_sample_data
    flagged_dep_sample_data = {
        'module_path': 'tests.repos.test',
        'class_name': 'TestRepoProxy',
        'flag': 'test',
        'params': {'test_param': 'test_value'},
    }

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

        # Create an aggregate and add a third dependency.
        aggregate = test_ctx.make_target()
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

        # Build the aggregate from the declared aggregate sample.
        aggregate = test_ctx.make_target()

        # Convert aggregate to YAML object and back.
        yaml_top = ServiceRegistrationConfigObject.from_model(aggregate)
        round_tripped = yaml_top.map()

        # Compare each dependency field in list order.
        assert len(round_tripped.dependencies) == len(aggregate.dependencies)
        for left, right in zip(round_tripped.dependencies, aggregate.dependencies):
            assert left.flag == right.flag
            assert left.module_path == right.module_path
            assert left.class_name == right.class_name
            assert left.parameters == right.parameters

    # * test: from_model_key_order
    def test_from_model_key_order(self, registration_for_transfer, reversed_registration):
        '''
        Test that from_model keys dependencies by flag in list order.

        :param registration_for_transfer: The service registration aggregate for transfer.
        :type registration_for_transfer: ServiceRegistrationAggregate
        :param reversed_registration: The service registration aggregate with dependencies reversed.
        :type reversed_registration: ServiceRegistrationAggregate
        '''

        # Convert each source and compare its keys and keyed child fields.
        for source, expected in (
            (registration_for_transfer, ['test', 'test2']),
            (reversed_registration, ['test2', 'test']),
        ):
            config = ServiceRegistrationConfigObject.from_model(source)
            assert list(config.dependencies) == expected
            for dep in source.dependencies:
                child = config.dependencies[dep.flag]
                assert child.module_path == dep.module_path
                assert child.class_name == dep.class_name
                assert child.parameters == dep.parameters

    # * test: map_key_order
    def test_map_key_order(self, service_registration_config, reversed_service_registration_config):
        '''
        Test that map orders dependencies by the declared deps key order.

        :param service_registration_config: The service registration config object.
        :type service_registration_config: ServiceRegistrationConfigObject
        :param reversed_service_registration_config: The service registration config object with deps reversed.
        :type reversed_service_registration_config: ServiceRegistrationConfigObject
        '''

        # Map each config object and compare flags with their child type fields.
        for config, expected in (
            (service_registration_config, [('test', 'TestRepoProxy'), ('test2', 'TestRepoProxy2')]),
            (reversed_service_registration_config, [('test2', 'TestRepoProxy2'), ('test', 'TestRepoProxy')]),
        ):
            aggregate = config.map()
            assert [(dep.flag, dep.class_name) for dep in aggregate.dependencies] == expected
            assert all(dep.module_path == 'tests.repos.test' for dep in aggregate.dependencies)

    # * test: from_model_repeated_flag_raises
    def test_from_model_repeated_flag_raises(self, repeat_registration):
        '''
        Test that from_model rejects a repeated flag without changing the source dependencies.

        :param repeat_registration: The service registration aggregate with a repeated flag.
        :type repeat_registration: ServiceRegistrationAggregate
        '''

        # Record the original ordered dependency fields.
        original = [dep.model_dump() for dep in repeat_registration.dependencies]

        # Convert the source with a repeated flag.
        with pytest.raises(ModelError) as exc_info:
            ServiceRegistrationConfigObject.from_model(repeat_registration)

        # Assert the exact repeated-flag model error.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert json.loads(str(error))['message'] == (
            "Flagged dependency 'dup_flag' is repeated in service registration 'test_repo'."
        )
        assert error.kwargs == {'attribute': 'dependencies', 'flag': 'dup_flag'}

        # The source dependencies are unchanged.
        assert [dep.model_dump() for dep in repeat_registration.dependencies] == original
