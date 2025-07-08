# *** imports

# ** app
from .settings import *

# *** contracts

# ** contract: cli_argument
class CliArgument(ModelContract):
    '''
    A contract representing a command line argument.
    '''
    pass

# ** contract: cli_command
class CliCommand(ModelContract):
    '''
    A contract representing a command in the command line interface.
    '''
    pass

# ** contract: cli_repository
class CliRepository(Repository):
    '''
    The CLI repository interface is used to manage the command line interface commands and arguments.
    It provides methods to retrieve and manipulate CLI commands and their arguments.
    '''

    # * method: get_command
    @abstractmethod
    def get_command(self, command_id: str) -> CliCommand:
        '''
        Get a command by its unique identifier.

        :param command_id: The unique identifier of the command.
        :type command_id: str
        :return: The command object.
        :rtype: CliCommand
        '''
        raise NotImplementedError('get_command method must be implemented in the CLI repository.')

# ** contract: cli_service
class CliService(Service):
    '''
    The CLI service interface is used to manage the command line interface of the application.
    '''

    # * method: get_command
    @abstractmethod
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
        raise NotImplementedError('get_command method must be implemented in the CLI service.')
