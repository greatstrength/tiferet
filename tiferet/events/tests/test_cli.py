"""Tests for Tiferet CLI Commands"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest
from unittest import mock

# ** app
from ..cli import (
    AddCliCommand,
    AddCliArgument,
    ListCliCommands,
    GetParentArguments,
)
from ...domain import CliCommand, CliArgument, DomainObject
from ...mappers import (
    CliCommandAggregate,
)
from ...mappers.settings import Aggregate
from ...interfaces import CliService
from ...assets import TiferetError
from ...events import DomainEvent

# *** fixtures

# ** fixture: mock_cli_service
@pytest.fixture
def mock_cli_service() -> CliService:
    '''
    A fixture for a mock CLI service.
    '''

    # Create the mock CLI service.
    return mock.Mock(spec=CliService)

# ** fixture: sample_cli_command
@pytest.fixture
def sample_cli_command() -> CliCommand:
    '''
    A sample CLI command for testing.
    '''

    return Aggregate.new(
        CliCommandAggregate,
        id='test.command',
        name='Test Command',
        key='command',
        group_key='test',
        description='A test command',
        arguments=[],
    )

# *** tests

# ** test: add_cli_command_success
def test_add_cli_command_success(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliCommand successfully creates a new CLI command.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    # Arrange the CLI service mock.
    mock_cli_service.exists.return_value = False

    command = AddCliCommand(cli_service=mock_cli_service)

    result = command.execute(
        id='test.new_command',
        name='New Command',
        key='new_command',
        group_key='test',
        description='A new command',
        arguments=[],
    )

    # Assert the command is created correctly.
    assert isinstance(result, CliCommand)
    assert result.id == 'test.new_command'
    assert result.name == 'New Command'
    assert result.key == 'new_command'
    assert result.group_key == 'test'
    assert result.description == 'A new command'
    assert isinstance(result.arguments, list)
    assert result.arguments == []

    # Assert the service was called to check existence and to save.
    mock_cli_service.exists.assert_called_once_with('test.new_command')
    mock_cli_service.save.assert_called_once_with(result)

# ** test: add_cli_command_with_arguments
def test_add_cli_command_with_arguments(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliCommand can create a command with initial arguments.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    mock_cli_service.exists.return_value = False

    command = AddCliCommand(cli_service=mock_cli_service)

    arguments = [
        {
            'name_or_flags': ['-v', '--verbose'],
            'description': 'Enable verbose output',
            'type': 'str',
        }
    ]

    result = command.execute(
        id='test.verbose_command',
        name='Verbose Command',
        key='verbose_command',
        group_key='test',
        description='A command with arguments',
        arguments=arguments,
    )

    assert isinstance(result, CliCommand)
    assert result.id == 'test.verbose_command'
    assert len(result.arguments) == 1

    mock_cli_service.exists.assert_called_once_with('test.verbose_command')
    mock_cli_service.save.assert_called_once_with(result)

# ** test: add_cli_command_missing_id
def test_add_cli_command_missing_id(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliCommand fails when id is missing or empty.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    mock_cli_service.exists.return_value = False

    command = AddCliCommand(cli_service=mock_cli_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='  ',  # empty after strip
            name='Test Command',
            key='command',
            group_key='test',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'COMMAND_PARAMETER_REQUIRED'

# ** test: add_cli_command_duplicate_id
def test_add_cli_command_duplicate_id(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliCommand fails when the command id already exists.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    mock_cli_service.exists.return_value = True

    command = AddCliCommand(cli_service=mock_cli_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='test.existing',
            name='Existing Command',
            key='existing',
            group_key='test',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'CLI_COMMAND_ALREADY_EXISTS'

# ** test: add_cli_command_via_command_handle
def test_add_cli_command_via_command_handle(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliCommand works via DomainEvent.handle.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    mock_cli_service.exists.return_value = False

    result = DomainEvent.handle(
        AddCliCommand,
        dependencies={'cli_service': mock_cli_service},
        id='test.handle_command',
        name='Handle Command',
        key='handle_command',
        group_key='test',
    )

    assert result.id == 'test.handle_command'
    mock_cli_service.exists.assert_called_once_with('test.handle_command')
    mock_cli_service.save.assert_called_once()

# ** test: add_cli_argument_success
def test_add_cli_argument_success(
    mock_cli_service: CliService,
    sample_cli_command: CliCommand,
):
    '''
    Test that AddCliArgument successfully adds an argument to a command.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    :param sample_cli_command: Sample CLI command.
    :type sample_cli_command: CliCommand
    '''

    mock_cli_service.get.return_value = sample_cli_command

    command = AddCliArgument(cli_service=mock_cli_service)

    result_id = command.execute(
        command_id='test.command',
        name_or_flags=['-v', '--verbose'],
        description='Enable verbose output',
    )

    assert result_id == 'test.command'
    assert len(sample_cli_command.arguments) == 1

    mock_cli_service.get.assert_called_once_with('test.command')
    mock_cli_service.save.assert_called_once_with(sample_cli_command)

# ** test: add_cli_argument_with_kwargs
def test_add_cli_argument_with_kwargs(
    mock_cli_service: CliService,
    sample_cli_command: CliCommand,
):
    '''
    Test that AddCliArgument handles additional kwargs for arguments.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    :param sample_cli_command: Sample CLI command.
    :type sample_cli_command: CliCommand
    '''

    mock_cli_service.get.return_value = sample_cli_command

    command = AddCliArgument(cli_service=mock_cli_service)

    result_id = command.execute(
        command_id='test.command',
        name_or_flags=['--count'],
        description='Number of items',
        type='int',
        required=True,
        default='5',
    )

    assert result_id == 'test.command'
    assert len(sample_cli_command.arguments) == 1

    mock_cli_service.get.assert_called_once_with('test.command')
    mock_cli_service.save.assert_called_once_with(sample_cli_command)

# ** test: add_cli_argument_missing_command_id
def test_add_cli_argument_missing_command_id(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliArgument fails when command_id is missing or empty.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    command = AddCliArgument(cli_service=mock_cli_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            command_id='  ',
            name_or_flags=['-v'],
            description='Verbose',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'COMMAND_PARAMETER_REQUIRED'

# ** test: add_cli_argument_command_not_found
def test_add_cli_argument_command_not_found(
    mock_cli_service: CliService,
):
    '''
    Test that AddCliArgument fails when the CLI command does not exist.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    mock_cli_service.get.return_value = None

    command = AddCliArgument(cli_service=mock_cli_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            command_id='test.missing',
            name_or_flags=['-v'],
            description='Verbose',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'CLI_COMMAND_NOT_FOUND'

# ** test: add_cli_argument_via_command_handle
def test_add_cli_argument_via_command_handle(
    mock_cli_service: CliService,
    sample_cli_command: CliCommand,
):
    '''
    Test that AddCliArgument works via DomainEvent.handle.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    :param sample_cli_command: Sample CLI command.
    :type sample_cli_command: CliCommand
    '''

    mock_cli_service.get.return_value = sample_cli_command

    result_id = DomainEvent.handle(
        AddCliArgument,
        dependencies={'cli_service': mock_cli_service},
        command_id='test.command',
        name_or_flags=['--debug'],
        description='Enable debug mode',
    )

    assert result_id == 'test.command'
    assert len(sample_cli_command.arguments) == 1
    mock_cli_service.get.assert_called_once_with('test.command')
    mock_cli_service.save.assert_called_once_with(sample_cli_command)

# ** test: add_cli_argument_multiple_arguments
def test_add_cli_argument_multiple_arguments(
    mock_cli_service: CliService,
    sample_cli_command: CliCommand,
):
    '''
    Test adding multiple arguments to the same command sequentially.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    :param sample_cli_command: Sample CLI command.
    :type sample_cli_command: CliCommand
    '''

    mock_cli_service.get.return_value = sample_cli_command

    command = AddCliArgument(cli_service=mock_cli_service)

    # Add first argument.
    command.execute(
        command_id='test.command',
        name_or_flags=['-v', '--verbose'],
        description='Verbose output',
    )

    # Add second argument.
    command.execute(
        command_id='test.command',
        name_or_flags=['-q', '--quiet'],
        description='Quiet mode',
    )

    assert len(sample_cli_command.arguments) == 2
    assert mock_cli_service.save.call_count == 2

# ** test: list_cli_commands_success
def test_list_cli_commands_success(
    mock_cli_service: CliService,
    sample_cli_command: CliCommand,
):
    '''
    Test that ListCliCommands successfully lists all CLI commands.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    :param sample_cli_command: Sample CLI command.
    :type sample_cli_command: CliCommand
    '''

    # Arrange the mock service to return a list of commands.
    command_list = [
        sample_cli_command,
        Aggregate.new(
            CliCommandAggregate,
            id='test.another',
            name='Another Command',
            key='another',
            group_key='test',
            description='Another test command',
            arguments=[],
        )
    ]
    mock_cli_service.list.return_value = command_list

    command = ListCliCommands(cli_service=mock_cli_service)

    result = command.execute()

    # Assert the result is a list of CLI commands.
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == 'test.command'
    assert result[1].id == 'test.another'

    # Assert the service was called.
    mock_cli_service.list.assert_called_once()

# ** test: list_cli_commands_empty
def test_list_cli_commands_empty(
    mock_cli_service: CliService,
):
    '''
    Test that ListCliCommands handles empty command lists.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    # Arrange the mock service to return an empty list.
    mock_cli_service.list.return_value = []

    command = ListCliCommands(cli_service=mock_cli_service)

    result = command.execute()

    # Assert the result is an empty list.
    assert isinstance(result, list)
    assert len(result) == 0

    # Assert the service was called.
    mock_cli_service.list.assert_called_once()

# ** test: list_cli_commands_via_command_handle
def test_list_cli_commands_via_command_handle(
    mock_cli_service: CliService,
    sample_cli_command: CliCommand,
):
    '''
    Test that ListCliCommands works via DomainEvent.handle.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    :param sample_cli_command: Sample CLI command.
    :type sample_cli_command: CliCommand
    '''

    mock_cli_service.list.return_value = [sample_cli_command]

    result = DomainEvent.handle(
        ListCliCommands,
        dependencies={'cli_service': mock_cli_service},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 'test.command'
    mock_cli_service.list.assert_called_once()

# ** test: get_parent_arguments_success
def test_get_parent_arguments_success(
    mock_cli_service: CliService,
):
    '''
    Test that GetParentArguments successfully retrieves parent arguments.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    # Arrange the mock service to return parent arguments.
    parent_args = [
        DomainObject.new(
            CliArgument,
            name_or_flags=['--verbose', '-v'],
            description='Enable verbose output',
            type='str',
            required=False,
        ),
        DomainObject.new(
            CliArgument,
            name_or_flags=['--debug'],
            description='Enable debug mode',
            type='str',
            required=False,
        )
    ]
    mock_cli_service.get_parent_arguments.return_value = parent_args

    command = GetParentArguments(cli_service=mock_cli_service)

    result = command.execute()

    # Assert the result is a list of parent arguments.
    assert isinstance(result, list)
    assert len(result) == 2
    assert '--verbose' in result[0].name_or_flags
    assert '--debug' in result[1].name_or_flags

    # Assert the service was called.
    mock_cli_service.get_parent_arguments.assert_called_once()

# ** test: get_parent_arguments_empty
def test_get_parent_arguments_empty(
    mock_cli_service: CliService,
):
    '''
    Test that GetParentArguments handles empty parent argument lists.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    # Arrange the mock service to return an empty list.
    mock_cli_service.get_parent_arguments.return_value = []

    command = GetParentArguments(cli_service=mock_cli_service)

    result = command.execute()

    # Assert the result is an empty list.
    assert isinstance(result, list)
    assert len(result) == 0

    # Assert the service was called.
    mock_cli_service.get_parent_arguments.assert_called_once()

# ** test: get_parent_arguments_via_command_handle
def test_get_parent_arguments_via_command_handle(
    mock_cli_service: CliService,
):
    '''
    Test that GetParentArguments works via DomainEvent.handle.

    :param mock_cli_service: The mock CLI service.
    :type mock_cli_service: CliService
    '''

    parent_args = [
        DomainObject.new(
            CliArgument,
            name_or_flags=['--config'],
            description='Config file path',
            type='str',
        )
    ]
    mock_cli_service.get_parent_arguments.return_value = parent_args

    result = DomainEvent.handle(
        GetParentArguments,
        dependencies={'cli_service': mock_cli_service},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert '--config' in result[0].name_or_flags
    mock_cli_service.get_parent_arguments.assert_called_once()
