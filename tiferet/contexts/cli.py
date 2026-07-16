"""Tiferet CLI Context"""

# *** imports

# ** core
import sys
import argparse
from typing import Any, Callable, Dict, List, Optional, Tuple

# ** app
from ..assets import TiferetAPIError
from ..domain import (
    DomainObject,
    CliArgument,
    CliCommand,
    CliRecord,
    CliOutputRecord,
    CliRecordList,
)
from ..events import DomainEvent
from .app import AppSessionContext
from .cache import CacheContext
from .request import RequestContext

# *** constants

# ** constant: cli_command_cache_prefix
CLI_COMMAND_CACHE_PREFIX: Tuple[str, ...] = ('cli', 'commands')

# *** functions

# ** function: add_default_cli_commands
def add_default_cli_commands(commands: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default CLI command
    domain objects.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each entry in ``commands`` is reconstituted into a ``CliCommand`` domain
    object (with its id re-injected) and stored in the cache under the
    ``CLI_COMMAND_CACHE_PREFIX`` namespace keyed by command id.

    Mirrors ``add_default_errors`` / ``add_default_app_services``.

    :param commands: An id-keyed mapping of command records (each value is the
        record without its id).
    :type commands: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default command domain objects.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw command dict into a CliCommand domain object
            # (re-injecting the id) and cache it under the commands namespace.
            for command_id, command_data in commands.items():
                cache.set(
                    command_id,
                    CliCommand.model_validate({**command_data, 'id': command_id}),
                    *CLI_COMMAND_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator


# ** function: get_default_cli_commands
def get_default_cli_commands(cache: CacheContext) -> List[CliCommand]:
    '''
    Return the default CLI command domain objects seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The default CLI command domain objects.
    :rtype: List[CliCommand]
    '''

    # Pull all entries from the CLI commands namespace and return their values.
    return list(cache.get_by_prefix(*CLI_COMMAND_CACHE_PREFIX).values())


# ** function: build_cli_record
def build_cli_record(result: Any) -> CliRecord:
    '''
    Build a :class:`CliRecord` by extracting fields from a raw domain result.

    Handles three shapes:

    * ``DomainObject`` — serialised via ``model_dump()``, ``None`` values
      omitted, all remaining values coerced to ``str``.
    * ``dict`` — iterated directly, each value coerced to ``str``.
    * Any other value — wrapped as ``{"value": str(result)}``.

    This factory lives in the context layer rather than on the domain object so
    that ``CliRecord`` remains a pure data structure with no knowledge of how
    results are produced by domain events.

    :param result: The raw result produced by a domain event.
    :type result: Any
    :return: A CliRecord populated from the result.
    :rtype: CliRecord
    '''

    # Serialise DomainObject instances via model_dump, omitting None values.
    if isinstance(result, DomainObject):
        fields = {
            k: str(v)
            for k, v in result.model_dump().items()
            if v is not None
        }

    # Iterate dict items directly, coercing each value to str.
    elif isinstance(result, dict):
        fields = {k: str(v) for k, v in result.items()}

    # Wrap primitives as a single-field record keyed by "value".
    else:
        fields = {'value': str(result)}

    # Construct and return the record.
    return CliRecord(fields=fields)


# *** contexts

# ** context: cli_request_context
class CliRequestContext(RequestContext):
    '''
    A CLI-specific request context that converts raw feature results into typed
    CLI output models on ``handle_response``.

    Does not declare ``domain_type`` so it is not registered in ``ContextMeta``
    and does not shadow the base ``RequestContext``. It is constructed
    directly by the CLI blueprint via ``create_cli_request_context``.
    '''

    # * method: handle_response
    def handle_response(self) -> Any:
        '''
        Convert the raw result into a typed CLI output model.

        A list result becomes a :class:`CliRecordList`; a dict or
        ``DomainObject`` result becomes a :class:`CliOutputRecord`; any other
        value passes through unchanged so the caller can print it directly.

        :return: A ``CliRecordList``, ``CliOutputRecord``, or the raw primitive.
        :rtype: Any
        '''

        # Retrieve the raw result from the request context.
        result = self.result

        # Convert a list to a CliRecordList by mapping each item to a CliRecord.
        if isinstance(result, list):
            records = [build_cli_record(item) for item in result]
            return CliRecordList(records=records)

        # Convert a single dict or DomainObject to a CliOutputRecord.
        elif isinstance(result, (dict, DomainObject)):
            cli_record = build_cli_record(result)
            return CliOutputRecord(record=cli_record)

        # Pass through primitives unchanged.
        else:
            return result


# ** context: cli_session_context
class CliSessionContext(AppSessionContext):
    '''
    The CLI session context extends the application session hub with
    command-line concerns.

    In the new (Phase 1) path the context receives an injected
    ``_parse_cli_args`` closure (built by the blueprint) that encapsulates
    argparse command discovery, parser construction, and request derivation.
    ``run(argv=None)`` invokes this closure, delegates execution to the
    inherited hub, and handles exit codes. ``build_response`` formats and
    prints the response when the request context is a
    :class:`CliRequestContext`.

    The legacy ``parse_cli_request`` / ``run_cli`` / event-collaborator
    path is kept functional (annotated ``# -- obsolete``) so
    ``build_tiferet_cli`` continues to work until it migrates to the core
    compose path in a subsequent phase.

    It intentionally omits ``domain_type`` so the ``ContextMeta`` registry
    keeps mapping ``AppSession`` to :class:`AppSessionContext`.
    '''

    # * attribute: _parse_cli_args
    _parse_cli_args: Callable

    # * attribute: list_commands_evt (obsolete)
    # -- obsolete: superseded by the injected _parse_cli_args closure; remove when
    #    build_tiferet_cli migrates to build_cli_session_context
    # ++ todo: remove when build_tiferet_cli migrates to the core compose path
    list_commands_evt: DomainEvent

    # * attribute: get_parent_args_evt (obsolete)
    # -- obsolete: superseded by the injected _parse_cli_args closure; remove when
    #    build_tiferet_cli migrates to build_cli_session_context
    # ++ todo: remove when build_tiferet_cli migrates to the core compose path
    get_parent_args_evt: DomainEvent

    # * init
    def __init__(self,
            logging_list_all_evt: DomainEvent,
            get_dependency: Callable,
            parse_cli_args: Callable = None,
            list_commands_evt: DomainEvent = None,
            get_parent_args_evt: DomainEvent = None,
            cache: CacheContext = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None,
            default_features: Dict[str, Dict[str, Any]] = None,
            default_commands: Dict[str, Dict[str, Any]] = None,
            get_feature_evt: DomainEvent = None,
            get_error_evt: DomainEvent = None,
        ):
        '''
        Initialize the CLI session context.

        :param logging_list_all_evt: The event used to list logging configurations.
        :type logging_list_all_evt: DomainEvent
        :param get_dependency: The injected service-resolution handler used to
            resolve feature step events and middleware.
        :type get_dependency: Callable
        :param parse_cli_args: Injected callable that parses ``argv`` and returns
            ``(feature_id, headers, data)``. Built by the CLI blueprint via
            ``parse_cli_args_handler``; when ``None`` the legacy event path
            applies.
        :type parse_cli_args: Callable
        :param list_commands_evt: Obsolete — command retrieval is now handled by the
            injected ``parse_cli_args`` closure; kept for ``build_tiferet_cli`` compat.
        :type list_commands_evt: DomainEvent
        :param get_parent_args_evt: Obsolete — parent argument retrieval is now handled
            by the injected ``parse_cli_args`` closure; kept for compat.
        :type get_parent_args_evt: DomainEvent
        :param cache: The shared cache context for all sub-contexts.
        :type cache: CacheContext
        :param execute_feature_handler: The feature-execution callable (FE4).
        :type execute_feature_handler: Callable
        :param create_request_handler: The request-creation callable (FE4).
        :type create_request_handler: Callable
        :param raise_error_handler: The error-raising callable (FE4).
        :type raise_error_handler: Callable
        :param response_handler: The response-extraction callable (FE4).
        :type response_handler: Callable
        :param default_features: Optional id-keyed feature records for bootstrap fallback.
        :type default_features: Dict[str, Dict[str, Any]]
        :param default_commands: Optional id-keyed CLI command records for bootstrap fallback.
        :type default_commands: Dict[str, Dict[str, Any]]
        :param get_feature_evt: Obsolete — superseded by execute_feature_handler.
        :type get_feature_evt: DomainEvent
        :param get_error_evt: Obsolete — superseded by raise_error_handler.
        :type get_error_evt: DomainEvent
        '''

        # Initialize the base application session hub.
        super().__init__(
            get_feature_evt=get_feature_evt,
            get_error_evt=get_error_evt,
            logging_list_all_evt=logging_list_all_evt,
            get_dependency=get_dependency,
            cache=cache,
            execute_feature_handler=execute_feature_handler,
            create_request_handler=create_request_handler,
            raise_error_handler=raise_error_handler,
            response_handler=response_handler,
            default_features=default_features,
            default_commands=default_commands,
        )

        # Store the new injected CLI arg-parser callable.
        self._parse_cli_args = parse_cli_args

        # Store the legacy CLI event collaborators (kept for build_tiferet_cli compat).
        self.list_commands_evt = list_commands_evt
        self.get_parent_args_evt = get_parent_args_evt

    # * method: build_response
    def build_response(self, request: RequestContext) -> Any:
        '''
        Build and (when appropriate) print the CLI response.

        Delegates to the injected ``_build_response`` handler when one is
        wired in, otherwise falls back to ``request.handle_response()``
        directly. The formatted or stringified result is printed only when the
        request is a :class:`CliRequestContext` (new path); the legacy path
        leaves printing to the caller (e.g. ``build_tiferet_cli``).

        :param request: The completed request context.
        :type request: RequestContext
        :return: The handled feature response.
        :rtype: Any
        '''

        # Use the injected handler when available, otherwise fall through.
        if self._build_response is not None:
            model = self._build_response(request)
        else:
            model = request.handle_response()

        # Only print when using the CLI request context (new path).
        if isinstance(request, CliRequestContext):
            if hasattr(model, 'format_output'):
                print(model.format_output())
            elif model is not None:
                print(str(model))

        # Return the model (formatted or raw).
        return model

    # * method: run
    def run(self, argv=None, **kwargs) -> Any:
        '''
        Parse CLI arguments and dispatch execution through the inherited run.

        **New path** (when ``_parse_cli_args`` is injected): parses ``argv``
        via the closure, then delegates to ``super().run(feature_id, headers,
        data)``.  Argparse failures exit with code 2; a ``TiferetAPIError``
        exits with code 1.

        **Legacy compatibility path** (when called with ``feature_id`` in
        ``kwargs`` or when ``_parse_cli_args`` is not wired in): delegates
        directly to the parent ``run``, preserving the existing
        ``build_tiferet_cli`` call convention.

        :param argv: Optional argument list for the new path; defaults to
            ``sys.argv[1:]`` when ``None``.  Unused on the legacy path.
        :type argv: Optional[List[str]]
        :param kwargs: Forwarded to ``super().run()`` on the legacy path.
        :type kwargs: dict
        :return: The feature response.
        :rtype: Any
        '''

        # Legacy compatibility path: delegate to parent when feature_id is
        # provided as a keyword argument, or when no CLI arg parser is wired in.
        # -- obsolete: remove this branch when build_tiferet_cli migrates to the
        #    new run(argv) interface
        if 'feature_id' in kwargs or self._parse_cli_args is None:
            return super().run(**({'feature_id': argv, **kwargs} if 'feature_id' not in kwargs and argv is not None else kwargs))

        # New CLI path: parse argv via the injected closure.
        try:
            feature_id, headers, data = self._parse_cli_args(argv)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(2)

        # Dispatch the feature and exit on a TiferetAPIError.
        try:
            return super().run(feature_id, headers=headers, data=data)
        except TiferetAPIError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    # * method: get_commands (obsolete)
    # -- obsolete: superseded by the injected _parse_cli_args closure; remove when
    #    build_tiferet_cli migrates to build_cli_session_context
    # ++ todo: remove when build_tiferet_cli migrates to the core compose path
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
        return _group_commands_by_key_legacy(cli_commands)

    # * method: parse_cli_request (obsolete)
    # -- obsolete: superseded by run(argv=None); remove when build_tiferet_cli
    #    migrates to build_cli_session_context
    # ++ todo: remove when build_tiferet_cli migrates to the core compose path
    def parse_cli_request(self, argv: Optional[List[str]] = None) -> RequestContext:
        '''
        Parse CLI arguments into a request context.

        :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
        :type argv: Optional[List[str]]
        :return: The parsed request context.
        :rtype: RequestContext
        '''

        # Retrieve the grouped commands and the parent-level arguments.
        commands = self.get_commands()
        parent_arguments = self.get_parent_args_evt.execute()

        # Build the parser and parse the provided argv into a namespace dict.
        parser = _build_parser_legacy(commands, parent_arguments)
        parsed = vars(parser.parse_args(argv))

        # Derive the feature id and headers from the parsed arguments.
        feature_id, headers = _derive_feature_request_legacy(parsed)

        # Delegate to the base request parsing to build the request context.
        return super().parse_request(
            headers=headers,
            data=parsed,
            feature_id=feature_id,
        )

    # * method: run_cli (obsolete)
    # -- obsolete: superseded by run(argv=None); remove when build_tiferet_cli
    #    migrates to build_cli_session_context
    # ++ todo: remove when build_tiferet_cli migrates to the core compose path
    def run_cli(self, argv: Optional[List[str]] = None) -> Any:
        '''
        Parse CLI arguments and dispatch execution through the inherited run.

        :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
        :type argv: Optional[List[str]]
        :return: The response from the feature execution.
        :rtype: Any
        '''

        # Parse the CLI request; argparse exits 2 on invalid arguments.
        try:
            request = self.parse_cli_request(argv)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(2)

        # Delegate execution through the run template method; convert API errors to exit 1.
        # Uses self.run so callers that patch run (e.g. tests) can intercept the call.
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


# ** context: cli_context (obsolete)
# -- obsolete: superseded by CliSessionContext; remove at v2.0.0 stable
CliContext = CliSessionContext


# *** functions (legacy helpers)
# -- obsolete: these module-level parsing helpers moved to blueprints/cli.py;
#    kept here only to support the obsolete parse_cli_request method above.
# ++ todo: remove with parse_cli_request when build_tiferet_cli migrates

# ** function: _group_commands_by_key_legacy
def _group_commands_by_key_legacy(cli_commands: List[CliCommand]) -> Dict[str, List[CliCommand]]:
    '''Legacy shim — group CLI commands by their group key.'''
    command_map: Dict[str, List[CliCommand]] = {}
    for command in cli_commands:
        command_map.setdefault(command.group_key, []).append(command)
    return command_map


# ** function: _build_parser_legacy
def _build_parser_legacy(
        commands: Dict[str, List[CliCommand]],
        parent_arguments: List[CliArgument],
    ) -> argparse.ArgumentParser:
    '''Legacy shim — build an argparse parser from grouped CLI commands.'''
    parser = argparse.ArgumentParser()
    group_subparsers = parser.add_subparsers(dest='group')
    for group_key in commands:
        group_subparser = group_subparsers.add_parser(
            group_key,
            help=f'Commands for the {group_key} group.',
        )
        cmd_subparsers = group_subparser.add_subparsers(dest='command')
        for cli_command in commands[group_key]:
            cli_command_parser = cmd_subparsers.add_parser(
                cli_command.key,
                help=cli_command.description,
            )
            for argument in cli_command.arguments:
                cli_command_parser.add_argument(
                    *argument.name_or_flags,
                    **argument.to_argparse_kwargs(),
                )
            for argument in parent_arguments:
                if not cli_command.has_argument(argument.name_or_flags):
                    cli_command_parser.add_argument(
                        *argument.name_or_flags,
                        **argument.to_argparse_kwargs(),
                    )
    return parser


# ** function: _derive_feature_request_legacy
def _derive_feature_request_legacy(parsed: Dict[str, Any]) -> Tuple[str, Dict[str, str]]:
    '''Legacy shim — derive feature id and headers from parsed CLI arguments.'''
    group = parsed.get('group')
    command = parsed.get('command')
    feature_id = '{}.{}'.format(
        group.replace('-', '_'),
        command.replace('-', '_'),
    )
    headers = dict(command_group=group, command_key=command)
    return feature_id, headers
