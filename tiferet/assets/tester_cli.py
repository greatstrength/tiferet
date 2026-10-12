"""Tester CLI catalog.

These definitions are not loaded from a consumer config file.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from .core import (
    TIFERET,
    TIFERET_EVENTS_PATH,
    create_default_cli_argument,
    create_default_cli_command_data,
    create_default_feature_data,
    create_params_schema,
    create_default_app_session_data,
    create_service_registration_data,
    create_service_module_path,
)

# *** constants (ids)

# ** constant: tester_cli_id
TESTER_CLI_ID = 'tester_cli'

# ** constant: fixture_add_id
FIXTURE_ADD_ID = 'fixture.add'

# ** constant: fixture_get_id
FIXTURE_GET_ID = 'fixture.get'

# ** constant: fixture_list_id
FIXTURE_LIST_ID = 'fixture.list'

# ** constant: fixture_update_id
FIXTURE_UPDATE_ID = 'fixture.update'

# ** constant: fixture_remove_id
FIXTURE_REMOVE_ID = 'fixture.remove'

# ** constant: test_add_id
TEST_ADD_ID = 'test.add'

# ** constant: test_get_id
TEST_GET_ID = 'test.get'

# ** constant: test_list_id
TEST_LIST_ID = 'test.list'

# ** constant: test_update_id
TEST_UPDATE_ID = 'test.update'

# ** constant: test_remove_id
TEST_REMOVE_ID = 'test.remove'

# ** constant: tester_add_id
TESTER_ADD_ID = 'tester.add'

# ** constant: tester_get_id
TESTER_GET_ID = 'tester.get'

# ** constant: tester_list_id
TESTER_LIST_ID = 'tester.list'

# ** constant: tester_update_id
TESTER_UPDATE_ID = 'tester.update'

# ** constant: tester_remove_id
TESTER_REMOVE_ID = 'tester.remove'

# ** constant: tester_attach_id
TESTER_ATTACH_ID = 'tester.attach'

# ** constant: tester_detach_id
TESTER_DETACH_ID = 'tester.detach'

# ** constant: module_run_id
MODULE_RUN_ID = 'module.run'

# ** constant: get_fixture_evt_id
GET_FIXTURE_EVT_ID = 'get_fixture_evt'

# ** constant: list_fixtures_evt_id
LIST_FIXTURES_EVT_ID = 'list_fixtures_evt'

# ** constant: get_test_evt_id
GET_TEST_EVT_ID = 'get_test_evt'

# ** constant: list_tests_evt_id
LIST_TESTS_EVT_ID = 'list_tests_evt'

# ** constant: get_tester_evt_id
GET_TESTER_EVT_ID = 'get_tester_evt'

# ** constant: list_testers_evt_id
LIST_TESTERS_EVT_ID = 'list_testers_evt'

# ** constant: add_fixture_evt_id
ADD_FIXTURE_EVT_ID = 'add_fixture_evt'

# ** constant: update_fixture_evt_id
UPDATE_FIXTURE_EVT_ID = 'update_fixture_evt'

# ** constant: remove_fixture_evt_id
REMOVE_FIXTURE_EVT_ID = 'remove_fixture_evt'

# ** constant: add_test_evt_id
ADD_TEST_EVT_ID = 'add_test_evt'

# ** constant: update_test_evt_id
UPDATE_TEST_EVT_ID = 'update_test_evt'

# ** constant: remove_test_evt_id
REMOVE_TEST_EVT_ID = 'remove_test_evt'

# ** constant: add_tester_evt_id
ADD_TESTER_EVT_ID = 'add_tester_evt'

# ** constant: update_tester_evt_id
UPDATE_TESTER_EVT_ID = 'update_tester_evt'

# ** constant: remove_tester_evt_id
REMOVE_TESTER_EVT_ID = 'remove_tester_evt'

# ** constant: attach_test_evt_id
ATTACH_TEST_EVT_ID = 'attach_test_evt'

# ** constant: detach_test_evt_id
DETACH_TEST_EVT_ID = 'detach_test_evt'

# *** constants (parent)

# ** constant: tester_base_dir_argument
TESTER_BASE_DIR_ARGUMENT = create_default_cli_argument(
    ['--base-dir'],
    description='Directory that contains tiferet_tests/.',
    default='.',
)

# ** constant: tester_default_parent_arguments
TESTER_DEFAULT_PARENT_ARGUMENTS: List[Dict[str, Any]] = [
    TESTER_BASE_DIR_ARGUMENT,
]

# *** constants (commands)

# ** constant: rel_argument
REL_ARGUMENT = {
    'name_or_flags': [
        'rel',
    ],
    'description': 'Relative path of the test module.',
}

# ** constant: fixture_name_argument
FIXTURE_NAME_ARGUMENT = {
    'name_or_flags': [
        'name',
    ],
    'description': 'Fixture name.',
}

# ** constant: test_name_argument
TEST_NAME_ARGUMENT = {
    'name_or_flags': [
        'name',
    ],
    'description': 'Test name.',
}

# ** constant: tester_name_argument
TESTER_NAME_ARGUMENT = {
    'name_or_flags': [
        'name',
    ],
    'description': 'Tester name.',
}

# ** constant: tester_flag_argument
TESTER_FLAG_ARGUMENT = {
    'name_or_flags': [
        '--tester',
    ],
    'description': 'Tester name.',
}

# ** constant: tester_positional_argument
TESTER_POSITIONAL_ARGUMENT = {
    'name_or_flags': [
        'tester',
    ],
    'description': 'Tester name.',
}

# ** constant: payload_argument
PAYLOAD_ARGUMENT = {
    'name_or_flags': [
        '--payload',
    ],
    'description': 'Opaque YAML fragment.',
    'type': 'str',
}

# ** constant: fragment_argument
FRAGMENT_ARGUMENT = {
    'name_or_flags': [
        '--fragment',
    ],
    'description': 'Fragment text.',
}

# ** constant: anchor_argument
ANCHOR_ARGUMENT = {
    'name_or_flags': [
        '--anchor',
    ],
    'description': 'Anchor name.',
}

# ** constant: merge_argument
MERGE_ARGUMENT = {
    'name_or_flags': [
        '--merge',
    ],
    'description': 'Merge anchor.',
}

# ** constant: fixture_name_and_tester_arguments
FIXTURE_NAME_AND_TESTER_ARGUMENTS = [
    create_default_cli_argument(
        **REL_ARGUMENT,
    ),
    create_default_cli_argument(
        **FIXTURE_NAME_ARGUMENT,
    ),
    create_default_cli_argument(
        **TESTER_FLAG_ARGUMENT,
    ),
]

# ** constant: test_name_and_tester_arguments
TEST_NAME_AND_TESTER_ARGUMENTS = [
    create_default_cli_argument(
        **REL_ARGUMENT,
    ),
    create_default_cli_argument(
        **TEST_NAME_ARGUMENT,
    ),
    create_default_cli_argument(
        **TESTER_FLAG_ARGUMENT,
    ),
]

# ** constant: tester_name_arguments
TESTER_NAME_ARGUMENTS = [
    create_default_cli_argument(
        **REL_ARGUMENT,
    ),
    create_default_cli_argument(
        **TESTER_NAME_ARGUMENT,
    ),
]

# ** constant: rel_and_tester_arguments
REL_AND_TESTER_ARGUMENTS = [
    create_default_cli_argument(
        **REL_ARGUMENT,
    ),
    create_default_cli_argument(
        **TESTER_FLAG_ARGUMENT,
    ),
]

# ** constant: attach_arguments
ATTACH_ARGUMENTS = [
    create_default_cli_argument(
        **REL_ARGUMENT,
    ),
    create_default_cli_argument(
        **TESTER_POSITIONAL_ARGUMENT,
    ),
    create_default_cli_argument(
        **TEST_NAME_ARGUMENT,
    ),
]

# ** constant: fixture_add_command_data
FIXTURE_ADD_COMMAND_DATA = create_default_cli_command_data(
    'add',
    'fixture',
    'Add Fixture',
    description='Add a fixture to a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
        create_default_cli_argument(
            **FIXTURE_NAME_ARGUMENT,
        ),
        create_default_cli_argument(
            **TESTER_FLAG_ARGUMENT,
        ),
        create_default_cli_argument(
            **PAYLOAD_ARGUMENT,
        ),
        create_default_cli_argument(
            **FRAGMENT_ARGUMENT,
        ),
        create_default_cli_argument(
            ['--alias'],
            description='Alias name.',
        ),
        create_default_cli_argument(
            **ANCHOR_ARGUMENT,
        ),
        create_default_cli_argument(
            **MERGE_ARGUMENT,
        ),
    ],
)

# ** constant: fixture_get_command_data
FIXTURE_GET_COMMAND_DATA = create_default_cli_command_data(
    'get',
    'fixture',
    'Get Fixture',
    description='Get a fixture from a test module.',
    arguments=FIXTURE_NAME_AND_TESTER_ARGUMENTS,
)

# ** constant: fixture_list_command_data
FIXTURE_LIST_COMMAND_DATA = create_default_cli_command_data(
    'list',
    'fixture',
    'List Fixtures',
    description='List fixtures in a test module.',
    arguments=REL_AND_TESTER_ARGUMENTS,
)

# ** constant: fixture_update_command_data
FIXTURE_UPDATE_COMMAND_DATA = create_default_cli_command_data(
    'update',
    'fixture',
    'Update Fixture',
    description='Update a fixture in a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
        create_default_cli_argument(
            **FIXTURE_NAME_ARGUMENT,
        ),
        create_default_cli_argument(
            **TESTER_FLAG_ARGUMENT,
        ),
        create_default_cli_argument(
            **PAYLOAD_ARGUMENT,
        ),
        create_default_cli_argument(
            **FRAGMENT_ARGUMENT,
        ),
        create_default_cli_argument(
            **MERGE_ARGUMENT,
        ),
    ],
)

# ** constant: fixture_remove_command_data
FIXTURE_REMOVE_COMMAND_DATA = create_default_cli_command_data(
    'remove',
    'fixture',
    'Remove Fixture',
    description='Remove a fixture from a test module.',
    arguments=FIXTURE_NAME_AND_TESTER_ARGUMENTS,
)

# ** constant: test_add_command_data
TEST_ADD_COMMAND_DATA = create_default_cli_command_data(
    'add',
    'test',
    'Add Test',
    description='Add a test to a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
        create_default_cli_argument(
            **TEST_NAME_ARGUMENT,
        ),
        create_default_cli_argument(
            **TESTER_FLAG_ARGUMENT,
        ),
        create_default_cli_argument(
            **PAYLOAD_ARGUMENT,
        ),
        create_default_cli_argument(
            **FRAGMENT_ARGUMENT,
        ),
        create_default_cli_argument(
            **ANCHOR_ARGUMENT,
        ),
    ],
)

# ** constant: test_get_command_data
TEST_GET_COMMAND_DATA = create_default_cli_command_data(
    'get',
    'test',
    'Get Test',
    description='Get a test from a test module.',
    arguments=TEST_NAME_AND_TESTER_ARGUMENTS,
)

# ** constant: test_list_command_data
TEST_LIST_COMMAND_DATA = create_default_cli_command_data(
    'list',
    'test',
    'List Tests',
    description='List tests in a test module.',
    arguments=REL_AND_TESTER_ARGUMENTS,
)

# ** constant: test_update_command_data
TEST_UPDATE_COMMAND_DATA = create_default_cli_command_data(
    'update',
    'test',
    'Update Test',
    description='Update a test in a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
        create_default_cli_argument(
            **TEST_NAME_ARGUMENT,
        ),
        create_default_cli_argument(
            **TESTER_FLAG_ARGUMENT,
        ),
        create_default_cli_argument(
            **PAYLOAD_ARGUMENT,
        ),
        create_default_cli_argument(
            **FRAGMENT_ARGUMENT,
        ),
    ],
)

# ** constant: test_remove_command_data
TEST_REMOVE_COMMAND_DATA = create_default_cli_command_data(
    'remove',
    'test',
    'Remove Test',
    description='Remove a test from a test module.',
    arguments=TEST_NAME_AND_TESTER_ARGUMENTS,
)

# ** constant: tester_add_command_data
TESTER_ADD_COMMAND_DATA = create_default_cli_command_data(
    'add',
    'tester',
    'Add Tester',
    description='Add a tester to a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
        create_default_cli_argument(
            **TESTER_NAME_ARGUMENT,
        ),
        create_default_cli_argument(
            **PAYLOAD_ARGUMENT,
        ),
        create_default_cli_argument(
            **FRAGMENT_ARGUMENT,
        ),
        create_default_cli_argument(
            **ANCHOR_ARGUMENT,
        ),
    ],
)

# ** constant: tester_get_command_data
TESTER_GET_COMMAND_DATA = create_default_cli_command_data(
    'get',
    'tester',
    'Get Tester',
    description='Get a tester from a test module.',
    arguments=TESTER_NAME_ARGUMENTS,
)

# ** constant: tester_list_command_data
TESTER_LIST_COMMAND_DATA = create_default_cli_command_data(
    'list',
    'tester',
    'List Testers',
    description='List testers in a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
    ],
)

# ** constant: tester_update_command_data
TESTER_UPDATE_COMMAND_DATA = create_default_cli_command_data(
    'update',
    'tester',
    'Update Tester',
    description='Update a tester in a test module.',
    arguments=[
        create_default_cli_argument(
            **REL_ARGUMENT,
        ),
        create_default_cli_argument(
            **TESTER_NAME_ARGUMENT,
        ),
        create_default_cli_argument(
            **PAYLOAD_ARGUMENT,
        ),
        create_default_cli_argument(
            **FRAGMENT_ARGUMENT,
        ),
    ],
)

# ** constant: tester_remove_command_data
TESTER_REMOVE_COMMAND_DATA = create_default_cli_command_data(
    'remove',
    'tester',
    'Remove Tester',
    description='Remove a tester from a test module.',
    arguments=TESTER_NAME_ARGUMENTS,
)

# ** constant: tester_attach_command_data
TESTER_ATTACH_COMMAND_DATA = create_default_cli_command_data(
    'attach',
    'tester',
    'Attach Test',
    description='Attach a test to a tester.',
    arguments=ATTACH_ARGUMENTS,
)

# ** constant: tester_detach_command_data
TESTER_DETACH_COMMAND_DATA = create_default_cli_command_data(
    'detach',
    'tester',
    'Detach Test',
    description='Detach a test from a tester.',
    arguments=ATTACH_ARGUMENTS,
)

# ** constant: module_run_command_data
MODULE_RUN_COMMAND_DATA = create_default_cli_command_data(
    'run',
    'module',
    'Run Test Module',
    description='Run a test module.',
    arguments=[
        create_default_cli_argument(
            ['module_path'],
            description='Python test module path.',
        ),
        create_default_cli_argument(
            ['--summary'],
            description='Print only the count line.',
            type='bool',
        ),
    ],
)

# *** constants (features)

# ** constant: optional_str_param
OPTIONAL_STR_PARAM = {
    'type': 'str',
    'required': False,
}

# ** constant: rel_param
REL_PARAM = {
    'rel': 'str',
}

# ** constant: name_param
NAME_PARAM = {
    'name': 'str',
}

# ** constant: rel_name_params
REL_NAME_PARAMS = {
    **REL_PARAM,
    **NAME_PARAM,
}

# ** constant: payload_fragment_params
PAYLOAD_FRAGMENT_PARAMS = {
    'payload': {
        **OPTIONAL_STR_PARAM,
    },
    'fragment': {
        **OPTIONAL_STR_PARAM,
    },
}

# ** constant: rel_name_tester_params
REL_NAME_TESTER_PARAMS = {
    **REL_NAME_PARAMS,
    'tester': {
        **OPTIONAL_STR_PARAM,
    },
}

# ** constant: rel_tester_params
REL_TESTER_PARAMS = {
    **REL_PARAM,
    'tester': {
        **OPTIONAL_STR_PARAM,
    },
}

# ** constant: attach_params
ATTACH_PARAMS = {
    **REL_PARAM,
    'tester': 'str',
    **NAME_PARAM,
}

# ** constant: fixture_add_feature_data
FIXTURE_ADD_FEATURE_DATA = create_default_feature_data(
    'Add Fixture',
    'fixture',
    'add',
    [
        {
            'service_id': ADD_FIXTURE_EVT_ID,
            'name': 'Add Fixture',
        },
    ],
    description='Add a fixture to a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
        tester={
            **OPTIONAL_STR_PARAM,
        },
        **PAYLOAD_FRAGMENT_PARAMS,
        alias={
            **OPTIONAL_STR_PARAM,
        },
        anchor={
            **OPTIONAL_STR_PARAM,
        },
        merge={
            **OPTIONAL_STR_PARAM,
        },
    ),
)

# ** constant: fixture_get_feature_data
FIXTURE_GET_FEATURE_DATA = create_default_feature_data(
    'Get Fixture',
    'fixture',
    'get',
    [
        {
            'service_id': GET_FIXTURE_EVT_ID,
            'name': 'Get Fixture',
        },
    ],
    description='Get a fixture from a test module.',
    params_schema=create_params_schema(
        **REL_NAME_TESTER_PARAMS,
    ),
)

# ** constant: fixture_list_feature_data
FIXTURE_LIST_FEATURE_DATA = create_default_feature_data(
    'List Fixtures',
    'fixture',
    'list',
    [
        {
            'service_id': LIST_FIXTURES_EVT_ID,
            'name': 'List Fixtures',
        },
    ],
    description='List fixtures in a test module.',
    params_schema=create_params_schema(
        **REL_TESTER_PARAMS,
    ),
)

# ** constant: fixture_update_feature_data
FIXTURE_UPDATE_FEATURE_DATA = create_default_feature_data(
    'Update Fixture',
    'fixture',
    'update',
    [
        {
            'service_id': UPDATE_FIXTURE_EVT_ID,
            'name': 'Update Fixture',
        },
    ],
    description='Update a fixture in a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
        tester={
            **OPTIONAL_STR_PARAM,
        },
        **PAYLOAD_FRAGMENT_PARAMS,
        merge={
            **OPTIONAL_STR_PARAM,
        },
    ),
)

# ** constant: fixture_remove_feature_data
FIXTURE_REMOVE_FEATURE_DATA = create_default_feature_data(
    'Remove Fixture',
    'fixture',
    'remove',
    [
        {
            'service_id': REMOVE_FIXTURE_EVT_ID,
            'name': 'Remove Fixture',
        },
    ],
    description='Remove a fixture from a test module.',
    params_schema=create_params_schema(
        **REL_NAME_TESTER_PARAMS,
    ),
)

# ** constant: test_add_feature_data
TEST_ADD_FEATURE_DATA = create_default_feature_data(
    'Add Test',
    'test',
    'add',
    [
        {
            'service_id': ADD_TEST_EVT_ID,
            'name': 'Add Test',
        },
    ],
    description='Add a test to a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
        tester={
            **OPTIONAL_STR_PARAM,
        },
        **PAYLOAD_FRAGMENT_PARAMS,
        anchor={
            **OPTIONAL_STR_PARAM,
        },
    ),
)

# ** constant: test_get_feature_data
TEST_GET_FEATURE_DATA = create_default_feature_data(
    'Get Test',
    'test',
    'get',
    [
        {
            'service_id': GET_TEST_EVT_ID,
            'name': 'Get Test',
        },
    ],
    description='Get a test from a test module.',
    params_schema=create_params_schema(
        **REL_NAME_TESTER_PARAMS,
    ),
)

# ** constant: test_list_feature_data
TEST_LIST_FEATURE_DATA = create_default_feature_data(
    'List Tests',
    'test',
    'list',
    [
        {
            'service_id': LIST_TESTS_EVT_ID,
            'name': 'List Tests',
        },
    ],
    description='List tests in a test module.',
    params_schema=create_params_schema(
        **REL_TESTER_PARAMS,
    ),
)

# ** constant: test_update_feature_data
TEST_UPDATE_FEATURE_DATA = create_default_feature_data(
    'Update Test',
    'test',
    'update',
    [
        {
            'service_id': UPDATE_TEST_EVT_ID,
            'name': 'Update Test',
        },
    ],
    description='Update a test in a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
        tester={
            **OPTIONAL_STR_PARAM,
        },
        **PAYLOAD_FRAGMENT_PARAMS,
    ),
)

# ** constant: test_remove_feature_data
TEST_REMOVE_FEATURE_DATA = create_default_feature_data(
    'Remove Test',
    'test',
    'remove',
    [
        {
            'service_id': REMOVE_TEST_EVT_ID,
            'name': 'Remove Test',
        },
    ],
    description='Remove a test from a test module.',
    params_schema=create_params_schema(
        **REL_NAME_TESTER_PARAMS,
    ),
)

# ** constant: tester_add_feature_data
TESTER_ADD_FEATURE_DATA = create_default_feature_data(
    'Add Tester',
    'tester',
    'add',
    [
        {
            'service_id': ADD_TESTER_EVT_ID,
            'name': 'Add Tester',
        },
    ],
    description='Add a tester to a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
        **PAYLOAD_FRAGMENT_PARAMS,
        anchor={
            **OPTIONAL_STR_PARAM,
        },
    ),
)

# ** constant: tester_get_feature_data
TESTER_GET_FEATURE_DATA = create_default_feature_data(
    'Get Tester',
    'tester',
    'get',
    [
        {
            'service_id': GET_TESTER_EVT_ID,
            'name': 'Get Tester',
        },
    ],
    description='Get a tester from a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
    ),
)

# ** constant: tester_list_feature_data
TESTER_LIST_FEATURE_DATA = create_default_feature_data(
    'List Testers',
    'tester',
    'list',
    [
        {
            'service_id': LIST_TESTERS_EVT_ID,
            'name': 'List Testers',
        },
    ],
    description='List testers in a test module.',
    params_schema=create_params_schema(
        **REL_PARAM,
    ),
)

# ** constant: tester_update_feature_data
TESTER_UPDATE_FEATURE_DATA = create_default_feature_data(
    'Update Tester',
    'tester',
    'update',
    [
        {
            'service_id': UPDATE_TESTER_EVT_ID,
            'name': 'Update Tester',
        },
    ],
    description='Update a tester in a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
        **PAYLOAD_FRAGMENT_PARAMS,
    ),
)

# ** constant: tester_remove_feature_data
TESTER_REMOVE_FEATURE_DATA = create_default_feature_data(
    'Remove Tester',
    'tester',
    'remove',
    [
        {
            'service_id': REMOVE_TESTER_EVT_ID,
            'name': 'Remove Tester',
        },
    ],
    description='Remove a tester from a test module.',
    params_schema=create_params_schema(
        **REL_NAME_PARAMS,
    ),
)

# ** constant: tester_attach_feature_data
TESTER_ATTACH_FEATURE_DATA = create_default_feature_data(
    'Attach Test',
    'tester',
    'attach',
    [
        {
            'service_id': ATTACH_TEST_EVT_ID,
            'name': 'Attach Test',
        },
    ],
    description='Attach a test to a tester.',
    params_schema=create_params_schema(
        **ATTACH_PARAMS,
    ),
)

# ** constant: tester_detach_feature_data
TESTER_DETACH_FEATURE_DATA = create_default_feature_data(
    'Detach Test',
    'tester',
    'detach',
    [
        {
            'service_id': DETACH_TEST_EVT_ID,
            'name': 'Detach Test',
        },
    ],
    description='Detach a test from a tester.',
    params_schema=create_params_schema(
        **ATTACH_PARAMS,
    ),
)

# ** constant: module_run_feature_data
MODULE_RUN_FEATURE_DATA = create_default_feature_data(
    'Run Test Module',
    'module',
    'run',
    [],
    description='Run a test module.',
    params_schema=create_params_schema(
        module_path='str',
        summary={
            'type': 'bool',
            'required': False,
        },
    ),
)

# *** constants (services)

# ** constant: tester_event_registration
TESTER_EVENT_REGISTRATION = {
    'module_path': create_service_module_path(
        TIFERET,
        TIFERET_EVENTS_PATH,
        'tester_module',
    ),
}

# ** constant: get_fixture_evt_data
GET_FIXTURE_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='GetFixture',
)

# ** constant: list_fixtures_evt_data
LIST_FIXTURES_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='ListFixtures',
)

# ** constant: get_test_evt_data
GET_TEST_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='GetTest',
)

# ** constant: list_tests_evt_data
LIST_TESTS_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='ListTests',
)

# ** constant: get_tester_evt_data
GET_TESTER_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='GetTester',
)

# ** constant: list_testers_evt_data
LIST_TESTERS_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='ListTesters',
)

# ** constant: add_fixture_evt_data
ADD_FIXTURE_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='AddFixture',
)

# ** constant: update_fixture_evt_data
UPDATE_FIXTURE_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='UpdateFixture',
)

# ** constant: remove_fixture_evt_data
REMOVE_FIXTURE_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='RemoveFixture',
)

# ** constant: add_test_evt_data
ADD_TEST_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='AddTest',
)

# ** constant: update_test_evt_data
UPDATE_TEST_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='UpdateTest',
)

# ** constant: remove_test_evt_data
REMOVE_TEST_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='RemoveTest',
)

# ** constant: add_tester_evt_data
ADD_TESTER_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='AddTester',
)

# ** constant: update_tester_evt_data
UPDATE_TESTER_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='UpdateTester',
)

# ** constant: remove_tester_evt_data
REMOVE_TESTER_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='RemoveTester',
)

# ** constant: attach_test_evt_data
ATTACH_TEST_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='AttachTest',
)

# ** constant: detach_test_evt_data
DETACH_TEST_EVT_DATA = create_service_registration_data(
    **TESTER_EVENT_REGISTRATION,
    class_name='DetachTest',
)

# *** constants (sessions)

# ** constant: tester_cli_session_data
TESTER_CLI_SESSION_DATA = create_default_app_session_data(
    'Tester CLI',
    description='Built-in CLI for the tester writer and module run.',
)

# *** constants (groups)

# ** constant: tester_default_commands
TESTER_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = {
    FIXTURE_ADD_ID: FIXTURE_ADD_COMMAND_DATA,
    FIXTURE_GET_ID: FIXTURE_GET_COMMAND_DATA,
    FIXTURE_LIST_ID: FIXTURE_LIST_COMMAND_DATA,
    FIXTURE_UPDATE_ID: FIXTURE_UPDATE_COMMAND_DATA,
    FIXTURE_REMOVE_ID: FIXTURE_REMOVE_COMMAND_DATA,
    TEST_ADD_ID: TEST_ADD_COMMAND_DATA,
    TEST_GET_ID: TEST_GET_COMMAND_DATA,
    TEST_LIST_ID: TEST_LIST_COMMAND_DATA,
    TEST_UPDATE_ID: TEST_UPDATE_COMMAND_DATA,
    TEST_REMOVE_ID: TEST_REMOVE_COMMAND_DATA,
    TESTER_ADD_ID: TESTER_ADD_COMMAND_DATA,
    TESTER_GET_ID: TESTER_GET_COMMAND_DATA,
    TESTER_LIST_ID: TESTER_LIST_COMMAND_DATA,
    TESTER_UPDATE_ID: TESTER_UPDATE_COMMAND_DATA,
    TESTER_REMOVE_ID: TESTER_REMOVE_COMMAND_DATA,
    TESTER_ATTACH_ID: TESTER_ATTACH_COMMAND_DATA,
    TESTER_DETACH_ID: TESTER_DETACH_COMMAND_DATA,
    MODULE_RUN_ID: MODULE_RUN_COMMAND_DATA,
}

# ** constant: tester_default_features
TESTER_DEFAULT_FEATURES: Dict[str, Dict[str, Any]] = {
    FIXTURE_ADD_ID: FIXTURE_ADD_FEATURE_DATA,
    FIXTURE_GET_ID: FIXTURE_GET_FEATURE_DATA,
    FIXTURE_LIST_ID: FIXTURE_LIST_FEATURE_DATA,
    FIXTURE_UPDATE_ID: FIXTURE_UPDATE_FEATURE_DATA,
    FIXTURE_REMOVE_ID: FIXTURE_REMOVE_FEATURE_DATA,
    TEST_ADD_ID: TEST_ADD_FEATURE_DATA,
    TEST_GET_ID: TEST_GET_FEATURE_DATA,
    TEST_LIST_ID: TEST_LIST_FEATURE_DATA,
    TEST_UPDATE_ID: TEST_UPDATE_FEATURE_DATA,
    TEST_REMOVE_ID: TEST_REMOVE_FEATURE_DATA,
    TESTER_ADD_ID: TESTER_ADD_FEATURE_DATA,
    TESTER_GET_ID: TESTER_GET_FEATURE_DATA,
    TESTER_LIST_ID: TESTER_LIST_FEATURE_DATA,
    TESTER_UPDATE_ID: TESTER_UPDATE_FEATURE_DATA,
    TESTER_REMOVE_ID: TESTER_REMOVE_FEATURE_DATA,
    TESTER_ATTACH_ID: TESTER_ATTACH_FEATURE_DATA,
    TESTER_DETACH_ID: TESTER_DETACH_FEATURE_DATA,
    MODULE_RUN_ID: MODULE_RUN_FEATURE_DATA,
}

# ** constant: tester_query_event_registrations
TESTER_QUERY_EVENT_REGISTRATIONS: Dict[str, Dict[str, Any]] = {
    GET_FIXTURE_EVT_ID: GET_FIXTURE_EVT_DATA,
    LIST_FIXTURES_EVT_ID: LIST_FIXTURES_EVT_DATA,
    GET_TEST_EVT_ID: GET_TEST_EVT_DATA,
    LIST_TESTS_EVT_ID: LIST_TESTS_EVT_DATA,
    GET_TESTER_EVT_ID: GET_TESTER_EVT_DATA,
    LIST_TESTERS_EVT_ID: LIST_TESTERS_EVT_DATA,
}

# ** constant: tester_write_event_registrations
TESTER_WRITE_EVENT_REGISTRATIONS: Dict[str, Dict[str, Any]] = {
    ADD_FIXTURE_EVT_ID: ADD_FIXTURE_EVT_DATA,
    UPDATE_FIXTURE_EVT_ID: UPDATE_FIXTURE_EVT_DATA,
    REMOVE_FIXTURE_EVT_ID: REMOVE_FIXTURE_EVT_DATA,
    ADD_TEST_EVT_ID: ADD_TEST_EVT_DATA,
    UPDATE_TEST_EVT_ID: UPDATE_TEST_EVT_DATA,
    REMOVE_TEST_EVT_ID: REMOVE_TEST_EVT_DATA,
    ADD_TESTER_EVT_ID: ADD_TESTER_EVT_DATA,
    UPDATE_TESTER_EVT_ID: UPDATE_TESTER_EVT_DATA,
    REMOVE_TESTER_EVT_ID: REMOVE_TESTER_EVT_DATA,
    ATTACH_TEST_EVT_ID: ATTACH_TEST_EVT_DATA,
    DETACH_TEST_EVT_ID: DETACH_TEST_EVT_DATA,
}

# ** constant: tester_cli_sessions
TESTER_CLI_SESSIONS: Dict[str, Dict[str, Any]] = {
    TESTER_CLI_ID: TESTER_CLI_SESSION_DATA,
}
