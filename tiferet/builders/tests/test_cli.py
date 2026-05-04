"""Tiferet CLI Builder Tests"""

# *** imports

# ** infra
import argparse
import pytest
from unittest import mock

# ** app
from ...assets import TiferetAPIError
from ...contexts.app import AppInterfaceContext
from ...domain import CliCommand, CliArgument
from ...events.cli import ListCliCommands, GetParentArguments
from ..main import AppBuilder
from ..cli import CliBuilder

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
                CliArgument(
                    name_or_flags=['--arg1', '-a'],
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

# ** fixture: interface_context
@pytest.fixture
def interface_context():
    '''
    Fixture to create a mock AppInterfaceContext.
    '''

    # Build and return a mock AppInterfaceContext with a default response.
    context = mock.Mock(spec=AppInterfaceContext)
    context.run.return_value = 'test-response'
    return context

# ** fixture: cli_builder
@pytest.fixture
def cli_builder(list_commands_evt, get_parent_args_evt, interface_context):
    '''
    Fixture to create a CliBuilder with a mocked service provider and interface context.
    '''

    # Create the builder and wire the mocked service provider.
    builder = CliBuilder()

    # Map service IDs to the mocked events.
    service_map = {
        'list_commands_evt': list_commands_evt,
        'get_parent_args_evt': get_parent_args_evt,
    }
    builder.service_provider = mock.Mock()
    builder.service_provider.get_service.side_effect = lambda sid: service_map[sid]

    # Patch load_interface to return the mocked interface context.
    builder.load_interface = mock.Mock(return_value=interface_context)

    # Return the configured builder.
    return builder

# *** tests

# ** test: cli_builder_is_app_builder_subclass
def test_cli_builder_is_app_builder_subclass():
    '''
    Test that CliBuilder is a subclass of AppBuilder.
    '''

    # Assert subclass relationship.
    assert issubclass(CliBuilder, AppBuilder)

# ** test: cli_builder_get_commands
def test_cli_builder_get_commands(cli_builder, list_commands_evt, cli_command_list):
    '''
    Test that get_commands groups CLI commands by group_key.

    :param cli_builder: The configured CliBuilder fixture.
    :type cli_builder: CliBuilder
    :param list_commands_evt: The mock ListCliCommands event.
    :type list_commands_evt: ListCliCommands
    :param cli_command_list: The sample list of CLI commands.
    :type cli_command_list: list
    '''

    # Invoke get_commands.
    command_map = cli_builder.get_commands()

    # Assert the list_commands_evt was invoked once.
    list_commands_evt.execute.assert_called_once()

    # Assert the returned map is grouped by group_key.
    assert 'test-group' in command_map
    assert len(command_map['test-group']) == 1
    assert command_map['test-group'][0].key == 'test-feature'

# ** test: cli_builder_get_parent_arguments
def test_cli_builder_get_parent_arguments(cli_builder, get_parent_args_evt):
    '''
    Test that get_parent_arguments delegates to the resolved event.

    :param cli_builder: The configured CliBuilder fixture.
    :type cli_builder: CliBuilder
    :param get_parent_args_evt: The mock GetParentArguments event.
    :type get_parent_args_evt: GetParentArguments
    '''

    # Invoke get_parent_arguments.
    parent_arguments = cli_builder.get_parent_arguments()

    # Assert event delegation and expected result.
    get_parent_args_evt.execute.assert_called_once()
    assert parent_arguments == []

# ** test: cli_builder_build_parser
def test_cli_builder_build_parser(cli_builder, cli_command_list):
    '''
    Test that build_parser produces a parser that accepts a valid argv.

    :param cli_builder: The configured CliBuilder fixture.
    :type cli_builder: CliBuilder
    :param cli_command_list: The sample list of CLI commands.
    :type cli_command_list: list
    '''

    # Build the parser from the grouped commands with no parent arguments.
    command_map = {'test-group': cli_command_list}
    parser = cli_builder.build_parser(command_map, [])

    # Assert the parser is an argparse.ArgumentParser.
    assert isinstance(parser, argparse.ArgumentParser)

    # Parse a valid argv and verify the namespace.
    parsed = vars(parser.parse_args(['test-group', 'test-feature', '--arg1', 'hello']))
    assert parsed['group'] == 'test-group'
    assert parsed['command'] == 'test-feature'
    assert parsed['arg1'] == 'hello'

# ** test: cli_builder_run_success
def test_cli_builder_run_success(cli_builder, interface_context, capsys):
    '''
    Test the happy-path run flow dispatches to interface_context.run and prints the response.

    :param cli_builder: The configured CliBuilder fixture.
    :type cli_builder: CliBuilder
    :param interface_context: The mock AppInterfaceContext.
    :type interface_context: AppInterfaceContext
    :param capsys: Pytest capsys fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Invoke run with a valid argv.
    response = cli_builder.run(
        'test_cli',
        argv=['test-group', 'test-feature', '--arg1', 'hello'],
    )

    # Assert the interface was loaded and run was called with derived feature_id/headers/data.
    cli_builder.load_interface.assert_called_once_with('test_cli')
    interface_context.run.assert_called_once()
    call_kwargs = interface_context.run.call_args.kwargs
    assert call_kwargs['feature_id'] == 'test_group.test_feature'
    assert call_kwargs['headers'] == dict(
        command_group='test-group',
        command_key='test-feature',
    )
    assert call_kwargs['data']['group'] == 'test-group'
    assert call_kwargs['data']['command'] == 'test-feature'
    assert call_kwargs['data']['arg1'] == 'hello'

    # Assert the response was returned and printed.
    assert response == 'test-response'
    captured = capsys.readouterr()
    assert 'test-response' in captured.out

# ** test: cli_builder_run_parse_error
def test_cli_builder_run_parse_error(cli_builder):
    '''
    Test that an argparse parse error triggers sys.exit(2).

    :param cli_builder: The configured CliBuilder fixture.
    :type cli_builder: CliBuilder
    '''

    # Invoke run with an invalid argv; expect SystemExit with code 2.
    with pytest.raises(SystemExit) as exc_info:
        cli_builder.run('test_cli', argv=['invalid-group'])

    # Assert the exit code is 2.
    assert exc_info.value.code == 2

# ** test: cli_builder_run_feature_error
def test_cli_builder_run_feature_error(cli_builder, interface_context):
    '''
    Test that a TiferetAPIError from interface_context.run triggers sys.exit(1).

    :param cli_builder: The configured CliBuilder fixture.
    :type cli_builder: CliBuilder
    :param interface_context: The mock AppInterfaceContext.
    :type interface_context: AppInterfaceContext
    '''

    # Configure the interface context to raise a TiferetAPIError.
    interface_context.run.side_effect = TiferetAPIError(
        error_code='FEATURE_EXECUTION_FAILED',
        name='Feature Execution Failed',
        message='Feature execution failed',
    )

    # Invoke run and expect SystemExit with code 1.
    with pytest.raises(SystemExit) as exc_info:
        cli_builder.run(
            'test_cli',
            argv=['test-group', 'test-feature', '--arg1', 'hello'],
        )

    # Assert the exit code is 1.
    assert exc_info.value.code == 1
