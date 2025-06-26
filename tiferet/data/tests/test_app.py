# *** imports

# ** infra
import pytest

# ** app
from ..app import *


# *** fixtures

# ** fixture: app_settings_yaml_data
@pytest.fixture
def app_settings_yaml_data():

    return DataObject.from_data(
        AppInterfaceYamlData,
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


# *** tests

# ** test: test_app_settings_yaml_data_map
def test_app_settings_yaml_data_map(app_settings_yaml_data):

    # Map the app interface yaml data to an app interface object.
    app_settings = app_settings_yaml_data.map()

    # Assert the mapped app interface is valid.
    assert isinstance(app_settings, AppInterface)
    assert app_settings.id == app_settings_yaml_data.id
    assert app_settings.name == app_settings_yaml_data.name
    assert app_settings.feature_flag == app_settings_yaml_data.feature_flag
    assert app_settings.data_flag == app_settings_yaml_data.data_flag

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