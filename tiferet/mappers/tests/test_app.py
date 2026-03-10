"""Tiferet App Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import AppServiceDependency, DomainObject
from ...assets import TiferetError, const
from ..settings import TransferObject, DEFAULT_MODULE_PATH, DEFAULT_CLASS_NAME
from ..app import (
    AppInterfaceAggregate,
    AppInterfaceYamlObject,
    AppServiceDependencyYamlObject,
)
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = {
    'id': 'test.interface',
    'name': 'Test Interface',
    'description': 'The test app interface.',
    'module_path': DEFAULT_MODULE_PATH,
    'class_name': DEFAULT_CLASS_NAME,
    'flags': ['test_feature', 'test_data'],
    'logger_id': 'default',
    'services': [
        {
            'attribute_id': 'test_attribute',
            'module_path': 'test.module.path',
            'class_name': 'TestClassName',
            'parameters': {'test_param': 'test_value', 'debug': '1'},
        },
        {
            'attribute_id': 'logging',
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
    'module_path',
    'class_name',
    'logger_id',
    'flags',
    'constants',
    'services',
]

# ** constant: svc_tuple
def SVC_TUPLE(s):
    '''
    Normalize a single service (dict or domain object) into a comparable tuple.
    '''

    if isinstance(s, dict):
        return (
            s['attribute_id'],
            s['module_path'],
            s['class_name'],
            tuple(sorted(s.get('parameters', {}).items())),
        )
    return (
        s.attribute_id,
        s.module_path,
        s.class_name,
        tuple(sorted((s.parameters or {}).items())),
    )

# ** constant: field_normalizers
FIELD_NORMALIZERS = {
    'flags': lambda v: sorted(v or []),
    'constants': lambda v: dict(sorted((k, v) for k, v in (v or {}).items())),
    'services': lambda svcs: tuple(sorted(SVC_TUPLE(s) for s in (svcs or []))),
}


# *** classes

# ** class: TestAppInterfaceAggregate
class TestAppInterfaceAggregate(AggregateTestBase):
    '''
    Tests for AppInterfaceAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = AppInterfaceAggregate

    sample_data = AGGREGATE_SAMPLE_DATA

    equality_fields = EQUALITY_FIELDS

    field_normalizers = FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name',         'Updated Interface',      None),
        ('description',  'New description text',   None),
        ('logger_id',    'custom.logger.id',       None),
        ('flags',        ['flag1', 'flag2'],       None),
        # invalid
        ('invalid_attr', 'value',                  const.INVALID_MODEL_ATTRIBUTE_ID),
        ('module_path',  '',                       const.INVALID_APP_INTERFACE_TYPE_ID),
        ('class_name',   '   ',                    const.INVALID_APP_INTERFACE_TYPE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> AppInterfaceAggregate:
        '''
        Override to use AppInterfaceAggregate.new(app_interface_data=...) signature.
        '''

        # Create an aggregate using the custom factory.
        return AppInterfaceAggregate.new(
            app_interface_data=(data if data is not None else self.sample_data).copy()
        )

    # *** fixtures

    # ** fixture: aggr_factory
    @pytest.fixture
    def aggr_factory(self):
        '''
        Factory for creating AppInterfaceAggregate with customizable services/constants.
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
            return AppInterfaceAggregate.new(app_interface_data=data)

        return factory

    # *** domain-specific mutation tests

    # ** test: set_constants_clear_when_none
    def test_set_constants_clear_when_none(self, aggr_factory):
        '''
        Test that set_constants clears all constants when called with None.
        '''

        # Create aggregate with seeded constants and clear them.
        aggr = aggr_factory(constants={'a': '1', 'b': '2'})
        aggr.set_constants(None)

        # All constants should be cleared.
        assert aggr.constants == {}

    # ** test: set_constants_merge_and_override
    def test_set_constants_merge_and_override(self, aggr_factory):
        '''
        Test that set_constants merges new constants and overrides existing keys.
        '''

        # Create aggregate with seeded constants and merge new ones.
        aggr = aggr_factory(constants={'keep': 'orig', 'old': 'v1'})
        aggr.set_constants({'old': 'v2', 'new': '42'})

        # Existing keys should be preserved or overridden as appropriate.
        assert aggr.constants == {'keep': 'orig', 'old': 'v2', 'new': '42'}

    # ** test: set_constants_remove_none_values
    def test_set_constants_remove_none_values(self, aggr_factory):
        '''
        Test that set_constants removes keys whose new value is None.
        '''

        # Create aggregate with seeded constants and remove one via None.
        aggr = aggr_factory(constants={'keep': '1', 'drop': 'x'})
        aggr.set_constants({'drop': None, 'add': 'yes'})

        # The key set to None should be removed.
        assert aggr.constants == {'keep': '1', 'add': 'yes'}

    # ** test: remove_service_various_positions_and_missing
    @pytest.mark.parametrize(
        "initial_ids, remove_id, expected_removed, expected_remaining",
        [
            (["first", "middle", "last"], "middle", "middle", ["first", "last"]),
            (["first", "middle", "last"], "first",  "first",  ["middle", "last"]),
            (["first", "middle", "last"], "last",   "last",   ["first", "middle"]),
            (["a", "b"],                  "c",      None,     ["a", "b"]),
            ([],                          "x",      None,     []),
        ]
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
        '''

        # Build services from the initial ids.
        services = [
            DomainObject.new(
                AppServiceDependency,
                attribute_id=aid,
                module_path=f"mod.{aid}",
                class_name=f"{aid.capitalize()}Class",
                parameters={'p': aid},
            )
            for aid in initial_ids
        ]

        # Create aggregate and attempt removal.
        aggr = aggr_factory(services=services)
        removed = aggr.remove_service(remove_id)

        # Verify the removed service (or None).
        if expected_removed:
            assert removed is not None
            assert removed.attribute_id == expected_removed
        else:
            assert removed is None

        # Verify the remaining services.
        assert [s.attribute_id for s in aggr.services] == expected_remaining

    # ** test: set_service_update_existing_merge_params
    def test_set_service_update_existing_merge_params(self, aggregate):
        '''
        Test that set_service updates an existing service and merges parameters.
        '''

        # Update the existing test_attribute service with new type and merged parameters.
        aggregate.set_service(
            attribute_id='test_attribute',
            module_path='new.mod.path',
            class_name='NewImplementation',
            parameters={'old': None, 'keep': 'yes', 'extra': '123', 'debug': '0'},
        )

        # Verify type fields were updated.
        svc = aggregate.get_service('test_attribute')
        assert svc.module_path == 'new.mod.path'
        assert svc.class_name == 'NewImplementation'

        # Existing params merged, None-valued keys removed, new keys added.
        assert svc.parameters == {
            'test_param': 'test_value',
            'keep': 'yes',
            'extra': '123',
            'debug': '0',
        }

    # ** test: set_service_create_new
    def test_set_service_create_new(self, aggregate):
        '''
        Test that set_service creates a new service when none exists.
        '''

        # Verify the service does not exist yet.
        assert aggregate.get_service('brand_new') is None

        # Create a new service via set_service.
        aggregate.set_service(
            attribute_id='brand_new',
            module_path='pkg.sub.module',
            class_name='FreshService',
            parameters={'p1': 'v1', 'p2': '42'},
        )

        # Verify the new service was created with the correct values.
        svc = aggregate.get_service('brand_new')
        assert svc is not None
        assert svc.module_path == 'pkg.sub.module'
        assert svc.class_name == 'FreshService'
        assert svc.parameters == {'p1': 'v1', 'p2': '42'}


# ** class: TestAppInterfaceYamlObject
class TestAppInterfaceYamlObject(TransferObjectTestBase):
    '''
    Tests for AppInterfaceYamlObject mapping, round-trip, and nested AppServiceDependencyYamlObject.
    '''

    transfer_cls = AppInterfaceYamlObject
    aggregate_cls = AppInterfaceAggregate

    # YAML-format sample data (services as dict keyed by attribute_id).
    sample_data = {
        'id': 'test.interface',
        'name': 'Test Interface',
        'description': 'The test app interface.',
        'module_path': DEFAULT_MODULE_PATH,
        'class_name': DEFAULT_CLASS_NAME,
        'flags': ['test_feature', 'test_data'],
        'logger_id': 'default',
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
        'constants': {
            'APP_NAME': 'Tiferet Test',
            'VERSION': '2.0.0a1',
            'DEBUG': '1',
        },
    }

    # Aggregate-format expected data (services as list, defaults filled in).
    aggregate_sample_data = AGGREGATE_SAMPLE_DATA

    equality_fields = EQUALITY_FIELDS

    field_normalizers = FIELD_NORMALIZERS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> AppInterfaceAggregate:
        '''
        Override to use AppInterfaceAggregate.new(app_interface_data=...) signature.
        '''

        # Create an aggregate using the custom factory.
        return AppInterfaceAggregate.new(
            app_interface_data=(data if data is not None else self.aggregate_sample_data).copy()
        )

    # *** child mapper: AppServiceDependencyYamlObject

    # ** constant: dependency_sample_data
    dependency_sample_data = {
        'module_path': 'example.service.module',
        'class_name': 'ExampleServiceImpl',
        'parameters': {'timeout': '30', 'retries': '3', 'ssl': '1'},
    }

    # ** test: app_service_dependency_yaml_map_basic
    def test_app_service_dependency_yaml_map_basic(self):
        '''
        Test mapping an AppServiceDependencyYamlObject to an AppServiceDependency.
        '''

        # Create a YAML object and map it.
        yaml_obj = TransferObject.from_data(
            AppServiceDependencyYamlObject,
            **self.dependency_sample_data,
        )
        dep = yaml_obj.map(attribute_id='injected_svc')

        # Verify the mapped entity.
        assert isinstance(dep, AppServiceDependency)
        assert dep.attribute_id == 'injected_svc'
        assert dep.module_path == 'example.service.module'
        assert dep.class_name == 'ExampleServiceImpl'
        assert dep.parameters == {'timeout': '30', 'retries': '3', 'ssl': '1'}

    # ** test: app_service_dependency_yaml_aliasing_params
    def test_app_service_dependency_yaml_aliasing_params(self):
        '''
        Test that the "params" serialized_name alias is correctly deserialized.
        '''

        # Create YAML object using the 'params' alias.
        yaml_obj = TransferObject.from_data(
            AppServiceDependencyYamlObject,
            module_path='alias.test.mod',
            class_name='AliasImpl',
            params={'alias_key': 'value'},
        )
        dep = yaml_obj.map(attribute_id='aliased_dep')

        # Verify aliased parameters were deserialized correctly.
        assert dep.parameters == {'alias_key': 'value'}

    # ** test: app_service_dependency_yaml_roles_to_model_excludes
    def test_app_service_dependency_yaml_roles_to_model_excludes(self):
        '''
        Test that to_model role excludes parameters and attribute_id.
        '''

        # Create YAML object with fields that should be excluded.
        yaml_obj = TransferObject.from_data(
            AppServiceDependencyYamlObject,
            module_path='ex.test.mod',
            class_name='ExcludeTest',
            parameters={'secret': 'dontleak'},
            attribute_id='should_ignore',
        )
        primitive = yaml_obj.to_primitive('to_model')

        # Verify excluded fields are absent.
        assert 'parameters' not in primitive
        assert 'attribute_id' not in primitive
        assert primitive['module_path'] == 'ex.test.mod'
        assert primitive['class_name'] == 'ExcludeTest'

    # ** test: app_service_dependency_yaml_round_trip_via_parent
    def test_app_service_dependency_yaml_round_trip_via_parent(self, aggregate):
        '''
        Test that services are preserved through the parent AppInterfaceYamlObject round-trip.
        '''

        # Convert aggregate to YAML object and back.
        yaml_top = AppInterfaceYamlObject.from_model(aggregate)
        round_tripped = yaml_top.map()

        # Use nested helper to verify services list preserved.
        self.assert_nested_list_matches(
            round_tripped.services,
            aggregate.services,
            key_field='attribute_id',
            compare_fields=['module_path', 'class_name', 'parameters'],
        )
