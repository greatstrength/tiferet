"""Tiferet CLI Builder Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...assets import TiferetAPIError
from ...contexts.app import AppInterfaceContext
from ...domain import CliCommand
from ...domain.cli import CliArgument
from ...domain.settings import DomainObject
from ..cli import CliBuilder

# *** fixtures

# ** fixture: cli_command_list
@pytest.fixture
def cli_command_list():
    '''
    Provide a list of mock CLI commands for the builder tests.

    :return: A list of CliCommand instances.
    :rtype: list
    '''

    # Build a single command with a required argument.
    return [
        CliCommand.new(
            group_key='test-group',
            key='test-feature',
            name='Test Feature Command',
            description='A test feature command.',
            arguments=[
                DomainObject.new(
                    CliArgument,
                    name_or_flags=['--arg1', '-a'],
                    description='Test argument 1',
                    required=True,
                    type='str',
                    default='default_value',
                )
            ]
        )
    ]

# ** fixture: service_provider
@pytest.fixture
def service_provider(cli_command_list):
    '''
    Provide a mock service provider that resolves CLI events.

    :param cli_command_list: The list of CLI commands returned by list_commands_evt.
    :type cli_command_list: list
    :return: A mock service provider.
    :rtype: mock.Mock
    '''

    # Create the mock list-commands event returning the fixture command list.
    list_commands_evt = mock.Mock()
    list_commands_evt.execute.return_value = cli_command_list

    # Create the mock parent-args event returning an empty list.
    get_parent_args_evt = mock.Mock()
    get_parent_args_evt.execute.return_value = []

    # Wire the provider to dispatch by service id.
    provider = mock.Mock()
    provider.get_service.side_effect = lambda service_id: {
        'list_commands_evt': list_commands_evt,
        'get_parent_args_evt': get_parent_args_evt,
    }[service_id]
    return provider

# ** fixture: interface_context
@pytest.fixture
def interface_context():
    '''
    Provide a mock AppInterfaceContext for the builder tests.

    :return: A mock AppInterfaceContext instance.
    :rtype: mock.Mock
    '''

    # Create a mock interface context with a successful run return.
    context = mock.Mock(spec=AppInterfaceContext)
    context.run.return_value = 'ok'
    return context

# ** fixture: cli_builder
@pytest.fixture
def cli_builder(service_provider, interface_context):
    '''
    Provide a CliBuilder with its service provider and load_interface patched.

    :param service_provider: The mock service provider.
    :type service_provider: mock.Mock
    :param interface_context: The mock AppInterfaceContext.
    :type interface_context: mock.Mock
    :return: The configured CliBuilder.
    :rtype: CliBuilder
    '''

    # Instantiate the builder and patch its runtime collaborators.
    builder = CliBuilder()
    builder.service_provider = service_provider
    builder.load_interface = mock.Mock(return_value=interface_context)
    return builder

# *** tests

# ** test: cli_builder_is_app_builder_subclass
def test_cli_builder_is_app_builder_subclass():
    '''
    Test that CliBuilder is a subclass of AppBuilder.
    '''

    # Import the parent and assert inheritance.
    from ..main import AppBuilder
    assert issubclass(CliBuilder, AppBuilder)

# ** test: cli_builder_get_commands
def test_cli_builder_get_commands(cli_builder):
    '''
    Test that get_commands groups commands by their group keys.

    :param cli_builder: The CliBuilder instance under test.
    :type cli_builder: CliBuilder
    '''

    # Resolve the command map from the builder.
    command_map = cli_builder.get_commands()

    # Assert grouping by group key and the underlying event was invoked.
    assert 'test-group' in command_map
    assert len(command_map['test-group']) == 1
    assert command_map['test-group'][0].key == 'test-feature'

# ** test: cli_builder_get_parent_arguments
def test_cli_builder_get_parent_arguments(cli_builder):
    '''
    Test that get_parent_arguments delegates to the parent-args event.

    :param cli_builder: The CliBuilder instance under test.
    :type cli_builder: CliBuilder
    '''

    # Resolve the parent arguments from the builder.
    parent_arguments = cli_builder.get_parent_arguments()

    # Assert the event returned the expected empty list.
    assert parent_arguments == []

# ** test: cli_builder_build_parser
def test_cli_builder_build_parser(cli_builder, cli_command_list):
    '''
    Test that build_parser produces a parser that accepts configured commands.

    :param cli_builder: The CliBuilder instance under test.
    :type cli_builder: CliBuilder
    :param cli_command_list: The fixture list of CLI commands.
    :type cli_command_list: list
    '''

    # Build the parser from the command map and empty parent args.
    command_map = {'test-group': cli_command_list}
    parser = cli_builder.build_parser(command_map, [])

    # Parse a sample argv and assert the parsed values.
    parsed = vars(parser.parse_args(['test-group', 'test-feature', '--arg1', 'test_value']))
    assert parsed['group'] == 'test-group'
    assert parsed['command'] == 'test-feature'
    assert parsed['arg1'] == 'test_value'

# ** test: cli_builder_run_success
def test_cli_builder_run_success(cli_builder, interface_context, capsys):
    '''
    Test the happy path of CliBuilder.run.

    :param cli_builder: The CliBuilder instance under test.
    :type cli_builder: CliBuilder
    :param interface_context: The mock AppInterfaceContext.
    :type interface_context: mock.Mock
    :param capsys: The pytest capsys fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Run the CLI with a valid argv.
    response = cli_builder.run(
        interface_id='test_cli',
        argv=['test-group', 'test-feature', '--arg1', 'default_value'],
    )

    # Assert the interface context was invoked with the derived request.
    interface_context.run.assert_called_once()
    call_kwargs = interface_context.run.call_args.kwargs
    assert call_kwargs['feature_id'] == 'test_group.test_feature'
    assert call_kwargs['headers'] == dict(
        command_group='test-group',
        command_key='test-feature',
    )
    assert call_kwargs['data']['arg1'] == 'default_value'

    # Assert the response was returned and printed to stdout.
    assert response == 'ok'
    captured = capsys.readouterr()
    assert 'ok' in captured.out

# ** test: cli_builder_run_parse_error
def test_cli_builder_run_parse_error(cli_builder):
    '''
    Test that an argparse error triggers sys.exit(2).

    :param cli_builder: The CliBuilder instance under test.
    :type cli_builder: CliBuilder
    '''

    # Run the CLI with an invalid command and assert the exit code.
    with pytest.raises(SystemExit) as exc_info:
        cli_builder.run(
            interface_id='test_cli',
            argv=['test-group', 'does-not-exist'],
        )
    assert exc_info.value.code == 2

# ** test: cli_builder_run_feature_error
def test_cli_builder_run_feature_error(cli_builder, interface_context):
    '''
    Test that a TiferetAPIError from the interface triggers sys.exit(1).

    :param cli_builder: The CliBuilder instance under test.
    :type cli_builder: CliBuilder
    :param interface_context: The mock AppInterfaceContext.
    :type interface_context: mock.Mock
    '''

    # Raise a TiferetAPIError from the interface context's run method.
    interface_context.run.side_effect = TiferetAPIError(
        'FEATURE_EXECUTION_FAILED',
        'Feature Execution Failed',
        'Feature execution failed',
    )

    # Run the CLI and assert the exit code.
    with pytest.raises(SystemExit) as exc_info:
        cli_builder.run(
            interface_id='test_cli',
            argv=['test-group', 'test-feature', '--arg1', 'default_value'],
        )
    assert exc_info.value.code == 1
