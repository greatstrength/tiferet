import argparse

from ..contexts.request import RequestContext
from ..objects.cli import CliInterface

def create_cli_parser(cli_interface: CliInterface):

    # Create parser.
    parser = argparse.ArgumentParser()

    # Add command subparsers
    command_subparsers = parser.add_subparsers(dest='command')
    for command_name, command in cli_interface.commands.items():
        command_name = command_name.replace('_', '-')
        command_subparser = command_subparsers.add_parser(
            command_name, **command.to_primitive('add_parser'))
        subcommand_subparsers = command_subparser.add_subparsers(
            dest='subcommand')
        for subcommand_name, subcommand in command.subcommands.items():
            subcommand_name = subcommand_name.replace('_', '-')
            subcommand_subparser = subcommand_subparsers.add_parser(
                subcommand_name, help=subcommand.help)
            for argument in subcommand.arguments:
                subcommand_subparser.add_argument(
                    *argument.name_or_flags, **argument.to_primitive('add_argument'))
            for argument in cli_interface.parent_arguments:
                subcommand_subparser.add_argument(
                    *argument.name_or_flags, **argument.to_primitive('add_argument'))

    return parser

def create_request(self, request: argparse.Namespace, **kwargs) -> RequestContext:
    return request
