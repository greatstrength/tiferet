"""Tiferet CLI Context"""

# *** imports

# ** core
import sys
import argparse
from typing import Any, Callable, Dict, List, Optional, Tuple

# ** app
from ..assets import TiferetAPIError
from ..domain import CliArgument, CliCommand
from ..events import DomainEvent
from .app import AppSessionContext
from .cache import CacheContext
from .request import RequestContext

# *** functions

# ** function: group_commands_by_key
def group_commands_by_key(cli_commands: List[CliCommand]) -> Dict[str, List[CliCommand]]:
    '''
    Group CLI commands by their group key, preserving encounter order.

    :param cli_commands: The CLI commands to group.
    :type cli_commands: List[CliCommand]
    :return: A mapping of group keys to lists of CLI commands.
    :rtype: Dict[str, List[CliCommand]]
    '''

    # Group the commands by their group key.
    command_map: Dict[str, List[CliCommand]] = {}
    for command in cli_commands:
        command_map.setdefault(command.group_key, []).append(command)

    # Return the grouped command map.
    return command_map


# ** function: build_parser
def build_parser(
        commands: Dict[str, List[CliCommand]],
        parent_arguments: List[CliArgument],
    ) -> argparse.ArgumentParser:
    '''
    Build an argparse parser from grouped CLI commands and parent arguments.

    :param commands: The CLI commands grouped by group key.
    :type commands: Dict[str, List[CliCommand]]
    :param parent_arguments: The parent-level arguments merged into each command.
    :type parent_arguments: List[CliArgument]
    :return: A configured argument parser.
    :rtype: argparse.ArgumentParser
    '''

    # Create the root parser and the group subparsers.
    parser = argparse.ArgumentParser()
    group_subparsers = parser.add_subparsers(dest='group')

    # Create a subparser for each command group.
    for group_key in commands:
        group_subparser = group_subparsers.add_parser(
            group_key,
            help=f'Commands for the {group_key} group.',
        )
        cmd_subparsers = group_subparser.add_subparsers(dest='command')

        # Create a subparser for each command in the group.
        for cli_command in commands[group_key]:
            cli_command_parser = cmd_subparsers.add_parser(
                cli_command.key,
                help=cli_command.description,
            )

            # Add the command-level arguments.
            for argument in cli_command.arguments:
                cli_command_parser.add_argument(
                    *argument.name_or_flags,
                    **argument.to_argparse_kwargs(),
                )

            # Add parent arguments that don't collide with command arguments.
            for argument in parent_arguments:
                if not cli_command.has_argument(argument.name_or_flags):
                    cli_command_parser.add_argument(
                        *argument.name_or_flags,
                        **argument.to_argparse_kwargs(),
                    )

    # Return the configured parser.
    return parser


# ** function: derive_feature_request
def derive_feature_request(parsed: Dict[str, Any]) -> Tuple[str, Dict[str, str]]:
    '''
    Derive the feature id and request headers from parsed CLI arguments.

    The feature id normalizes hyphens to underscores; the headers retain the
    raw group and command values.

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

# *** contexts

# ** context: cli_context
class CliContext(AppSessionContext):
    '''
    The CLI context extends the application session hub with command-line
    concerns: it retrieves CLI commands, builds and parses an argparse parser,
    derives a feature request from the parsed arguments, and dispatches the
    request through the inherited run pipeline.

    Stateless parsing helpers (command grouping, parser construction, and
    request derivation) live as side-effect-free module-level functions, and
    per-argument argparse translation lives on ``CliArgument.to_argparse_kwargs``;
    the context methods orchestrate them with the injected event collaborators.

    It intentionally omits ``domain_type`` so the ``ContextMeta`` registry
    keeps mapping ``AppSession`` to :class:`AppSessionContext`; the CLI
    context is selected explicitly through a session's configured
    ``module_path`` / ``class_name``.
    '''

    # * attribute: list_commands_evt
    list_commands_evt: DomainEvent

    # * attribute: get_parent_args_evt
    get_parent_args_evt: DomainEvent

    # * init
    def __init__(self,
            get_feature_evt: DomainEvent,
            get_error_evt: DomainEvent,
            logging_list_all_evt: DomainEvent,
            get_dependency: Callable,
            list_commands_evt: DomainEvent,
            get_parent_args_evt: DomainEvent,
            cache: CacheContext = None,
            default_features: Dict[str, Dict[str, Any]] = None,
            default_commands: Dict[str, Dict[str, Any]] = None,
        ):
        '''
        Initialize the CLI context.

        :param get_feature_evt: The event used to retrieve features.
        :type get_feature_evt: DomainEvent
        :param get_error_evt: The event used to retrieve errors.
        :type get_error_evt: DomainEvent
        :param logging_list_all_evt: The event used to list logging configurations.
        :type logging_list_all_evt: DomainEvent
        :param get_dependency: The injected service-resolution handler used to
            resolve feature step events and middleware.
        :type get_dependency: Callable
        :param list_commands_evt: The event used to list CLI commands.
        :type list_commands_evt: DomainEvent
        :param get_parent_args_evt: The event used to retrieve parent-level CLI arguments.
        :type get_parent_args_evt: DomainEvent
        :param cache: The shared cache context for all sub-contexts.
        :type cache: CacheContext
        :param default_features: Optional id-keyed feature records for bootstrap fallback.
        :type default_features: Dict[str, Dict[str, Any]]
        :param default_commands: Optional id-keyed CLI command records for bootstrap fallback.
        :type default_commands: Dict[str, Dict[str, Any]]
        '''

        # Initialize the base application interface hub.
        super().__init__(
            get_feature_evt=get_feature_evt,
            get_error_evt=get_error_evt,
            logging_list_all_evt=logging_list_all_evt,
            get_dependency=get_dependency,
            cache=cache,
            default_features=default_features,
            default_commands=default_commands,
        )

        # Store the CLI-specific event collaborators.
        self.list_commands_evt = list_commands_evt
        self.get_parent_args_evt = get_parent_args_evt

    # * method: get_commands
    def get_commands(self) -> Dict[str, List[CliCommand]]:
        '''
        Retrieve all CLI commands grouped by their group key.

        :return: A mapping of group keys to lists of CLI commands.
        :rtype: Dict[str, List[CliCommand]]
        '''

        # Retrieve commands via the event, falling back to the bootstrap default
        # command list when the repository returns no commands.
        cli_commands = self.list_commands_evt.execute() or self.default_commands_list

        # Group the commands by their group key.
        return group_commands_by_key(cli_commands)

    # * method: parse_cli_request
    def parse_cli_request(self, argv: Optional[List[str]] = None) -> RequestContext:
        '''
        Parse CLI arguments into a request context.

        Retrieves the grouped commands and parent arguments, builds the parser,
        parses ``argv``, derives the feature id from the command group and key,
        and delegates to the base request parsing to build the request context.

        :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
        :type argv: Optional[List[str]]
        :return: The parsed request context.
        :rtype: RequestContext
        '''

        # Retrieve the grouped commands and the parent-level arguments.
        commands = self.get_commands()
        parent_arguments = self.get_parent_args_evt.execute()

        # Build the parser and parse the provided argv into a namespace dict.
        parser = build_parser(commands, parent_arguments)
        parsed = vars(parser.parse_args(argv))

        # Derive the feature id and headers from the parsed arguments.
        feature_id, headers = derive_feature_request(parsed)

        # Delegate to the base request parsing to build the request context.
        return super().parse_request(
            headers=headers,
            data=parsed,
            feature_id=feature_id,
        )

    # * method: run_cli
    def run_cli(self, argv: Optional[List[str]] = None) -> Any:
        '''
        Parse CLI arguments and dispatch execution through the inherited run.

        Parser failures exit with code 2; a ``TiferetAPIError`` raised during
        execution is printed to stderr and exits with code 1. On success the
        response is printed and returned.

        :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
        :type argv: Optional[List[str]]
        :return: The response from the feature execution.
        :rtype: Any
        '''

        # Parse the CLI request; argparse exits 2 on invalid arguments, and any
        # other parsing failure is reported to stderr and exits with code 2.
        try:
            request = self.parse_cli_request(argv)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(2)

        # Delegate execution to the inherited hub run; convert API errors to exit 1.
        try:
            response = self.run(
                feature_id=request.feature_id,
                headers=request.headers,
                data=request.data,
            )
        except TiferetAPIError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        # Print and return the response.
        print(response)
        return response
