"""Tiferet CLI Context Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetAPIError
from tiferet.domain import CliArgument, CliCommand
from tiferet.mappers import AppInterfaceAggregate
from tiferet.contexts.cli import (
    CliContext,
    build_parser,
    derive_feature_request,
    group_commands_by_key,
)
from tiferet.contexts.request import RequestContext

# *** fixtures

# ** fixture: app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create an AppInterfaceAggregate bound as the CLI context domain.

    :return: An AppInterfaceAggregate instance.
    :rtype: AppInterfaceAggregate
    '''

    # Create a test interface pointing at the CLI context.
    return AppInterfaceAggregate(
        id='test_cli',
        name='Test CLI',
        module_path='tiferet.contexts.cli',
        class_name='CliContext',
        description='The test CLI interface.',
        flags=['test'],
        services=[],
    )

# ** fixture: cli_context
@pytest.fixture
def cli_context(app_interface):
    '''
    Fixture to create a CliContext bound to the test interface with mock events.

    The CLI collaborators default to returning empty lists; individual tests
    override ``list_commands_evt`` / ``get_parent_args_evt`` return values.

    :return: A CliContext instance.
    :rtype: CliContext
    '''

    # Build mock CLI collaborators with empty defaults.
    list_commands_evt = mock.Mock()
    list_commands_evt.execute.return_value = []
    get_parent_args_evt = mock.Mock()
    get_parent_args_evt.execute.return_value = []

    # Construct the CLI context declaratively from the loaded interface.
    return CliContext.from_domain(
        app_interface,
        get_feature_evt=mock.Mock(),
        get_error_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        list_commands_evt=list_commands_evt,
        get_parent_args_evt=get_parent_args_evt,
    )

# *** tests

# ** test: group_commands_by_key
def test_group_commands_by_key():
    '''
    Test that group_commands_by_key groups commands by group key in order.
    '''

    # Group a flat list of commands spanning two groups.
    commands = group_commands_by_key([
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Subtract', key='subtract', group_key='calc'),
        CliCommand(name='Boot', key='boot', group_key='sys'),
    ])

    # Assert the commands are grouped by group key preserving order.
    assert set(commands.keys()) == {'calc', 'sys'}
    assert [c.key for c in commands['calc']] == ['add', 'subtract']
    assert [c.key for c in commands['sys']] == ['boot']

# ** test: derive_feature_request
def test_derive_feature_request():
    '''
    Test that derive_feature_request builds the feature id and headers,
    normalizing hyphens to underscores in the feature id only.
    '''

    # Derive from a parsed namespace with hyphenated group and command.
    feature_id, headers = derive_feature_request(
        {'group': 'my-calc', 'command': 'sub-tract', 'a': 1},
    )

    # Assert the feature id is normalized and headers keep raw values.
    assert feature_id == 'my_calc.sub_tract'
    assert headers == {'command_group': 'my-calc', 'command_key': 'sub-tract'}

# ** test: get_commands_groups_by_group_key
def test_get_commands_groups_by_group_key(cli_context):
    '''
    Test that get_commands groups commands by their group key in order.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange the list-commands event to return commands across two groups.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Subtract', key='subtract', group_key='calc'),
        CliCommand(name='Boot', key='boot', group_key='sys'),
    ]

    # Retrieve the grouped command map.
    commands = cli_context.get_commands()

    # Assert the commands are grouped by group key preserving order.
    assert set(commands.keys()) == {'calc', 'sys'}
    assert [c.key for c in commands['calc']] == ['add', 'subtract']
    assert [c.key for c in commands['sys']] == ['boot']

# ** test: get_commands_falls_back_to_default_commands
def test_get_commands_falls_back_to_default_commands(app_interface):
    '''
    Test that get_commands falls back to the context's bootstrap default command
    list when the repository (event) returns no commands.

    :param app_interface: The bound app interface.
    :type app_interface: AppInterfaceAggregate
    '''

    # Build a CLI context seeded with an id-keyed bootstrap default command.
    list_commands_evt = mock.Mock()
    list_commands_evt.execute.return_value = []
    context = CliContext.from_domain(
        app_interface,
        get_feature_evt=mock.Mock(),
        get_error_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        list_commands_evt=list_commands_evt,
        get_parent_args_evt=mock.Mock(),
        default_commands={'sys.boot': {'name': 'Boot', 'key': 'boot', 'group_key': 'sys'}},
    )

    # Retrieve the commands; the empty event result falls back to the defaults.
    result = context.get_commands()

    # Assert the event was called with no default arguments and the bootstrap
    # default command was used as the fallback.
    list_commands_evt.execute.assert_called_once_with()
    assert set(result.keys()) == {'sys'}
    assert [c.key for c in result['sys']] == ['boot']

# ** test: build_parser_parses_command_arguments
def test_build_parser_parses_command_arguments():
    '''
    Test that build_parser produces a parser that parses command arguments.
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
    parser = build_parser(commands, [])
    parsed = vars(parser.parse_args(['calc', 'add', '1', '2']))

    # Assert the group, command, and typed values parse correctly.
    assert parsed['group'] == 'calc'
    assert parsed['command'] == 'add'
    assert parsed['a'] == 1
    assert parsed['b'] == 2

# ** test: build_parser_merges_parent_args_and_skips_collisions
def test_build_parser_merges_parent_args_and_skips_collisions():
    '''
    Test that parent arguments are merged but colliding flags are skipped.
    '''

    # Arrange parent arguments including one that collides with the command arg.
    parent_arguments = [
        CliArgument(name_or_flags=['--verbose'], action='store_true'),
        CliArgument(name_or_flags=['a']),
    ]

    # Build a command map whose command declares a colliding 'a' argument.
    commands = {
        'calc': [
            CliCommand(
                name='Add', key='add', group_key='calc',
                arguments=[CliArgument(name_or_flags=['a'], type='int')],
            ),
        ],
    }

    # Build the parser and parse argv including the non-colliding parent flag.
    parser = build_parser(commands, parent_arguments)
    parsed = vars(parser.parse_args(['calc', 'add', '5', '--verbose']))

    # Assert the command arg parses and the parent flag is merged in.
    assert parsed['a'] == 5
    assert parsed['verbose'] is True

# ** test: parse_cli_request_builds_request
def test_parse_cli_request_builds_request(cli_context):
    '''
    Test that parse_cli_request derives feature id, headers, and data.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a single typed command.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(
            name='Add', key='add', group_key='calc',
            arguments=[
                CliArgument(name_or_flags=['a'], type='int'),
                CliArgument(name_or_flags=['b'], type='int'),
            ],
        ),
    ]

    # Parse the CLI request.
    request = cli_context.parse_cli_request(['calc', 'add', '1', '2'])

    # Assert the request context carries the derived feature id, headers, and data.
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'calc.add'
    assert request.headers['command_group'] == 'calc'
    assert request.headers['command_key'] == 'add'
    assert request.headers['interface_id'] == cli_context.domain.id
    assert request.data['a'] == 1
    assert request.data['b'] == 2

# ** test: parse_cli_request_normalizes_hyphens
def test_parse_cli_request_normalizes_hyphens(cli_context):
    '''
    Test that hyphenated group/command keys normalize to an underscore feature id.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a command with hyphenated group and key.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(name='Subtract', key='sub-tract', group_key='my-calc'),
    ]

    # Parse the CLI request.
    request = cli_context.parse_cli_request(['my-calc', 'sub-tract'])

    # Assert the feature id normalizes hyphens while headers keep raw values.
    assert request.feature_id == 'my_calc.sub_tract'
    assert request.headers['command_group'] == 'my-calc'
    assert request.headers['command_key'] == 'sub-tract'

# ** test: run_cli_success_prints_and_returns
def test_run_cli_success_prints_and_returns(cli_context, capsys):
    '''
    Test that run_cli delegates to run, prints, and returns the response.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Arrange a single typed command and stub the inherited run.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(
            name='Add', key='add', group_key='calc',
            arguments=[
                CliArgument(name_or_flags=['a'], type='int'),
                CliArgument(name_or_flags=['b'], type='int'),
            ],
        ),
    ]
    cli_context.run = mock.Mock(return_value='RESULT')

    # Run the CLI for a valid command.
    result = cli_context.run_cli(['calc', 'add', '1', '2'])

    # Assert the response is returned and printed.
    assert result == 'RESULT'
    assert 'RESULT' in capsys.readouterr().out

    # Assert the inherited run was delegated to with the parsed request data.
    call = cli_context.run.call_args
    assert call.kwargs['feature_id'] == 'calc.add'
    assert call.kwargs['headers']['command_group'] == 'calc'
    assert call.kwargs['headers']['command_key'] == 'add'
    assert call.kwargs['data']['a'] == 1
    assert call.kwargs['data']['b'] == 2

# ** test: run_cli_parser_failure_exits_2
def test_run_cli_parser_failure_exits_2(cli_context):
    '''
    Test that an invalid CLI invocation exits with code 2.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a known command group.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(name='Add', key='add', group_key='calc'),
    ]

    # Run the CLI with an unknown group and assert an exit code of 2.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run_cli(['nonexistent-group'])
    assert exc_info.value.code == 2

# ** test: run_cli_api_error_exits_1
def test_run_cli_api_error_exits_1(cli_context):
    '''
    Test that a TiferetAPIError during execution exits with code 1.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a valid command and make the inherited run raise an API error.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(
            name='Add', key='add', group_key='calc',
            arguments=[CliArgument(name_or_flags=['a'], type='int')],
        ),
    ]
    cli_context.run = mock.Mock(
        side_effect=TiferetAPIError(error_code='X', name='X Error', message='boom'),
    )

    # Run the CLI for a valid command and assert an exit code of 1.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run_cli(['calc', 'add', '1'])
    assert exc_info.value.code == 1
