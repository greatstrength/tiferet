"""Tiferet CLI Context"""

# *** imports

# ** core
import sys
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

    Receives an injected ``_parse_cli_args`` closure (built by the CLI
    blueprint) that encapsulates argparse command discovery, parser
    construction, and request derivation.  ``run(argv=None)`` invokes this
    closure, delegates execution to the inherited hub, and handles exit codes.
    ``build_response`` formats and prints the response when the request
    context is a :class:`CliRequestContext`.

    It intentionally omits ``domain_type`` so the ``ContextMeta`` registry
    keeps mapping ``AppSession`` to :class:`AppSessionContext`.
    '''

    # * attribute: _parse_cli_args
    _parse_cli_args: Callable

    # * init
    def __init__(self,
            get_dependency: Callable,
            logging_context = None,
            parse_cli_args: Callable = None,
            cache: CacheContext = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None,
        ):
        '''
        Initialize the CLI session context.

        :param get_dependency: The injected service-resolution handler used to
            resolve feature step events and middleware.
        :type get_dependency: Callable
        :param logging_context: The pre-built logging context for this session.
        :type logging_context: LoggingContext
        :param parse_cli_args: Injected callable that parses ``argv`` and returns
            ``(feature_id, headers, data)``. Built by the CLI blueprint via
            ``parse_cli_args_handler``.
        :type parse_cli_args: Callable
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
        '''

        # Initialize the base application session hub.
        super().__init__(
            logging_context=logging_context,
            get_dependency=get_dependency,
            cache=cache,
            execute_feature_handler=execute_feature_handler,
            create_request_handler=create_request_handler,
            raise_error_handler=raise_error_handler,
            response_handler=response_handler,
        )

        # Store the injected CLI arg-parser callable.
        self._parse_cli_args = parse_cli_args

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

        Parses ``argv`` via the injected ``_parse_cli_args`` closure, then
        delegates to ``super().run(feature_id, headers, data)``.  Argparse
        failures exit with code 2; a ``TiferetAPIError`` exits with code 1.

        :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when
            ``None``.
        :type argv: Optional[List[str]]
        :param kwargs: Not used; present for signature compatibility.
        :type kwargs: dict
        :return: The feature response.
        :rtype: Any
        '''

        # Parse argv via the injected closure.
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


# ** context: cli_context (obsolete)
# -- obsolete: superseded by CliSessionContext; remove at v2.0.0 stable
CliContext = CliSessionContext
