"""Tiferet CLI Builder"""

# *** imports

# ** core
import sys
import argparse
from typing import Dict, Any, List, Optional

# ** app
from .main import AppBuilder
from ..assets import TiferetAPIError
from ..domain import CliCommand

# *** builders

# ** builder: cli_builder
class CliBuilder(AppBuilder):
    '''
    The CLI application builder for Tiferet v2.0+.

    Extends :class:`AppBuilder` to absorb the argparse-based CLI build procedure
    (command resolution, parser construction, argument parsing) and defers
    feature execution to the resolved :class:`AppInterfaceContext` via its
    standard ``run`` method. Exposed as ``CLI`` in the top-level exports.
    '''

    # * method: get_commands
    def get_commands(self) -> Dict[str, List[CliCommand]]:
        '''
        Resolve and group the CLI commands registered on the loaded interface.

        :return: A dictionary of CLI commands mapped by their group keys.
        :rtype: Dict[str, List[CliCommand]]
        '''

        # Resolve and execute the list-commands event via the service provider.
        list_commands_evt = self.service_provider.get_service('list_commands_evt')
        cli_commands = list_commands_evt.execute()

        # Group the commands by their group keys.
        command_map: Dict[str, List[CliCommand]] = {}
        for command in cli_commands:
            command_map.setdefault(command.group_key, []).append(command)

        # Return the grouped command map.
        return command_map

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List:
        '''
        Resolve the parent-level CLI arguments registered on the loaded interface.

        :return: The list of parent-level CLI arguments.
        :rtype: List
        '''

        # Resolve and execute the parent-arguments event via the service provider.
        get_parent_args_evt = self.service_provider.get_service('get_parent_args_evt')
        return get_parent_args_evt.execute()

    # * method: build_parser
    def build_parser(self,
            cli_commands: Dict[str, List[CliCommand]],
            parent_arguments: List,
        ) -> argparse.ArgumentParser:
        '''
        Build the argparse parser tree from the command map and parent arguments.

        :param cli_commands: The grouped CLI command map.
        :type cli_commands: Dict[str, List[CliCommand]]
        :param parent_arguments: The parent-level CLI arguments.
        :type parent_arguments: List
        :return: The configured argparse parser.
        :rtype: argparse.ArgumentParser
        '''

        # Create the root argument parser and the group-level subparsers.
        parser = argparse.ArgumentParser()
        group_subparsers = parser.add_subparsers(dest='group')

        # Build a parser for every command group.
        for group_key, cli_group_commands in cli_commands.items():
            group_subparser = group_subparsers.add_parser(
                group_key,
                help=f'Commands for the {group_key} group.'
            )
            cmd_subparsers = group_subparser.add_subparsers(dest='command')

            # Build a parser for every command within the group.
            for cli_command in cli_group_commands:
                cli_command_parser = cmd_subparsers.add_parser(
                    cli_command.key,
                    help=cli_command.description,
                )

                # Add the command-level arguments.
                for argument in cli_command.arguments:
                    args = dict(
                        help=argument.description,
                        type=argument.get_type(),
                        default=argument.default,
                        nargs=argument.nargs,
                        choices=argument.choices,
                        action=argument.action,
                    )
                    if argument.required is not None:
                        args['required'] = argument.required
                    cli_command_parser.add_argument(*argument.name_or_flags, **args)

                # Add any parent arguments not already declared on the command.
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
                            action=argument.action,
                        )

        # Return the configured parser.
        return parser

    # * method: run
    def run(self, interface_id: str, argv: Optional[List[str]] = None) -> Any:
        '''
        Run the CLI by parsing argv and delegating to the interface context.

        :param interface_id: The interface ID of the CLI application.
        :type interface_id: str
        :param argv: Optional argv overriding ``sys.argv`` for testing.
        :type argv: Optional[List[str]]
        :return: The response from the executed feature.
        :rtype: Any
        '''

        # Load the interface context via the parent builder.
        interface_context = self.load_interface(interface_id)

        # Resolve CLI metadata and build the argparse parser.
        cli_commands = self.get_commands()
        parent_arguments = self.get_parent_arguments()
        parser = self.build_parser(cli_commands, parent_arguments)

        # Attempt to parse the CLI arguments.
        try:
            parsed = vars(parser.parse_args(argv))

        # Handle any exceptions raised during argument parsing.
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(2)

        # Derive the feature id and headers from the parsed arguments.
        feature_id = '{}.{}'.format(
            parsed.get('group').replace('-', '_'),
            parsed.get('command').replace('-', '_'),
        )
        headers = dict(
            command_group=parsed.get('group'),
            command_key=parsed.get('command'),
        )

        # Delegate to the interface context's run method.
        try:
            response = interface_context.run(
                feature_id=feature_id,
                headers=headers,
                data=parsed,
            )

        # Handle any TiferetAPIError exceptions surfaced by the interface context.
        except TiferetAPIError as api_error:
            print(api_error, file=sys.stderr)
            sys.exit(1)

        # Print the response on successful feature execution.
        print(response)
        return response
