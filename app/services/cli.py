import argparse

from ..contexts.request import RequestContext
from ..objects.cli import CliInterface
from ..objects.cli import CliArgument


def create_argument_data(cli_argument: CliArgument):
    if cli_argument.action:
        return cli_argument.exclude('name_or_flags', 'type', 'nargs', 'choices')
    if cli_argument.type == 'str':
        data_type = str
    elif cli_argument.type == 'int':
        data_type = int
    elif cli_argument.type == 'float':
        data_type = float
    
    for name in cli_argument.name_or_flags:
        # Exclude flags that are named parameters.
        if not name.startswith('--'):
            return dict(
                **cli_argument.exclude('name_or_flags', 'required', 'type'),
                type=data_type
            )
    return dict(
        **cli_argument.exclude('name_or_flags', 'arg_type', 'type'),
        type=data_type
    )


def create_headers(data: dict):
    headers = dict(
        group_id=data.pop('group'),
        command_id=data.pop('command'),
    )
    headers['feature_id'] = f"{headers['group_id']}.{headers['command_id']}".replace('-', '_')
    return headers


def create_cli_parser(cli_interface: CliInterface):

    # Format commands into a dictionary lookup by group id.
    commands = {}
    for command in cli_interface.commands:
        group_id = command.group_id
        if group_id not in commands:
            commands[group_id] = []
        commands[group_id].append(command)

    # Create parser.
    parser = argparse.ArgumentParser()

    # Add command subparsers
    command_subparsers = parser.add_subparsers(dest='group')
    for group_id, commands in commands.items():
        group_name = group_id.replace('_', '-')
        command_subparser = command_subparsers.add_parser(
            group_name)
        subcommand_subparsers = command_subparser.add_subparsers(
            dest='command')
        for command in commands:
            command_name = command.feature_id.split('.')[-1].replace('_', '-')
            subcommand_subparser = subcommand_subparsers.add_parser(
                command_name)
            for argument in command.arguments:
                subcommand_subparser.add_argument(
                    *argument.name_or_flags, **create_argument_data(argument))
        for argument in cli_interface.parent_arguments:
            subcommand_subparser.add_argument(
                *argument.name_or_flags, **create_argument_data(argument))

    return parser


def create_request(request: argparse.Namespace, **kwargs) -> RequestContext:

    # Convert argparse.Namespace to dictionary.
    data = vars(request)

    # Create header values.
    headers = create_headers(data)

    # Create request context.
    return RequestContext(data=data, headers=headers, **headers, **kwargs)
