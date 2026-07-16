"""Tiferet CLI Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
import tiferet.blueprints.cli as cli_blueprint
from tiferet.blueprints.cli import build_app
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
                 'cli_response_handler', 'build_cli_session_context'):
        assert hasattr(cli_blueprint, name), f'{name} not found on cli blueprint'

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
