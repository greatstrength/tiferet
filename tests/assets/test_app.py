"""Tests for Tiferet Assets App"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.app import (
    CORE_DEFAULT_SERVICES,
    CORE_DEFAULT_CONSTANTS,
    DEFAULT_CONFIG_FILE,
    DI_SERVICE_ID,
    ERROR_SERVICE_ID,
    LOGGING_SERVICE_ID,
    FEATURE_SERVICE_ID,
    GET_ERROR_EVT_ID,
    GET_FEATURE_EVT_ID,
    LOGGING_LIST_ALL_EVT_ID,
    CLI_SERVICE_ID,
    LIST_COMMANDS_EVT_ID,
    GET_PARENT_ARGS_EVT_ID,
    DI_LIST_ALL_CONFIGS_EVT_ID,
    CLI_CONFIG_ID,
    DI_CONFIG_ID,
    ERROR_CONFIG_ID,
    LOGGING_CONFIG_ID,
    FEATURE_CONFIG_ID,
)

# *** constants

# ** constant: expected_service_ids
EXPECTED_SERVICE_IDS = {
    DI_SERVICE_ID,
    ERROR_SERVICE_ID,
    LOGGING_SERVICE_ID,
    FEATURE_SERVICE_ID,
    GET_ERROR_EVT_ID,
    GET_FEATURE_EVT_ID,
    LOGGING_LIST_ALL_EVT_ID,
    CLI_SERVICE_ID,
    LIST_COMMANDS_EVT_ID,
    GET_PARENT_ARGS_EVT_ID,
    DI_LIST_ALL_CONFIGS_EVT_ID,
}

# ** constant: expected_config_ids
EXPECTED_CONFIG_IDS = {
    CLI_CONFIG_ID,
    DI_CONFIG_ID,
    ERROR_CONFIG_ID,
    LOGGING_CONFIG_ID,
    FEATURE_CONFIG_ID,
}

# *** tests

# ** test: core_default_services_keys_match_service_ids
def test_core_default_services_keys_match_service_ids() -> None:
    '''
    Test that CORE_DEFAULT_SERVICES is keyed by the eleven core service ids.
    '''

    # Assert the catalog has exactly the eleven expected service ids.
    assert len(CORE_DEFAULT_SERVICES) == 11
    assert set(CORE_DEFAULT_SERVICES.keys()) == EXPECTED_SERVICE_IDS

# ** test: core_default_services_entries_have_expected_shape
def test_core_default_services_entries_have_expected_shape() -> None:
    '''
    Test that each CORE_DEFAULT_SERVICES value carries the four dependency keys
    and that its key matches the embedded service_id.
    '''

    # Assert each entry carries the four expected keys with a matching service_id.
    for service_id, record in CORE_DEFAULT_SERVICES.items():
        assert set(record.keys()) == {
            'service_id',
            'module_path',
            'class_name',
            'parameters',
        }
        assert record['service_id'] == service_id

# ** test: core_default_constants_keys_match_config_ids
def test_core_default_constants_keys_match_config_ids() -> None:
    '''
    Test that CORE_DEFAULT_CONSTANTS is keyed by the five config ids, each
    mapping to the shared default config file.
    '''

    # Assert the catalog has exactly the five expected config ids.
    assert len(CORE_DEFAULT_CONSTANTS) == 5
    assert set(CORE_DEFAULT_CONSTANTS.keys()) == EXPECTED_CONFIG_IDS

    # Assert every value is the shared default config file.
    assert all(value == DEFAULT_CONFIG_FILE for value in CORE_DEFAULT_CONSTANTS.values())
    assert all(value == 'config.yml' for value in CORE_DEFAULT_CONSTANTS.values())
