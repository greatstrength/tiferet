# *** imports

# ** core
import argparse
from typing import Dict, Any

# ** app
from ..contracts.cli import *

# *** handlers

# ** handler: cli_handler
class CliHandler(CliService):
    '''
    The CLI handler is used to manage the command line interface of the application.
    It provides methods to retrieve and manipulate CLI commands and their arguments.
    '''
    
    # * attribute: cli_repo
    cli_repo: CliRepository
    
    # * method: init
    def __init__(self, cli_repo: CliRepository):
        '''
        Initialize the CLI handler with a CLI repository.
        :param cli_repo: The CLI repository to use.
        :type cli_repo: CliRepository
        '''
        # Set the CLI repository.
        self.cli_repo = cli_repo
    
    # * method: get_commands
    def get_commands(self) -> Dict[str, CliCommand]:
        '''
        Get all commands available in the CLI service mapped by their group keys.
        :return: A dictionary of CLI commands mapped by their group keys.
        :rtype: Dict[str, CliCommand]
        '''
        # Retrieve the commands from the CLI repository.
        cli_commands = self.cli_repo.get_commands()
        
        # Create a map of commands by their group keys.
        command_map = {}
        for command in cli_commands:
            # If the group key is not set within the map, add the command to a list before adding it to the map.
            if command.group_key not in command_map:
                command_map[command.group_key] = [command]
            # Otherwise, append the command to the existing list for that group key.
            else:
                command_map[command.group_key].append(command)
        
        # Return the command map.
        return command_map
    
    # * method: parse_arguments
    def parse_arguments(self, cli_commands: Dict[str, CliCommand]) -> Dict[str, Any]:
        '''
        Parse the command line arguments for a list of CLI commands.
        :param cli_commands: The CLI commands to parse arguments for.
        :type cli_commands: Dict[str, CliCommand]
        :return: A dictionary of parsed arguments.
        :rtype: Dict[str, Any]
        '''
        # Retrieve the parent arguments from the CLI repository.
        parent_arguments = self.cli_repo.get_parent_arguments()
        
        # Create an argument parser.
        parser = argparse.ArgumentParser()
        
        # Add command subparsers for the command group.
        group_subparsers = parser.add_subparsers(dest='group')
        
        # Loop through the command map and create a parser for each command.
        for group_key in cli_commands:
            # Create a subparser for the command group.
            group_subparser = group_subparsers.add_parser(
                group_key,
                help=f'Commands for the {group_key} group.'
            )
            
            # Get the CLI commands from the map.
            cli_group_commands = cli_commands[group_key]
            
            # Create a subparser for each command in the group.
            cmd_subparsers = group_subparser.add_subparsers(dest='command')
            
            # Loop through each CLI command in the group.
            for cli_command in cli_group_commands:

                # Create a subparser for the CLI command.
                cli_command_parser = cmd_subparsers.add_parser(
                    cli_command.key,
                    help=cli_command.description
                )
                
                # Add the CLI command arguments to the command parser.
                for argument in cli_command.arguments:

                    # Create the argument data for the command parser.
                    args = dict(
                        help=argument.description,
                        type=argument.get_type(),
                        default=argument.default,
                        nargs=argument.nargs,
                        choices=argument.choices,
                        action=argument.action
                    )
                    
                    # Add the required flag if the value is set.
                    if argument.required is not None:
                        args['required'] = argument.required
                    
                    cli_command_parser.add_argument(
                        *argument.name_or_flags,
                        **args
                    )
                
                # Add the parent arguments to the command parser if they are not already present in the command.
                for argument in parent_arguments:
                    if not cli_command.has_argument(argument.name_or_flags):
                        cli_command_parser.add_argument(
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