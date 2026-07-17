"""Tiferet CLI Blueprints"""

# *** imports

# ** core
import argparse
from typing import Any, Callable, Dict, List, Optional, Tuple

# ** app
from .. import assets as a
from . import core
from ..contexts.cli import (
    CliArgument,
    CliCommand,
    CliRecord,
    CliOutputRecord,
    CliRecordList,
    CliRequestContext,
    CliSessionContext,
    add_default_cli_commands,
    get_default_cli_commands,
    CLI_COMMAND_CACHE_PREFIX,
)
from ..contexts.cache import CacheContext
from ..contexts.request import RequestContext
from ..di import injectable_parameter_names

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


# ** function: build_argument_parser
def build_argument_parser(
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

            # Add parent arguments that do not collide with command arguments.
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

    The feature id normalises hyphens to underscores; the headers retain the
    raw group and command values.

    :param parsed: The parsed argument namespace as a dictionary.
    :type parsed: Dict[str, Any]
    :return: A tuple of (feature_id, headers).
    :rtype: Tuple[str, Dict[str, str]]
    '''

    # Extract the group and command from the parsed arguments.
    group = parsed.get('group')
    command = parsed.get('command')

    # Derive the feature id by normalising hyphens to underscores.
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


# *** blueprints

# ** blueprint: build_cli_cache
@add_default_cli_commands(a.cli.ADMIN_DEFAULT_COMMANDS)
def build_cli_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build a cache context seeded with the framework defaults plus the
    built-in Tiferet CLI command catalog.

    Extends :func:`core.build_cache` by stacking
    :func:`add_default_cli_commands` on top so the CLI command defaults are
    available alongside the standard error, service, and constant defaults.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized cache context seeded with all framework defaults
        and the built-in CLI commands.
    :rtype: CacheContext
    '''

    # Delegate to the core cache builder; the decorator stacks CLI commands on top.
    return core.build_cache(cache)


# ** blueprint: parse_cli_args_handler
def parse_cli_args_handler(
        list_commands_evt,
        get_parent_args_evt,
        default_commands_list: List[CliCommand] = None,
    ) -> Callable:
    '''
    Build a CLI arg-parser closure from the resolved event collaborators and
    the bootstrap default command list.

    Returns a callable ``handler(argv=None) -> (feature_id, headers, data)``
    that retrieves commands from ``list_commands_evt`` (falling back to
    ``default_commands_list``), builds the argparse parser, parses ``argv``,
    and derives the feature request tuple.

    :param list_commands_evt: The event used to list CLI commands.
    :param get_parent_args_evt: The event used to retrieve parent-level CLI arguments.
    :param default_commands_list: Bootstrap default commands used when the
        repository returns no results.
    :type default_commands_list: List[CliCommand] | None
    :return: A closure that parses argv and returns (feature_id, headers, data).
    :rtype: Callable
    '''

    # Return the handler closure with events and defaults captured.
    def handler(argv=None) -> Tuple[str, Dict[str, str], Dict[str, Any]]:

        # Retrieve commands from the event, falling back to bootstrap defaults.
        cli_commands = list_commands_evt.execute() or default_commands_list or []

        # Group the commands by their group key.
        commands = group_commands_by_key(cli_commands)

        # Retrieve the parent-level arguments.
        parent_arguments = get_parent_args_evt.execute() or []

        # Build the argument parser from the grouped commands and parent arguments.
        parser = build_argument_parser(commands, parent_arguments)

        # Parse argv into a namespace dict.
        parsed = vars(parser.parse_args(argv))

        # Derive the feature id and headers from the parsed dict.
        feature_id, headers = derive_feature_request(parsed)

        # Return the feature request tuple.
        return feature_id, headers, parsed

    return handler


# ** blueprint: create_cli_request_context
def create_cli_request_context(
    interface_id: str,
    feature_id: str,
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None,
) -> CliRequestContext:
    '''
    Compose a CLI request context for a feature execution.

    Mirrors :func:`core.create_session_request` but constructs a
    :class:`CliRequestContext` so ``handle_response`` converts results into
    typed CLI output models.

    :param interface_id: The interface id injected into the request headers.
    :type interface_id: str
    :param feature_id: The feature id seeded on the request context.
    :type feature_id: str
    :param headers: Optional request headers merged with the interface id.
    :type headers: Dict[str, str] | None
    :param data: Optional request data payload.
    :type data: Dict[str, Any] | None
    :return: The composed CLI request context.
    :rtype: CliRequestContext
    '''

    # Compose and return the CLI request context, enriching headers with the interface id.
    return CliRequestContext(
        headers={**(headers or {}), 'interface_id': interface_id},
        data=data,
        feature_id=feature_id,
    )


# ** blueprint: cli_response_handler
def cli_response_handler(request: RequestContext) -> Any:
    '''
    Extract the handled response from a completed CLI request context.

    Delegates to ``request.handle_response()``. For a
    :class:`CliRequestContext` this converts the raw result into a typed CLI
    output model; :class:`CliSessionContext.build_response` then formats and
    prints it.

    :param request: The completed request context.
    :type request: RequestContext
    :return: The handled feature response.
    :rtype: Any
    '''

    # Delegate to the request context's response handler.
    return request.handle_response()


# ** blueprint: build_cli_session_context
def build_cli_session_context(
    app_session,
    cache: CacheContext,
) -> CliSessionContext:
    '''
    Build a fully wired CLI session context from a resolved app session.

    Parallel to :func:`core.build_app_session_context` but dedicated to the
    CLI path: uses :class:`CliSessionContext` directly (blueprint-level context
    class selection), resolves the CLI event collaborators to build the
    injected ``_parse_cli_args`` closure, and overrides the
    ``create_request_handler`` and ``response_handler`` FE4 slots with
    CLI-specific implementations.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context (seeded with CLI commands
        in addition to the standard framework defaults).
    :type cache: CacheContext
    :return: The wired CLI session context.
    :rtype: CliSessionContext
    '''

    # Build the app service container from defaults and interface overrides.
    app_container = core.build_app_service_container(cache, app_session)

    # Build the feature-level resolver from the app container.
    resolver = core.build_service_resolver(app_container)

    # Resolve the CLI event collaborators from the app container.
    list_commands_evt = app_container.get_dependency('list_commands_evt')
    get_parent_args_evt = app_container.get_dependency('get_parent_args_evt')

    # Build the _parse_cli_args closure from the resolved events and defaults.
    parse_cli_args = parse_cli_args_handler(
        list_commands_evt,
        get_parent_args_evt,
        get_default_cli_commands(cache),
    )

    # Resolve the context's other collaborators from the app container by id,
    # skipping the explicitly supplied handler params, resolver, cache, and
    # the CLI arg-parser (injected separately below).
    reserved = {
        'get_dependency',
        'cache',
        'execute_feature_handler',
        'create_request_handler',
        'raise_error_handler',
        'response_handler',
        'parse_cli_args',
    }
    collaborators = {
        name: app_container.get_dependency(name)
        for name in injectable_parameter_names(CliSessionContext)
        if name not in reserved
        and not name.startswith('default_')
        and app_container.has_dependency(name)
    }

    # Build the four FE4 handlers, overriding the request and response slots
    # with CLI-specific implementations.
    handlers = dict(
        execute_feature_handler=core.execute_feature_handler(resolver.get_dependency, cache),
        create_request_handler=create_cli_request_context,
        raise_error_handler=core.raise_error_handler(core.get_error(cache, resolver.get_dependency)),
        response_handler=cli_response_handler,
    )

    # Construct and return the CLI session context via from_domain.
    return CliSessionContext.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        parse_cli_args=parse_cli_args,
        **handlers,
        **collaborators,
    )


# ** blueprint: build_app
def build_app(
    interface_id: str,
    argv: Optional[List[str]] = None,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters
) -> Any:
    '''
    Build the CLI session context and dispatch argv through its CLI pipeline.

    Orchestrates the CLI composition chain in fixed order: builds the shared
    cache seeded with CLI commands (via :func:`build_cli_cache`), resolves the
    app session, composes the wired :class:`CliSessionContext` via
    :func:`build_cli_session_context`, and delegates argument parsing, feature
    dispatch, exit-code handling, and response formatting/printing to
    :meth:`CliSessionContext.run`.

    :param interface_id: The CLI interface identifier.
    :type interface_id: str
    :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
    :type argv: Optional[List[str]]
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Additional parameters passed to the app service constructor.
    :type parameters: dict
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Build the CLI cache (seeded with errors, services, constants, and CLI commands).
    cache = build_cli_cache()

    # Resolve the app session.
    app_session = core.get_app_session(interface_id, cache, module_path, class_name, **parameters)

    # Compose the wired CLI session context.
    cli_context = build_cli_session_context(app_session, cache)

    # Dispatch argv through the CLI session context.
    return cli_context.run(argv)
