"""Tiferet CLI Builder"""

# *** imports

# ** core
import sys
import argparse
from typing import Any, Dict, List, Optional

# ** app
from ..assets import TiferetAPIError
from ..domain import CliCommand
from .main import AppBuilder

# *** builders

# ** builder: cli_builder
class CliBuilder(AppBuilder):
    '''
    Specialized application builder for CLI applications.

    Extends AppBuilder with argparse-based build-time translation of sys.argv
    into a feature invocation and delegates runtime execution to the resolved
    AppInterfaceContext.
    '''

    # * method: get_commands
    def get_commands(self) -> Dict[str, List[CliCommand]]:
        '''
        Retrieve the CLI commands grouped by their group_key.

        :return: A dictionary mapping group keys to lists of CLI commands.
        :rtype: Dict[str, List[CliCommand]]
        '''

        # Resolve the list CLI commands event and execute it.
        list_commands_evt = self.service_provider.get_service('list_commands_evt')
        cli_commands = list_commands_evt.execute()

        # Group the commands by group_key.
        command_map: Dict[str, List[CliCommand]] = {}
        for command in cli_commands:
            if command.group_key not in command_map:
                command_map[command.group_key] = [command]
            else:
                command_map[command.group_key].append(command)

        # Return the command map.
        return command_map

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List:
        '''
        Retrieve the parent-level CLI arguments.

        :return: A list of parent-level CLI arguments.
        :rtype: List
        '''

        # Resolve the parent arguments event and execute it.
        get_parent_args_evt = self.service_provider.get_service('get_parent_args_evt')
        return get_parent_args_evt.execute()

    # * method: build_parser
    def build_parser(self,
                     cli_commands: Dict[str, List[CliCommand]],
                     parent_arguments: List) -> argparse.ArgumentParser:
        '''
        Build an argparse.ArgumentParser from grouped CLI commands and parent arguments.

        :param cli_commands: The CLI commands grouped by group_key.
        :type cli_commands: Dict[str, List[CliCommand]]
        :param parent_arguments: The parent-level CLI arguments.
        :type parent_arguments: List
        :return: A configured argument parser.
        :rtype: argparse.ArgumentParser
        '''

        # Create the root parser.
        parser = argparse.ArgumentParser()

        # Add command subparsers for the command groups.
        group_subparsers = parser.add_subparsers(dest='group')

        # Loop through the command map and create a parser for each command.
        for group_key in cli_commands:
            group_subparser = group_subparsers.add_parser(
                group_key,
                help=f'Commands for the {group_key} group.'
            )
            cli_group_commands = cli_commands[group_key]
            cmd_subparsers = group_subparser.add_subparsers(dest='command')

            # Add each command's parser with its arguments.
            for cli_command in cli_group_commands:
                cli_command_parser = cmd_subparsers.add_parser(
                    cli_command.key,
                    help=cli_command.description
                )

                # Add the command-level arguments.
                for argument in cli_command.arguments:
                    args = dict(
                        help=argument.description,
                        type=argument.get_type(),
                        default=argument.default,
                        nargs=argument.nargs,
                        choices=argument.choices,
                        action=argument.action
                    )
                    if argument.required is not None:
                        args['required'] = argument.required
                    cli_command_parser.add_argument(*argument.name_or_flags, **args)

                # Add parent arguments that don't collide with declared command arguments.
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

        # Return the configured parser.
        return parser

    # * method: run
    def run(self, interface_id: str, argv: Optional[List[str]] = None) -> Any:
        '''
        Build the CLI parser, parse arguments, and dispatch to the interface feature.

        :param interface_id: The CLI interface identifier.
        :type interface_id: str
        :param argv: Optional argument list; defaults to sys.argv[1:] when None.
        :type argv: Optional[List[str]]
        :return: The response from the feature execution.
        :rtype: Any
        '''

        # Load the interface context.
        interface_context = self.load_interface(interface_id)

        # Build the CLI parser from the resolved commands and parent arguments.
        cli_commands = self.get_commands()
        parent_arguments = self.get_parent_arguments()
        parser = self.build_parser(cli_commands, parent_arguments)

        # Parse the CLI arguments; on failure, print to stderr and exit with code 2.
        try:
            parsed = vars(parser.parse_args(argv))
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(2)

        # Derive the feature id and headers from the parsed arguments.
        group = parsed.get('group')
        command = parsed.get('command')
        feature_id = '{}.{}'.format(
            group.replace('-', '_'),
            command.replace('-', '_'),
        )
        headers = dict(
            command_group=group,
            command_key=command,
        )

        # Execute the feature via the interface context; on API error, exit 1.
        try:
            response = interface_context.run(
                feature_id=feature_id,
                headers=headers,
                data=parsed,
            )
        except TiferetAPIError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        # Print and return the response.
        print(response)
        return response
