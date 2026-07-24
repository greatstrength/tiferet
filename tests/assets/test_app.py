"""Tiferet App Assets Tests"""

# *** imports

# ** app
from tiferet.assets import app
from tiferet.assets.core import create_app_service_dependency

# *** tests

# ** test: create_app_service_dependency_structure
def test_create_app_service_dependency_structure():
    '''
    Verify create_app_service_dependency returns a dict with the expected keys.
    '''

    # Create a test service dependency.
    result = create_app_service_dependency(
        'test_service',
        'tiferet.repos.test',
        'TestRepository',
    )

    # Verify the result has all expected keys.
    assert 'service_id' in result
    assert 'module_path' in result
    assert 'class_name' in result
    assert 'parameters' in result


# ** test: create_app_service_dependency_default_parameters
def test_create_app_service_dependency_default_parameters():
    '''
    Verify omitting parameters yields an empty dict.
    '''

    # Create a dependency without explicit parameters.
    result = create_app_service_dependency(
        'test_service',
        'tiferet.repos.test',
        'TestRepository',
    )

    # Verify parameters defaults to an empty dict.
    assert result['parameters'] == {}


# ** test: core_default_services_keys
def test_core_default_services_keys():
    '''
    Verify CORE_DEFAULT_SERVICES contains all expected service ID keys.
    '''

    # Define the expected service IDs.
    expected_ids = [
        app.DI_SERVICE_ID,
        app.ERROR_SERVICE_ID,
        app.LOGGING_SERVICE_ID,
        app.FEATURE_SERVICE_ID,
        app.GET_ERROR_EVT_ID,
        app.GET_FEATURE_EVT_ID,
        app.LOGGING_LIST_ALL_EVT_ID,
        app.CLI_SERVICE_ID,
        app.LIST_COMMANDS_EVT_ID,
        app.GET_PARENT_ARGS_EVT_ID,
        app.DI_LIST_ALL_CONFIGS_EVT_ID,
    ]

    # Verify all expected service IDs are present in CORE_DEFAULT_SERVICES.
    for service_id in expected_ids:
        assert service_id in app.CORE_DEFAULT_SERVICES


# ** test: core_default_constants_config_ids
def test_core_default_constants_config_ids():
    '''
    Verify CORE_DEFAULT_CONSTANTS maps each config ID to 'config.yml'.
    '''

    # Define the expected config IDs.
    expected_config_ids = [
        app.CLI_CONFIG_ID,
        app.DI_CONFIG_ID,
        app.ERROR_CONFIG_ID,
        app.LOGGING_CONFIG_ID,
        app.FEATURE_CONFIG_ID,
    ]

    # Verify each config ID maps to 'config.yml'.
    for config_id in expected_config_ids:
        assert app.CORE_DEFAULT_CONSTANTS[config_id] == 'config.yml'


# ** test: default_app_service_class_name
def test_default_app_service_class_name():
    '''
    Verify DEFAULT_APP_SERVICE_CLASS_NAME is 'AppConfigRepository'.
    '''

    # Verify the class name.
    assert app.DEFAULT_APP_SERVICE_CLASS_NAME == 'AppConfigRepository'
