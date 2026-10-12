"""Tiferet Tester CLI Blueprint"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List, Optional, Tuple

# ** app
from .. import a
from . import core
from .cli import create_cli_request_context, parse_cli_args_handler
from .tester import run_test_module
from ..assets.tester_cli import (
    TESTER_CLI_ID,
    TESTER_CLI_SESSIONS,
    TESTER_DEFAULT_COMMANDS,
    TESTER_DEFAULT_FEATURES,
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

# *** functions

# ** function: parent_argument_spec
def parent_argument_spec(
        arguments: List[Dict[str, Any]],
    ) -> Tuple[List[str], Any, Optional[str]]:
    '''
    Read the one catalog parent argument.

    The list is the catalog. This function does not spell a second flag
    and does not build a parser.

    :param arguments: The catalog parent-argument list.
    :type arguments: List[Dict[str, Any]]
    :return: The item's name_or_flags, default, and description.
    :rtype: Tuple[List[str], Any, Optional[str]]
    '''

    # The catalog list is one item. Read its three fields and return them.
    item = arguments[0]
    return (
        item['name_or_flags'],
        item.get('default'),
        item.get('description'),
    )

# *** blueprints

# ** blueprint: build_cache
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
@add_default_logging_settings(a.logging.CORE_DEFAULT_LOGGING_SETTINGS)
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

# ** blueprint: empty_parent_arguments
def empty_parent_arguments() -> Callable:
    '''
    Return a zero-arg callable that returns no parent arguments.

    The subparser must not define the pre-parsed parent flag a second time.

    :return: A callable that returns an empty list.
    :rtype: Callable
    '''

    # The handler is zero-arg. The subparser receives no parent flags.
    def handler() -> List:
        return []

    return handler

# ** blueprint: parse_tester_args
def parse_tester_args(
        cache: CacheContext,
        base_dir: str,
        replace_module: Callable,
    ) -> Callable:
    '''
    Build the tester argv closure from the catalog commands.

    After a successful parse the closure drops the group and command keys,
    sets the pre-parsed base directory, and passes the address resolver
    through without calling it.

    :param cache: The shared cache context.
    :type cache: CacheContext
    :param base_dir: The pre-parsed base directory.
    :type base_dir: str
    :param replace_module: The injected file-replace callable.
    :type replace_module: Callable
    :return: A closure that returns (feature_id, headers, data).
    :rtype: Callable
    '''

    # List commands from the cache. Parent arguments stay empty.
    def commands() -> List:
        return list_tester_commands(cache)

    inner = parse_cli_args_handler(
        list_commands=commands,
        get_parent_args=empty_parent_arguments(),
    )

    # Return the closure. It sets the address resolver and does not call it.
    def handler(argv=None) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
        feature_id, headers, parsed = inner(argv)
        parsed.pop('group', None)
        parsed.pop('command', None)
        parsed['base_dir'] = base_dir
        parsed['resolve_address'] = TestModuleContext._address
        parsed['replace_module'] = replace_module
        return feature_id, headers, parsed

    return handler

# ** blueprint: build_tester_cli_session_context
def build_tester_cli_session_context(
        app_session: AppSession,
        cache: CacheContext,
        base_dir: str,
    ) -> TesterCliSessionContext:
    '''
    Build a wired tester CLI session context from a resolved app session.

    The context class is passed to composition. This function does not
    call the context constructor.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :param base_dir: The pre-parsed base directory.
    :type base_dir: str
    :return: The wired tester CLI session context.
    :rtype: TesterCliSessionContext
    '''

    # Replace through a sibling temp file. Delete that temp on failure.
    def replace_module(path, text, *, create):
        '''Replace the module with a sibling temp file.'''

        import os
        import tempfile
        from pathlib import Path

        # A missing parent is created only when the file itself is absent.
        target = Path(path)
        created = []
        temp_name = None
        replaced = False
        try:
            if create:
                parent = target.parent
                cursor = parent
                while not cursor.exists():
                    created.append(cursor)
                    cursor = cursor.parent
                parent.mkdir(parents=True, exist_ok=True)

            # Write a sibling temp, then replace. A failure unlinks the temp.
            descriptor, temp_name = tempfile.mkstemp(
                prefix='.test-module-',
                suffix='.yml',
                dir=str(target.parent),
            )
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(text)
            os.replace(temp_name, target)
            replaced = True
            temp_name = None
        finally:
            if temp_name is not None:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
            if not replaced:
                for directory in created:
                    try:
                        directory.rmdir()
                    except OSError:
                        break

    # Build the app container and the empty-flag resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = build_tester_service_resolver(app_container)

    # The command handler reads the cache. Parent arguments stay empty.
    def commands_handler() -> List:
        return list_tester_commands(cache)

    parent_args_handler = empty_parent_arguments()
    parse_cli_args = parse_tester_args(
        cache,
        base_dir,
        replace_module,
    )

    # Compose the context. The class is passed, not called.
    return core.compose_session_context(
        TesterCliSessionContext,
        app_session,
        cache,
        resolver,
        create_request_handler=create_cli_request_context,
        response_handler=core.response_handler,
        parse_cli_args=parse_cli_args,
        list_commands_handler=commands_handler,
        get_parent_args_handler=parent_args_handler,
        run_test_module=run_test_module,
    )

# ** blueprint: build_tester_cli
def build_tester_cli(
        base_dir: str = '.',
        argv: Optional[List[str]] = None,
    ) -> Any:
    '''
    Build the tester CLI session and dispatch argv.

    The session is the cache hit. This entry has no consumer config file
    and does not re-seed session constants.

    :param base_dir: The pre-parsed base directory.
    :type base_dir: str
    :param argv: Optional argument list; defaults to sys.argv[1:] when None.
    :type argv: Optional[List[str]]
    :return: The command result.
    :rtype: Any
    '''

    # Build the catalog cache and resolve the seeded session.
    cache = build_cache()
    app_session = core.get_app_session(TESTER_CLI_ID, cache)

    # Compose the context and dispatch argv.
    cli_context = build_tester_cli_session_context(
        app_session,
        cache,
        base_dir=base_dir,
    )
    return cli_context.run(argv)

# ** blueprint: main
def main() -> None:
    '''
    Entry point for the ``tiferet-tester`` console script.

    Pre-parses the catalog parent argument, strips it from the remaining
    argv, and delegates to :func:`build_tester_cli`.

    :return: None
    :rtype: None
    '''

    import argparse

    # Read the catalog parent spec. Do not spell the flag here.
    flags, default, description = parent_argument_spec(
        TESTER_DEFAULT_PARENT_ARGUMENTS,
    )
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        *flags,
        default=default,
        help=description,
    )
    pre_args, remaining = pre_parser.parse_known_args()

    # The destination is derived from the catalog flag, then stripped.
    dest = flags[0].lstrip('-').replace('-', '_')
    build_tester_cli(
        base_dir=getattr(pre_args, dest),
        argv=remaining,
    )

# ** blueprint: tester_cli (alias)
TesterCLI = build_tester_cli
