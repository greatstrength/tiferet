"""Tiferet CLI Blueprints Tests"""

# *** imports

# ** core
import argparse

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.blueprints import core
from tiferet.blueprints.cli import (
    group_commands_by_key,
    build_argument_parser,
    derive_feature_request,
    parse_cli_args_handler,
    create_cli_request_context,
    build_cli_cache,
    list_commands_handler,
    get_parent_args_handler,
    build_cli_session_context,
    build_app,
)
from tiferet.blueprints import cli as cli_blueprint
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import (
    CliRequestContext,
    CliSessionContext,
    CLI_COMMAND_CACHE_PREFIX,
)
from tiferet.domain import AppSession, CliArgument, CliCommand

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

# ** test: blueprint_exposes_parsing_helpers
def test_blueprint_exposes_parsing_helpers() -> None:
    '''
    Test that the CLI blueprint module exposes the parsing helpers and injected
    handlers, and no longer exposes the retired response handler or parser helpers.
    '''

    # Assert the retained parsing helpers and injected handlers are present.
    for name in (
        'group_commands_by_key',
        'build_argument_parser',
        'derive_feature_request',
        'build_cli_cache',
        'parse_cli_args_handler',
        'create_cli_request_context',
        'list_commands_handler',
        'get_parent_args_handler',
        'build_cli_session_context',
    ):
        assert hasattr(cli_blueprint, name)

    # Assert the retired names are absent.
    for name in (
        'cli_response_handler',
        'get_commands',
        'get_parent_arguments',
        'build_argument_kwargs',
        'parse_argv',
    ):
        assert not hasattr(cli_blueprint, name)

# ** test: list_commands_handler_returns_event_result
def test_list_commands_handler_returns_event_result() -> None:
    '''
    Test that list_commands_handler resolves the app-scoped event and returns a
    non-None list as the same object.
    '''

    # Build an event whose execute returns a specific list object.
    commands = [CliCommand(name='Add', key='add', group_key='calc')]
    event = mock.Mock()
    event.execute.return_value = commands
    get_dependency = mock.Mock(return_value=event)

    # Invoke the handler.
    result = list_commands_handler(CacheContext(), get_dependency)()

    # Assert the event was resolved once and its list returned unchanged.
    get_dependency.assert_called_once_with('list_commands_evt', 'app')
    event.execute.assert_called_once_with()
    assert result is commands

# ** test: list_commands_handler_falls_back_when_event_returns_none
def test_list_commands_handler_falls_back_when_event_returns_none() -> None:
    '''
    Test that a None event result falls back to the cache defaults, which are
    empty when the cache has no CLI commands.
    '''

    # Build an event that returns None.
    event = mock.Mock()
    event.execute.return_value = None
    get_dependency = mock.Mock(return_value=event)

    # Invoke the handler against an unseeded cache.
    result = list_commands_handler(CacheContext(), get_dependency)()

    # Assert the fallback is an empty list and the event was app-scoped.
    assert result == []
    get_dependency.assert_called_once_with('list_commands_evt', 'app')

# ** test: list_commands_handler_empty_list_does_not_fall_back
def test_list_commands_handler_empty_list_does_not_fall_back() -> None:
    '''
    Test that an empty event result is returned unchanged and does not read the
    cache-seeded defaults.
    '''

    # Build an event that returns an empty list.
    event = mock.Mock()
    event.execute.return_value = []
    get_dependency = mock.Mock(return_value=event)

    # Invoke the handler with the default-command reader patched.
    with mock.patch('tiferet.blueprints.cli.get_default_cli_commands') as mock_defaults:
        result = list_commands_handler(CacheContext(), get_dependency)()

    # Assert the empty list is returned and the cache fallback was not used.
    assert result == []
    mock_defaults.assert_not_called()

# ** test: get_parent_args_handler_resolves_app_scoped_event
def test_get_parent_args_handler_resolves_app_scoped_event() -> None:
    '''
    Test that get_parent_args_handler resolves the app-scoped event and returns
    its execute result.
    '''

    # Build an event whose execute returns a parent-argument list.
    arguments = [CliArgument(name_or_flags=['--verbose'])]
    event = mock.Mock()
    event.execute.return_value = arguments
    get_dependency = mock.Mock(return_value=event)

    # Invoke the handler.
    result = get_parent_args_handler(get_dependency)()

    # Assert the event was resolved once and its result returned.
    get_dependency.assert_called_once_with('get_parent_args_evt', 'app')
    assert result is arguments

# ** test: get_parent_args_handler_returns_none_unchanged
def test_get_parent_args_handler_returns_none_unchanged() -> None:
    '''
    Test that a None parent-argument result is returned unchanged.
    '''

    # Build an event that returns None.
    event = mock.Mock()
    event.execute.return_value = None
    get_dependency = mock.Mock(return_value=event)

    # Assert None passes through.
    assert get_parent_args_handler(get_dependency)() is None

# ** test: parse_cli_args_handler_returns_feature_request_tuple
def test_parse_cli_args_handler_returns_feature_request_tuple() -> None:
    '''
    Test that parse_cli_args_handler derives the feature tuple from injected callables.
    '''

    # Build the handler from injected command and parent-argument callables.
    handler = parse_cli_args_handler(
        list_commands=lambda: [CliCommand(name='Add', key='add', group_key='calc')],
        get_parent_args=lambda: [],
    )

    # Parse a fully qualified argv.
    feature_id, headers, data = handler(['calc', 'add'])

    # Assert the derived feature request.
    assert feature_id == 'calc.add'
    assert headers == {'command_group': 'calc', 'command_key': 'add'}
    assert data['group'] == 'calc'
    assert data['command'] == 'add'

# ** test: parse_cli_args_handler_applies_parse_value
def test_parse_cli_args_handler_applies_parse_value() -> None:
    '''
    Test that the handler maps each parsed value through the owning argument's
    get_dest / parse_value pair.
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

    # Build the handler from injected callables and parse structured argv.
    handler = parse_cli_args_handler(
        list_commands=lambda: [command],
        get_parent_args=lambda: [],
    )
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

    # Assert the standard feature-not-found error is seeded by app.build_cache.
    assert cache.get('FEATURE_NOT_FOUND', 'app', 'errors') is not None

# ** test: build_cli_session_context_passes_handlers_not_raw_events
def test_build_cli_session_context_passes_handlers_not_raw_events() -> None:
    '''
    Test that build_cli_session_context passes injected handlers and does not
    resolve CLI events during construction.
    '''

    # Isolate container and resolver construction.
    app_session = AppSession(id='test_cli', name='Test CLI Session')
    cache = CacheContext()
    app_container = mock.Mock(name='app_container')
    resolver = mock.Mock(name='resolver')
    composed = object()
    with mock.patch('tiferet.blueprints.cli.core.build_app_service_container', return_value=app_container) as mock_container, \
         mock.patch('tiferet.blueprints.cli.core.build_service_resolver', return_value=resolver) as mock_resolver, \
         mock.patch('tiferet.blueprints.cli.core.compose_session_context', return_value=composed) as mock_compose:
        result = build_cli_session_context(app_session, cache)

    # Assert the container and resolver were built once and not queried.
    mock_container.assert_called_once_with(cache, app_session)
    mock_resolver.assert_called_once_with(app_container)
    app_container.get_dependency.assert_not_called()
    resolver.get_dependency.assert_not_called()

    # Assert composition receives the resolver, not the container, plus the CLI callables.
    positional = mock_compose.call_args.args
    assert positional[:4] == (CliSessionContext, app_session, cache, resolver)
    assert app_container not in positional
    keywords = mock_compose.call_args.kwargs
    assert keywords['response_handler'] is core.response_handler
    assert keywords['create_request_handler'] is create_cli_request_context
    assert callable(keywords['list_commands_handler'])
    assert callable(keywords['get_parent_args_handler'])
    assert callable(keywords['parse_cli_args'])
    assert result is composed

# ** test: build_app_delegates_to_context
def test_build_app_delegates_to_context() -> None:
    '''
    Test that build_app composes the CLI session context and delegates argv to
    its run method.
    '''

    # Isolate build_app from the cache, session resolution, and context composition.
    with mock.patch('tiferet.blueprints.cli.build_cli_cache') as mock_cache, \
         mock.patch('tiferet.blueprints.cli.core.get_app_session') as mock_get_session, \
         mock.patch('tiferet.blueprints.cli.build_cli_session_context') as mock_build_ctx:
        mock_cache.return_value = CacheContext()
        mock_get_session.return_value = AppSession(id='test_cli', name='Test CLI Session')
        mock_context = mock.Mock(spec=CliSessionContext)
        mock_context.run.return_value = 'test-response'
        mock_build_ctx.return_value = mock_context

        # Invoke build_app with an explicit argv.
        response = build_app('test_cli', argv=['test-group', 'test-feature'])

    # Assert the cache was built once and the session id was the first positional.
    mock_cache.assert_called_once_with()
    assert mock_get_session.call_args.args[0] == 'test_cli'

    # Assert the context's run was invoked with the supplied argv.
    mock_context.run.assert_called_once_with(['test-group', 'test-feature'])

    # Assert the run response is returned unchanged.
    assert response == 'test-response'

# ** test: build_app_defaults_argv_none
def test_build_app_defaults_argv_none() -> None:
    '''
    Test that build_app forwards a missing argv as None.
    '''

    # Isolate build_app from the cache, session resolution, and context composition.
    with mock.patch('tiferet.blueprints.cli.build_cli_cache'), \
         mock.patch('tiferet.blueprints.cli.core.get_app_session') as mock_get_session, \
         mock.patch('tiferet.blueprints.cli.build_cli_session_context') as mock_build_ctx:
        mock_get_session.return_value = AppSession(id='test_cli', name='Test CLI Session')
        mock_context = mock.Mock(spec=CliSessionContext)
        mock_build_ctx.return_value = mock_context

        # Invoke build_app without argv.
        build_app('test_cli')

    # Assert run was called once with None.
    mock_context.run.assert_called_once_with(None)
