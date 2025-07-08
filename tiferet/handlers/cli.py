# *** imports

# ** core
import argparse

# ** app
from ..commands import raise_error
from ..contracts.cli import *

# *** handlers

# ** handler: cli_handler
class CliHandler(CliService):
    '''
    The CLI handler is used to manage the command line interface of the application.
    It provides methods to retrieve and manipulate CLI commands and their arguments.
    '''

    # * attribute: cli_repository
    cli_repository: CliRepository

    # * init
    def __init__(self, cli_repository: CliRepository):
        '''
        Initialize the CLI handler with a CLI repository.

        :param cli_repository: The CLI repository to use.
        :type cli_repository: CliRepository
        '''
        
        # Set the CLI repository.
        self.cli_repository = cli_repository


    # * method: get_command
    def get_command(self, group: str, command: str) -> CliCommand:
        '''
        Get a command by its group and name.

        :param group: The group of the command.
        :type group: str
        :param command: The name of the command.
        :type command: str
        :return: The command object.
        :rtype: CliCommand
        '''
        
        # Format the command ID.
        command_id = f'{group}.{command}'

        # Retrieve the command from the repository.
        command = self.cli_repository.get_command(command_id)

        # If the command is not found, raise an error.
        if not command:
            raise_error.execute(
                'CLI_COMMAND_NOT_FOUND',
                f'Command {command_id} not found.',
                command_id
            )

        # Return the command.
        return command
    
    # * method: parse_arguments
    def parse_arguments(self, cli_command: CliCommand) -> Dict[str, Any]:
        '''
        Parse the command line arguments for a given CLI command.

        :param cli_command: The CLI command to parse arguments for.
        :type cli_command: CliCommand
        :return: A dictionary of parsed arguments.
        :rtype: Dict[str, Any]
        '''

         # Create an argument parser.
        parser = argparse.ArgumentParser(
            description=cli_command.description
        )

        # Retrieve the parent arguments from the CLI repository.
        # Add the parent arguments to the command if they do not already exist.
        parent_arguments = self.cli_repository.get_parent_arguments()
        for argument in parent_arguments:
            if not cli_command.has_argument(argument.name_or_flags):
                cli_command.add_argument(argument)

        # Add the cli command arguments to the parser.
        for argument in cli_command.arguments:
            parser.add_argument(
                *argument.name_or_flags,
                help=argument.description,
                type=argument.get_type(),
                default=argument.default,
                required=argument.required,
                nargs=argument.nargs,
                choices=argument.choices,
                action=argument.action
            )

        # Return the parsed arguments as a dictionary.
        return vars(parser.parse_args())
        