"""Tiferet CLI Commands"""

# *** imports

# ** core
from typing import Optional, List

# ** app
from ..entities import CliCommand
from ..events import DomainEvent
from ..interfaces import CliService
from ..mappers import CliCommandAggregate
from ..mappers.settings import Aggregate

# *** commands

# ** command: list_cli_commands
class ListCliCommands(DomainEvent):
    '''
    Command to list all CLI commands.
    '''

    # * attribute: cli_service
    cli_service: CliService

    # * init
    def __init__(self, cli_service: CliService):
        '''
        Initialize the list CLI commands command.

        :param cli_service: The CLI service.
        :type cli_service: CliService
        '''

        # Set the command attributes.
        self.cli_service = cli_service

    # * method: execute
    def execute(self, **kwargs) -> List[CliCommand]:
        '''
        List all CLI commands.

        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: List of CLI commands.
        :rtype: List[CliCommand]
        '''

        # Delegate to the CLI service.
        return self.cli_service.list()


# ** command: get_parent_arguments
class GetParentArguments(DomainEvent):
    '''
    Command to retrieve parent-level CLI arguments.
    '''

    # * attribute: cli_service
    cli_service: CliService

    # * init
    def __init__(self, cli_service: CliService):
        '''
        Initialize the get parent arguments command.

        :param cli_service: The CLI service.
        :type cli_service: CliService
        '''

        # Set the command attributes.
        self.cli_service = cli_service

    # * method: execute
    def execute(self, **kwargs) -> List:
        '''
        Get parent-level CLI arguments.

        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: List of parent CLI arguments.
        :rtype: List
        '''

        # Delegate to the CLI service.
        return self.cli_service.get_parent_arguments()

# ** command: add_cli_command
class AddCliCommand(DomainEvent):
    '''
    Command to add a new CLI command.
    '''

    # * attribute: cli_service
    cli_service: CliService

    # * method: init
    def __init__(self, cli_service: CliService):
        '''
        Initialize the add CLI command.

        :param cli_service: The CLI service.
        :type cli_service: CliService
        '''

        # Set the command attributes.
        self.cli_service = cli_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(
        self,
        id: str,
        name: str,
        key: str,
        group_key: str,
        description: Optional[str] = None,
        arguments: Optional[list] = [],
        **kwargs,
    ) -> CliCommand:
        '''
        Add a new CLI command.

        :param id: Required unique identifier.
        :type id: str
        :param name: The command name.
        :type name: str
        :param key: The command key.
        :type key: str
        :param group_key: The group key.
        :type group_key: str
        :param description: Optional command description.
        :type description: str | None
        :param arguments: Optional list of arguments.
        :type arguments: list | None
        :return: Created CliCommand model.
        :rtype: CliCommand
        '''

        # Check for existing command id.
        self.verify(
            not self.cli_service.exists(id),
            'CLI_COMMAND_ALREADY_EXISTS',
            id=id,
        )

        # Create CLI command aggregate.
        command = Aggregate.new(
            CliCommandAggregate,
            id=id,
            name=name,
            key=key,
            group_key=group_key,
            description=description,
            arguments=arguments,
        )

        # Save the new command and return it.
        self.cli_service.save(command)
        return command


# ** command: add_cli_argument
class AddCliArgument(DomainEvent):
    '''
    Command to add an argument to an existing CLI command.
    '''

    # * attribute: cli_service
    cli_service: CliService

    # * method: init
    def __init__(self, cli_service: CliService):
        '''
        Initialize the add CLI argument command.

        :param cli_service: The CLI service.
        :type cli_service: CliService
        '''

        # Set the command attributes.
        self.cli_service = cli_service

    # * method: execute
    @DomainEvent.parameters_required(['command_id'])
    def execute(
        self,
        command_id: str,
        name_or_flags: list,
        description: Optional[str] = None,
        **kwargs,
    ) -> str:
        '''
        Add an argument to an existing CLI command.

        :param command_id: The CLI command identifier.
        :type command_id: str
        :param name_or_flags: The argument name or flags.
        :type name_or_flags: list
        :param description: Optional argument description.
        :type description: str | None
        :return: The CLI command id.
        :rtype: str
        '''

        # Retrieve the existing CLI command.
        command = self.cli_service.get(command_id)

        # Verify that the command exists.
        self.verify(
            command is not None,
            'CLI_COMMAND_NOT_FOUND',
            command_id=command_id,
        )

        # Add the argument via the aggregate's method.
        command.add_argument(
            name_or_flags=name_or_flags,
            description=description,
            **kwargs,
        )

        # Persist the updated command.
        self.cli_service.save(command)

        # Return the id for confirmation.
        return command_id
