"""Tiferet Admin CLI Blueprint — Built-in CLI Management Interface"""

# *** imports

# ** core
import argparse
from typing import Any, Dict, List, Optional

# ** app
from .. import assets as a
from . import admin, core
from .cli import (
    parse_cli_args_handler,
    create_cli_request_context,
    cli_response_handler,
)
from ..contexts.app import AppSession
from ..contexts.cache import CacheContext
from ..contexts.cli import (
    CliSessionContext,
    add_default_cli_commands,
    get_default_cli_commands,
)

# *** blueprints

# ** blueprint: build_cache
@add_default_cli_commands(a.cli.ADMIN_DEFAULT_COMMANDS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the admin CLI bootstrap cache.

    Layers the admin CLI command catalog on top of the full admin catalog
    already seeded by ``admin.build_cache`` (errors, admin services, admin
    constants, and admin features).

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The pre-seeded admin CLI cache context.
    :rtype: CacheContext
    '''

    # Delegate to the admin cache builder; the decorator stacks CLI commands.
    return admin.build_cache(cache=cache)

# ** blueprint: build_admin_cli_session_context
def build_admin_cli_session_context(app_session: AppSession,
        cache: CacheContext) -> CliSessionContext:
    '''
    Compose a fully wired admin CLI session context from a loaded app session.

    Parallel to ``cli.build_cli_session_context`` but uses
    ``admin.build_admin_service_resolver`` so feature steps resolve from the
    admin container by default.

    :param app_session: The loaded app session domain object.
    :type app_session: AppSession
    :param cache: The admin CLI bootstrap cache.
    :type cache: CacheContext
    :return: The fully wired admin CLI session context.
    :rtype: CliSessionContext
    '''

    # Build the app service container and compose the admin service resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = admin.build_admin_service_resolver(app_container, cache)

    # Resolve the CLI event collaborators from the app container.
    list_commands_evt = app_container.get_dependency('list_commands_evt')
    get_parent_args_evt = app_container.get_dependency('get_parent_args_evt')

    # Build the standard arg-parsing closure from events and cache defaults.
    parse_cli_args = parse_cli_args_handler(
        list_commands_evt,
        get_parent_args_evt,
        get_default_cli_commands(cache),
    )

    # Delegate handler wiring, collaborator resolution, and construction.
    return core.compose_session_context(
        CliSessionContext,
        app_session,
        cache,
        app_container,
        resolver,
        create_request_handler=create_cli_request_context,
        response_handler=cli_response_handler,
        parse_cli_args=parse_cli_args,
    )

# ** blueprint: build_admin_cli
def build_admin_cli(app_config: str, argv: Optional[List[str]] = None) -> Any:
    '''
    Build the admin CLI session context and dispatch argv through it.

    Resolves the built-in ``admin_cli`` session from the cache-seeded defaults,
    re-seeds session constants so every config-file repository points at the
    consumer-supplied config path, then dispatches through ``CliSessionContext.run``.

    :param app_config: Path to the consumer configuration file.
    :type app_config: str
    :param argv: The argument list; defaults to sys.argv[1:] when None.
    :type argv: Optional[List[str]]
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Build the admin CLI bootstrap cache.
    cache = build_cache()

    # Resolve the built-in admin CLI session; no consumer config entry required.
    app_session = core.get_app_session(
        a.app.TIFERET_ADMIN_CLI_ID,
        cache,
        app_config=app_config,
    )

    # Re-seed session constants so every config-file repository uses app_config.
    session_constants = {
        **(app_session.constants or {}),
        'app_config': app_config,
        'cli_config': app_config,
        'di_config': app_config,
        'error_config': app_config,
        'feature_config': app_config,
        'logging_config': app_config,
    }
    app_session.constants = session_constants

    # Compose the wired admin CLI session context.
    cli_context = build_admin_cli_session_context(app_session, cache)

    # Dispatch argv through the CLI session context.
    return cli_context.run(argv)

# ** blueprint: main
def main() -> None:
    '''
    Console entry point for the ``tiferet`` admin CLI script.

    Uses a pre-parser with ``add_help=False`` so ``--config`` is extracted
    without consuming the remaining argv meant for the full command parser,
    and so ``--help``/``-h`` is handled by the full parser inside
    ``build_admin_cli``.
    '''

    # Pre-parse --config without consuming remaining argv or help flags.
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument('--config', default='config.yml')
    pre_args, remaining = pre_parser.parse_known_args()

    # Delegate to the admin CLI blueprint with the resolved config path.
    build_admin_cli(app_config=pre_args.config, argv=remaining)

# ** blueprint: admin_cli (alias)
AdminCLI = build_admin_cli
