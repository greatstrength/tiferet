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
from tiferet.events.settings import DomainEvent, TiferetError, a
from tiferet.domain import CliCommand, CliArgument
from tiferet.interfaces import CliService
from tiferet.mappers import CliCommandAggregate
from tiferet.testing import DomainEventTestBase, ServiceEventTestBase

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

# *** tests

# ** class: TestCliEvent
class TestCliEvent:
    '''
    Tests for the CliEvent base event shared by all CLI events.
    '''

    # * method: test_base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that CliEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(CliEvent, DomainEvent)

    # * method: test_concrete_events_extend_base
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

    # * method: test_service_injection
    def test_service_injection(self):
        '''
        Test that constructing a CLI event wires the shared service attribute.
        '''

        # Create a mock CLI service.
        service = mock.Mock(spec=CliService)

        # Assert the base and a concrete event both expose the injected service.
        assert CliEvent(cli_service=service).cli_service is service
        assert AddCliCommand(cli_service=service).cli_service is service


# ** test: TestAddCliCommand
class TestAddCliCommand(DomainEventTestBase):
    '''
    Tests for AddCliCommand using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddCliCommand

    # * attribute: dependencies
    dependencies = {'cli_service': CliService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test.new_command',
        name='New Command',
        key='new_command',
        group_key='test',
    )

    # * attribute: required_params
    required_params = ['id']

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

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test that AddCliCommand successfully creates a new CLI command.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

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

    # * method: test_with_arguments
    def test_with_arguments(self, mock_dependencies):
        '''
        Test that AddCliCommand can create a command with initial arguments.
        '''

        # Execute via the harness handle helper with arguments.
        result = self.handle(
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

    # * method: test_duplicate_id
    def test_duplicate_id(self, mock_dependencies):
        '''
        Test that AddCliCommand fails when the command id already exists.
        '''

        # Configure the service to report the id exists.
        mock_dependencies['cli_service'].exists.return_value = True

        # Execute and expect a CLI_COMMAND_ALREADY_EXISTS error.
        with pytest.raises(Exception) as exc_info:
            self.handle(mock_dependencies)

        # Assert the correct error code.
        assert exc_info.value.error_code == a.const.CLI_COMMAND_ALREADY_EXISTS_ID

    # * method: test_none_arguments_coerced
    def test_none_arguments_coerced(self, mock_dependencies):
        '''
        Test that None arguments are coerced to an empty list.
        '''

        # Execute with arguments explicitly set to None (as argparse may pass).
        result = self.handle(mock_dependencies, arguments=None)

        # Assert the command was created with an empty argument list.
        assert isinstance(result, CliCommand)
        assert result.arguments == []
        mock_dependencies['cli_service'].save.assert_called_once_with(result)


# ** test: TestAddCliArgument
class TestAddCliArgument(ServiceEventTestBase):
    '''
    Tests for AddCliArgument using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddCliArgument

    # * attribute: dependencies
    dependencies = {'cli_service': CliService}

    # * attribute: service_attr
    service_attr = 'cli_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        command_id='test.command',
        name_or_flags=['-v', '--verbose'],
        description='Enable verbose output',
    )

    # * attribute: required_params
    required_params = ['command_id']

    # * attribute: not_found_error_code
    not_found_error_code = a.const.CLI_COMMAND_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        command_id='test.missing',
        name_or_flags=['-v'],
        description='Verbose',
    )

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

    # * method: test_success
    def test_success(self, mock_dependencies, cli_command):
        '''
        Test that AddCliArgument successfully adds an argument to a command.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the result is the command id and argument was added.
        assert result == 'test.command'
        assert len(cli_command.arguments) == 1

        # Assert service interactions.
        mock_dependencies['cli_service'].get.assert_called_once_with('test.command')
        mock_dependencies['cli_service'].save.assert_called_once_with(cli_command)

    # * method: test_with_kwargs
    def test_with_kwargs(self, mock_dependencies, cli_command):
        '''
        Test that AddCliArgument handles additional kwargs for arguments.
        '''

        # Execute via the harness handle helper with additional kwargs.
        result = self.handle(
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

    # * method: test_multiple_arguments
    def test_multiple_arguments(self, mock_dependencies, cli_command):
        '''
        Test adding multiple arguments to the same command sequentially.
        '''

        # Add first argument.
        self.handle(mock_dependencies)

        # Add second argument.
        self.handle(
            mock_dependencies,
            name_or_flags=['-q', '--quiet'],
            description='Quiet mode',
        )

        # Assert both arguments were added.
        assert len(cli_command.arguments) == 2
        assert mock_dependencies['cli_service'].save.call_count == 2


# ** test: TestListCliCommands
class TestListCliCommands(DomainEventTestBase):
    '''
    Tests for ListCliCommands using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = ListCliCommands

    # * attribute: dependencies
    dependencies = {'cli_service': CliService}

    # * attribute: sample_kwargs
    sample_kwargs = dict()

    # * method: test_empty
    def test_empty(self, mock_dependencies):
        '''
        Test that ListCliCommands returns an empty list when no commands exist.
        '''

        # Configure the service to return an empty list.
        mock_dependencies['cli_service'].list.return_value = []

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert an empty list is returned.
        assert result == []
        mock_dependencies['cli_service'].list.assert_called_once()

    # * method: test_multiple
    def test_multiple(self, mock_dependencies, cli_command):
        '''
        Test that ListCliCommands returns multiple commands.
        '''

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
        result = self.handle(mock_dependencies)

        # Assert both commands are returned.
        assert len(result) == 2
        assert result[0].id == 'test.command'
        assert result[1].id == 'test.another'
        mock_dependencies['cli_service'].list.assert_called_once()


# ** test: TestGetParentArguments
class TestGetParentArguments(DomainEventTestBase):
    '''
    Tests for GetParentArguments using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = GetParentArguments

    # * attribute: dependencies
    dependencies = {'cli_service': CliService}

    # * attribute: sample_kwargs
    sample_kwargs = dict()

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test that GetParentArguments returns parent arguments.
        '''

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
        result = self.handle(mock_dependencies)

        # Assert the results.
        assert len(result) == 2
        assert '--verbose' in result[0].name_or_flags
        assert '--debug' in result[1].name_or_flags
        mock_dependencies['cli_service'].get_parent_arguments.assert_called_once()

    # * method: test_empty
    def test_empty(self, mock_dependencies):
        '''
        Test that GetParentArguments handles empty parent argument lists.
        '''

        # Configure the service to return an empty list.
        mock_dependencies['cli_service'].get_parent_arguments.return_value = []

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert an empty list is returned.
        assert result == []
        mock_dependencies['cli_service'].get_parent_arguments.assert_called_once()
