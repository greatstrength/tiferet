"""Tiferet CLI Domain Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.cli import (
    CliEvent,
    AddCliCommand,
    AddCliArgument,
    ListCliCommands,
    GetParentArguments,
)
from tiferet.events.core import DomainEvent, TiferetError, a
from tiferet.domain import CliCommand, CliArgument
from tiferet.interfaces import CliService
from tiferet.mappers import CliCommandAggregate
from tiferet.blueprints.tester import use_tester

# *** fixtures

# ** fixture: cli_command
@pytest.fixture
def cli_command():
    '''
    Fixture to create a CliCommand aggregate for testing.

    :return: A CliCommandAggregate instance.
    :rtype: CliCommandAggregate
    '''

    # Create a test CliCommand instance.
    return CliCommandAggregate(
        id='test.command',
        name='Test Command',
        key='command',
        group_key='test',
        description='A test command',
        arguments=[],
    )

# *** testers

# ** tester: test_cli_event
class TestCliEvent:
    '''
    Tests for the CliEvent base event shared by all CLI events.
    '''

    # * test: base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that CliEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(CliEvent, DomainEvent)

    # * test: concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        Test that every concrete CLI event extends CliEvent.
        '''

        # Assert each concrete event extends the module base.
        for event_cls in (
            ListCliCommands,
            GetParentArguments,
            AddCliCommand,
            AddCliArgument,
        ):
            assert issubclass(event_cls, CliEvent)

    # * test: service_injection
    def test_service_injection(self):
        '''
        Test that constructing a CLI event wires the shared service attribute.
        '''

        # Create a mock CLI service.
        service = mock.Mock(spec=CliService)

        # Assert the base and a concrete event both expose the injected service.
        assert CliEvent(cli_service=service).cli_service is service
        assert AddCliCommand(cli_service=service).cli_service is service

# ** tester: test_add_cli_command
@use_tester(
    type='domain_event',
    target_cls=AddCliCommand,
    dependencies={
        'cli_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'CliService',
        },
    },
    sample_kwargs=dict(
        id='test.new_command',
        name='New Command',
        key='new_command',
        group_key='test',
    ),
    required_params=['id'],
)
class TestAddCliCommand:
    '''
    Tests for AddCliCommand using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self):
        '''
        Override to provide a CLI service mock pre-configured with exists=False.
        '''

        # Create a mock CliService that returns False for exists.
        service = mock.Mock(spec=CliService)
        service.exists.return_value = False
        return {'cli_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies):
        '''
        Test that AddCliCommand successfully creates a new CLI command.
        '''

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result is a CliCommand instance with expected fields.
        assert isinstance(result, CliCommand)
        assert result.id == 'test.new_command'
        assert result.name == 'New Command'
        assert result.key == 'new_command'
        assert result.group_key == 'test'
        assert result.arguments == []

        # Assert the service was called to check existence and to save.
        mock_dependencies['cli_service'].exists.assert_called_once_with('test.new_command')
        mock_dependencies['cli_service'].save.assert_called_once_with(result)

    # * test: with_arguments
    def test_with_arguments(self, test_ctx, mock_dependencies):
        '''
        Test that AddCliCommand can create a command with initial arguments.
        '''

        # Execute via the harness handle helper with arguments.
        result = test_ctx.handle(
            mock_dependencies,
            id='test.verbose_command',
            name='Verbose Command',
            key='verbose_command',
            description='A command with arguments',
            arguments=[
                {
                    'name_or_flags': ['-v', '--verbose'],
                    'description': 'Enable verbose output',
                    'type': 'str',
                }
            ],
        )

        # Assert the result has arguments.
        assert isinstance(result, CliCommand)
        assert result.id == 'test.verbose_command'
        assert len(result.arguments) == 1

        # Assert the service interactions.
        mock_dependencies['cli_service'].exists.assert_called_once_with('test.verbose_command')
        mock_dependencies['cli_service'].save.assert_called_once_with(result)

    # * test: duplicate_id
    def test_duplicate_id(self, test_ctx, mock_dependencies):
        '''
        Test that AddCliCommand fails when the command id already exists.
        '''

        # Configure the service to report the id exists.
        mock_dependencies['cli_service'].exists.return_value = True

        # Execute and expect a CLI_COMMAND_ALREADY_EXISTS error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies)

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.CLI_COMMAND_ALREADY_EXISTS_ID

    # * test: none_arguments_coerced
    def test_none_arguments_coerced(self, test_ctx, mock_dependencies):
        '''
        Test that None arguments are coerced to an empty list.
        '''

        # Execute with arguments explicitly set to None (as argparse may pass).
        result = test_ctx.handle(mock_dependencies, arguments=None)

        # Assert the command was created with an empty argument list.
        assert isinstance(result, CliCommand)
        assert result.arguments == []
        mock_dependencies['cli_service'].save.assert_called_once_with(result)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

# ** tester: test_add_cli_argument
@use_tester(
    type='service_event',
    target_cls=AddCliArgument,
    dependencies={
        'cli_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'CliService',
        },
    },
    sample_kwargs=dict(
        command_id='test.command',
        name_or_flags=['-v', '--verbose'],
        description='Enable verbose output',
    ),
    required_params=['command_id'],
    service_attr='cli_service',
    not_found_error_code=a.error.CLI_COMMAND_NOT_FOUND_ID,
    not_found_kwargs=dict(
        command_id='test.missing',
        name_or_flags=['-v'],
        description='Verbose',
    ),
)
class TestAddCliArgument:
    '''
    Tests for AddCliArgument using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, cli_command):
        '''
        Override to provide a CLI service mock pre-configured with a cli_command.
        '''

        # Create a mock CliService that returns the cli_command on get.
        service = mock.Mock(spec=CliService)
        service.get.return_value = cli_command
        return {'cli_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies, cli_command):
        '''
        Test that AddCliArgument successfully adds an argument to a command.
        '''

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result is the command id and argument was added.
        assert result == 'test.command'
        assert len(cli_command.arguments) == 1

        # Assert service interactions.
        mock_dependencies['cli_service'].get.assert_called_once_with('test.command')
        mock_dependencies['cli_service'].save.assert_called_once_with(cli_command)

    # * test: with_kwargs
    def test_with_kwargs(self, test_ctx, mock_dependencies, cli_command):
        '''
        Test that AddCliArgument handles additional kwargs for arguments.
        '''

        # Execute via the harness handle helper with additional kwargs.
        result = test_ctx.handle(
            mock_dependencies,
            name_or_flags=['--count'],
            description='Number of items',
            type='int',
            required=True,
            default='5',
        )

        # Assert the result and argument was added.
        assert result == 'test.command'
        assert len(cli_command.arguments) == 1

        # Assert service interactions.
        mock_dependencies['cli_service'].get.assert_called_once_with('test.command')
        mock_dependencies['cli_service'].save.assert_called_once_with(cli_command)

    # * test: multiple_arguments
    def test_multiple_arguments(self, test_ctx, mock_dependencies, cli_command):
        '''
        Test adding multiple arguments to the same command sequentially.
        '''

        # Add first argument.
        test_ctx.handle(mock_dependencies)

        # Add second argument.
        test_ctx.handle(
            mock_dependencies,
            name_or_flags=['-q', '--quiet'],
            description='Quiet mode',
        )

        # Assert both arguments were added.
        assert len(cli_command.arguments) == 2
        assert mock_dependencies['cli_service'].save.call_count == 2

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: test_list_cli_commands
@use_tester(
    type='domain_event',
    target_cls=ListCliCommands,
    dependencies={
        'cli_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'CliService',
        },
    },
    sample_kwargs=dict(),
)
class TestListCliCommands:
    '''
    Tests for ListCliCommands using the domain event test harness.
    '''

    # * test: empty
    def test_empty(self, test_ctx):
        '''
        Test that ListCliCommands returns an empty list when no commands exist.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the service to return an empty list.
        mock_dependencies['cli_service'].list.return_value = []

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert an empty list is returned.
        assert result == []
        mock_dependencies['cli_service'].list.assert_called_once()

    # * test: multiple
    def test_multiple(self, test_ctx, cli_command):
        '''
        Test that ListCliCommands returns multiple commands.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Create another command for the list.
        another = CliCommandAggregate(
            id='test.another',
            name='Another Command',
            key='another',
            group_key='test',
        )

        # Configure the service to return multiple commands.
        mock_dependencies['cli_service'].list.return_value = [cli_command, another]

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert both commands are returned.
        assert len(result) == 2
        assert result[0].id == 'test.command'
        assert result[1].id == 'test.another'
        mock_dependencies['cli_service'].list.assert_called_once()

# ** tester: test_get_parent_arguments
@use_tester(
    type='domain_event',
    target_cls=GetParentArguments,
    dependencies={
        'cli_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'CliService',
        },
    },
    sample_kwargs=dict(),
)
class TestGetParentArguments:
    '''
    Tests for GetParentArguments using the domain event test harness.
    '''

    # * test: success
    def test_success(self, test_ctx):
        '''
        Test that GetParentArguments returns parent arguments.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Create sample parent arguments.
        parent_args = [
            CliArgument(
                name_or_flags=['--verbose', '-v'],
                description='Enable verbose output',
                type='str',
                required=False,
            ),
            CliArgument(
                name_or_flags=['--debug'],
                description='Enable debug mode',
                type='str',
                required=False,
            ),
        ]

        # Configure the service to return parent arguments.
        mock_dependencies['cli_service'].get_parent_arguments.return_value = parent_args

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the results.
        assert len(result) == 2
        assert '--verbose' in result[0].name_or_flags
        assert '--debug' in result[1].name_or_flags
        mock_dependencies['cli_service'].get_parent_arguments.assert_called_once()

    # * test: empty
    def test_empty(self, test_ctx):
        '''
        Test that GetParentArguments handles empty parent argument lists.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the service to return an empty list.
        mock_dependencies['cli_service'].get_parent_arguments.return_value = []

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert an empty list is returned.
        assert result == []
        mock_dependencies['cli_service'].get_parent_arguments.assert_called_once()

