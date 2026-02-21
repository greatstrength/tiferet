# *** imports

# ** core
import sys
import argparse
from typing import Dict, Any, Callable

# ** app
from .app import *
from ..domain import CliCommand
from ..events.cli import ListCliCommands, GetParentArguments

# *** contexts

# ** context: cli_context
class CliContext(AppInterfaceContext):
    '''
    The CLI context is used to manage the command line interface of the application.
    It provides methods to handle command line arguments, commands, and their execution.
    '''

    # * attribute: list_commands_handler
    list_commands_handler: Callable

    # * attribute: get_parent_args_handler
    get_parent_args_handler: Callable

    # * init
    def __init__(self,
                 interface_id: str,
                 features: FeatureContext,
                 errors: ErrorContext,
                 logging: LoggingContext,
                 list_commands_cmd: ListCliCommands,
                 get_parent_args_cmd: GetParentArguments):
        '''
        Initialize the CLI context with command handlers.

        :param interface_id: The unique identifier for the CLI interface.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        :param logging: The logging context.
        :type logging: LoggingContext
        :param list_commands_cmd: Command to list all CLI commands.
        :type list_commands_cmd: ListCliCommands
        :param get_parent_args_cmd: Command to get parent arguments.
        :type get_parent_args_cmd: GetParentArguments
        '''

        # Set the command handlers.
        self.list_commands_handler = list_commands_cmd.execute
        self.get_parent_args_handler = get_parent_args_cmd.execute

        # Initialize the base class with the interface ID, features, and errors.
        super().__init__(
            interface_id=interface_id,
            features=features,
            errors=errors,
            logging=logging
        )

    # * method: get_commands
    def get_commands(self) -> Dict[str, CliCommand]:
        '''
        Get all commands available in the CLI mapped by their group keys.

        :return: A dictionary of CLI commands mapped by their group keys.
        :rtype: Dict[str, CliCommand]
        '''

        # Retrieve the commands via the list commands handler.
        cli_commands = self.list_commands_handler()

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

        # Retrieve the parent arguments via the get parent args handler.
        parent_arguments = self.get_parent_args_handler()

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

    # * method: parse_request
    def parse_request(self) -> RequestContext:
        '''
        Parse the command line arguments and return a Request object.

        :return: The parsed request context.
        :rtype: RequestContext
        '''

        # Retrieve the command map via get_commands.
        cli_commands = self.get_commands()

        # Parse the command line arguments for the CLI command.
        data = self.parse_arguments(cli_commands)

        # Fashion the feature id from the command group and key.
        feature_id = '{}.{}'.format(
            data.get('group').replace('-', '_'),
            data.get('command').replace('-', '_')
        )

        # Create a RequestContext object with the parsed data and headers.
        return super().parse_request(
            headers=dict(
                command_group=data.get('group'),
                command_key=data.get('command'),
            ),
            data=data,
            feature_id=feature_id,
        )

    # * method: run
    def run(self) -> Any:
        '''
        Run the CLI context by parsing the request and executing the command.

        :return: The result of the command execution.
        :rtype: Any
        '''

        # Create a logger for the CLI context.
        logger = self.logging.build_logger()

        # Attempt to parse the command line request.
        try:
            logger.debug('Parsing CLI request...')
            cli_request = self.parse_request()

        # Handle any exceptions that may occur during request parsing.
        except Exception as e:
            logger.error(f'Error parsing CLI request: {e}')
            print(e, file=sys.stderr)
            sys.exit(2)

        # Attempt to execute the feature for the parsed CLI request.
        try:
            logger.info(f'Executing feature for CLI request: {cli_request.feature_id}')
            logger.debug(f'CLI request data: {cli_request.data}')
            self.execute_feature(
                feature_id=cli_request.feature_id,
                request=cli_request,
                logger=logger,
            )
        
        # Handle any TiferetError exceptions that may occur during feature execution.
        except TiferetError as e:
            logger.error(f'Error executing CLI feature {cli_request.feature_id}: {e}')
            try:
                self.handle_error(e)
            except TiferetAPIError as api_error:
                print(api_error, file=sys.stderr)
            sys.exit(1)
        
        # Return the result of the command execution.
        logger.debug('CLI request executed successfully.')
        print(cli_request.handle_response())
