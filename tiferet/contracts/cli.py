# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import *

# *** contracts

# ** contract: cli_argument
class CliArgument(ModelContract):
    '''
    A contract representing a command line argument.
    '''
    
    # * attribute: name_or_flags
    name_or_flags: List[str]

    # * attribute: description
    description: str

    # * attribute: required
    required: bool

    # * attribute: default
    default: str

    # * attribute: choices
    choices: List[str]

    # * attribute: nargs
    nargs: str

    # * attribute: action
    action: str

    # * method: get_type
    def get_type(self) -> str |int | float:
        '''
        Get the type of the argument.

        :return: The type of the argument.
        :rtype: str | int | float
        '''
        raise NotImplementedError('get_type method must be implemented in the CliArgument contract.')

# ** contract: cli_command
class CliCommand(ModelContract):
    '''
    A contract representing a command in the command line interface.
    '''
    
    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: description
    description: str

    # * attribute: arguments
    arguments: List[CliArgument]

    # * method: has_argument
    def has_argument(self, flags: List[str]) -> bool:
        '''
        Check if the command has an argument with the given flags.

        :param flags: The flags to check for.
        :type flags: List[str]
        :return: True if the command has the argument, False otherwise.
        :rtype: bool
        '''
        raise NotImplementedError('has_argument method must be implemented in the CliCommand contract.')
    
    # * method: add_argument
    def add_argument(self, cli_argument: CliArgument):
        '''
        Add an argument to the command.

        :param cli_argument: The CLI argument to add.
        :type cli_argument: CliArgument
        '''
        raise NotImplementedError('add_argument method must be implemented in the CliCommand contract.')

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

    # * method: get_parent_arguments
    @abstractmethod
    def get_parent_arguments(self) -> List[CliArgument]:
        '''
        Get the parent arguments for the command line interface.

        :return: A list of parent arguments.
        :rtype: List[CliArgument]
        '''
        raise NotImplementedError('get_parent_arguments method must be implemented in the CLI repository.')

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
    
    # * method: parse_arguments
    @abstractmethod
    def parse_arguments(self, cli_command: CliCommand) -> Dict[str, Any]:
        '''
        Parse the command line arguments for a given CLI command.
        
        :param cli_command: The CLI command to parse arguments for.
        :type cli_command: CliCommand
        :return: A dictionary of parsed arguments.
        :rtype: Dict[str, Any]
        '''
        raise NotImplementedError('parse_arguments method must be implemented in the CLI service.')
