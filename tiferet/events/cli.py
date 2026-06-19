"""Tiferet CLI Domain Events"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from .settings import DomainEvent, a
from ..domain import CliCommand
from ..interfaces import CliService
from ..mappers import CliCommandAggregate

# *** events

# ** event: cli_event
class CliEvent(DomainEvent):
    '''
    Base event providing the shared CliService dependency for CLI domain events.
    '''

    # * attribute: cli_service
    cli_service: CliService

    # * init
    def __init__(self, cli_service: CliService):
        '''
        Initialize the CLI event with its shared service dependency.

        :param cli_service: The CLI service shared across CLI events.
        :type cli_service: CliService
        '''

        # Set the CLI service dependency.
        self.cli_service = cli_service

# ** event: list_cli_commands
class ListCliCommands(CliEvent):
    '''
    A domain event to list all CLI commands.
    '''

    # * method: execute
    def execute(self, default_commands_list: List[CliCommand] = [], **kwargs) -> List[CliCommand]:
        '''
        List all CLI commands, falling back to a provided default command list
        when the repository returns no results.

        :param default_commands_list: Optional list of CLI commands used as an
            execute-time fallback when the repository returns no commands.
        :type default_commands_list: List[CliCommand]
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: List of CLI commands.
        :rtype: List[CliCommand]
        '''

        # Retrieve commands from the service; fall back to the provided defaults if empty.
        commands = self.cli_service.list()
        return commands or list(default_commands_list or [])


# ** event: get_parent_arguments
class GetParentArguments(CliEvent):
    '''
    A domain event to retrieve parent-level CLI arguments.
    '''

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

# ** event: add_cli_command
class AddCliCommand(CliEvent):
    '''
    A domain event to add a new CLI command.
    '''

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
            a.const.CLI_COMMAND_ALREADY_EXISTS_ID,
            id=id,
        )

        # Coerce optional list args that argparse may pass as None.
        arguments = arguments or []

        # Create CLI command aggregate.
        command = CliCommandAggregate(
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


# ** event: add_cli_argument
class AddCliArgument(CliEvent):
    '''
    A domain event to add an argument to an existing CLI command.
    '''

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
            a.const.CLI_COMMAND_NOT_FOUND_ID,
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
