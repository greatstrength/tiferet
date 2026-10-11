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
    Verify both catalogs use the same eighteen id constants, in order.
    '''

    # Assert the command and feature catalogs are the same ordered keys.
    assert list(tester_cli.TESTER_DEFAULT_COMMANDS) == COMMAND_IDS
    assert list(tester_cli.TESTER_DEFAULT_FEATURES) == COMMAND_IDS
    assert tester_cli.MODULE_RUN_ID == 'module.run'
    assert tester_cli.MODULE_RUN_ID in tester_cli.TESTER_DEFAULT_COMMANDS
    assert tester_cli.MODULE_RUN_ID in tester_cli.TESTER_DEFAULT_FEATURES

    # Assert neither value embeds an id.
    for feature_id in COMMAND_IDS:
        command = tester_cli.TESTER_DEFAULT_COMMANDS[feature_id]
        feature = tester_cli.TESTER_DEFAULT_FEATURES[feature_id]
        assert 'id' not in command
        assert 'id' not in feature
        group, key = feature_id.split('.')
        assert command['key'] == key
        assert command['group_key'] == group
        assert feature['feature_key'] == key
        assert feature['group_id'] == group
        assert command['name'] == feature['name']

# ** test: command_arguments_match_the_landed_signatures
def test_command_arguments_match_the_landed_signatures():
    '''
    Verify each command's flags follow the writer and module-run signatures.
    '''

    # Assert flag order, and that parent and config flags stay off the command.
    for feature_id, flags in COMMAND_ARGUMENT_FLAGS.items():
        arguments = tester_cli.TESTER_DEFAULT_COMMANDS[feature_id]['arguments']
        actual = [argument['name_or_flags'][0] for argument in arguments]
        assert actual == flags, feature_id
        assert '--base-dir' not in actual
        assert 'base_dir' not in actual
        assert '--config' not in actual
        assert 'config' not in actual

# ** test: parent_argument_is_base_dir_only
def test_parent_argument_is_base_dir_only():
    '''
    Verify the parent catalog is the one --base-dir definition.
    '''

    # Assert the single parent argument and its default.
    assert len(tester_cli.TESTER_DEFAULT_PARENT_ARGUMENTS) == 1
    argument = tester_cli.TESTER_DEFAULT_PARENT_ARGUMENTS[0]
    assert argument['name_or_flags'] == ['--base-dir']
    assert argument['default'] == '.'
    assert 'type' not in argument
    assert 'required' not in argument
    assert 'tiferet_tests/' in argument['description']

# ** test: payload_is_str_and_summary_is_bool_without_default
def test_payload_is_str_and_summary_is_bool_without_default():
    '''
    Verify payload stays a string and summary is a flag without a default.
    '''

    # Assert every payload argument is an opaque string.
    for feature_id, command in tester_cli.TESTER_DEFAULT_COMMANDS.items():
        for argument in command['arguments']:
            flag = argument['name_or_flags'][0]
            if flag == '--payload':
                assert argument['type'] == 'str', feature_id
            assert argument.get('type') not in ('json', 'yaml', 'dict')

    # Assert summary is the only bool and stores no default.
    summary = tester_cli.TESTER_DEFAULT_COMMANDS['module.run']['arguments'][1]
    assert summary['name_or_flags'] == ['--summary']
    assert summary['type'] == 'bool'
    assert 'default' not in summary

# ** test: writer_features_name_existing_events
def test_writer_features_name_existing_events():
    '''
    Verify each writer feature is one existing event step, and module run is empty.
    '''

    # Assert the seventeen writer steps and the empty module-run steps.
    registrations = dict(tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS)
    registrations.update(tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS)
    for feature_id, feature in tester_cli.TESTER_DEFAULT_FEATURES.items():
        schema = feature['params_schema']
        assert 'base_dir' not in schema
        assert 'group' not in schema
        assert 'command' not in schema
        assert 'document' not in schema
        assert 'working' not in schema
        if feature_id == 'module.run':
            assert feature['steps'] == []
            assert set(schema) == {'module_path', 'summary'}
            assert schema['summary'] == {'type': 'bool', 'required': False}
            assert 'default' not in schema['summary']
            continue
        assert len(feature['steps']) == 1, feature_id
        step = feature['steps'][0]
        assert 'operation' not in step
        assert 'parameters' not in step
        assert step['service_id'] == FEATURE_SERVICE_IDS[feature_id]
        assert step['service_id'] in registrations

# ** test: registrations_split_query_and_write
def test_registrations_split_query_and_write():
    '''
    Verify the two registration dicts name the existing tester-module classes.
    '''

    # Assert the combined name was not invented, and the split names were.
    assert not hasattr(tester_cli, 'TESTER_EVENT_REGISTRATIONS')
    assert list(tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS) == list(
        QUERY_REGISTRATIONS,
    )
    assert list(tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS) == list(
        WRITE_REGISTRATIONS,
    )

    # Assert each value is the existing class on the tester module path.
    expected = dict(QUERY_REGISTRATIONS)
    expected.update(WRITE_REGISTRATIONS)
    actual = dict(tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS)
    actual.update(tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS)
    assert set(actual) == set(expected)
    for service_id, registration in actual.items():
        assert registration['module_path'] == 'tiferet.events.tester_module'
        assert registration['class_name'] == expected[service_id]
        assert 'parameters' not in registration or registration['parameters'] == {}
        assert 'id' not in registration
        assert 'service_id' not in registration

# ** test: session_is_tester_cli_without_wiring
def test_session_is_tester_cli_without_wiring():
    '''
    Verify the tester CLI session is a name and description only.
    '''

    # Assert the session id and the keys the factory is allowed to write.
    assert tester_cli.TESTER_CLI_ID == 'tester_cli'
    assert list(tester_cli.TESTER_CLI_SESSIONS) == [tester_cli.TESTER_CLI_ID]
    session = tester_cli.TESTER_CLI_SESSIONS[tester_cli.TESTER_CLI_ID]
    assert session['name'] == 'Tester CLI'
    assert session['description'] == (
        'Built-in CLI for the tester writer and module run.'
    )
    for forbidden in (
        'services',
        'constants',
        'module_path',
        'class_name',
        'config',
    ):
        assert forbidden not in session

# ** test: module_sections_and_forbidden_names
def test_module_sections_and_forbidden_names():
    '''
    Verify the catalog module keeps the locked sections and names no new class.
    '''

    # Read the catalog source. This test checks shape, not a second catalog.
    source = Path(tester_cli.__file__).read_text()
    positions = [source.index(section) for section in SECTION_ORDER]
    assert positions == sorted(positions)
    assert 'def ' not in source
    assert 'class ' not in source
    for forbidden in (
        'QueryTestModuleCommand',
        'WriteTestModuleCommand',
        'tiferet.events.tester_cli',
        '--config',
        'config.yml',
        'ServiceContainer',
        'ServiceResolver',
    ):
        assert forbidden not in source
