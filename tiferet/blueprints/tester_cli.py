"""Tiferet Tester CLI Blueprint"""

# *** imports

# ** core
from collections.abc import Mapping
from typing import Any, Callable, Dict, List, Optional

# ** app
from .. import a
from . import core
from .cli import create_cli_request_context, parse_cli_args_handler
from .tester import (
    _read_test_module_text,
    _replace_test_module,
    run_test_module,
)
from ..assets.tester_cli import (
    TESTER_CLI_ID,
    TESTER_CLI_SESSIONS,
    TESTER_DEFAULT_COMMANDS,
    TESTER_DEFAULT_FEATURES,
    TESTER_DEFAULT_LOGGING_SETTINGS,
    TESTER_DEFAULT_PARENT_ARGUMENTS,
    TESTER_QUERY_EVENT_REGISTRATIONS,
    TESTER_WRITE_EVENT_REGISTRATIONS,
)
from ..contexts.app import (
    AppSession,
    add_default_app_constants,
    add_default_app_services,
    add_default_app_sessions,
)
from ..contexts.cache import CacheContext
from ..contexts.cli import (
    CliArgument,
    add_default_cli_commands,
    get_default_cli_commands,
)
from ..contexts.error import add_default_errors
from ..contexts.feature import add_default_features
from ..contexts.logging import add_default_logging_settings
from ..contexts.tester_cli import TesterCliSessionContext
from ..contexts.tester_module import TestModuleContext
from ..di.core import ServiceResolver
from ..di.dependency_injector import (
    DIAppServiceContainer,
    DIDynamicServiceResolver,
)

# *** blueprints

# ** blueprint: build_cache
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
@add_default_logging_settings(TESTER_DEFAULT_LOGGING_SETTINGS)
@add_default_app_sessions(TESTER_CLI_SESSIONS)
@add_default_cli_commands(TESTER_DEFAULT_COMMANDS)
@add_default_features(TESTER_DEFAULT_FEATURES)
@add_default_app_services(TESTER_QUERY_EVENT_REGISTRATIONS)
@add_default_app_services(TESTER_WRITE_EVENT_REGISTRATIONS)
@add_default_app_services({
    a.app.DI_SERVICE_ID: a.app.DI_SERVICE_DATA,
})
@add_default_app_constants({
    a.app.DI_CONFIG_ID: 'unused',
})
def build_cache(
        cache: Dict[str, Any] = None,
    ) -> CacheContext:
    '''
    Build a tester CLI cache from the bare core cache.

    Seeds the catalog session, commands, features, and the two registration
    dicts. The DI service pair and the unused DI config constant exist so
    the resolver can be constructed. This cache has no consumer config file.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The cache seeded with the tester catalog.
    :rtype: CacheContext
    '''

    # Delegate to the bare core cache. The decorators seed the catalog.
    return core.build_cache(cache=cache)

# ** blueprint: build_tester_service_resolver
def build_tester_service_resolver(
        app_container: DIAppServiceContainer,
        parse_parameter: Callable = core.parse_parameter,
    ) -> ServiceResolver:
    '''
    Build a feature resolver whose empty-flag container is the app container.

    A catalog step passes no flag. Registering the same container under
    ``app`` and again with no flag lets that step resolve.

    :param app_container: The pre-built app-scoped service container.
    :type app_container: DIAppServiceContainer
    :param parse_parameter: The parameter parser injected into the resolver.
    :type parse_parameter: Callable
    :return: The composed feature-level service resolver.
    :rtype: ServiceResolver
    '''

    # Read the DI service the resolver constructor requires.
    di_service = app_container.get_dependency(a.app.DI_SERVICE_ID)

    # Compose the resolver. Do not build a second container.
    resolver = DIDynamicServiceResolver(
        di_service=di_service,
        parse_parameter=parse_parameter,
    )

    # The app container is also the empty-flag container.
    resolver.add_container(app_container, 'app')
    resolver.add_container(app_container)
    return resolver

# ** blueprint: list_tester_commands
def list_tester_commands(cache: CacheContext) -> List:
    '''
    Return the catalog commands seeded on the cache.

    :param cache: The shared cache context.
    :type cache: CacheContext
    :return: The seeded CLI commands.
    :rtype: List
    '''

    # The catalog is already on the cache. Do not resolve a command event.
    return get_default_cli_commands(cache)

# ** blueprint: catalog_parent_arguments
def catalog_parent_arguments() -> List[CliArgument]:
    '''
    Return the catalog parent argument as CLI argument objects.

    The existing parser merges this list into each command. This entry
    does not build a second parser and does not load the flag from a service.

    :return: The catalog parent arguments.
    :rtype: List[CliArgument]
    '''

    # The catalog list is the only parent argument.
    return [
        CliArgument.model_validate(argument)
        for argument in TESTER_DEFAULT_PARENT_ARGUMENTS
    ]

# ** blueprint: parse_tester_args
def parse_tester_args(cache: CacheContext) -> Callable:
    '''
    Build the tester argv closure from the catalog commands.

    After a successful parse the closure drops the group and command keys.
    The parent argument stays in the parsed data. Address resolution and
    file replacement are context slots, not parse fields.

    :param cache: The shared cache context.
    :type cache: CacheContext
    :return: A closure that returns (feature_id, headers, data).
    :rtype: Callable
    '''

    # List commands from the cache. Parent arguments come from the catalog.
    def commands() -> List:
        return list_tester_commands(cache)

    inner = parse_cli_args_handler(
        list_commands=commands,
        get_parent_args=catalog_parent_arguments,
    )

    # Drop the parse keys. Do not inject context slots into the dict.
    def handler(argv=None):
        feature_id, headers, parsed = inner(argv)
        parsed.pop('group', None)
        parsed.pop('command', None)
        return feature_id, headers, parsed

    return handler

# ** blueprint: build_tester_cli_session_context
def build_tester_cli_session_context(
        app_session: AppSession,
        cache: CacheContext,
    ) -> TesterCliSessionContext:
    '''
    Build a wired tester CLI session context from a resolved app session.

    The context class is passed to composition. This function does not
    call the context constructor.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :return: The wired tester CLI session context.
    :rtype: TesterCliSessionContext
    '''

    # Build the app container and the empty-flag resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = build_tester_service_resolver(app_container)

    # The command handler reads the cache. Parent arguments are the catalog.
    def commands_handler() -> List:
        return list_tester_commands(cache)

    # Compose the context. The class is passed, not called.
    return core.compose_session_context(
        TesterCliSessionContext,
        app_session,
        cache,
        resolver,
        create_request_handler=create_cli_request_context,
        response_handler=core.response_handler,
        parse_cli_args=parse_tester_args(cache),
        list_commands_handler=commands_handler,
        get_parent_args_handler=catalog_parent_arguments,
        run_test_module=run_test_module,
        read_text=_read_test_module_text,
        replace_module=_replace_test_module,
        resolve_address=TestModuleContext._address,
    )

# ** blueprint: build_tester_cli
def build_tester_cli(
        argv: Optional[List[str]] = None,
    ) -> Any:
    '''
    Build the tester CLI session and dispatch argv.

    The session is the cache hit. This entry has no consumer config file
    and does not re-seed session constants. The parent argument is parsed
    with the command, not before it.

    :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
    :type argv: Optional[List[str]]
    :return: The command result.
    :rtype: Any
    '''

    # Build the catalog cache and resolve the seeded session.
    cache = build_cache()
    app_session = core.get_app_session(TESTER_CLI_ID, cache=cache)

    # Compose the context and dispatch argv.
    cli_context = build_tester_cli_session_context(app_session, cache)
    return cli_context.run(argv)

# ** blueprint: main
def main() -> int:
    '''
    Entry point for the ``tiferet-tester`` console script.

    Delegates to :func:`build_tester_cli`. The catalog parent argument is
    parsed with the command.

    :return: The exit status: 1 when the result is a module-run report with a
        non-empty ``failures`` list, otherwise 0.
    :rtype: int
    '''

    # The calculator entry is the shape. Do not build a second parser.
    result = build_tester_cli()

    # A module-run report with failures exits 1.
    failures = result.get('failures') if isinstance(result, Mapping) else None
    if isinstance(failures, list) and failures:
        return 1

    # Every other completed run exits 0.
    return 0

# ** blueprint: tester_cli (alias)
TesterCLI = build_tester_cli
