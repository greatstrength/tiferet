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
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build a tester CLI cache from the bare core cache.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The cache seeded by the catalog decorators.
    :rtype: CacheContext
    '''

    # Return the bare core cache. The decorators seed the catalog.
    return core.build_cache(cache=cache)

# ** blueprint: build_tester_service_resolver
def build_tester_service_resolver(app_container: DIAppServiceContainer,
        parse_parameter: Callable = core.parse_parameter) -> ServiceResolver:
    '''
    The empty-flag container is the app container, so a catalog step with no flag can resolve.

    :param app_container: The built app service container.
    :type app_container: DIAppServiceContainer
    :param parse_parameter: The parameter parser injected into the resolver.
    :type parse_parameter: Callable
    :return: The resolver whose empty-flag container is the app container.
    :rtype: ServiceResolver
    '''

    # Read the DI service from the app container.
    di_service = app_container.get_dependency(a.app.DI_SERVICE_ID)

    # Construct the resolver. Do not build a second container.
    resolver = DIDynamicServiceResolver(
        di_service=di_service,
        parse_parameter=parse_parameter,
    )

    # Register the app container under the app flag, then under no flag.
    resolver.add_container(app_container, 'app')
    resolver.add_container(app_container)

    # Return that resolver.
    return resolver

# ** blueprint: list_tester_commands
def list_tester_commands(cache: CacheContext) -> List:
    '''
    The catalog commands are already on the cache.

    :param cache: The catalog cache.
    :type cache: CacheContext
    :return: The seeded CLI commands.
    :rtype: List
    '''

    # Return the commands already seeded on the cache.
    return get_default_cli_commands(cache)

# ** blueprint: catalog_parent_arguments
def catalog_parent_arguments() -> List[CliArgument]:
    '''
    The existing parser merges this list; this entry does not build a second parser.

    :return: The catalog parent arguments, in catalog order.
    :rtype: List[CliArgument]
    '''

    # Validate each catalog item. Do not spell the flag in this module.
    return [
        CliArgument.model_validate(argument)
        for argument in TESTER_DEFAULT_PARENT_ARGUMENTS
    ]

# ** blueprint: parse_tester_args
def parse_tester_args(cache: CacheContext) -> Callable:
    '''
    Address resolution and file replacement are context slots, not parse fields.

    :param cache: The catalog cache whose commands the parser reads.
    :type cache: CacheContext
    :return: A closure that returns a feature id, headers, and parsed data.
    :rtype: Callable
    '''

    # Read catalog commands from the cache when the parser asks.
    def commands() -> List:
        return list_tester_commands(cache)

    # Build the existing parser handler. This entry does not build a second parser.
    handler = parse_cli_args_handler(
        list_commands=commands,
        get_parent_args=catalog_parent_arguments,
    )

    # Drop routing keys. Leave address resolution and file replacement off the dict.
    def parse(argv: Optional[List[str]] = None):
        feature_id, headers, parsed = handler(argv)
        parsed.pop('group', None)
        parsed.pop('command', None)
        return feature_id, headers, parsed

    # Return the closure.
    return parse

# ** blueprint: build_tester_cli_session_context
def build_tester_cli_session_context(app_session: AppSession,
        cache: CacheContext) -> TesterCliSessionContext:
    '''
    The context class is passed to composition.

    :param app_session: The seeded tester CLI session.
    :type app_session: AppSession
    :param cache: The catalog cache.
    :type cache: CacheContext
    :return: The composed tester CLI session context.
    :rtype: TesterCliSessionContext
    '''

    # Build the app container, then the empty-flag resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = build_tester_service_resolver(app_container)

    # List catalog commands without resolving a command event.
    def list_commands_handler() -> List:
        return list_tester_commands(cache)

    # Pass the context class to composition. Do not call the constructor.
    return core.compose_session_context(
        TesterCliSessionContext,
        app_session,
        cache,
        resolver,
        create_request_handler=create_cli_request_context,
        response_handler=core.response_handler,
        parse_cli_args=parse_tester_args(cache),
        list_commands_handler=list_commands_handler,
        get_parent_args_handler=catalog_parent_arguments,
        run_test_module=run_test_module,
        read_text=_read_test_module_text,
        replace_module=_replace_test_module,
        resolve_address=TestModuleContext._address,
    )

# ** blueprint: build_tester_cli
def build_tester_cli(argv: Optional[List[str]] = None) -> Any:
    '''
    The session is the cache hit; the parent argument is parsed with the command.

    :param argv: The argument list; defaults to sys.argv[1:] when None.
    :type argv: Optional[List[str]]
    :return: The module-run outcome or the feature response.
    :rtype: Any
    '''

    # Build the catalog cache. No consumer config file is read.
    cache = build_cache()

    # Resolve the seeded session. Do not re-seed session constants.
    app_session = core.get_app_session(
        TESTER_CLI_ID,
        cache=cache,
    )

    # Compose the session and dispatch argv.
    cli_context = build_tester_cli_session_context(app_session, cache)
    return cli_context.run(argv)

# ** blueprint: main
def main() -> int:
    '''
    Entry point for the ``tiferet-tester`` console script.

    :return: The exit status: 1 when the result is a module-run report with a
        non-empty ``failures`` list, otherwise 0.
    :rtype: int
    '''

    # Dispatch with no arguments. Do not pre-parse a config path.
    result = build_tester_cli()

    # A module-run report with failures exits 1.
    failures = result.get('failures') if isinstance(result, Mapping) else None
    if isinstance(failures, list) and failures:
        return 1

    # Every other completed run exits 0.
    return 0

# ** blueprint: tester_cli (alias)
TesterCLI = build_tester_cli
