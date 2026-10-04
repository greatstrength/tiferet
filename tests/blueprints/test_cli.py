"""Tiferet CLI Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
import tiferet.blueprints.cli as cli_blueprint
from tiferet.blueprints.cli import build_app
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import CliSessionContext
from tiferet.domain import CliArgument, CliCommand

# *** tests

# ** test: build_app_delegates_to_run
def test_build_app_delegates_to_run():
    '''
    Test that build_app builds the cache, resolves the session, composes the CLI
    context via build_cli_session_context, and delegates argv to context.run.
    '''

    # Arrange a mock CLI context whose run returns a sentinel response.
    mock_cli_context = mock.Mock()
    mock_cli_context.run.return_value = 'cli-response'

    # Patch the internal composition helpers to isolate build_app.
    with mock.patch.object(cli_blueprint, 'build_cli_cache') as mock_cache, \
         mock.patch.object(cli_blueprint.core, 'get_app_session') as mock_session, \
         mock.patch.object(cli_blueprint, 'build_cli_session_context', return_value=mock_cli_context) as mock_ctx:

        # Invoke build_app with a sample argv.
        argv = ['calc', 'add', '1', '2']
        response = build_app('test_cli', argv=argv)

    # Assert the cache was built and the session resolved for the requested id.
    mock_cache.assert_called_once()
    mock_session.assert_called_once()
    assert mock_session.call_args[0][0] == 'test_cli'

    # Assert the CLI context was composed and argv delegated to run.
    mock_ctx.assert_called_once()
    mock_cli_context.run.assert_called_once_with(argv)
    assert response == 'cli-response'


# ** test: build_app_defaults_argv_none
def test_build_app_defaults_argv_none():
    '''
    Test that build_app forwards a None argv to context.run when none is provided.
    '''

    # Arrange a mock CLI context.
    mock_cli_context = mock.Mock()
    mock_cli_context.run.return_value = None

    # Patch the internal helpers and invoke without an explicit argv.
    with mock.patch.object(cli_blueprint, 'build_cli_cache'), \
         mock.patch.object(cli_blueprint.core, 'get_app_session'), \
         mock.patch.object(cli_blueprint, 'build_cli_session_context', return_value=mock_cli_context):
        build_app('test_cli')

    # Assert run received None (argv defaults to sys.argv[1:] inside the context).
    mock_cli_context.run.assert_called_once_with(None)


# ** test: blueprint_exposes_parsing_helpers
def test_blueprint_exposes_parsing_helpers():
    '''
    Test that the expanded blueprint exposes the argparse helpers that moved
    here from contexts/cli.py.
    '''

    # Assert the canonical parsing helpers are on the blueprint module.
    for name in ('group_commands_by_key', 'build_argument_parser', 'derive_feature_request'):
        assert hasattr(cli_blueprint, name), f'{name} not found on cli blueprint'

    # Assert the blueprint owns the new composition helpers.
    for name in ('build_cli_cache', 'parse_cli_args_handler', 'create_cli_request_context',
                 'list_commands_handler', 'get_parent_args_handler', 'build_cli_session_context'):
        assert hasattr(cli_blueprint, name), f'{name} not found on cli blueprint'

    # Assert the retired CLI response alias is absent.
    assert not hasattr(cli_blueprint, 'cli_response_handler')

    # Assert legacy names that never belonged here are absent.
    for name in ('get_commands', 'get_parent_arguments', 'build_argument_kwargs', 'parse_argv'):
        assert not hasattr(cli_blueprint, name), f'{name} should not be on cli blueprint'


# ** test: group_commands_by_key_groups_correctly
def test_group_commands_by_key_groups_correctly():
    '''
    Test that group_commands_by_key groups commands by group key in order.
    '''

    # Group a flat list of commands spanning two groups.
    commands = cli_blueprint.group_commands_by_key([
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Subtract', key='subtract', group_key='calc'),
        CliCommand(name='Boot', key='boot', group_key='sys'),
    ])

    # Assert the commands are grouped by group key preserving order.
    assert set(commands.keys()) == {'calc', 'sys'}
    assert [c.key for c in commands['calc']] == ['add', 'subtract']
    assert [c.key for c in commands['sys']] == ['boot']


# ** test: build_argument_parser_parses_command_arguments
def test_build_argument_parser_parses_command_arguments():
    '''
    Test that build_argument_parser produces a parser that parses command arguments.
    '''

    # Build a command map with a single typed command.
    commands = {
        'calc': [
            CliCommand(
                name='Add', key='add', group_key='calc',
                arguments=[
                    CliArgument(name_or_flags=['a'], type='int'),
                    CliArgument(name_or_flags=['b'], type='int'),
                ],
            ),
        ],
    }

    # Build the parser (no parent arguments) and parse a sample argv.
    parser = cli_blueprint.build_argument_parser(commands, [])
    parsed = vars(parser.parse_args(['calc', 'add', '1', '2']))

    # Assert the group, command, and typed values parse correctly.
    assert parsed['group'] == 'calc'
    assert parsed['command'] == 'add'
    assert parsed['a'] == 1
    assert parsed['b'] == 2


# ** test: derive_feature_request_normalizes_hyphens
def test_derive_feature_request_normalizes_hyphens():
    '''
    Test that derive_feature_request builds the feature id and headers,
    normalizing hyphens to underscores in the feature id only.
    '''

    # Derive from a parsed namespace with hyphenated group and command.
    feature_id, headers = cli_blueprint.derive_feature_request(
        {'group': 'my-calc', 'command': 'sub-tract', 'a': 1},
    )

    # Assert the feature id is normalized and headers keep raw values.
    assert feature_id == 'my_calc.sub_tract'
    assert headers == {'command_group': 'my-calc', 'command_key': 'sub-tract'}

# ** test: list_commands_handler_returns_event_result
def test_list_commands_handler_returns_event_result():
    '''
    Test that list_commands_handler resolves list_commands_evt through the
    app flag and returns the event result.
    '''

    # Arrange an app-scoped event that returns commands.
    commands = [CliCommand(name='Add', key='add', group_key='calc')]
    event = mock.Mock()
    event.execute.return_value = commands
    get_dependency = mock.Mock(return_value=event)

    # Build and invoke the handler.
    handler = cli_blueprint.list_commands_handler(CacheContext(), get_dependency)
    result = handler()

    # Assert the event was resolved on the app flag and its result returned.
    get_dependency.assert_called_once_with('list_commands_evt', 'app')
    event.execute.assert_called_once_with()
    assert result is commands

# ** test: list_commands_handler_falls_back_when_event_returns_none
def test_list_commands_handler_falls_back_when_event_returns_none():
    '''
    Test that list_commands_handler falls back to cache-seeded defaults when
    the event returns none.
    '''

    # Arrange an event that returns none and a cache with no seeded commands.
    event = mock.Mock()
    event.execute.return_value = None
    get_dependency = mock.Mock(return_value=event)
    cache = CacheContext()

    # Build and invoke the handler.
    handler = cli_blueprint.list_commands_handler(cache, get_dependency)
    result = handler()

    # Assert the app-scoped event was consulted and the cache fallback used.
    get_dependency.assert_called_once_with('list_commands_evt', 'app')
    assert result == []

# ** test: get_parent_args_handler_resolves_app_scoped_event
def test_get_parent_args_handler_resolves_app_scoped_event():
    '''
    Test that get_parent_args_handler resolves get_parent_args_evt through
    the app flag and returns the event result.
    '''

    # Arrange an app-scoped event that returns parent arguments.
    arguments = [CliArgument(name_or_flags=['--verbose'])]
    event = mock.Mock()
    event.execute.return_value = arguments
    get_dependency = mock.Mock(return_value=event)

    # Build and invoke the handler.
    handler = cli_blueprint.get_parent_args_handler(get_dependency)
    result = handler()

    # Assert the event was resolved on the app flag and its result returned.
    get_dependency.assert_called_once_with('get_parent_args_evt', 'app')
    event.execute.assert_called_once_with()
    assert result is arguments

# ** test: parse_cli_args_handler_returns_feature_request_tuple
def test_parse_cli_args_handler_returns_feature_request_tuple():
    '''
    Test that parse_cli_args_handler takes the injected callables and returns
    (feature_id, headers, data).
    '''

    # Arrange handlers that return one command and no parent arguments.
    command = CliCommand(name='Add', key='add', group_key='calc')
    handler = cli_blueprint.parse_cli_args_handler(
        list_commands=lambda: [command],
        get_parent_args=lambda: [],
    )

    # Parse a minimal argv.
    feature_id, headers, data = handler(['calc', 'add'])

    # Assert the feature request tuple.
    assert feature_id == 'calc.add'
    assert headers == {'command_group': 'calc', 'command_key': 'add'}
    assert data['group'] == 'calc'
    assert data['command'] == 'add'

# ** test: build_cli_session_context_passes_handlers_not_raw_events
def test_build_cli_session_context_passes_handlers_not_raw_events():
    '''
    Test that build_cli_session_context still builds the container and resolver,
    does not resolve the CLI events by service id, and passes the handlers
    through compose_session_context.
    '''

    # Isolate composition from container and resolver construction.
    app_session = mock.Mock()
    cache = CacheContext()
    app_container = mock.Mock()
    resolver = mock.Mock()
    composed = mock.Mock()
    with mock.patch.object(
        cli_blueprint.core, 'build_app_service_container', return_value=app_container,
    ) as build_container, mock.patch.object(
        cli_blueprint.core, 'build_service_resolver', return_value=resolver,
    ) as build_resolver, mock.patch.object(
        cli_blueprint.core, 'compose_session_context', return_value=composed,
    ) as compose:
        result = cli_blueprint.build_cli_session_context(app_session, cache)

    # Assert the container and resolver are still constructed.
    build_container.assert_called_once_with(cache, app_session)
    build_resolver.assert_called_once_with(app_container)
    app_container.get_dependency.assert_not_called()
    resolver.get_dependency.assert_not_called()

    # Assert the handlers are passed and the container is not.
    assert compose.call_args.args[:4] == (
        CliSessionContext, app_session, cache, resolver,
    )
    assert app_container not in compose.call_args.args
    assert compose.call_args.kwargs['response_handler'] is cli_blueprint.core.response_handler
    assert compose.call_args.kwargs['create_request_handler'] is cli_blueprint.create_cli_request_context
    assert callable(compose.call_args.kwargs['list_commands_handler'])
    assert callable(compose.call_args.kwargs['get_parent_args_handler'])
    assert callable(compose.call_args.kwargs['parse_cli_args'])
    assert result is composed
