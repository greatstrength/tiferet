"""Tiferet App Mapper Tests"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from tiferet.domain import (
    ATTRIBUTE_NOT_SETTABLE_ID,
    INVALID_MODEL_VALUE_ID,
    AppServiceDependency,
    ModelError,
)
from tiferet.mappers.app import (
    AppSessionAggregate,
    AppSessionConfigObject,
    AppServiceDependencyConfigObject,
)
from tiferet.blueprints.tester import use_tester

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

# *** fixtures

# ** fixture: app_session_aggregate
@pytest.fixture
def app_session_aggregate() -> AppSessionAggregate:
    '''
    Fixture for an app session aggregate with two ordered services.

    :return: The app session aggregate.
    :rtype: AppSessionAggregate
    '''

    # Create the aggregate with test_attribute then logging.
    return AppSessionAggregate(
        id='test.interface',
        name='Test Interface',
        services=[
            AppServiceDependency(
                service_id='test_attribute',
                module_path='test.module.path',
                class_name='TestClassName',
                parameters={'test_param': 'test_value', 'debug': '1'},
            ),
            AppServiceDependency(
                service_id='logging',
                module_path='tiferet.utils.logging',
                class_name='LoggingService',
                parameters={},
            ),
        ],
    )

# ** fixture: overlay_session
@pytest.fixture
def overlay_session() -> AppSessionAggregate:
    '''
    Fixture for an app session aggregate whose services carry overlay parameters.

    :return: The app session aggregate.
    :rtype: AppSessionAggregate
    '''

    # Create the aggregate with first then second.
    return AppSessionAggregate(
        id='test.interface',
        name='Test Interface',
        services=[
            AppServiceDependency(
                service_id='first',
                module_path='mod.first',
                class_name='FirstClass',
                parameters={'keep': 'original', 'override': 'old'},
            ),
            AppServiceDependency(
                service_id='second',
                module_path='mod.second',
                class_name='SecondClass',
                parameters={'p': 'second'},
            ),
        ],
    )

# ** fixture: repeat_session
@pytest.fixture
def repeat_session() -> AppSessionAggregate:
    '''
    Fixture for an app session aggregate with a repeated service id around another service.

    :return: The app session aggregate.
    :rtype: AppSessionAggregate
    '''

    # Create the aggregate with dup_svc, other_svc, then dup_svc again.
    return AppSessionAggregate(
        id='test.interface',
        name='Test Interface',
        services=[
            AppServiceDependency(
                service_id='dup_svc',
                module_path='mod.dup',
                class_name='DupOne',
                parameters={'p': 'one'},
            ),
            AppServiceDependency(
                service_id='other_svc',
                module_path='mod.other',
                class_name='OtherClass',
                parameters={'p': 'other'},
            ),
            AppServiceDependency(
                service_id='dup_svc',
                module_path='mod.dup',
                class_name='DupTwo',
                parameters={'p': 'two'},
            ),
        ],
    )

# ** fixture: reversed_session
@pytest.fixture
def reversed_session() -> AppSessionAggregate:
    '''
    Fixture for an app session aggregate with the two services in reverse order.

    :return: The app session aggregate.
    :rtype: AppSessionAggregate
    '''

    # Create the aggregate with logging then test_attribute.
    return AppSessionAggregate(
        id='test.interface',
        name='Test Interface',
        services=[
            AppServiceDependency(
                service_id='logging',
                module_path='tiferet.utils.logging',
                class_name='LoggingService',
                parameters={},
            ),
            AppServiceDependency(
                service_id='test_attribute',
                module_path='test.module.path',
                class_name='TestClassName',
                parameters={'test_param': 'test_value', 'debug': '1'},
            ),
        ],
    )

# ** fixture: app_session_config
@pytest.fixture
def app_session_config() -> AppSessionConfigObject:
    '''
    Fixture for an app session config object with services keyed in declared order.

    :return: The app session config object.
    :rtype: AppSessionConfigObject
    '''

    # Create the config object with test_attribute then logging.
    return AppSessionConfigObject.model_validate({
        'id': 'test.interface',
        'name': 'Test Interface',
        'services': {
            'test_attribute': {
                'module_path': 'test.module.path',
                'class_name': 'TestClassName',
                'parameters': {'test_param': 'test_value', 'debug': '1'},
            },
            'logging': {
                'module_path': 'tiferet.utils.logging',
                'class_name': 'LoggingService',
                'parameters': {},
            },
        },
    })

# ** fixture: reversed_app_session_config
@pytest.fixture
def reversed_app_session_config() -> AppSessionConfigObject:
    '''
    Fixture for an app session config object with attrs keyed in reverse order.

    :return: The app session config object.
    :rtype: AppSessionConfigObject
    '''

    # Create the config object with logging then test_attribute.
    return AppSessionConfigObject.model_validate({
        'id': 'test.interface',
        'name': 'Test Interface',
        'attrs': {
            'logging': {
                'module_path': 'tiferet.utils.logging',
                'class_name': 'LoggingService',
                'parameters': {},
            },
            'test_attribute': {
                'module_path': 'test.module.path',
                'class_name': 'TestClassName',
                'params': {'test_param': 'test_value', 'debug': '1'},
            },
        },
    })

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
        Test that set_constants clears all constants when called with None.

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
        Test that set_constants merges new constants and overrides existing keys.

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
        Test that set_constants removes keys whose new value is None.

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
        Test that remove_service removes and returns a matching service, or None if missing.

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
        Test that add_service appends a dependency, taking service_id first so its positional order matches set_service.

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
        Test that add_service defaults parameters to an empty dict when omitted.

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
        Test that set_service updates an existing service and merges parameters.

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

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
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

    # * test: add_service_existing_id_raises
    def test_add_service_existing_id_raises(self, app_session_aggregate):
        '''
        Test that add_service rejects an existing service id without changing the services list.

        :param app_session_aggregate: The seeded app session aggregate.
        :type app_session_aggregate: AppSessionAggregate
        '''

        # Record the original ordered service fields.
        original = [service.model_dump() for service in app_session_aggregate.services]

        # Add a service under an existing service id.
        with pytest.raises(ModelError) as exc_info:
            app_session_aggregate.add_service(
                'test_attribute',
                'pkg.other.module',
                'OtherService',
                parameters={'other': 'value'},
            )

        # Assert the exact already-exists model error.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert json.loads(str(error))['message'] == (
            "Service dependency 'test_attribute' already exists in app session 'test.interface'."
        )
        assert error.kwargs == {'attribute': 'services', 'service_id': 'test_attribute'}

        # The services list is unchanged.
        assert [service.model_dump() for service in app_session_aggregate.services] == original

    # * test: add_service_drops_none_values
    def test_add_service_drops_none_values(self, app_session_aggregate):
        '''
        Test that add_service omits None-valued parameters and creates empty parameters for None.

        :param app_session_aggregate: The seeded app session aggregate.
        :type app_session_aggregate: AppSessionAggregate
        '''

        # Add one service with a None-valued parameter and one with None parameters.
        app_session_aggregate.add_service(
            'pruned_svc',
            'pkg.pruned',
            'PrunedService',
            parameters={'p1': 'v1', 'gone': None},
        )
        app_session_aggregate.add_service(
            'null_svc',
            'pkg.null',
            'NullService',
            parameters=None,
        )

        # Verify the created service fields.
        pruned = app_session_aggregate.get_service('pruned_svc')
        assert (pruned.service_id, pruned.module_path, pruned.class_name) == ('pruned_svc', 'pkg.pruned', 'PrunedService')
        assert pruned.parameters == {'p1': 'v1'}
        assert isinstance(pruned.parameters, dict)
        null = app_session_aggregate.get_service('null_svc')
        assert (null.service_id, null.module_path, null.class_name) == ('null_svc', 'pkg.null', 'NullService')
        assert null.parameters == {}
        assert isinstance(null.parameters, dict)

        # The new services are appended in order.
        assert [service.service_id for service in app_session_aggregate.services] == [
            'test_attribute',
            'logging',
            'pruned_svc',
            'null_svc',
        ]

    # * test: set_service_existing_none_parameters_leaves_existing
    def test_set_service_existing_none_parameters_leaves_existing(self, app_session_aggregate):
        '''
        Test that set_service updates type fields and leaves existing parameters unchanged for None.

        :param app_session_aggregate: The seeded app session aggregate.
        :type app_session_aggregate: AppSessionAggregate
        '''

        # Update the existing service with None parameters.
        app_session_aggregate.set_service(
            'test_attribute',
            module_path='new.mod.path',
            class_name='NewImplementation',
            parameters=None,
        )

        # The type fields are updated and the parameters are unchanged.
        updated = app_session_aggregate.get_service('test_attribute')
        assert updated.module_path == 'new.mod.path'
        assert updated.class_name == 'NewImplementation'
        assert updated.parameters == {'test_param': 'test_value', 'debug': '1'}
        assert list(updated.parameters) == ['test_param', 'debug']

    # * test: set_service_existing_overlay_in_place
    def test_set_service_existing_overlay_in_place(self, overlay_session):
        '''
        Test that set_service overlays parameters on the existing service instance without moving it.

        :param overlay_session: The app session aggregate with overlay parameters.
        :type overlay_session: AppSessionAggregate
        '''

        # Retain the original first service instance.
        first = overlay_session.services[0]

        # Overlay the first service and apply an empty overlay to the second.
        overlay_session.set_service(
            'first',
            module_path='mod.first.updated',
            class_name='FirstUpdated',
            parameters={'override': 'new', 'remove': None, 'add': 'added'},
        )
        overlay_session.set_service(
            'second',
            module_path='mod.second',
            class_name='SecondClass',
            parameters={},
        )

        # The first service is updated in place with the overlaid parameters.
        updated = overlay_session.services[0]
        assert updated is first
        assert updated.module_path == 'mod.first.updated'
        assert updated.class_name == 'FirstUpdated'
        assert updated.parameters == {'keep': 'original', 'override': 'new', 'add': 'added'}
        assert list(updated.parameters) == ['keep', 'override', 'add']

        # The empty overlay preserves the second service parameters, and the order is unchanged.
        assert overlay_session.get_service('second').parameters == {'p': 'second'}
        assert [service.service_id for service in overlay_session.services] == ['first', 'second']

    # * test: set_service_create_drops_none_values
    def test_set_service_create_drops_none_values(self, app_session_aggregate):
        '''
        Test that set_service creates services omitting None-valued parameters and with empty parameters for None.

        :param app_session_aggregate: The seeded app session aggregate.
        :type app_session_aggregate: AppSessionAggregate
        '''

        # Create one service with a None-valued parameter and one with None parameters.
        app_session_aggregate.set_service(
            'pruned_new',
            module_path='pkg.pruned',
            class_name='PrunedService',
            parameters={'p1': 'v1', 'gone': None},
        )
        app_session_aggregate.set_service(
            'null_new',
            module_path='pkg.null',
            class_name='NullService',
            parameters=None,
        )

        # Verify the created service fields.
        pruned = app_session_aggregate.get_service('pruned_new')
        assert (pruned.service_id, pruned.module_path, pruned.class_name) == ('pruned_new', 'pkg.pruned', 'PrunedService')
        assert pruned.parameters == {'p1': 'v1'}
        assert isinstance(pruned.parameters, dict)
        null = app_session_aggregate.get_service('null_new')
        assert (null.service_id, null.module_path, null.class_name) == ('null_new', 'pkg.null', 'NullService')
        assert null.parameters == {}
        assert isinstance(null.parameters, dict)

        # The new services are appended in order.
        assert [service.service_id for service in app_session_aggregate.services] == [
            'test_attribute',
            'logging',
            'pruned_new',
            'null_new',
        ]

    # * test: remove_service_drops_every_match
    def test_remove_service_drops_every_match(self, repeat_session):
        '''
        Test that remove_service removes every matching service and returns the first match.

        :param repeat_session: The app session aggregate with a repeated service id.
        :type repeat_session: AppSessionAggregate
        '''

        # Retain the original first matching service instance.
        first = repeat_session.services[0]

        # Remove the repeated service id.
        removed = repeat_session.remove_service('dup_svc')

        # The first match is returned.
        assert removed is first
        assert removed.model_dump() == {
            'service_id': 'dup_svc',
            'module_path': 'mod.dup',
            'class_name': 'DupOne',
            'parameters': {'p': 'one'},
        }

        # Only the other service survives.
        assert [service.model_dump() for service in repeat_session.services] == [
            {
                'service_id': 'other_svc',
                'module_path': 'mod.other',
                'class_name': 'OtherClass',
                'parameters': {'p': 'other'},
            },
        ]

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

    # * test: app_service_dependency_yaml_round_trip_via_parent
    def test_app_service_dependency_yaml_round_trip_via_parent(self, test_ctx):
        '''
        Test that services are preserved through the parent AppSessionConfigObject round-trip.

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

    # * test: from_model_key_order
    def test_from_model_key_order(self, app_session_aggregate, reversed_session):
        '''
        Test that from_model keys services by service id in list order.

        :param app_session_aggregate: The seeded app session aggregate.
        :type app_session_aggregate: AppSessionAggregate
        :param reversed_session: The app session aggregate with services reversed.
        :type reversed_session: AppSessionAggregate
        '''

        # Convert each source and compare its keys and keyed child fields.
        for source, expected in (
            (app_session_aggregate, ['test_attribute', 'logging']),
            (reversed_session, ['logging', 'test_attribute']),
        ):
            config = AppSessionConfigObject.from_model(source)
            assert list(config.services) == expected
            for service in source.services:
                child = config.services[service.service_id]
                assert child.module_path == service.module_path
                assert child.class_name == service.class_name
                assert child.parameters == service.parameters

    # * test: map_key_order
    def test_map_key_order(self, app_session_config, reversed_app_session_config):
        '''
        Test that map orders services by the declared mapping-key order.

        :param app_session_config: The app session config object.
        :type app_session_config: AppSessionConfigObject
        :param reversed_app_session_config: The app session config object with attrs reversed.
        :type reversed_app_session_config: AppSessionConfigObject
        '''

        # Map each config object.
        aggregate = app_session_config.map()
        reversed_aggregate = reversed_app_session_config.map()

        # The service order follows each mapping-key order.
        assert [service.service_id for service in aggregate.services] == ['test_attribute', 'logging']
        assert [service.service_id for service in reversed_aggregate.services] == ['logging', 'test_attribute']

        # The reversed params alias supplies the test_attribute parameters.
        assert reversed_aggregate.get_service('test_attribute').parameters == {
            'test_param': 'test_value',
            'debug': '1',
        }

    # * test: from_model_repeated_service_id_raises
    def test_from_model_repeated_service_id_raises(self, repeat_session):
        '''
        Test that from_model rejects a repeated service id without changing the source services.

        :param repeat_session: The app session aggregate with a repeated service id.
        :type repeat_session: AppSessionAggregate
        '''

        # Record the original ordered service fields.
        original = [service.model_dump() for service in repeat_session.services]

        # Convert the source with a repeated service id.
        with pytest.raises(ModelError) as exc_info:
            AppSessionConfigObject.from_model(repeat_session)

        # Assert the exact repeated-identity model error.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert json.loads(str(error))['message'] == (
            "Service dependency 'dup_svc' is repeated in app session 'test.interface'."
        )
        assert error.kwargs == {'attribute': 'services', 'service_id': 'dup_svc'}

        # The source services are unchanged.
        assert [service.model_dump() for service in repeat_session.services] == original
