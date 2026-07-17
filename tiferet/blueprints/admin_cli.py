"""Tiferet Admin CLI Blueprint — Built-in CLI Management Interface"""

# *** imports

# ** core
import json
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

# ** app
from .. import assets as a
from . import core
from . import admin
from .cli import (
    parse_cli_args_handler,
    create_cli_request_context,
    cli_response_handler,
)
from ..contexts.app import (
    AppSession,
    AppSessionContext,
)
from ..contexts.cache import CacheContext
from ..contexts.cli import (
    CliSessionContext,
    add_default_cli_commands,
    get_default_cli_commands,
)
from ..di import injectable_parameter_names

# *** functions

# ** function: _decode_json_arguments
def _decode_json_arguments(parsed: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Decode JSON-valued CLI arguments in place.

    Complex arguments (``parameters``, ``constants``, ``services``, and
    ``flagged_dependencies``) arrive from argparse as raw strings.  This helper
    parses each present string value with ``json.loads`` so domain events
    receive structured data.  Malformed JSON results in a controlled CLI exit
    rather than an unhandled traceback.

    :param parsed: The parsed argument namespace as a dictionary.
    :type parsed: Dict[str, Any]
    :return: The parsed dictionary with JSON-valued arguments decoded.
    :rtype: Dict[str, Any]
    '''

    # The complex argument keys whose string values carry JSON payloads.
    json_keys = ('parameters', 'constants', 'services', 'flagged_dependencies')

    # Decode each present string value, failing cleanly on malformed JSON.
    for key in json_keys:
        value = parsed.get(key)
        if isinstance(value, str):
            try:
                parsed[key] = json.loads(value)
            except json.JSONDecodeError as e:
                print(
                    f"Invalid JSON for argument '--{key.replace('_', '-')}': {e}",
                    file=sys.stderr,
                )
                sys.exit(2)

    # Return the parsed dictionary with decoded values.
    return parsed


# ** function: _admin_parse_cli_args_handler
def _admin_parse_cli_args_handler(
        list_commands_evt,
        get_parent_args_evt,
        default_commands_list=None,
    ) -> Callable:
    '''
    Build a CLI arg-parser closure that includes JSON decoding for admin arguments.

    Wraps the standard :func:`parse_cli_args_handler` and post-processes the
    parsed data dict through :func:`_decode_json_arguments` so complex admin CLI
    arguments (``--parameters``, ``--constants``, etc.) are decoded from raw
    JSON strings into structured Python objects before feature dispatch.

    :param list_commands_evt: The event used to list CLI commands.
    :param get_parent_args_evt: The event used to retrieve parent-level CLI arguments.
    :param default_commands_list: Bootstrap default commands used when the
        repository returns no results.
    :type default_commands_list: List | None
    :return: A closure that parses argv and returns (feature_id, headers, data)
        with JSON-valued arguments decoded.
    :rtype: Callable
    '''

    # Build the standard parse handler and wrap it with JSON decoding.
    base_handler = parse_cli_args_handler(
        list_commands_evt,
        get_parent_args_evt,
        default_commands_list,
    )

    # Return the wrapping handler closure.
    def handler(argv=None) -> Tuple[str, Dict[str, str], Dict[str, Any]]:

        # Delegate to the standard handler to parse argv.
        feature_id, headers, data = base_handler(argv)

        # Decode JSON-valued arguments before returning.
        data = _decode_json_arguments(data)

        # Return the feature request tuple with decoded data.
        return feature_id, headers, data

    return handler


# *** blueprints

# ** blueprint: build_cache
@add_default_cli_commands(a.cli.ADMIN_DEFAULT_COMMANDS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build an admin CLI cache context pre-seeded with the full admin catalog
    plus the built-in admin CLI command definitions.

    Extends :func:`admin.build_cache` by stacking
    :func:`add_default_cli_commands` on top so the admin CLI command defaults
    are available alongside the admin errors, service dependencies, bootstrap
    constants, and feature definitions.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized cache context seeded with all admin defaults and
        CLI commands.
    :rtype: CacheContext
    '''

    # Delegate to the admin cache builder; the decorator layers CLI commands on top.
    return admin.build_cache(cache=cache)


# ** blueprint: build_admin_cli_session_context
def build_admin_cli_session_context(
    app_session: AppSession,
    cache: CacheContext,
) -> CliSessionContext:
    '''
    Build a fully wired admin CLI session context from a resolved app session.

    Parallel to :func:`cli.build_cli_session_context` but uses
    :func:`admin.build_admin_service_resolver` in place of
    :func:`core.build_service_resolver`, so the feature-level resolver carries
    the admin service catalog alongside the standard app container.  The
    ``_parse_cli_args`` closure is built via
    :func:`_admin_parse_cli_args_handler`, which extends the standard handler
    with JSON decoding of complex admin CLI arguments.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context (seeded with admin CLI
        commands in addition to the standard admin catalog).
    :type cache: CacheContext
    :return: The wired admin CLI session context.
    :rtype: CliSessionContext
    '''

    # Build the app service container from defaults and interface overrides.
    app_container = core.build_app_service_container(cache, app_session)

    # Build the feature-level resolver using the admin resolver (adds admin container).
    resolver = admin.build_admin_service_resolver(app_container, cache)

    # Resolve the CLI event collaborators from the app container.
    list_commands_evt = app_container.get_dependency('list_commands_evt')
    get_parent_args_evt = app_container.get_dependency('get_parent_args_evt')

    # Build the _parse_cli_args closure with admin JSON-decoding support.
    parse_cli_args = _admin_parse_cli_args_handler(
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

    # Construct and return the admin CLI session context via from_domain.
    return CliSessionContext.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        parse_cli_args=parse_cli_args,
        **handlers,
        **collaborators,
    )


# ** blueprint: build_admin_cli
def build_admin_cli(
    app_config: str,
    argv: Optional[List[str]] = None,
) -> Any:
    '''
    Build the built-in admin CLI session context and dispatch ``argv``.

    Parallel to the consumer-facing :func:`cli.build_app` but targeted at the
    built-in admin interface: uses the admin cache (full admin catalog plus CLI
    commands), resolves the ``tiferet_cli`` session with a built-in fallback,
    re-seeds the session constants so all config-file repos point to the
    consumer's ``app_config`` file, builds the admin CLI session context via
    :func:`build_admin_cli_session_context`, and delegates parsing, dispatch,
    exit-code handling, and response printing to
    :meth:`CliSessionContext.run`.

    :param app_config: Required path to the consumer's configuration file.
        All domain events that read or write configuration data use this path.
    :type app_config: str
    :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when
        ``None``.
    :type argv: Optional[List[str]]
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Build the admin CLI cache (seeded with admin errors, services, constants,
    # features, and CLI commands).
    cache = build_cache()

    # Resolve the session; built-in sessions are cache-seeded so no fallback needed.
    app_session = core.get_app_session('tiferet_cli', cache, app_config=app_config)

    # Re-seed the session constants so all config-file repos point to the
    # consumer's app_config file rather than the seeded 'config.yml' placeholders.
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

    # Dispatch argv through the admin CLI session context.
    return cli_context.run(argv)



# ** blueprint: main
def main() -> None:
    '''
    Entry point for the ``tiferet`` console script.

    Parses ``--config`` from ``sys.argv`` before delegating to
    :func:`build_admin_cli`, enabling invocations of the form::

        tiferet --config config.yml feature add ...
        tiferet feature add ...   # uses config.yml by default

    :return: None
    :rtype: None
    '''

    import argparse

    # Create a minimal pre-parser to extract --config before the full parse.
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        '--config',
        default='config.yml',
        help='Path to the app configuration file (default: config.yml).',
    )
    pre_args, remaining = pre_parser.parse_known_args()

    # Delegate to build_admin_cli with the resolved config path.
    build_admin_cli(app_config=pre_args.config, argv=remaining)
