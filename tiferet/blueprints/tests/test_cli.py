"""Tiferet CLI Blueprint Tests"""

# *** imports

# ** infra
import argparse
import pytest
from unittest import mock

# ** app
from ...assets import TiferetAPIError
from ...domain import CliCommand, CliArgument
from ...events.cli import ListCliCommands, GetParentArguments
from ..cli import (
    build_app,
    get_commands,
    get_parent_arguments,
    build_parser,
    parse_argv,
    derive_feature_request,
)

# *** fixtures

# ** fixture: cli_command_list
@pytest.fixture
def cli_command_list():
    '''
    Fixture to create a list of mock CLI commands.
    '''

    # Return a list of test CLI commands.
    return [
        CliCommand(
            group_key='test-group',
            key='test-feature',
            name='Test Feature Command',
            description='A test feature command.',
            arguments=[
                CliArgument(name_or_flags=['--arg1', '-a'],
                    description='Test argument 1',
                    required=True,
                    type='str',
                    default='default_value',
                )
            ]
        )
    ]

# ** fixture: list_commands_evt
@pytest.fixture
def list_commands_evt(cli_command_list):
    '''
    Fixture to create a mock ListCliCommands event.
    '''

    # Build and return a mock ListCliCommands event.
    evt = mock.Mock(spec=ListCliCommands)
    evt.execute.return_value = cli_command_list
    return evt

# ** fixture: get_parent_args_evt
@pytest.fixture
def get_parent_args_evt():
    '''
    Fixture to create a mock GetParentArguments event.
    '''

    # Build and return a mock GetParentArguments event.
    evt = mock.Mock(spec=GetParentArguments)
    evt.execute.return_value = []
    return evt

# ** fixture: mock_get_dependency
@pytest.fixture
def mock_get_dependency(list_commands_evt, get_parent_args_evt):
    '''
    Fixture to create a mock get_dependency handler wired with CLI events.
    '''

    # Map service IDs to the mocked events.
    service_map = {
        'list_commands_evt': list_commands_evt,
        'get_parent_args_evt': get_parent_args_evt,
    }

    # Build and return the mock get_dependency callable.
    return mock.Mock(side_effect=lambda sid, *flags: service_map[sid])

# *** tests

# ** test: get_commands_groups_by_key
def test_get_commands_groups_by_key(mock_get_dependency, list_commands_evt):
    '''
    Test that get_commands groups CLI commands by group_key.

    :param mock_get_dependency: The mock get_dependency fixture.
    :type mock_get_dependency: mock.Mock
    :param list_commands_evt: The mock ListCliCommands event.
    :type list_commands_evt: ListCliCommands
    '''

    # Invoke get_commands with the mock get_dependency handler.
    command_map = get_commands(mock_get_dependency)

    # Assert the list_commands_evt was invoked once.
    list_commands_evt.execute.assert_called_once()

    # Assert the returned map is grouped by group_key.
    assert 'test-group' in command_map
    assert len(command_map['test-group']) == 1
    assert command_map['test-group'][0].key == 'test-feature'

# ** test: get_parent_arguments_delegates
def test_get_parent_arguments_delegates(mock_get_dependency, get_parent_args_evt):
    '''
    Test that get_parent_arguments delegates to the resolved event.

    :param mock_get_dependency: The mock get_dependency fixture.
    :type mock_get_dependency: mock.Mock
    :param get_parent_args_evt: The mock GetParentArguments event.
    :type get_parent_args_evt: GetParentArguments
    '''

    # Invoke get_parent_arguments with the mock get_dependency handler.
    parent_arguments = get_parent_arguments(mock_get_dependency)

    # Assert event delegation and expected result.
    get_parent_args_evt.execute.assert_called_once()
    assert parent_arguments == []

# ** test: build_parser_produces_valid_parser
def test_build_parser_produces_valid_parser(cli_command_list):
    '''
    Test that build_parser produces a parser that accepts a valid argv.

    :param cli_command_list: The sample list of CLI commands.
    :type cli_command_list: list
    '''

    # Build the parser from the grouped commands with no parent arguments.
    command_map = {'test-group': cli_command_list}
    parser = build_parser(command_map, [])

    # Assert the parser is an argparse.ArgumentParser.
    assert isinstance(parser, argparse.ArgumentParser)

    # Parse a valid argv and verify the namespace.
    parsed = vars(parser.parse_args(['test-group', 'test-feature', '--arg1', 'hello']))
    assert parsed['group'] == 'test-group'
    assert parsed['command'] == 'test-feature'
    assert parsed['arg1'] == 'hello'

# ** test: parse_argv_success
def test_parse_argv_success(cli_command_list):
    '''
    Test that parse_argv returns a dict from valid arguments.

    :param cli_command_list: The sample list of CLI commands.
    :type cli_command_list: list
    '''

    # Build a parser and parse valid argv.
    parser = build_parser({'test-group': cli_command_list}, [])
    parsed = parse_argv(parser, ['test-group', 'test-feature', '--arg1', 'hello'])

    # Assert the result is a dict with expected values.
    assert isinstance(parsed, dict)
    assert parsed['group'] == 'test-group'
    assert parsed['arg1'] == 'hello'

# ** test: parse_argv_exits_on_error
def test_parse_argv_exits_on_error(cli_command_list):
    '''
    Test that parse_argv exits with code 2 on invalid arguments.

    :param cli_command_list: The sample list of CLI commands.
    :type cli_command_list: list
    '''

    # Build a parser and attempt to parse invalid argv.
    parser = build_parser({'test-group': cli_command_list}, [])

    # Assert SystemExit with code 2.
    with pytest.raises(SystemExit) as exc_info:
        parse_argv(parser, ['invalid-group'])
    assert exc_info.value.code == 2

# ** test: derive_feature_request_normalizes
def test_derive_feature_request_normalizes():
    '''
    Test that derive_feature_request normalizes hyphens to underscores.
    '''

    # Derive feature request from parsed arguments.
    parsed = {'group': 'test-group', 'command': 'test-feature'}
    feature_id, headers = derive_feature_request(parsed)

    # Assert normalization.
    assert feature_id == 'test_group.test_feature'
    assert headers == dict(
        command_group='test-group',
        command_key='test-feature',
    )

# ** test: build_app_success
def test_build_app_success(mock_get_dependency, capsys):
    '''
    Test the happy-path build_app flow dispatches to the app session context's run.

    :param mock_get_dependency: The mock get_dependency fixture.
    :type mock_get_dependency: mock.Mock
    :param capsys: Pytest capsys fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Create a mock app session context wired with the mock get_dependency handler.
    mock_context = mock.Mock()
    mock_context.get_dependency = mock_get_dependency
    mock_context.run.return_value = 'test-response'

    # Patch the core build_app entry point to isolate the CLI blueprint.
    with mock.patch('tiferet.blueprints.cli._core_build_app', return_value=mock_context):

        # Invoke build_app.
        response = build_app(
            'test_cli',
            argv=['test-group', 'test-feature', '--arg1', 'hello'],
        )

    # Assert the app session context was invoked with the correct arguments.
    mock_context.run.assert_called_once()
    call_kwargs = mock_context.run.call_args.kwargs
    assert call_kwargs['feature_id'] == 'test_group.test_feature'
    assert call_kwargs['headers'] == dict(
        command_group='test-group',
        command_key='test-feature',
    )
    assert call_kwargs['data']['arg1'] == 'hello'

    # Assert the response was returned and printed.
    assert response == 'test-response'
    captured = capsys.readouterr()
    assert 'test-response' in captured.out

# ** test: build_app_feature_error
def test_build_app_feature_error(mock_get_dependency):
    '''
    Test that a TiferetAPIError from the app session context's run triggers sys.exit(1).

    :param mock_get_dependency: The mock get_dependency fixture.
    :type mock_get_dependency: mock.Mock
    '''

    # Create a mock app session context that raises a TiferetAPIError.
    mock_context = mock.Mock()
    mock_context.get_dependency = mock_get_dependency
    mock_context.run.side_effect = TiferetAPIError(
        error_code='FEATURE_EXECUTION_FAILED',
        name='Feature Execution Failed',
        message='Feature execution failed',
    )

    # Patch the core build_app entry point to isolate the CLI blueprint.
    with mock.patch('tiferet.blueprints.cli._core_build_app', return_value=mock_context):

        # Invoke build_app and expect SystemExit with code 1.
        with pytest.raises(SystemExit) as exc_info:
            build_app(
                'test_cli',
                argv=['test-group', 'test-feature', '--arg1', 'hello'],
            )

        # Assert the exit code is 1.
        assert exc_info.value.code == 1
