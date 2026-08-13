"""Tiferet CLI Blueprints Tests"""

# *** imports

# ** core
import argparse

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.blueprints.cli import (
    group_commands_by_key,
    build_argument_parser,
    derive_feature_request,
    parse_cli_args_handler,
    create_cli_request_context,
    cli_response_handler,
    build_cli_cache,
    build_cli_session_context,
    build_app,
)
from tiferet.contexts.app import add_default_app_services
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import (
    CliRequestContext,
    CliSessionContext,
    CLI_COMMAND_CACHE_PREFIX,
)
from tiferet.domain import AppSession, CliArgument, CliCommand
from tiferet.events.cli import GetParentArguments, ListCliCommands

# *** fixtures

# ** fixture: cli_command_list
@pytest.fixture
def cli_command_list() -> list:
    '''
    Build a list of CLI commands spanning two groups.

    :return: The sample CLI commands.
    :rtype: list
    '''

    # Return two commands in the first group and one in the second.
    return [
        CliCommand(
            group_key='test-group',
            key='test-feature',
            name='Test Feature Command',
            description='A test feature command.',
            arguments=[
                CliArgument(
                    name_or_flags=['--arg1', '-a'],
                    description='Test argument 1.',
                    type='str',
                ),
            ],
        ),
        CliCommand(
            group_key='test-group',
            key='other-feature',
            name='Other Feature Command',
            description='Another test feature command.',
        ),
        CliCommand(
            group_key='alt-group',
            key='alt-feature',
            name='Alt Feature Command',
            description='An alternate group command.',
        ),
    ]

# ** fixture: list_commands_evt
@pytest.fixture
def list_commands_evt(cli_command_list: list):
    '''
    Build a mock ListCliCommands event returning the sample commands.

    :param cli_command_list: The sample CLI commands.
    :type cli_command_list: list
    :return: The mocked list-commands event.
    :rtype: mock.Mock
    '''

    # Build and return the mocked event.
    evt = mock.Mock(spec=ListCliCommands)
    evt.execute.return_value = cli_command_list
    return evt

# ** fixture: get_parent_args_evt
@pytest.fixture
def get_parent_args_evt():
    '''
    Build a mock GetParentArguments event returning no parent arguments.

    :return: The mocked parent-arguments event.
    :rtype: mock.Mock
    '''

    # Build and return the mocked event.
    evt = mock.Mock(spec=GetParentArguments)
    evt.execute.return_value = []
    return evt

# *** tests

# ** test: group_commands_by_key
def test_group_commands_by_key(cli_command_list: list) -> None:
    '''
    Test that group_commands_by_key groups by group key and preserves order.

    :param cli_command_list: The sample CLI commands.
    :type cli_command_list: list
    '''

    # Group the sample commands.
    grouped = group_commands_by_key(cli_command_list)

    # Assert the group keys are present in encounter order.
    assert list(grouped.keys()) == ['test-group', 'alt-group']

    # Assert the commands within a group preserve insertion order.
    assert [command.key for command in grouped['test-group']] == ['test-feature', 'other-feature']
    assert [command.key for command in grouped['alt-group']] == ['alt-feature']

# ** test: build_argument_parser_structure
def test_build_argument_parser_structure(cli_command_list: list) -> None:
    '''
    Test that build_argument_parser returns a parser wired with the groups,
    commands, and command arguments.

    :param cli_command_list: The sample CLI commands.
    :type cli_command_list: list
    '''

    # Build the parser from the grouped commands and a single parent argument.
    parent_argument = CliArgument(
        name_or_flags=['--verbose'],
        description='Enable verbose output.',
        type='bool',
    )
    parser = build_argument_parser(group_commands_by_key(cli_command_list), [parent_argument])

    # Assert the result is a configured argument parser.
    assert isinstance(parser, argparse.ArgumentParser)

    # Assert a fully qualified command parses into the expected namespace.
    parsed = vars(parser.parse_args(['test-group', 'test-feature', '--arg1', 'hello', '--verbose']))
    assert parsed['group'] == 'test-group'
    assert parsed['command'] == 'test-feature'
    assert parsed['arg1'] == 'hello'
    assert parsed['verbose'] is True

    # Assert the second group is registered as well.
    alt_parsed = vars(parser.parse_args(['alt-group', 'alt-feature']))
    assert alt_parsed['group'] == 'alt-group'
    assert alt_parsed['command'] == 'alt-feature'

# ** test: derive_feature_request_normalizes
def test_derive_feature_request_normalizes() -> None:
    '''
    Test that derive_feature_request normalises hyphens into the feature id
    while the headers retain the raw group and command values.
    '''

    # Derive the feature request from a hyphenated group and command.
    feature_id, headers = derive_feature_request({'group': 'test-group', 'command': 'test-feature'})

    # Assert the feature id is normalised and the headers are raw.
    assert feature_id == 'test_group.test_feature'
    assert headers == dict(command_group='test-group', command_key='test-feature')

# ** test: parse_cli_args_handler_fallback
def test_parse_cli_args_handler_fallback(cli_command_list: list, get_parent_args_evt) -> None:
    '''
    Test that the handler falls back to the bootstrap default command list when
    the list-commands event returns no results.

    :param cli_command_list: The sample CLI commands used as bootstrap defaults.
    :type cli_command_list: list
    :param get_parent_args_evt: The mocked parent-arguments event.
    :type get_parent_args_evt: mock.Mock
    '''

    # Build an event that returns no commands.
    empty_evt = mock.Mock(spec=ListCliCommands)
    empty_evt.execute.return_value = []

    # Build the handler with the sample commands as the bootstrap defaults.
    handler = parse_cli_args_handler(empty_evt, get_parent_args_evt, cli_command_list)

    # Parse an argv drawn only from the default command catalog.
    feature_id, headers, data = handler(['test-group', 'test-feature', '--arg1', 'hello'])

    # Assert the defaults were used to build the parser.
    assert feature_id == 'test_group.test_feature'
    assert headers == dict(command_group='test-group', command_key='test-feature')
    assert data['arg1'] == 'hello'

# ** test: parse_cli_args_handler_applies_parse_value
def test_parse_cli_args_handler_applies_parse_value(get_parent_args_evt) -> None:
    '''
    Test that the handler maps each parsed value through the owning argument's
    get_dest / parse_value pair.

    :param get_parent_args_evt: The mocked parent-arguments event.
    :type get_parent_args_evt: mock.Mock
    '''

    # Build a command carrying a dict-typed and a json-typed argument.
    command = CliCommand(
        group_key='service',
        key='set-constants',
        name='Set Service Constants',
        arguments=[
            CliArgument(name_or_flags=['--constant-pairs'], type='dict'),
            CliArgument(name_or_flags=['--parameters'], type='json'),
        ],
    )
    list_evt = mock.Mock(spec=ListCliCommands)
    list_evt.execute.return_value = [command]

    # Build the handler and parse structured argv.
    handler = parse_cli_args_handler(list_evt, get_parent_args_evt)
    _, _, data = handler([
        'service',
        'set-constants',
        '--constant-pairs', 'a=1', 'b=2',
        '--parameters', '{"x": 1}',
    ])

    # Assert the dict tokens were assembled under the derived dest.
    assert data['constant_pairs'] == {'a': '1', 'b': '2'}

    # Assert the JSON value was decoded at parse time.
    assert data['parameters'] == {'x': 1}

# ** test: create_cli_request_context_type
def test_create_cli_request_context_type() -> None:
    '''
    Test that create_cli_request_context returns a CliRequestContext stamped
    with the interface id.
    '''

    # Compose the CLI request context.
    request = create_cli_request_context(
        'test_cli',
        'test_group.test_feature',
        headers=dict(command_group='test-group'),
        data=dict(arg1='hello'),
    )

    # Assert the composed type and the stamped headers.
    assert isinstance(request, CliRequestContext)
    assert request.headers['interface_id'] == 'test_cli'
    assert request.headers['command_group'] == 'test-group'
    assert request.feature_id == 'test_group.test_feature'
    assert request.data == dict(arg1='hello')

# ** test: cli_response_handler
def test_cli_response_handler() -> None:
    '''
    Test that cli_response_handler delegates to the request's handle_response.
    '''

    # Build a request whose handle_response returns a sentinel.
    request = mock.Mock()
    request.handle_response.return_value = 'handled'

    # Invoke the handler.
    result = cli_response_handler(request)

    # Assert the delegation and the returned value.
    request.handle_response.assert_called_once_with()
    assert result == 'handled'

# ** test: build_cli_cache_seeds_commands
def test_build_cli_cache_seeds_commands() -> None:
    '''
    Test that build_cli_cache seeds the built-in CLI command catalog under the
    CLI command cache prefix alongside the core framework defaults.
    '''

    # Build the CLI cache.
    cache = build_cli_cache()

    # Assert the cache is a real cache context seeded with the CLI commands.
    assert isinstance(cache, CacheContext)
    seeded = cache.get_by_prefix(*CLI_COMMAND_CACHE_PREFIX)
    assert seeded
    assert all(isinstance(command, CliCommand) for command in seeded.values())

    # Assert a known built-in command id is present.
    assert 'cli.list_commands' in seeded

# ** test: build_cli_session_context_wires_cli_handlers
def test_build_cli_session_context_wires_cli_handlers() -> None:
    '''
    Test that build_cli_session_context composes a CliSessionContext with the
    CLI-specific request and response handlers and the injected arg parser.
    '''

    # Seed a cache with the app services the CLI composition chain resolves.
    placeholder = {
        'module_path': 'tiferet.contexts.cache',
        'class_name': 'CacheContext',
    }
    cache = add_default_app_services({
        'di_service': {'service_id': 'di_service', **placeholder},
        'list_commands_evt': {'service_id': 'list_commands_evt', **placeholder},
        'get_parent_args_evt': {'service_id': 'get_parent_args_evt', **placeholder},
    })(lambda: CacheContext())()

    # Bypass the real logging pipeline; this test targets handler wiring only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    with mock.patch('tiferet.blueprints.core.build_logger_handler', return_value=fake_build_logger):
        context = build_cli_session_context(
            AppSession(id='test_cli', name='Test CLI Session'),
            cache,
        )

    # Assert the CLI session context was composed with the CLI handler slots.
    assert isinstance(context, CliSessionContext)
    assert context._create_request is create_cli_request_context
    assert context._build_response is cli_response_handler
    assert context._parse_cli_args is not None
    assert context._build_logger is fake_build_logger

# ** test: build_app_delegates_to_context
def test_build_app_delegates_to_context() -> None:
    '''
    Test that build_app composes the CLI session context and delegates argv to
    its run method.
    '''

    # Isolate build_app from the session resolution and context composition.
    with mock.patch('tiferet.blueprints.cli.core.get_app_session') as mock_get_session, \
         mock.patch('tiferet.blueprints.cli.build_cli_session_context') as mock_build_ctx:
        mock_get_session.return_value = AppSession(id='test_cli', name='Test CLI Session')
        mock_context = mock.Mock(spec=CliSessionContext)
        mock_context.run.return_value = 'test-response'
        mock_build_ctx.return_value = mock_context

        # Invoke build_app with an explicit argv.
        response = build_app('test_cli', argv=['test-group', 'test-feature'])

    # Assert the context's run was invoked with the supplied argv.
    mock_context.run.assert_called_once_with(['test-group', 'test-feature'])

    # Assert the run response is returned unchanged.
    assert response == 'test-response'
