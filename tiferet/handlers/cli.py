# *** imports

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
        