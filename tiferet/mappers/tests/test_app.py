"""Tiferet App Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...entities import AppAttribute
from ..settings import TransferObject, DEFAULT_MODULE_PATH, DEFAULT_CLASS_NAME
from ..app import AppInterfaceAggregate, AppInterfaceYamlObject, AppAttributeYamlObject

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
        feature_flag='test_app_yaml_data',
        data_flag='test_app_yaml_data',
        attributes=dict(
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
        'feature_flag': 'test_feature',
        'data_flag': 'test_data',
        'attributes': [
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

# ** test: app_interface_aggregate_set_attribute
def test_app_interface_aggregate_set_attribute(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test setting attributes on an AppInterfaceAggregate.

    :param app_interface_aggr: The app interface aggregate.
    :type app_interface_aggr: AppInterfaceAggregate
    '''

    # Update the name attribute.
    app_interface_aggr.set_attribute('name', 'Updated Name')

    # Assert the attribute was updated.
    assert app_interface_aggr.name == 'Updated Name'

# ** test: app_attribute_yaml_object_map
def test_app_attribute_yaml_object_map():
    '''
    Test mapping an AppAttributeYamlObject to an AppAttribute entity.
    '''

    # Create an AppAttributeYamlObject.
    yaml_obj = TransferObject.from_data(
        AppAttributeYamlObject,
        module_path='test.module',
        class_name='TestClass',
        parameters={'key': 'value'},
    )

    # Map to entity.
    entity = yaml_obj.map(attribute_id='test_attr')

    # Assert the mapping is correct.
    assert isinstance(entity, AppAttribute)
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
    assert 'test_attribute' in yaml_obj.attributes
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
    assert app_settings.feature_flag == app_interface_yaml_obj.feature_flag
    assert app_settings.data_flag == app_interface_yaml_obj.data_flag

    # Assert that the module path and class name are correctly set.
    assert app_settings.module_path == DEFAULT_MODULE_PATH
    assert app_settings.class_name == DEFAULT_CLASS_NAME

    # Assert that the mapped app attribute contains the correct data.
    attr = next(
        attr for attr in app_settings.attributes if attr.attribute_id == 'test_attribute')
    assert attr is not None
    assert isinstance(attr, AppAttribute)
    assert attr.module_path == 'test_module_path'
    assert attr.class_name == 'test_class_name'

    # Assert that the parameters are correctly set.
    param = next(
        (p for p in attr.parameters if p == 'test_param'), None)
    assert param is not None
    assert param == 'test_param'
    assert attr.parameters['test_param'] == 'test_value'

    # Assert that the constants are correctly set.
    assert app_settings.constants
    assert app_settings.constants['test_const'] == 'test_const_value'

# ** test: app_interface_config_data_round_trip
def test_app_interface_config_data_round_trip(app_interface_aggr: AppInterfaceAggregate):
    '''
    Test round-trip mapping: app interface aggregate -> app interface yaml object -> app interface aggregate.
    '''

    data_obj = TransferObject.from_model(AppInterfaceYamlObject, app_interface_aggr)
    round_tripped = data_obj.map()

    # Core fields
    assert round_tripped.id == app_interface_aggr.id
    assert round_tripped.name == app_interface_aggr.name
    assert round_tripped.module_path == app_interface_aggr.module_path
    assert round_tripped.class_name == app_interface_aggr.class_name

    # Attributes
    assert len(round_tripped.attributes) == len(app_interface_aggr.attributes)
    for orig_attr, rt_attr in zip(app_interface_aggr.attributes, round_tripped.attributes):
        assert rt_attr.attribute_id == orig_attr.attribute_id
        assert rt_attr.module_path == orig_attr.module_path
        assert rt_attr.class_name == orig_attr.class_name
        assert rt_attr.parameters == orig_attr.parameters

    # Constants
    assert round_tripped.constants == app_interface_aggr.constants