"""Tests for the tester CLI catalog."""

# *** imports

# ** core
from pathlib import Path

# ** app
from tiferet.assets import tester_cli

# *** constants

# ** constant: command_ids
COMMAND_IDS = [
    'fixture.add',
    'fixture.get',
    'fixture.list',
    'fixture.update',
    'fixture.remove',
    'test.add',
    'test.get',
    'test.list',
    'test.update',
    'test.remove',
    'tester.add',
    'tester.get',
    'tester.list',
    'tester.update',
    'tester.remove',
    'tester.attach',
    'tester.detach',
    'module.run',
]

# ** constant: command_argument_flags
COMMAND_ARGUMENT_FLAGS = {
    'fixture.add': [
        'rel',
        'name',
        '--tester',
        '--payload',
        '--fragment',
        '--alias',
        '--anchor',
        '--merge',
    ],
    'fixture.get': [
        'rel',
        'name',
        '--tester',
    ],
    'fixture.list': [
        'rel',
        '--tester',
    ],
    'fixture.update': [
        'rel',
        'name',
        '--tester',
        '--payload',
        '--fragment',
        '--merge',
    ],
    'fixture.remove': [
        'rel',
        'name',
        '--tester',
    ],
    'test.add': [
        'rel',
        'name',
        '--tester',
        '--payload',
        '--fragment',
        '--anchor',
    ],
    'test.get': [
        'rel',
        'name',
        '--tester',
    ],
    'test.list': [
        'rel',
        '--tester',
    ],
    'test.update': [
        'rel',
        'name',
        '--tester',
        '--payload',
        '--fragment',
    ],
    'test.remove': [
        'rel',
        'name',
        '--tester',
    ],
    'tester.add': [
        'rel',
        'name',
        '--payload',
        '--fragment',
        '--anchor',
    ],
    'tester.get': [
        'rel',
        'name',
    ],
    'tester.list': [
        'rel',
    ],
    'tester.update': [
        'rel',
        'name',
        '--payload',
        '--fragment',
    ],
    'tester.remove': [
        'rel',
        'name',
    ],
    'tester.attach': [
        'rel',
        'tester',
        'name',
    ],
    'tester.detach': [
        'rel',
        'tester',
        'name',
    ],
    'module.run': [
        'module_path',
        '--summary',
    ],
}

# ** constant: feature_service_ids
FEATURE_SERVICE_IDS = {
    'fixture.add': 'add_fixture_evt',
    'fixture.update': 'update_fixture_evt',
    'fixture.remove': 'remove_fixture_evt',
    'test.add': 'add_test_evt',
    'test.update': 'update_test_evt',
    'test.remove': 'remove_test_evt',
    'tester.add': 'add_tester_evt',
    'tester.update': 'update_tester_evt',
    'tester.remove': 'remove_tester_evt',
    'tester.attach': 'attach_test_evt',
    'tester.detach': 'detach_test_evt',
    'fixture.get': 'get_fixture_evt',
    'fixture.list': 'list_fixtures_evt',
    'test.get': 'get_test_evt',
    'test.list': 'list_tests_evt',
    'tester.get': 'get_tester_evt',
    'tester.list': 'list_testers_evt',
}

# ** constant: query_registrations
QUERY_REGISTRATIONS = {
    'get_fixture_evt': 'GetFixture',
    'list_fixtures_evt': 'ListFixtures',
    'get_test_evt': 'GetTest',
    'list_tests_evt': 'ListTests',
    'get_tester_evt': 'GetTester',
    'list_testers_evt': 'ListTesters',
}

# ** constant: write_registrations
WRITE_REGISTRATIONS = {
    'add_fixture_evt': 'AddFixture',
    'update_fixture_evt': 'UpdateFixture',
    'remove_fixture_evt': 'RemoveFixture',
    'add_test_evt': 'AddTest',
    'update_test_evt': 'UpdateTest',
    'remove_test_evt': 'RemoveTest',
    'add_tester_evt': 'AddTester',
    'update_tester_evt': 'UpdateTester',
    'remove_tester_evt': 'RemoveTester',
    'attach_test_evt': 'AttachTest',
    'detach_test_evt': 'DetachTest',
}

# ** constant: section_order
SECTION_ORDER = [
    '# *** imports',
    '# *** constants (ids)',
    '# *** constants (parent)',
    '# *** constants (commands)',
    '# *** constants (features)',
    '# *** constants (services)',
    '# *** constants (sessions)',
    '# *** constants (groups)',
]

# *** tests

# ** test: command_and_feature_catalogs_share_eighteen_ids
def test_command_and_feature_catalogs_share_eighteen_ids():
    '''
    Verify command and feature catalogs share eighteen ids.
    '''

    # Read both catalogs and the module-run id.
    commands = tester_cli.TESTER_DEFAULT_COMMANDS
    features = tester_cli.TESTER_DEFAULT_FEATURES

    # Assert ordered keys and module-run membership.
    assert list(commands) == COMMAND_IDS
    assert list(features) == COMMAND_IDS
    assert tester_cli.MODULE_RUN_ID == 'module.run'
    assert tester_cli.MODULE_RUN_ID in commands
    assert tester_cli.MODULE_RUN_ID in features

    # Assert each pair omits id and matches prefix, suffix, and name.
    for command_id in COMMAND_IDS:
        command = commands[command_id]
        feature = features[command_id]
        prefix, suffix = command_id.split('.')
        assert 'id' not in command
        assert 'id' not in feature
        assert command['key'] == suffix
        assert command['group_key'] == prefix
        assert feature['feature_key'] == suffix
        assert feature['group_id'] == prefix
        assert command['name'] == feature['name']

# ** test: command_arguments_match_the_landed_signatures
def test_command_arguments_match_the_landed_signatures():
    '''
    Verify each command's first flags match the landed signature.
    '''

    # Read each command's first flags and reject parent or config flags.
    for command_id, flags in COMMAND_ARGUMENT_FLAGS.items():
        command = tester_cli.TESTER_DEFAULT_COMMANDS[command_id]
        actual = [
            argument['name_or_flags'][0]
            for argument in command['arguments']
        ]
        assert actual == flags
        assert '--base-dir' not in actual
        assert 'base_dir' not in actual
        assert '--config' not in actual
        assert 'config' not in actual

# ** test: parent_argument_is_base_dir_only
def test_parent_argument_is_base_dir_only():
    '''
    Verify the parent list is a single untyped --base-dir argument.
    '''

    # Read the parent list and its one item.
    parent = tester_cli.TESTER_DEFAULT_PARENT_ARGUMENTS
    item = parent[0]

    # Assert the parent is --base-dir with default '.' and no type or required.
    assert len(parent) == 1
    assert item['name_or_flags'] == ['--base-dir']
    assert item['default'] == '.'
    assert 'type' not in item
    assert 'required' not in item
    assert 'tiferet_tests/' in item['description']

# ** test: payload_is_str_and_summary_is_bool_without_default
def test_payload_is_str_and_summary_is_bool_without_default():
    '''
    Verify --payload is str and --summary is bool without a default.
    '''

    # Read every command argument, then the second argument of module.run.
    for command in tester_cli.TESTER_DEFAULT_COMMANDS.values():
        for argument in command['arguments']:
            if argument['name_or_flags'][0] == '--payload':
                assert argument['type'] == 'str'
            assert argument.get('type') not in [
                'json',
                'yaml',
                'dict',
            ]

    summary = tester_cli.TESTER_DEFAULT_COMMANDS['module.run']['arguments'][1]

    # Assert --summary is bool and has no default.
    assert summary['name_or_flags'] == ['--summary']
    assert summary['type'] == 'bool'
    assert 'default' not in summary

# ** test: writer_features_name_existing_events
def test_writer_features_name_existing_events():
    '''
    Verify writer features name existing events and omit working keys.
    '''

    # Read each feature's steps and params_schema.
    query = tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS
    write = tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS
    forbidden = [
        'base_dir',
        'group',
        'command',
        'document',
        'working',
    ]

    for feature_id, feature in tester_cli.TESTER_DEFAULT_FEATURES.items():
        schema = feature['params_schema']
        for key in forbidden:
            assert key not in schema

        if feature_id == 'module.run':
            assert feature['steps'] == []
            assert set(schema) == {
                'module_path',
                'summary',
            }
            assert schema['summary']['type'] == 'bool'
            assert schema['summary']['required'] is False
            assert 'default' not in schema['summary']
            continue

        step = feature['steps'][0]
        assert len(feature['steps']) == 1
        assert 'operation' not in step
        assert 'parameters' not in step
        assert step['service_id'] == FEATURE_SERVICE_IDS[feature_id]
        assert step['service_id'] in query or step['service_id'] in write

# ** test: registrations_split_query_and_write
def test_registrations_split_query_and_write():
    '''
    Verify query and write registrations stay split and name writer classes.
    '''

    # Read the two registration dicts.
    query = tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS
    write = tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS

    # Assert there is no combined catalog and keys match the fixtures.
    assert getattr(tester_cli, 'TESTER_EVENT_REGISTRATIONS', None) is None
    assert list(query) == list(QUERY_REGISTRATIONS)
    assert list(write) == list(WRITE_REGISTRATIONS)

    # Assert each registration names the writer module and class.
    for catalog, fixture in [
        (query, QUERY_REGISTRATIONS),
        (write, WRITE_REGISTRATIONS),
    ]:
        for service_id, class_name in fixture.items():
            registration = catalog[service_id]
            assert registration['module_path'] == 'tiferet.events.tester_module'
            assert registration['class_name'] == class_name
            assert 'id' not in registration
            assert 'service_id' not in registration
            assert registration.get('parameters', {}) == {}

# ** test: session_is_tester_cli_without_wiring
def test_session_is_tester_cli_without_wiring():
    '''
    Verify the tester CLI session has no wiring fields.
    '''

    # Read the session id and the session value.
    session = tester_cli.TESTER_CLI_SESSIONS[tester_cli.TESTER_CLI_ID]

    # Assert the session is tester_cli without services or config.
    assert tester_cli.TESTER_CLI_ID == 'tester_cli'
    assert list(tester_cli.TESTER_CLI_SESSIONS) == [tester_cli.TESTER_CLI_ID]
    assert session['name'] == 'Tester CLI'
    assert session['description'] == (
        'Built-in CLI for the tester writer and module run.'
    )
    assert 'services' not in session
    assert 'constants' not in session
    assert 'module_path' not in session
    assert 'class_name' not in session
    assert 'config' not in session

# ** test: module_sections_and_forbidden_names
def test_module_sections_and_forbidden_names():
    '''
    Verify catalog section order and forbidden names.
    '''

    # Read the catalog module text.
    text = Path(tester_cli.__file__).read_text()
    indexes = [text.index(heading) for heading in SECTION_ORDER]

    # Assert headings appear in order and forbidden names are absent.
    assert indexes == sorted(indexes)
    assert 'def ' not in text
    assert 'class ' not in text
    assert 'QueryTestModuleCommand' not in text
    assert 'WriteTestModuleCommand' not in text
    assert 'tiferet.events.tester_cli' not in text
    assert '--config' not in text
    assert 'config.yml' not in text
    assert 'ServiceContainer' not in text
    assert 'ServiceResolver' not in text
