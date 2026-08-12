"""Tiferet App Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain import AppServiceDependency
from tiferet.assets import TiferetError, error
from tiferet.mappers.app import (
    AppSessionAggregate,
    AppSessionConfigObject,
    AppServiceDependencyConfigObject,
)
from tiferet.testing import AggregateTestBase, TransferObjectTestBase


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

# ** constant: session_aggregate_sample_data
SESSION_AGGREGATE_SAMPLE_DATA = {
    'id': 'test.session',
    'name': 'Test Session',
    'description': 'The test app session.',
    'flags': ['test_feature', 'test_data'],
    'logger_id': 'default',
    'services': [
        {
            'service_id': 'test_service',
            'module_path': 'test.module.path',
            'class_name': 'TestServiceClass',
            'parameters': {'test_param': 'test_value'},
        },
    ],
    'constants': {
        'SESSION_KEY': 'session_value',
        'DEBUG': '1',
    },
}

# ** constant: session_equality_fields
SESSION_EQUALITY_FIELDS = [
    'id',
    'name',
    'description',
    'logger_id',
    'flags',
    'constants',
    'services',
]

# ** constant: session_field_normalizers
SESSION_FIELD_NORMALIZERS = {
    'flags': lambda v: sorted(v or []),
    'constants': lambda v: dict(sorted((k, v) for k, v in (v or {}).items())),
    'services': lambda svcs: tuple(sorted(SVC_TUPLE(s) for s in (svcs or []))),
}


# *** classes

# ** class: TestAppSessionAggregate
class TestAppSessionAggregate(AggregateTestBase):
    '''
    Tests for AppSessionAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * attribute: aggregate_cls
    aggregate_cls = AppSessionAggregate

    # * attribute: sample_data
    sample_data = SESSION_AGGREGATE_SAMPLE_DATA

    # * attribute: equality_fields
    equality_fields = SESSION_EQUALITY_FIELDS

    # * attribute: field_normalizers
    field_normalizers = SESSION_FIELD_NORMALIZERS

    # * attribute: set_attribute_params
    set_attribute_params = [
        # valid scalars
        ('name',         'Updated Session',    None),
        ('description',  'New description',    None),
        ('logger_id',    'custom.logger',      None),
        ('flags',        ['flag1', 'flag2'],   None),
        # invalid
        ('invalid_attr', 'value',              error.INVALID_MODEL_ATTRIBUTE_ID),
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

    # * method: test_add_service
    def test_add_service(self, aggregate):
        '''
        Test that add_service appends a new service dependency.
        '''

        # Verify the service does not exist yet.
        assert aggregate.get_service('new_svc') is None
        initial_count = len(aggregate.services)

        # Add a new service.
        aggregate.add_service(
            service_id='new_svc',
            module_path='new.mod.path',
            class_name='NewClass',
            parameters={'p': '1'},
        )

        # Verify the service was added with the correct values.
        svc = aggregate.get_service('new_svc')
        assert svc is not None
        assert svc.module_path == 'new.mod.path'
        assert svc.class_name == 'NewClass'
        assert svc.parameters == {'p': '1'}
        assert len(aggregate.services) == initial_count + 1

    # * method: test_remove_service
    def test_remove_service(self, aggregate):
        '''
        Test that remove_service removes an existing service and returns it.
        '''

        # Precondition: service exists.
        assert aggregate.get_service('test_service') is not None
        initial_count = len(aggregate.services)

        # Remove the service.
        removed = aggregate.remove_service('test_service')

        # Verify it was removed and returned.
        assert removed is not None
        assert removed.service_id == 'test_service'
        assert aggregate.get_service('test_service') is None
        assert len(aggregate.services) == initial_count - 1

    # * method: test_remove_service_missing_is_idempotent
    def test_remove_service_missing_is_idempotent(self, aggregate):
        '''
        Test that remove_service returns None and leaves the list unchanged for a missing service.
        '''

        # Precondition: service does not exist.
        initial_count = len(aggregate.services)

        # Remove a non-existent service.
        removed = aggregate.remove_service('nonexistent')

        # Verify nothing changed.
        assert removed is None
        assert len(aggregate.services) == initial_count

    # * method: test_set_service_update_existing
    def test_set_service_update_existing(self, aggregate):
        '''
        Test that set_service updates an existing service and merges parameters.
        '''

        # Update the existing test_service.
        aggregate.set_service(
            service_id='test_service',
            module_path='updated.mod',
            class_name='UpdatedClass',
            parameters={'test_param': None, 'new_param': 'new_val'},
        )

        # Verify the service was updated.
        svc = aggregate.get_service('test_service')
        assert svc.module_path == 'updated.mod'
        assert svc.class_name == 'UpdatedClass'
        # test_param set to None should be removed; new_param added.
        assert svc.parameters == {'new_param': 'new_val'}

    # * method: test_set_service_create_new
    def test_set_service_create_new(self, aggregate):
        '''
        Test that set_service creates a new service when none exists.
        '''

        # Verify the service does not exist.
        assert aggregate.get_service('brand_new') is None

        # Create via set_service.
        aggregate.set_service(
            service_id='brand_new',
            module_path='brand.new.mod',
            class_name='BrandNewClass',
            parameters={'x': '42'},
        )

        # Verify the new service.
        svc = aggregate.get_service('brand_new')
        assert svc is not None
        assert svc.module_path == 'brand.new.mod'
        assert svc.class_name == 'BrandNewClass'
        assert svc.parameters == {'x': '42'}

    # * method: test_set_constants_clear
    def test_set_constants_clear(self, aggregate):
        '''
        Test that set_constants clears all constants when called with None.
        '''

        # Clear constants.
        aggregate.set_constants(None)

        # Verify they are cleared.
        assert aggregate.constants == {}

    # * method: test_set_constants_merge
    def test_set_constants_merge(self, aggregate):
        '''
        Test that set_constants merges and removes None-valued keys.
        '''

        # Merge constants.
        aggregate.set_constants({'DEBUG': None, 'NEW_KEY': 'new_val'})

        # DEBUG was set to None (removed); NEW_KEY added; SESSION_KEY preserved.
        assert 'DEBUG' not in aggregate.constants
        assert aggregate.constants['NEW_KEY'] == 'new_val'
        assert aggregate.constants['SESSION_KEY'] == 'session_value'


# ** class: TestAppSessionConfigObject
class TestAppSessionConfigObject(TransferObjectTestBase):
    '''
    Tests for AppSessionConfigObject mapping, round-trip, and child mapper.
    '''

    # * attribute: transfer_cls
    transfer_cls = AppSessionConfigObject

    # * attribute: aggregate_cls
    aggregate_cls = AppSessionAggregate

    # * attribute: sample_data
    sample_data = {
        'id': 'test.session',
        'name': 'Test Session',
        'description': 'The test app session.',
        'flags': ['test_feature', 'test_data'],
        'logger_id': 'default',
        'services': {
            'test_service': {
                'module_path': 'test.module.path',
                'class_name': 'TestServiceClass',
                'parameters': {'test_param': 'test_value'},
            },
        },
        'constants': {
            'SESSION_KEY': 'session_value',
            'DEBUG': '1',
        },
    }

    # * attribute: aggregate_sample_data
    aggregate_sample_data = SESSION_AGGREGATE_SAMPLE_DATA

    # * attribute: equality_fields
    equality_fields = SESSION_EQUALITY_FIELDS

    # * attribute: field_normalizers
    field_normalizers = SESSION_FIELD_NORMALIZERS

    # * method: test_child_mapper_map_with_service_id
    def test_child_mapper_map_with_service_id(self):
        '''
        Test AppServiceDependencyConfigObject.map(service_id=...) injects service_id.
        '''

        # Create a child config object and map it with an injected service_id.
        config_obj = AppServiceDependencyConfigObject.model_validate({
            'module_path': 'child.module',
            'class_name': 'ChildClass',
            'parameters': {'key': 'val'},
        })
        dep = config_obj.map(service_id='injected_id')

        # Verify the injected service_id and other fields.
        assert isinstance(dep, AppServiceDependency)
        assert dep.service_id == 'injected_id'
        assert dep.module_path == 'child.module'
        assert dep.class_name == 'ChildClass'
        assert dep.parameters == {'key': 'val'}

    # * method: test_round_trip_preserves_services
    def test_round_trip_preserves_services(self, aggregate):
        '''
        Test that services are preserved through the AppSessionConfigObject round-trip.
        '''

        # Convert aggregate to config object and back.
        config_top = AppSessionConfigObject.from_model(aggregate)
        round_tripped = config_top.map()

        # Verify services are preserved.
        self.assert_nested_list_matches(
            round_tripped.services,
            aggregate.services,
            key_field='service_id',
            compare_fields=['module_path', 'class_name', 'parameters'],
        )

    # *** child mapper: AppServiceDependencyConfigObject

    # ** constant: dependency_sample_data
    dependency_sample_data = {
        'module_path': 'example.service.module',
        'class_name': 'ExampleServiceImpl',
        'parameters': {'timeout': '30', 'retries': '3', 'ssl': '1'},
    }

    # ** test: app_service_dependency_yaml_map_basic
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

    # ** test: app_service_dependency_yaml_aliasing_params
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

    # ** test: app_service_dependency_yaml_roles_to_model_excludes
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
