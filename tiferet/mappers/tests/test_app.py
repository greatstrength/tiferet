"""Tiferet App Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import AppServiceDependency, DomainObject
from ...assets import TiferetError
from ..settings import TransferObject, DEFAULT_MODULE_PATH, DEFAULT_CLASS_NAME
from ..app import AppInterfaceAggregate, AppInterfaceYamlObject, AppServiceDependencyYamlObject

# *** fixtures

# ** fixture: app_interface_yaml_obj
@pytest.fixture
def app_interface_yaml_obj() -> AppInterfaceYamlObject:
    '''
    A fixture for an app interface yaml data object.

    :return: The app interface yaml data object.
    :rtype: AppInterfaceYamlObject
    '''

    # Create and return the app interface yaml data object.
    return TransferObject.from_data(
        AppInterfaceYamlObject,
        id='app_yaml_data',
        name='Test App YAML Data',
        module_path=DEFAULT_MODULE_PATH,
        class_name=DEFAULT_CLASS_NAME,
        flags=['test_app_yaml_data'],
        services=dict(
            test_attribute=dict(
                module_path='test_module_path',
                class_name='test_class_name',
                parameters=dict(
                    test_param='test_value',
                )
            )
        ),
        constants=dict(
            test_const='test_const_value',
        )
    )

# ** fixture: app_interface_aggr
@pytest.fixture
def app_interface_aggr() -> AppInterfaceAggregate:
    '''
    Fixture to provide a sample AppInterface model for round-trip testing.

    :return: A sample AppInterface instance.
    :rtype: AppInterfaceAggregate
    '''

    # Create and return a sample AppInterfaceAggregate instance.
    app_interface_data = {
        'id': 'test.interface',
        'name': 'Test Interface',
        'description': 'The test app interface.',
        'module_path': DEFAULT_MODULE_PATH,
        'class_name': DEFAULT_CLASS_NAME,
        'flags': ['test_feature', 'test_data'],
        'services': [
             {
                'attribute_id': 'test_attribute',
                'module_path': 'test_module_path',
                'class_name': 'test_class_name',
                'parameters': {
                    'test_param': 'test_value',
                },
            }
        ],
        'constants': {
            'TEST_CONST': 'test_const_value',
        }
    }

    return AppInterfaceAggregate.new(app_interface_data=app_interface_data)

# *** tests

# ** test: app_interface_aggregate_new
def test_app_interface_aggregate_new(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test creating an AppInterfaceAggregate.

    :param app_interface_aggr: The app interface aggregate fixture.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Assert the aggregate is correctly instantiated.
    assert isinstance(app_interface_aggr, AppInterfaceAggregate)
    assert app_interface_aggr.id == 'test.interface'
    assert app_interface_aggr.name == 'Test Interface'
    assert app_interface_aggr.module_path == DEFAULT_MODULE_PATH
    assert app_interface_aggr.class_name == DEFAULT_CLASS_NAME

# ** test: app_interface_aggregate_set_attribute_valid_updates
def test_app_interface_aggregate_set_attribute_valid_updates(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_attribute successfully updates supported attributes and validates the aggregate.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Update multiple supported attributes.
    app_interface_aggr.set_attribute('name', 'Updated App')
    app_interface_aggr.set_attribute('description', 'Updated description')
    app_interface_aggr.set_attribute('logger_id', 'updated_logger')
    app_interface_aggr.set_attribute('flags', ['updated_flag'])

    # Assert that the attributes were updated.
    assert app_interface_aggr.name == 'Updated App'
    assert app_interface_aggr.description == 'Updated description'
    assert app_interface_aggr.logger_id == 'updated_logger'
    assert app_interface_aggr.flags == ['updated_flag']

# ** test: app_interface_aggregate_set_attribute_invalid_name
def test_app_interface_aggregate_set_attribute_invalid_name(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_attribute rejects an unsupported attribute name.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Attempt to update an unsupported attribute and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface_aggr.set_attribute('invalid_attribute', 'value')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'
    assert exc_info.value.kwargs.get('attribute') == 'invalid_attribute'

# ** test: app_interface_aggregate_set_attribute_invalid_module_path
def test_app_interface_aggregate_set_attribute_invalid_module_path(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_attribute enforces non-empty string for module_path.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Attempt to set an empty module_path and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface_aggr.set_attribute('module_path', '')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_APP_INTERFACE_TYPE'
    assert exc_info.value.kwargs.get('attribute') == 'module_path'

# ** test: app_interface_aggregate_set_attribute_invalid_class_name
def test_app_interface_aggregate_set_attribute_invalid_class_name(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_attribute enforces non-empty string for class_name.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Attempt to set an empty class_name and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface_aggr.set_attribute('class_name', '   ')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_APP_INTERFACE_TYPE'
    assert exc_info.value.kwargs.get('attribute') == 'class_name'

# ** test: app_interface_aggregate_set_constants_clears_when_none
def test_app_interface_aggregate_set_constants_clears_when_none(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_constants clears all constants when called with None.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Seed existing constants on the aggregate.
    app_interface_aggr.constants = {
        'existing': 'value',
        'another': 'value',
    }

    # Call set_constants with None to clear all constants.
    app_interface_aggr.set_constants(None)

    # All constants should be cleared.
    assert app_interface_aggr.constants == {}

# ** test: app_interface_aggregate_set_constants_merges_and_overrides
def test_app_interface_aggregate_set_constants_merges_and_overrides(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_constants merges new constants and overrides existing keys.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Seed existing constants on the aggregate.
    app_interface_aggr.constants = {
        'keep': 'original',
        'override': 'old',
    }

    # Merge new constants, overriding existing keys and adding new ones.
    app_interface_aggr.set_constants(
        {
            'override': 'new',
            'add': 'added',
        },
    )

    # Existing keys should be preserved or overridden as appropriate.
    assert app_interface_aggr.constants == {
        'keep': 'original',
        'override': 'new',
        'add': 'added',
    }

# ** test: app_interface_aggregate_set_constants_removes_none_valued_keys
def test_app_interface_aggregate_set_constants_removes_none_valued_keys(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_constants removes keys whose new value is None.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Seed existing constants on the aggregate.
    app_interface_aggr.constants = {
        'keep': 'value',
        'remove': 'value',
    }

    # Provide an update that sets one key to None.
    app_interface_aggr.set_constants(
        {
            'remove': None,
        },
    )

    # The key set to None should be removed, and others preserved.
    assert app_interface_aggr.constants == {
        'keep': 'value',
    }

# ** test: app_interface_aggregate_set_constants_mixed_operations
def test_app_interface_aggregate_set_constants_mixed_operations(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test that set_constants supports mixed operations of clearing, overriding,
    adding, and preserving keys in a single call.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Seed existing constants on the aggregate.
    app_interface_aggr.constants = {
        'remove': 'value',
        'override': 'old',
        'preserve': 'present',
    }

    # Perform a mixed update.
    app_interface_aggr.set_constants(
        {
            'remove': None,
            'override': 'new',
            'add': 'added',
        },
    )

    # Verify mixed behavior across keys.
    assert app_interface_aggr.constants == {
        'override': 'new',
        'preserve': 'present',
        'add': 'added',
    }

# ** test: app_attribute_yaml_object_map
def test_app_attribute_yaml_object_map():
    '''
    Test mapping an AppServiceDependencyYamlObject to an AppServiceDependency entity.
    '''

    # Create an AppServiceDependencyYamlObject.
    yaml_obj = TransferObject.from_data(
        AppServiceDependencyYamlObject,
        module_path='test.module',
        class_name='TestClass',
        parameters={'key': 'value'},
    )

    # Map to entity.
    entity = yaml_obj.map(attribute_id='test_attr')

    # Assert the mapping is correct.
    assert isinstance(entity, AppServiceDependency)
    assert entity.attribute_id == 'test_attr'
    assert entity.module_path == 'test.module'
    assert entity.class_name == 'TestClass'
    assert entity.parameters == {'key': 'value'}

# ** test: app_interface_yaml_object_from_model
def test_app_interface_yaml_object_from_model(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test creating an AppInterfaceYamlObject from an AppInterfaceAggregate.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Create YamlObject from aggregate using the custom from_model method.
    yaml_obj = AppInterfaceYamlObject.from_model(app_interface_aggr)

    # Assert the conversion is correct.
    assert isinstance(yaml_obj, AppInterfaceYamlObject)
    assert yaml_obj.id == app_interface_aggr.id
    assert yaml_obj.name == app_interface_aggr.name
    assert yaml_obj.module_path == app_interface_aggr.module_path
    assert yaml_obj.class_name == app_interface_aggr.class_name
    assert 'test_attribute' in yaml_obj.services
    assert yaml_obj.constants == app_interface_aggr.constants

# ** test: app_settings_yaml_data_map
def test_app_settings_yaml_data_map(app_interface_yaml_obj: AppInterfaceYamlObject):
    '''
    Tests the mapping of an app interface yaml data object to an app interface object.

    :param app_interface_yaml_obj: The app interface yaml data object.
    :type app_interface_yaml_obj: AppInterfaceYamlObject
    '''

    # Map the app interface yaml data to an app interface object.
    app_settings = app_interface_yaml_obj.map()

    # Assert the mapped app interface is valid.
    assert isinstance(app_settings, AppInterfaceAggregate)
    assert app_settings.id == app_interface_yaml_obj.id
    assert app_settings.name == app_interface_yaml_obj.name
    assert app_settings.flags == app_interface_yaml_obj.flags

    # Assert that the module path and class name are correctly set.
    assert app_settings.module_path == DEFAULT_MODULE_PATH
    assert app_settings.class_name == DEFAULT_CLASS_NAME

    # Assert that the mapped service contains the correct data.
    svc = next(
        svc for svc in app_settings.services if svc.attribute_id == 'test_attribute')
    assert svc is not None
    assert isinstance(svc, AppServiceDependency)
    assert svc.module_path == 'test_module_path'
    assert svc.class_name == 'test_class_name'

    # Assert that the parameters are correctly set.
    param = next(
        (p for p in svc.parameters if p == 'test_param'), None)
    assert param is not None
    assert param == 'test_param'
    assert svc.parameters['test_param'] == 'test_value'

    # Assert that the constants are correctly set.
    assert app_settings.constants
    assert app_settings.constants['test_const'] == 'test_const_value'

# ** test: app_interface_aggregate_remove_service_removes_matching_from_middle_start_end
def test_app_interface_aggregate_remove_service_removes_matching_from_middle_start_end() -> None:
    '''
    Test that remove_service removes and returns services when attribute_id
    matches for items in the middle, start, and end positions.
    '''

    # Create three service dependencies with distinct attribute_ids.
    first = DomainObject.new(
        AppServiceDependency,
        attribute_id='first',
        module_path='module.first',
        class_name='FirstClass',
    )
    middle = DomainObject.new(
        AppServiceDependency,
        attribute_id='middle',
        module_path='module.middle',
        class_name='MiddleClass',
    )
    last = DomainObject.new(
        AppServiceDependency,
        attribute_id='last',
        module_path='module.last',
        class_name='LastClass',
    )

    # Create an app interface aggregate seeded with the three services.
    app_interface = AppInterfaceAggregate.new(app_interface_data=dict(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        services=[first, middle, last],
    ))

    # Remove the middle service and verify it is returned and removed.
    removed_middle = app_interface.remove_service('middle')
    assert removed_middle is not None
    assert removed_middle.attribute_id == 'middle'
    assert [svc.attribute_id for svc in app_interface.services] == ['first', 'last']

    # Remove the first service and verify it is returned and removed.
    removed_first = app_interface.remove_service('first')
    assert removed_first is not None
    assert removed_first.attribute_id == 'first'
    assert [svc.attribute_id for svc in app_interface.services] == ['last']

    # Remove the last remaining service and verify it is returned and removed.
    removed_last = app_interface.remove_service('last')
    assert removed_last is not None
    assert removed_last.attribute_id == 'last'
    assert app_interface.services == []

# ** test: app_interface_aggregate_remove_service_missing_returns_none_and_does_not_modify
def test_app_interface_aggregate_remove_service_missing_returns_none_and_does_not_modify() -> None:
    '''
    Test that remove_service returns None and leaves the services list
    unchanged when no service with the given attribute_id exists.
    '''

    # Create two service dependencies and an app interface aggregate seeded with them.
    first = DomainObject.new(
        AppServiceDependency,
        attribute_id='first',
        module_path='module.first',
        class_name='FirstClass',
    )
    second = DomainObject.new(
        AppServiceDependency,
        attribute_id='second',
        module_path='module.second',
        class_name='SecondClass',
    )
    app_interface = AppInterfaceAggregate.new(app_interface_data=dict(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        services=[first, second],
    ))

    # Capture the original list of services for comparison.
    original_services = list(app_interface.services)

    # Attempt to remove a non-existent service.
    result = app_interface.remove_service('missing')

    # Verify the method returns None and the list is unchanged.
    assert result is None
    assert app_interface.services == original_services

# ** test: app_interface_aggregate_remove_service_on_empty_services_returns_none
def test_app_interface_aggregate_remove_service_on_empty_services_returns_none() -> None:
    '''
    Test that remove_service returns None when called on an app interface aggregate with
    an empty services list.
    '''

    # Create an app interface aggregate with no services.
    app_interface = AppInterfaceAggregate.new(app_interface_data=dict(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        services=[],
    ))

    # Attempt to remove any service and verify None is returned.
    result = app_interface.remove_service('anything')
    assert result is None

# ** test: app_interface_aggregate_set_service_updates_existing_and_merges_parameters
def test_app_interface_aggregate_set_service_updates_existing_and_merges_parameters(
    app_interface_aggr: AppInterfaceAggregate,
) -> None:
    '''
    Test that set_service updates an existing dependency and merges parameters,
    removing keys whose values are None.

    :param app_interface_aggr: The app interface aggregate to test.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Seed existing parameters on the dependency.
    dependency = app_interface_aggr.get_service('test_attribute')
    dependency.parameters = {
        'keep': 'original',
        'override': 'old',
        'remove': 'value',
    }

    # Perform an update with new type information and parameter overrides.
    app_interface_aggr.set_service(
        attribute_id='test_attribute',
        module_path='updated.module',
        class_name='UpdatedClass',
        parameters={
            'override': 'new',
            'remove': None,
            'add': 'added',
        },
    )

    # Reload the dependency and assert type fields were updated.
    updated = app_interface_aggr.get_service('test_attribute')
    assert updated.module_path == 'updated.module'
    assert updated.class_name == 'UpdatedClass'

    # Existing parameters should be merged, with None-valued keys removed.
    assert updated.parameters == {
        'keep': 'original',
        'override': 'new',
        'add': 'added',
    }

# ** test: app_interface_aggregate_set_service_clears_parameters_when_none
def test_app_interface_aggregate_set_service_clears_parameters_when_none(
    app_interface_aggr: AppInterfaceAggregate,
) -> None:
    '''
    Test that set_service clears parameters when parameters is None.

    :param app_interface_aggr: The app interface aggregate to test.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Seed parameters on the dependency.
    dependency = app_interface_aggr.get_service('test_attribute')
    dependency.parameters = {
        'existing': 'value',
    }

    # Call set_service with parameters=None.
    app_interface_aggr.set_service(
        attribute_id='test_attribute',
        module_path='cleared.module',
        class_name='ClearedClass',
        parameters=None,
    )

    # Parameters should be cleared while type fields are updated.
    updated = app_interface_aggr.get_service('test_attribute')
    assert updated.module_path == 'cleared.module'
    assert updated.class_name == 'ClearedClass'
    assert updated.parameters == {}

# ** test: app_interface_aggregate_set_service_creates_new
def test_app_interface_aggregate_set_service_creates_new(
    app_interface_aggr: AppInterfaceAggregate,
) -> None:
    '''
    Test that set_service creates a new dependency when none exists.

    :param app_interface_aggr: The app interface aggregate to test.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Ensure that no dependency exists with the new attribute_id.
    assert app_interface_aggr.get_service('new_attribute') is None

    # Create a new dependency via set_service.
    app_interface_aggr.set_service(
        attribute_id='new_attribute',
        module_path='new.module',
        class_name='NewClass',
        parameters={
            'param': 'value',
        },
    )

    # Verify that the dependency was created with the correct values.
    new_svc = app_interface_aggr.get_service('new_attribute')
    assert new_svc is not None
    assert new_svc.module_path == 'new.module'
    assert new_svc.class_name == 'NewClass'
    assert new_svc.parameters == {'param': 'value'}

# ** test: app_interface_config_data_round_trip
def test_app_interface_config_data_round_trip(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test round-trip mapping: app interface aggregate -> app interface yaml object -> app interface aggregate.
    '''

    data_obj = AppInterfaceYamlObject.from_model(app_interface_aggr)
    round_tripped = data_obj.map()

    # Core fields
    assert round_tripped.id == app_interface_aggr.id
    assert round_tripped.name == app_interface_aggr.name
    assert round_tripped.module_path == app_interface_aggr.module_path
    assert round_tripped.class_name == app_interface_aggr.class_name

    # Services
    assert len(round_tripped.services) == len(app_interface_aggr.services)
    for orig_svc, rt_svc in zip(app_interface_aggr.services, round_tripped.services):
        assert rt_svc.attribute_id == orig_svc.attribute_id
        assert rt_svc.module_path == orig_svc.module_path
        assert rt_svc.class_name == orig_svc.class_name
        assert rt_svc.parameters == orig_svc.parameters

    # Constants
    assert round_tripped.constants == app_interface_aggr.constants