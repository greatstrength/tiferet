"""Tiferet CLI Blueprints"""

# *** imports

# ** core
import sys
import argparse
from typing import Any, Dict, List, Optional, Tuple

# ** app
from ..assets import TiferetAPIError
from ..domain import CliArgument, CliCommand
from .. import assets as a
from ..events import DomainEvent
from ..events.app import GetAppInterface
from .main import (
    wire_services,
    load_default_services,
    resolve_interface,
    realize_interface,
)

# *** blueprints

# ** blueprint: get_commands
def get_commands(registry: Dict[str, Any]) -> Dict[str, List[CliCommand]]:
    '''
    Retrieve the CLI commands grouped by their group_key.

    :param registry: The wiring registry of instantiated services keyed by id.
    :type registry: Dict[str, Any]
    :return: A dictionary mapping group keys to lists of CLI commands.
    :rtype: Dict[str, List[CliCommand]]
    '''

    # Resolve the list CLI commands event and execute it.
    list_commands_evt = registry['list_commands_evt']
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


# ** blueprint: get_parent_arguments
def get_parent_arguments(registry: Dict[str, Any]) -> List:
    '''
    Retrieve the parent-level CLI arguments.

    :param registry: The wiring registry of instantiated services keyed by id.
    :type registry: Dict[str, Any]
    :return: A list of parent-level CLI arguments.
    :rtype: List
    '''

    # Resolve the parent arguments event and execute it.
    get_parent_args_evt = registry['get_parent_args_evt']
    return get_parent_args_evt.execute()


# ** blueprint: build_argument_kwargs
def build_argument_kwargs(argument: CliArgument) -> Dict[str, Any]:
    '''
    Build the ``argparse.add_argument`` keyword arguments for a CLI argument.

    Value-only keywords (``type``, ``nargs``, ``choices``) are included only for
    value-consuming actions (``store``, ``append``, or the default).  Flag and
    const actions such as ``store_true`` reject those keywords, so they are
    omitted to keep parser construction valid.

    :param argument: The CLI argument definition.
    :type argument: CliArgument
    :return: The keyword arguments for ``add_argument``.
    :rtype: Dict[str, Any]
    '''

    # Start with keywords accepted by every argparse action.
    kwargs: Dict[str, Any] = dict(help=argument.description)

    # Include the action only when explicitly configured.
    if argument.action is not None:
        kwargs['action'] = argument.action

    # Value-consuming actions accept type, nargs, and choices.
    if argument.action in (None, 'store', 'append'):
        kwargs['type'] = argument.get_type()
        kwargs['nargs'] = argument.nargs
        kwargs['choices'] = argument.choices

    # Include an explicit default only when configured so flag actions keep
    # their argparse-native defaults (e.g. store_true defaults to False).
    if argument.default is not None:
        kwargs['default'] = argument.default

    # Required is only meaningful for optional (flagged) arguments.
    if argument.required is not None:
        kwargs['required'] = argument.required

    # Return the assembled keyword arguments.
    return kwargs


# ** blueprint: build_parser
def build_parser(
    cli_commands: Dict[str, List[CliCommand]],
    parent_arguments: List,
) -> argparse.ArgumentParser:
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
                cli_command_parser.add_argument(
                    *argument.name_or_flags,
                    **build_argument_kwargs(argument),
                )

            # Add parent arguments that don't collide with declared command arguments.
            for argument in parent_arguments:
                if not cli_command.has_argument(argument.name_or_flags):
                    cli_command_parser.add_argument(
                        *argument.name_or_flags,
                        **build_argument_kwargs(argument),
                    )

    # Return the configured parser.
    return parser


# ** blueprint: parse_argv
def parse_argv(
    parser: argparse.ArgumentParser,
    argv: Optional[List[str]] = None,
) -> Dict[str, Any]:
    '''
    Parse CLI arguments from the given parser, exiting on failure.

    :param parser: The configured argument parser.
    :type parser: argparse.ArgumentParser
    :param argv: Optional argument list; defaults to sys.argv[1:] when None.
    :type argv: Optional[List[str]]
    :return: The parsed arguments as a dictionary.
    :rtype: Dict[str, Any]
    '''

    # Parse the CLI arguments; on failure, print to stderr and exit with code 2.
    try:
        return vars(parser.parse_args(argv))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)


# ** blueprint: derive_feature_request
def derive_feature_request(
    parsed: Dict[str, Any],
) -> Tuple[str, Dict[str, str]]:
    '''
    Derive the feature ID and request headers from parsed CLI arguments.

    :param parsed: The parsed argument namespace as a dictionary.
    :type parsed: Dict[str, Any]
    :return: A tuple of (feature_id, headers).
    :rtype: Tuple[str, Dict[str, str]]
    '''

    # Extract the group and command from the parsed arguments.
    group = parsed.get('group')
    command = parsed.get('command')

    # Derive the feature id by normalizing hyphens to underscores.
    feature_id = '{}.{}'.format(
        group.replace('-', '_'),
        command.replace('-', '_'),
    )

    # Build the request headers from the raw group and command values.
    headers = dict(
        command_group=group,
        command_key=command,
    )

    # Return the derived feature id and headers.
    return feature_id, headers


# ** blueprint: build_app
def build_app(
    interface_id: str,
    argv: Optional[List[str]] = None,
    module_path: str = a.bps.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.bps.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters
) -> Any:
    '''
    Build the CLI application, parse arguments, and dispatch to the interface feature.

    Loads the app service, resolves the interface, builds the CLI parser from
    configured commands, parses argv, and executes the corresponding feature.

    :param interface_id: The CLI interface identifier.
    :type interface_id: str
    :param argv: Optional argument list; defaults to sys.argv[1:] when None.
    :type argv: Optional[List[str]]
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Resolve the interface definition in a single pass.
    app_interface, default_services = resolve_interface(
        interface_id, module_path, class_name, **parameters)

    # Merge constants in priority order: defaults < interface < user parameters.
    merged_constants = {
        **{k: v for dep in default_services for k, v in dep.parameters.items()},
        **a.bps.DEFAULT_CONSTANTS,
        **(app_interface.constants or {}),
        **parameters,
    }

    # Declaratively wire the default service dependencies with the merged
    # constants so the CLI events can resolve without an app-level container.
    registry = wire_services(default_services, merged_constants)

    # Build the CLI parser from the resolved commands and parent arguments.
    cli_commands = get_commands(registry)
    parent_arguments = get_parent_arguments(registry)
    parser = build_parser(cli_commands, parent_arguments)

    # Parse the CLI arguments.
    parsed = parse_argv(parser, argv)

    # Derive the feature id and headers from the parsed arguments.
    feature_id, headers = derive_feature_request(parsed)

    # Realize the app interface context from the already-resolved definition.
    interface_context = realize_interface(app_interface, interface_id)

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
