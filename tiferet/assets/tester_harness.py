"""Tiferet Tester Harness Config.

Frozen literal data the tester harness seeds for itself. This module does not
import tiferet/assets/core.py and calls no factory, so a broken factory fails
its tests instead of the harness. tests/assets/test_tester_harness.py asserts
that each constant equals the factory-built constant it replaces.
"""

# *** imports

# ** core
from typing import Any, Dict

# *** constants (ids)

# ** constant: tester_cli_id
HARNESS_TESTER_CLI_ID = 'tester_cli'

# ** constant: di_service_id
HARNESS_DI_SERVICE_ID = 'di_service'

# ** constant: di_config_id
HARNESS_DI_CONFIG_ID = 'di_config'

# ** constant: feature_service_id
HARNESS_FEATURE_SERVICE_ID = 'feature_service'

# ** constant: feature_config_id
HARNESS_FEATURE_CONFIG_ID = 'feature_config'

# ** constant: get_feature_evt_id
HARNESS_GET_FEATURE_EVT_ID = 'get_feature_evt'

# ** constant: default_config_file
HARNESS_DEFAULT_CONFIG_FILE = 'config.yml'

# ** constant: harness_error_prefix
HARNESS_ERROR_PREFIX = 'tiferet-tester harness error:'

# ** constant: harness_error_exit_code
# Distinct from 1 (a failed case or load error) and 2 (a usage error).
HARNESS_ERROR_EXIT_CODE = 3

# *** constants (data)

# ** constant: di_service_data
# Frozen copy of tiferet.assets.app.DI_SERVICE_DATA.
HARNESS_DI_SERVICE_DATA: Dict[str, Any] = {
    'module_path': 'tiferet.repos.di',
    'class_name': 'DIConfigRepository',
    'parameters': {},
}

# ** constant: feature_service_data
# Frozen copy of tiferet.assets.app.FEATURE_SERVICE_DATA.
HARNESS_FEATURE_SERVICE_DATA: Dict[str, Any] = {
    'module_path': 'tiferet.repos.feature',
    'class_name': 'FeatureConfigRepository',
    'parameters': {},
}

# ** constant: get_feature_evt_data
# Frozen copy of tiferet.assets.app.GET_FEATURE_EVT_DATA.
HARNESS_GET_FEATURE_EVT_DATA: Dict[str, Any] = {
    'module_path': 'tiferet.events.feature',
    'class_name': 'GetFeature',
    'parameters': {},
}

# ** constant: core_default_errors
# Frozen copy of tiferet.assets.error.CORE_DEFAULT_ERRORS.
HARNESS_CORE_DEFAULT_ERRORS: Dict[str, Any] = {
    'APP_ERROR': {
        'name': 'App Error',
        'message': [
            {
                'lang': 'en_US',
                'text': 'An error occurred in the app: {error_message}.',
            },
        ],
    },
    'APP_SESSION_NOT_FOUND': {
        'name': 'App Session Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'App session with ID {interface_id} not found.',
            },
        ],
    },
    'COMMAND_PARAMETER_REQUIRED': {
        'name': 'Command Parameter Required',
        'message': [
            {
                'lang': 'en_US',
                'text': 'The required parameter {parameter} for command {command} is missing.',
            },
        ],
    },
    'CONTEXT_NOT_FOUND': {
        'name': 'Context Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'No context registered for domain type: {domain_type}.',
            },
        ],
    },
    'ERROR_NOT_FOUND': {
        'name': 'Error Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Error not found: {id}.',
            },
        ],
    },
    'FEATURE_NOT_FOUND': {
        'name': 'Feature Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Feature not found: {feature_id}.',
            },
        ],
    },
    'FEATURE_STEP_LOADING_FAILED': {
        'name': 'Feature Step Loading Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Failed to load feature step: {service_id}. Error: {exception}.',
            },
        ],
    },
    'INVALID_APP_SESSION_TYPE': {
        'name': 'Invalid App Session Type',
        'message': [
            {
                'lang': 'en_US',
                'text': '{attribute} must be a non-empty string.',
            },
        ],
    },
    'LOGGER_CREATION_FAILED': {
        'name': 'Logger Creation Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Failed to create logger with ID {logger_id}: {exception}.',
            },
        ],
    },
    'LOGGING_CONFIG_FAILED': {
        'name': 'Logging Configuration Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Failed to configure logging: {exception}.',
            },
        ],
    },
    'MIDDLEWARE_LOADING_FAILED': {
        'name': 'Middleware Loading Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Failed to load middleware: {service_id}. Error: {exception}.',
            },
        ],
    },
    'PARAMETER_NOT_FOUND': {
        'name': 'Parameter Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Parameter {parameter} not found in request data.',
            },
        ],
    },
    'PARAMETER_PARSING_FAILED': {
        'name': 'Parameter Parsing Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Failed to parse parameter: {parameter}. Error: {exception}.',
            },
        ],
    },
    'REQUEST_NOT_FOUND': {
        'name': 'Request Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Request data is not available for parameter parsing.',
            },
        ],
    },
    'REQUEST_VALIDATION_FAILED': {
        'name': 'Request Validation Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Request validation failed for feature {feature_id}: {violations}.',
            },
        ],
    },
    'TEST_PRESET_NOT_FOUND': {
        'name': 'Test Preset Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Test preset not found: {preset_id}.',
            },
        ],
    },
    'PHASE_FIXTURE_NOT_FOUND': {
        'name': 'Phase Fixture Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Fixture {name} was not found.',
            },
        ],
    },
    'PHASE_NAME_COLLISION': {
        'name': 'Phase Name Collision',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Mock and fixture names collide: {names}.',
            },
        ],
    },
    'PHASE_REFERENCE_NOT_FOUND': {
        'name': 'Phase Reference Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Missing runtime reference {reference}.',
            },
        ],
    },
    'PHASE_HANDLER_MISMATCH': {
        'name': 'Phase Handler Mismatch',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Phase handler received {received}, not {expected}.',
            },
        ],
    },
    'PHASE_STEP_FAILED': {
        'name': 'Phase Step Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Phase step failed: {detail}.',
            },
        ],
    },
    'PHASE_CHECK_FAILED': {
        'name': 'Phase Check Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Phase check {check} failed: {detail}.',
            },
        ],
    },
}

# ** constant: tester_cli_sessions
# Frozen copy of tiferet.assets.tester_cli.TESTER_CLI_SESSIONS.
HARNESS_TESTER_CLI_SESSIONS: Dict[str, Any] = {
    'tester_cli': {
        'name': 'Tester CLI',
        'description': 'Built-in CLI for the tester writer and module run.',
    },
}

# ** constant: tester_default_commands
# Frozen copy of tiferet.assets.tester_cli.TESTER_DEFAULT_COMMANDS.
HARNESS_TESTER_DEFAULT_COMMANDS: Dict[str, Any] = {
    'fixture.add': {
        'key': 'add',
        'group_key': 'fixture',
        'name': 'Add Fixture',
        'description': 'Add a fixture to a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Fixture name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    '--payload',
                ],
                'description': 'Opaque YAML fragment.',
                'type': 'str',
            },
            {
                'name_or_flags': [
                    '--fragment',
                ],
                'description': 'Fragment text.',
            },
            {
                'name_or_flags': [
                    '--alias',
                ],
                'description': 'Alias name.',
            },
            {
                'name_or_flags': [
                    '--anchor',
                ],
                'description': 'Anchor name.',
            },
            {
                'name_or_flags': [
                    '--merge',
                ],
                'description': 'Merge anchor.',
            },
        ],
    },
    'fixture.get': {
        'key': 'get',
        'group_key': 'fixture',
        'name': 'Get Fixture',
        'description': 'Get a fixture from a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Fixture name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'fixture.list': {
        'key': 'list',
        'group_key': 'fixture',
        'name': 'List Fixtures',
        'description': 'List fixtures in a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'fixture.update': {
        'key': 'update',
        'group_key': 'fixture',
        'name': 'Update Fixture',
        'description': 'Update a fixture in a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Fixture name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    '--payload',
                ],
                'description': 'Opaque YAML fragment.',
                'type': 'str',
            },
            {
                'name_or_flags': [
                    '--fragment',
                ],
                'description': 'Fragment text.',
            },
            {
                'name_or_flags': [
                    '--merge',
                ],
                'description': 'Merge anchor.',
            },
        ],
    },
    'fixture.remove': {
        'key': 'remove',
        'group_key': 'fixture',
        'name': 'Remove Fixture',
        'description': 'Remove a fixture from a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Fixture name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'test.add': {
        'key': 'add',
        'group_key': 'test',
        'name': 'Add Test',
        'description': 'Add a test to a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Test name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    '--payload',
                ],
                'description': 'Opaque YAML fragment.',
                'type': 'str',
            },
            {
                'name_or_flags': [
                    '--fragment',
                ],
                'description': 'Fragment text.',
            },
            {
                'name_or_flags': [
                    '--anchor',
                ],
                'description': 'Anchor name.',
            },
        ],
    },
    'test.get': {
        'key': 'get',
        'group_key': 'test',
        'name': 'Get Test',
        'description': 'Get a test from a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Test name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'test.list': {
        'key': 'list',
        'group_key': 'test',
        'name': 'List Tests',
        'description': 'List tests in a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'test.update': {
        'key': 'update',
        'group_key': 'test',
        'name': 'Update Test',
        'description': 'Update a test in a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Test name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    '--payload',
                ],
                'description': 'Opaque YAML fragment.',
                'type': 'str',
            },
            {
                'name_or_flags': [
                    '--fragment',
                ],
                'description': 'Fragment text.',
            },
        ],
    },
    'test.remove': {
        'key': 'remove',
        'group_key': 'test',
        'name': 'Remove Test',
        'description': 'Remove a test from a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Test name.',
            },
            {
                'name_or_flags': [
                    '--tester',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'tester.add': {
        'key': 'add',
        'group_key': 'tester',
        'name': 'Add Tester',
        'description': 'Add a tester to a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    '--payload',
                ],
                'description': 'Opaque YAML fragment.',
                'type': 'str',
            },
            {
                'name_or_flags': [
                    '--fragment',
                ],
                'description': 'Fragment text.',
            },
            {
                'name_or_flags': [
                    '--anchor',
                ],
                'description': 'Anchor name.',
            },
        ],
    },
    'tester.get': {
        'key': 'get',
        'group_key': 'tester',
        'name': 'Get Tester',
        'description': 'Get a tester from a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'tester.list': {
        'key': 'list',
        'group_key': 'tester',
        'name': 'List Testers',
        'description': 'List testers in a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
        ],
    },
    'tester.update': {
        'key': 'update',
        'group_key': 'tester',
        'name': 'Update Tester',
        'description': 'Update a tester in a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    '--payload',
                ],
                'description': 'Opaque YAML fragment.',
                'type': 'str',
            },
            {
                'name_or_flags': [
                    '--fragment',
                ],
                'description': 'Fragment text.',
            },
        ],
    },
    'tester.remove': {
        'key': 'remove',
        'group_key': 'tester',
        'name': 'Remove Tester',
        'description': 'Remove a tester from a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Tester name.',
            },
        ],
    },
    'tester.attach': {
        'key': 'attach',
        'group_key': 'tester',
        'name': 'Attach Test',
        'description': 'Attach a test to a tester.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'tester',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Test name.',
            },
        ],
    },
    'tester.detach': {
        'key': 'detach',
        'group_key': 'tester',
        'name': 'Detach Test',
        'description': 'Detach a test from a tester.',
        'arguments': [
            {
                'name_or_flags': [
                    'rel',
                ],
                'description': 'Relative path of the test module.',
            },
            {
                'name_or_flags': [
                    'tester',
                ],
                'description': 'Tester name.',
            },
            {
                'name_or_flags': [
                    'name',
                ],
                'description': 'Test name.',
            },
        ],
    },
    'module.run': {
        'key': 'run',
        'group_key': 'module',
        'name': 'Run Test Module',
        'description': 'Run a test module.',
        'arguments': [
            {
                'name_or_flags': [
                    'module_path',
                ],
                'description': 'Python test module path.',
            },
            {
                'name_or_flags': [
                    '--summary',
                ],
                'description': 'Print only the count line.',
                'type': 'bool',
            },
        ],
    },
}

# ** constant: tester_default_features
# Frozen copy of tiferet.assets.tester_cli.TESTER_DEFAULT_FEATURES.
HARNESS_TESTER_DEFAULT_FEATURES: Dict[str, Any] = {
    'fixture.add': {
        'name': 'Add Fixture',
        'group_id': 'fixture',
        'feature_key': 'add',
        'steps': [
            {
                'service_id': 'add_fixture_evt',
                'name': 'Add Fixture',
            },
        ],
        'description': 'Add a fixture to a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
            'payload': {
                'type': 'str',
                'required': False,
            },
            'fragment': {
                'type': 'str',
                'required': False,
            },
            'alias': {
                'type': 'str',
                'required': False,
            },
            'anchor': {
                'type': 'str',
                'required': False,
            },
            'merge': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'fixture.get': {
        'name': 'Get Fixture',
        'group_id': 'fixture',
        'feature_key': 'get',
        'steps': [
            {
                'service_id': 'get_fixture_evt',
                'name': 'Get Fixture',
            },
        ],
        'description': 'Get a fixture from a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'fixture.list': {
        'name': 'List Fixtures',
        'group_id': 'fixture',
        'feature_key': 'list',
        'steps': [
            {
                'service_id': 'list_fixtures_evt',
                'name': 'List Fixtures',
            },
        ],
        'description': 'List fixtures in a test module.',
        'params_schema': {
            'rel': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'fixture.update': {
        'name': 'Update Fixture',
        'group_id': 'fixture',
        'feature_key': 'update',
        'steps': [
            {
                'service_id': 'update_fixture_evt',
                'name': 'Update Fixture',
            },
        ],
        'description': 'Update a fixture in a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
            'payload': {
                'type': 'str',
                'required': False,
            },
            'fragment': {
                'type': 'str',
                'required': False,
            },
            'merge': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'fixture.remove': {
        'name': 'Remove Fixture',
        'group_id': 'fixture',
        'feature_key': 'remove',
        'steps': [
            {
                'service_id': 'remove_fixture_evt',
                'name': 'Remove Fixture',
            },
        ],
        'description': 'Remove a fixture from a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'test.add': {
        'name': 'Add Test',
        'group_id': 'test',
        'feature_key': 'add',
        'steps': [
            {
                'service_id': 'add_test_evt',
                'name': 'Add Test',
            },
        ],
        'description': 'Add a test to a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
            'payload': {
                'type': 'str',
                'required': False,
            },
            'fragment': {
                'type': 'str',
                'required': False,
            },
            'anchor': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'test.get': {
        'name': 'Get Test',
        'group_id': 'test',
        'feature_key': 'get',
        'steps': [
            {
                'service_id': 'get_test_evt',
                'name': 'Get Test',
            },
        ],
        'description': 'Get a test from a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'test.list': {
        'name': 'List Tests',
        'group_id': 'test',
        'feature_key': 'list',
        'steps': [
            {
                'service_id': 'list_tests_evt',
                'name': 'List Tests',
            },
        ],
        'description': 'List tests in a test module.',
        'params_schema': {
            'rel': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'test.update': {
        'name': 'Update Test',
        'group_id': 'test',
        'feature_key': 'update',
        'steps': [
            {
                'service_id': 'update_test_evt',
                'name': 'Update Test',
            },
        ],
        'description': 'Update a test in a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
            'payload': {
                'type': 'str',
                'required': False,
            },
            'fragment': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'test.remove': {
        'name': 'Remove Test',
        'group_id': 'test',
        'feature_key': 'remove',
        'steps': [
            {
                'service_id': 'remove_test_evt',
                'name': 'Remove Test',
            },
        ],
        'description': 'Remove a test from a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'tester': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'tester.add': {
        'name': 'Add Tester',
        'group_id': 'tester',
        'feature_key': 'add',
        'steps': [
            {
                'service_id': 'add_tester_evt',
                'name': 'Add Tester',
            },
        ],
        'description': 'Add a tester to a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'payload': {
                'type': 'str',
                'required': False,
            },
            'fragment': {
                'type': 'str',
                'required': False,
            },
            'anchor': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'tester.get': {
        'name': 'Get Tester',
        'group_id': 'tester',
        'feature_key': 'get',
        'steps': [
            {
                'service_id': 'get_tester_evt',
                'name': 'Get Tester',
            },
        ],
        'description': 'Get a tester from a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
        },
    },
    'tester.list': {
        'name': 'List Testers',
        'group_id': 'tester',
        'feature_key': 'list',
        'steps': [
            {
                'service_id': 'list_testers_evt',
                'name': 'List Testers',
            },
        ],
        'description': 'List testers in a test module.',
        'params_schema': {
            'rel': 'str',
        },
    },
    'tester.update': {
        'name': 'Update Tester',
        'group_id': 'tester',
        'feature_key': 'update',
        'steps': [
            {
                'service_id': 'update_tester_evt',
                'name': 'Update Tester',
            },
        ],
        'description': 'Update a tester in a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
            'payload': {
                'type': 'str',
                'required': False,
            },
            'fragment': {
                'type': 'str',
                'required': False,
            },
        },
    },
    'tester.remove': {
        'name': 'Remove Tester',
        'group_id': 'tester',
        'feature_key': 'remove',
        'steps': [
            {
                'service_id': 'remove_tester_evt',
                'name': 'Remove Tester',
            },
        ],
        'description': 'Remove a tester from a test module.',
        'params_schema': {
            'rel': 'str',
            'name': 'str',
        },
    },
    'tester.attach': {
        'name': 'Attach Test',
        'group_id': 'tester',
        'feature_key': 'attach',
        'steps': [
            {
                'service_id': 'attach_test_evt',
                'name': 'Attach Test',
            },
        ],
        'description': 'Attach a test to a tester.',
        'params_schema': {
            'rel': 'str',
            'tester': 'str',
            'name': 'str',
        },
    },
    'tester.detach': {
        'name': 'Detach Test',
        'group_id': 'tester',
        'feature_key': 'detach',
        'steps': [
            {
                'service_id': 'detach_test_evt',
                'name': 'Detach Test',
            },
        ],
        'description': 'Detach a test from a tester.',
        'params_schema': {
            'rel': 'str',
            'tester': 'str',
            'name': 'str',
        },
    },
    'module.run': {
        'name': 'Run Test Module',
        'group_id': 'module',
        'feature_key': 'run',
        'steps': [],
        'description': 'Run a test module.',
        'params_schema': {
            'module_path': 'str',
            'summary': {
                'type': 'bool',
                'required': False,
            },
        },
    },
}

# ** constant: tester_query_event_registrations
# Frozen copy of tiferet.assets.tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS.
HARNESS_TESTER_QUERY_EVENT_REGISTRATIONS: Dict[str, Any] = {
    'get_fixture_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'GetFixture',
        'parameters': {},
    },
    'list_fixtures_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'ListFixtures',
        'parameters': {},
    },
    'get_test_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'GetTest',
        'parameters': {},
    },
    'list_tests_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'ListTests',
        'parameters': {},
    },
    'get_tester_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'GetTester',
        'parameters': {},
    },
    'list_testers_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'ListTesters',
        'parameters': {},
    },
}

# ** constant: tester_write_event_registrations
# Frozen copy of tiferet.assets.tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS.
HARNESS_TESTER_WRITE_EVENT_REGISTRATIONS: Dict[str, Any] = {
    'add_fixture_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'AddFixture',
        'parameters': {},
    },
    'update_fixture_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'UpdateFixture',
        'parameters': {},
    },
    'remove_fixture_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'RemoveFixture',
        'parameters': {},
    },
    'add_test_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'AddTest',
        'parameters': {},
    },
    'update_test_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'UpdateTest',
        'parameters': {},
    },
    'remove_test_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'RemoveTest',
        'parameters': {},
    },
    'add_tester_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'AddTester',
        'parameters': {},
    },
    'update_tester_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'UpdateTester',
        'parameters': {},
    },
    'remove_tester_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'RemoveTester',
        'parameters': {},
    },
    'attach_test_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'AttachTest',
        'parameters': {},
    },
    'detach_test_evt': {
        'module_path': 'tiferet.events.tester_module',
        'class_name': 'DetachTest',
        'parameters': {},
    },
}

# ** constant: tester_default_logging_settings
# Frozen copy of tiferet.assets.tester_cli.TESTER_DEFAULT_LOGGING_SETTINGS.
HARNESS_TESTER_DEFAULT_LOGGING_SETTINGS: Dict[str, Any] = {
    'formatters': [
        {
            'id': 'default',
            'name': 'Default Formatter',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'description': 'The default logging formatter.',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    ],
    'handlers': [
        {
            'id': 'default_root',
            'name': 'Default Root Handler',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'WARNING',
            'formatter': 'default',
            'description': 'The default root logging handler.',
            'stream': 'ext://sys.stderr',
        },
        {
            'id': 'default',
            'name': 'Default Handler',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'description': 'The default logging handler.',
            'stream': 'ext://sys.stdout',
        },
        {
            'id': 'debug',
            'name': 'Debug Handler',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'description': 'A handler for debugging purposes.',
            'stream': 'ext://sys.stdout',
        },
        {
            'id': 'tester_error',
            'name': 'Tester Error Handler',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'ERROR',
            'formatter': 'default',
            'description': 'Writes tester module-run errors to stderr.',
            'stream': 'ext://sys.stderr',
        },
    ],
    'loggers': [
        {
            'id': 'root',
            'name': 'Default Root Logger',
            'level': 'WARNING',
            'handlers': [
                'default_root',
            ],
            'propagate': False,
            'is_root': True,
            'description': 'The default logging configuration.',
        },
        {
            'id': 'default',
            'name': 'Default Logger',
            'level': 'INFO',
            'handlers': [
                'default',
            ],
            'propagate': True,
            'is_root': False,
            'description': 'The default logging configuration.',
        },
        {
            'id': 'debug',
            'name': 'Debug Logger',
            'level': 'DEBUG',
            'handlers': [
                'debug',
            ],
            'propagate': True,
            'is_root': False,
            'description': 'A logger for debugging purposes.',
        },
        {
            'id': 'tester',
            'name': 'Tester Logger',
            'level': 'ERROR',
            'handlers': [
                'tester_error',
            ],
            'propagate': False,
            'is_root': False,
            'description': 'Logs tester module-run failures and load errors.',
        },
    ],
}

# ** constant: core_default_tester_sessions
# Frozen copy of tiferet.assets.tester.CORE_DEFAULT_TESTER_SESSIONS.
HARNESS_CORE_DEFAULT_TESTER_SESSIONS: Dict[str, Any] = {
    'tester': {
        'name': 'Tester',
        'description': 'Default built-in test-harness application session',
    },
}

# ** constant: core_default_testers
# Frozen copy of tiferet.assets.tester.CORE_DEFAULT_TESTERS.
HARNESS_CORE_DEFAULT_TESTERS: Dict[str, Any] = {
    'domain.ErrorMessage': {
        'type': 'domain',
        'module_path': 'tiferet.domain.error',
        'class_name': 'ErrorMessage',
        'sample_data': {
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
        'equality_fields': [
            'lang',
            'text',
        ],
        'description_cases': [
            (
                'format',
                (),
                'An error occurred.',
            ),
        ],
    },
    'aggregate.ErrorAggregate': {
        'type': 'aggregate',
        'module_path': 'tiferet.mappers.error',
        'class_name': 'ErrorAggregate',
        'sample_data': {
            'id': 'TEST_ERROR',
            'name': 'Test Error',
            'message': [
                {
                    'lang': 'en_US',
                    'text': 'An error occurred.',
                },
            ],
        },
        'equality_fields': [
            'id',
            'name',
            'error_code',
        ],
        'set_attribute_params': [
            (
                'name',
                'Updated Error',
                None,
            ),
            (
                'invalid_attribute',
                'value',
                'INVALID_MODEL_ATTRIBUTE',
            ),
        ],
    },
    'transfer_object.ErrorConfigObject': {
        'type': 'transfer_object',
        'module_path': 'tiferet.mappers.error',
        'class_name': 'ErrorConfigObject',
        'sample_data': {
            'id': 'TEST_ERROR',
            'name': 'Test Error',
            'message': [
                {
                    'lang': 'en_US',
                    'text': 'An error occurred.',
                },
            ],
        },
        'equality_fields': [
            'id',
            'name',
            'error_code',
        ],
        'aggregate_module_path': 'tiferet.mappers.error',
        'aggregate_class_name': 'ErrorAggregate',
        'aggregate_sample_data': {
            'id': 'TEST_ERROR',
            'name': 'Test Error',
            'message': [
                {
                    'lang': 'en_US',
                    'text': 'An error occurred.',
                },
            ],
        },
    },
    'service_event.GetError': {
        'type': 'service_event',
        'module_path': 'tiferet.events.error',
        'class_name': 'GetError',
        'sample_data': {},
        'equality_fields': [],
        'dependencies': {
            'error_service': {
                'module_path': 'tiferet.interfaces',
                'class_name': 'ErrorService',
            },
        },
        'sample_kwargs': {
            'id': 'TEST_ERROR',
        },
        'required_params': [],
        'service_attr': 'error_service',
        'not_found_error_code': 'ERROR_NOT_FOUND',
    },
    'repo.ErrorConfigRepository': {
        'type': 'repo',
        'module_path': 'tiferet.repos.error',
        'class_name': 'ErrorConfigRepository',
        'sample_data': {},
        'equality_fields': [
            'id',
            'name',
        ],
        'config_parameter': 'error_config',
        'aggregate_module_path': 'tiferet.mappers.error',
        'aggregate_class_name': 'ErrorAggregate',
        'aggregate_sample_data': {
            'id': 'TEST_ERROR',
            'name': 'Test Error',
            'message': [
                {
                    'lang': 'en_US',
                    'text': 'An error occurred.',
                },
            ],
        },
        'exists_cases': [
            (
                'TEST_ERROR_CODE',
                True,
            ),
            (
                'MISSING_ERROR_CODE',
                False,
            ),
        ],
        'get_cases': [
            (
                'TEST_ERROR_CODE',
                {
                    'id': 'TEST_ERROR_CODE',
                    'name': 'Test Error',
                },
            ),
            (
                'MISSING_ERROR_CODE',
                None,
            ),
        ],
        'list_ids': [
            'TEST_ERROR_CODE',
        ],
        'delete_ids': [
            'TEST_ERROR_CODE',
        ],
    },
    'context.RequestContext': {
        'type': 'context',
        'module_path': 'tiferet.contexts.request',
        'class_name': 'RequestContext',
        'sample_data': {
            'session_id': 'test-session',
            'feature_id': 'test.feature',
        },
        'equality_fields': [],
        'domain_module_path': 'tiferet.domain.request',
        'domain_class_name': 'Request',
        'from_domain_cases': [
            {
                'data': {
                    'session_id': 'test-session',
                    'feature_id': 'test.feature',
                },
            },
        ],
        'domain_type_cases': [
            {
                'declares': True,
            },
        ],
        'for_domain_cases': [
            {
                'domain_module_path': 'tiferet.domain.request',
                'domain_class_name': 'Request',
                'context_module_path': 'tiferet.contexts.request',
                'context_class_name': 'RequestContext',
            },
        ],
    },
}
