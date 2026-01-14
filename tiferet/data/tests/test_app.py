"""Tiferet App Data Object Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    DataObject,
    DEFAULT_MODULE_PATH,
    DEFAULT_CLASS_NAME
)
from ..app import (
    AppInterfaceConfigData,
    AppInterface,
    AppAttribute,
)
from ...models import ModelObject

# *** fixtures

# ** fixture: app_settings_config_data
@pytest.fixture
def app_settings_config_data() -> AppInterfaceConfigData:
    '''
    A fixture for an app interface yaml data object.

    :return: The app interface yaml data object.
    :rtype: AppInterfaceConfigData
    '''

    # Create and return the app interface yaml data object.
    return DataObject.from_data(
        AppInterfaceConfigData,
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

# ** fixture: sample_app_interface
@pytest.fixture
def sample_app_interface() -> AppInterface:
    '''
    Fixture to provide a sample AppInterface model for round-trip testing.

    :return: A sample AppInterface instance.
    :rtype: AppInterface
    '''

    return ModelObject.new(
        AppInterface,
        id='test.interface',
        name='Test Interface',
        description='The test app interface.',
        module_path=DEFAULT_MODULE_PATH,
        class_name=DEFAULT_CLASS_NAME,
        feature_flag='test_feature',
        data_flag='test_data',
        attributes=[
            ModelObject.new(
                AppAttribute,
                attribute_id='test_attribute',
                module_path='test_module_path',
                class_name='test_class_name',
                parameters={
                    'test_param': 'test_value',
                },
            ),
        ],
        constants={
            'TEST_CONST': 'test_const_value',
        },
    )

# *** tests

# ** test: app_settings_yaml_data_map
def test_app_settings_yaml_data_map(app_settings_config_data: AppInterfaceConfigData):
    '''
    Tests the mapping of an app interface yaml data object to an app interface object.

    :param app_settings_yaml_data: The app interface yaml data object.
    :type app_settings_yaml_data: AppInterfaceConfigData
    '''

    # Map the app interface yaml data to an app interface object.
    app_settings = app_settings_config_data.map()

    # Assert the mapped app interface is valid.
    assert isinstance(app_settings, AppInterface)
    assert app_settings.id == app_settings_config_data.id
    assert app_settings.name == app_settings_config_data.name
    assert app_settings.feature_flag == app_settings_config_data.feature_flag
    assert app_settings.data_flag == app_settings_config_data.data_flag

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
def test_app_interface_config_data_round_trip(sample_app_interface: AppInterface):
    '''
    Test round-trip mapping: model → data → model.
    '''

    data_obj = AppInterfaceConfigData.from_model(sample_app_interface)
    round_tripped = data_obj.map()

    # Core fields
    assert round_tripped.id == sample_app_interface.id
    assert round_tripped.name == sample_app_interface.name
    assert round_tripped.module_path == sample_app_interface.module_path
    assert round_tripped.class_name == sample_app_interface.class_name

    # Attributes
    assert len(round_tripped.attributes) == len(sample_app_interface.attributes)
    for orig_attr, rt_attr in zip(sample_app_interface.attributes, round_tripped.attributes):
        assert rt_attr.attribute_id == orig_attr.attribute_id
        assert rt_attr.module_path == orig_attr.module_path
        assert rt_attr.class_name == orig_attr.class_name
        assert rt_attr.parameters == orig_attr.parameters

    # Constants
    assert round_tripped.constants == sample_app_interface.constants
