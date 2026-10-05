"""Tiferet App Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain import ATTRIBUTE_NOT_SETTABLE_ID, AppServiceDependency
from tiferet.mappers.app import (
    AppSessionAggregate,
    AppSessionConfigObject,
    AppServiceDependencyConfigObject,
)

# *** constants

# ** constant: svc_tuple
def SVC_TUPLE(s):
    '''
    Normalize a single service (dict or domain object) into a comparable tuple.
    '''

    if isinstance(s, dict):
        return (
            s['service_id'],
            s['module_path'],
            s['class_name'],
            tuple(sorted(s.get('parameters', {}).items())),
        )
    return (
        s.service_id,
        s.module_path,
        s.class_name,
        tuple(sorted((s.parameters or {}).items())),
    )

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = {
    'id': 'test.interface',
    'name': 'Test Interface',
    'description': 'The test app interface.',
    'flags': [
        'test_feature',
        'test_data',
    ],
    'logger_id': 'default',
    'services': [
        {
            'service_id': 'test_attribute',
            'module_path': 'test.module.path',
            'class_name': 'TestClassName',
            'parameters': {
                'test_param': 'test_value',
                'debug': '1',
            },
        },
        {
            'service_id': 'logging',
            'module_path': 'tiferet.utils.logging',
            'class_name': 'LoggingService',
            'parameters': {},
        },
    ],
    'constants': {
        'APP_NAME': 'Tiferet Test',
        'VERSION': '2.0.0a1',
        'DEBUG': '1',
    },
}

# ** constant: equality_fields
EQUALITY_FIELDS = [
    'id',
    'name',
    'description',
    'logger_id',
    'flags',
    'constants',
    'services',
]

# ** constant: field_normalizers
FIELD_NORMALIZERS = {
    'flags': lambda v: sorted(v or []),
    'constants': lambda v: dict(sorted((k, v) for k, v in (v or {}).items())),
    'services': lambda svcs: tuple(sorted(SVC_TUPLE(s) for s in (svcs or []))),
}

# ** constant: test_app_session_config_object_sample_data
TEST_APP_SESSION_CONFIG_OBJECT_SAMPLE_DATA = {
    'id': 'test.interface',
    'name': 'Test Interface',
    'description': 'The test app interface.',
    'flags': [
        'test_feature',
        'test_data',
    ],
    'logger_id': 'default',
    'services': {
        'test_attribute': {
            'module_path': 'test.module.path',
            'class_name': 'TestClassName',
            'parameters': {
                'test_param': 'test_value',
                'debug': '1',
            },
        },
        'logging': {
            'module_path': 'tiferet.utils.logging',
            'class_name': 'LoggingService',
            'parameters': {},
        },
    },
    'constants': {
        'APP_NAME': 'Tiferet Test',
        'VERSION': '2.0.0a1',
        'DEBUG': '1',
    },
}

# *** testers

# ** tester: test_app_session_aggregate
@use_tester(
    type='aggregate',
    target_cls=AppSessionAggregate,
    sample_data=AGGREGATE_SAMPLE_DATA,
    equality_fields=EQUALITY_FIELDS,
    field_normalizers=FIELD_NORMALIZERS,
    set_attribute_params=[
        ('name', 'Updated Interface', None),
        ('description', 'New description text', None),
        ('logger_id', 'custom.logger.id', None),
        ('flags', ['flag1', 'flag2'], None),
        ('invalid_attr', 'value', ATTRIBUTE_NOT_SETTABLE_ID),
    ],
)
class TestAppSessionAggregate:
    '''
    Tests for AppSessionAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * test: new
    def test_new(self, test_ctx):
        '''
        Verify aggregate construction against declared expected data.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert construction against the declared sample.
        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''
        Verify declared set_attribute cases.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert each declared set_attribute case.
        test_ctx.assert_set_attribute()

    # * attribute: aggregate_cls
    aggregate_cls = AppSessionAggregate

    # * attribute: sample_data
    sample_data = AGGREGATE_SAMPLE_DATA

    # * attribute: equality_fields
    equality_fields = EQUALITY_FIELDS

    # * attribute: field_normalizers
    field_normalizers = FIELD_NORMALIZERS

    # * attribute: set_attribute_params
    set_attribute_params = [
        ('name', 'Updated Interface', None),
        ('description', 'New description text', None),
        ('logger_id', 'custom.logger.id', None),
        ('flags', ['flag1', 'flag2'], None),
        ('invalid_attr', 'value', ATTRIBUTE_NOT_SETTABLE_ID),
    ]

    # * fixture: aggr_factory
    @pytest.fixture
    def aggr_factory(self):
        '''
        Factory for creating AppSessionAggregate with customizable services/constants.
        '''

        def factory(services=None, constants=None, **overrides):

            # Start from a copy of the shared sample data.
            data = self.sample_data.copy()

            # Override services and constants if provided.
            if services is not None:
                data['services'] = services
            if constants is not None:
                data['constants'] = constants
            data.update(overrides)

            # Create and return the aggregate.
            return AppSessionAggregate(**data)

        return factory

    # * test: set_constants_clear_when_none
    def test_set_constants_clear_when_none(self, aggr_factory):
        '''
        Test that set_constants clears constants when called with None.

        :param aggr_factory: Factory for a seeded AppSessionAggregate.
        :type aggr_factory: callable
        '''

        # Seed constants, then clear them.
        aggregate = aggr_factory(constants={'a': '1', 'b': '2'})
        aggregate.set_constants(None)

        # Verify the constants were cleared.
        assert aggregate.constants == {}

    # * test: set_constants_merge_and_override
    def test_set_constants_merge_and_override(self, aggr_factory):
        '''
        Test that set_constants merges new keys and overrides existing ones.

        :param aggr_factory: Factory for a seeded AppSessionAggregate.
        :type aggr_factory: callable
        '''

        # Seed constants, then merge an override and a new key.
        aggregate = aggr_factory(constants={'keep': 'orig', 'old': 'v1'})
        aggregate.set_constants({'old': 'v2', 'new': '42'})

        # Verify the merge kept, overrode, and added keys.
        assert aggregate.constants == {
            'keep': 'orig',
            'old': 'v2',
            'new': '42',
        }

    # * test: set_constants_remove_none_values
    def test_set_constants_remove_none_values(self, aggr_factory):
        '''
        Test that set_constants removes keys whose merged value is None.

        :param aggr_factory: Factory for a seeded AppSessionAggregate.
        :type aggr_factory: callable
        '''

        # Seed constants, then drop one key and add another.
        aggregate = aggr_factory(constants={'keep': '1', 'drop': 'x'})
        aggregate.set_constants({'drop': None, 'add': 'yes'})

        # Verify the None value was removed and the new key was added.
        assert aggregate.constants == {
            'keep': '1',
            'add': 'yes',
        }

    # * test: remove_service_various_positions_and_missing
    @pytest.mark.parametrize(
        'initial_ids, remove_id, expected_removed, expected_remaining',
        [
            (['first', 'middle', 'last'], 'middle', 'middle', ['first', 'last']),
            (['first', 'middle', 'last'], 'first', 'first', ['middle', 'last']),
            (['first', 'middle', 'last'], 'last', 'last', ['first', 'middle']),
            (['a', 'b'], 'c', None, ['a', 'b']),
            ([], 'x', None, []),
        ],
    )
    def test_remove_service_various_positions_and_missing(
            self,
            aggr_factory,
            initial_ids,
            remove_id,
            expected_removed,
            expected_remaining,
        ):
        '''
        Test remove_service at each list position and when the id is missing.

        :param aggr_factory: Factory for a seeded AppSessionAggregate.
        :type aggr_factory: callable
        :param initial_ids: Service ids to seed, in order.
        :type initial_ids: list
        :param remove_id: The service id to remove.
        :type remove_id: str
        :param expected_removed: The removed service id, or None.
        :type expected_removed: str | None
        :param expected_remaining: Remaining service ids, in order.
        :type expected_remaining: list
        '''

        # Build each seeded service with keyword arguments.
        services = [
            AppServiceDependency(
                service_id=aid,
                module_path=f'mod.{aid}',
                class_name=f'{aid.capitalize()}Class',
                parameters={'p': aid},
            )
            for aid in initial_ids
        ]
        aggregate = aggr_factory(services=services)

        # Remove the named service.
        removed = aggregate.remove_service(remove_id)

        # A missing id returns None; a hit returns that service id.
        if expected_removed is None:
            assert removed is None
        else:
            assert removed.service_id == expected_removed

        # Remaining service ids stay in order.
        assert [service.service_id for service in aggregate.services] == expected_remaining

    # * test: add_service_appends_with_service_id_first
    def test_add_service_appends_with_service_id_first(self, test_ctx):
        '''
        Test that add_service appends a service when service_id is positional.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # The added service is absent on a fresh aggregate.
        aggregate = test_ctx.make_target()
        assert aggregate.get_service('added_svc') is None

        # Append with the first three arguments positional.
        aggregate.add_service(
            'added_svc',
            'pkg.added.module',
            'AddedService',
            parameters={'p1': 'v1'},
        )

        # Verify the appended service fields.
        added = aggregate.get_service('added_svc')
        assert added.module_path == 'pkg.added.module'
        assert added.class_name == 'AddedService'
        assert added.parameters == {'p1': 'v1'}

    # * test: add_service_defaults_parameters_to_empty
    def test_add_service_defaults_parameters_to_empty(self, test_ctx):
        '''
        Test that add_service defaults omitted parameters to an empty dict.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Add a service without a parameters argument.
        aggregate = test_ctx.make_target()
        aggregate.add_service(
            service_id='no_params_svc',
            module_path='pkg.noparams',
            class_name='NoParamsService',
        )

        # Verify parameters default to empty.
        assert aggregate.get_service('no_params_svc').parameters == {}

    # * test: set_service_update_existing_merge_params
    def test_set_service_update_existing_merge_params(self, test_ctx):
        '''
        Test that set_service merges parameters and drops None values.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Update the seeded test_attribute service.
        aggregate = test_ctx.make_target()
        aggregate.set_service(
            service_id='test_attribute',
            module_path='new.mod.path',
            class_name='NewImplementation',
            parameters={
                'old': None,
                'keep': 'yes',
                'extra': '123',
                'debug': '0',
            },
        )

        # Verify the merge kept, dropped, overrode, and added keys.
        updated = aggregate.get_service('test_attribute')
        assert updated.parameters == {
            'test_param': 'test_value',
            'keep': 'yes',
            'extra': '123',
            'debug': '0',
        }

    # * test: set_service_create_new
    def test_set_service_create_new(self, test_ctx):
        '''
        Test that set_service creates a new service when none exists.
        '''

        # Verify the service does not exist.
        aggregate = test_ctx.make_target()
        assert aggregate.get_service('brand_new') is None

        # Create via set_service.
        aggregate.set_service(
            service_id='brand_new',
            module_path='pkg.sub.module',
            class_name='FreshService',
            parameters={'p1': 'v1', 'p2': '42'},
        )

        # Verify the new service.
        created = aggregate.get_service('brand_new')
        assert created.module_path == 'pkg.sub.module'
        assert created.class_name == 'FreshService'
        assert created.parameters == {'p1': 'v1', 'p2': '42'}


# ** tester: test_app_session_config_object
@use_tester(
    type='transfer_object',
    target_cls=AppSessionConfigObject,
    aggregate_cls=AppSessionAggregate,
    sample_data=TEST_APP_SESSION_CONFIG_OBJECT_SAMPLE_DATA,
    aggregate_sample_data=AGGREGATE_SAMPLE_DATA,
    equality_fields=EQUALITY_FIELDS,
    field_normalizers=FIELD_NORMALIZERS,
)
class TestAppSessionConfigObject:
    '''
    Tests for AppSessionConfigObject mapping, round-trip, and child mapper.
    '''

    # * test: map
    def test_map(self, test_ctx):
        '''
        Verify transfer construction and mapping to the declared aggregate.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert mapping against the declared aggregate sample.
        test_ctx.assert_map()

    # * test: from_model
    def test_from_model(self, test_ctx):
        '''
        Verify aggregate conversion to the declared transfer-object type.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the transfer-object type.
        test_ctx.assert_from_model()

    # * test: round_trip
    def test_round_trip(self, test_ctx):
        '''
        Verify aggregate conversion through the transfer object and back.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the round-trip matches the aggregate sample.
        test_ctx.assert_round_trip()

    # * attribute: transfer_cls
    transfer_cls = AppSessionConfigObject

    # * attribute: aggregate_cls
    aggregate_cls = AppSessionAggregate

    # * attribute: sample_data
    sample_data = TEST_APP_SESSION_CONFIG_OBJECT_SAMPLE_DATA

    # * attribute: aggregate_sample_data
    aggregate_sample_data = AGGREGATE_SAMPLE_DATA

    # * attribute: equality_fields
    equality_fields = EQUALITY_FIELDS

    # * attribute: field_normalizers
    field_normalizers = FIELD_NORMALIZERS

    # * attribute: dependency_sample_data
    dependency_sample_data = {
        'module_path': 'example.service.module',
        'class_name': 'ExampleServiceImpl',
        'parameters': {
            'timeout': '30',
            'retries': '3',
            'ssl': '1',
        },
    }

    # * test: app_service_dependency_yaml_round_trip_via_parent
    def test_app_service_dependency_yaml_round_trip_via_parent(self, test_ctx):
        '''
        Test that parent round-trip preserves each service field.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Round-trip the aggregate through the parent config object.
        aggregate = test_ctx.make_target()
        round_tripped = AppSessionConfigObject.from_model(aggregate).map()

        # Lengths match, and each zipped pair keeps its service fields.
        assert len(round_tripped.services) == len(aggregate.services)
        for original, mapped in zip(aggregate.services, round_tripped.services):
            assert mapped.service_id == original.service_id
            assert mapped.module_path == original.module_path
            assert mapped.class_name == original.class_name
            assert mapped.parameters == original.parameters

    # * test: app_service_dependency_yaml_map_basic
    def test_app_service_dependency_yaml_map_basic(self):
        '''
        Test mapping an AppServiceDependencyConfigObject to an AppServiceDependency.
        '''

        # Create a YAML object and map it.
        yaml_obj = AppServiceDependencyConfigObject.model_validate(
            self.dependency_sample_data,
        )
        dep = yaml_obj.map(service_id='injected_svc')

        # Verify the mapped entity.
        assert isinstance(dep, AppServiceDependency)
        assert dep.service_id == 'injected_svc'
        assert dep.module_path == 'example.service.module'
        assert dep.class_name == 'ExampleServiceImpl'
        assert dep.parameters == {'timeout': '30', 'retries': '3', 'ssl': '1'}

    # * test: app_service_dependency_yaml_aliasing_params
    def test_app_service_dependency_yaml_aliasing_params(self):
        '''
        Test that the "params" alias is correctly deserialized.
        '''

        # Create YAML object using the 'params' alias.
        yaml_obj = AppServiceDependencyConfigObject.model_validate(dict(
            module_path='alias.test.mod',
            class_name='AliasImpl',
            params={'alias_key': 'value'},
        ))
        dep = yaml_obj.map(service_id='aliased_dep')

        # Verify aliased parameters were deserialized correctly.
        assert dep.parameters == {'alias_key': 'value'}

    # * test: app_service_dependency_yaml_roles_to_model_excludes
    def test_app_service_dependency_yaml_roles_to_model_excludes(self):
        '''
        Test that to_model role excludes parameters and service_id.
        '''

        # Create YAML object with fields that should be excluded.
        yaml_obj = AppServiceDependencyConfigObject.model_validate(dict(
            module_path='ex.test.mod',
            class_name='ExcludeTest',
            parameters={'secret': 'dontleak'},
            service_id='should_ignore',
        ))
        primitive = yaml_obj.to_primitive('to_model')

        # Verify excluded fields are absent.
        assert 'parameters' not in primitive
        assert 'service_id' not in primitive
        assert primitive['module_path'] == 'ex.test.mod'
        assert primitive['class_name'] == 'ExcludeTest'
