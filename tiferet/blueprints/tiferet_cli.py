"""Tiferet CLI Blueprint — Built-in CLI Management Interface"""

# *** imports

# ** core
import json
import sys
from typing import Any, Dict, List, Optional

# ** app
from ..assets import TiferetAPIError
from ..domain import AppServiceDependency
from .. import assets as a
from .core import build_cache
from .main import (
    resolve_interface,
    realize_interface,
)
from ..contexts.app import get_default_app_services

# *** blueprints

# ** blueprint: _decode_json_arguments
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


# ** blueprint: build_tiferet_cli
def build_tiferet_cli(
    app_config: str,
    argv: Optional[List[str]] = None,
) -> Any:
    '''
    Build the built-in Tiferet CLI, parse arguments, and dispatch to a feature.

    All CRUD operations performed by domain events target the consumer's
    ``app_config`` file.  The CLI commands and feature workflows are bootstrapped
    from framework asset modules — they are never loaded from the config file.
    The built-in ``tiferet_cli`` interface resolves to :class:`CliContext`, so
    parser construction, request parsing, exit-code handling, and dispatch are
    owned by the context; this blueprint only seeds bootstrap defaults and
    decodes the management CLI's JSON-valued arguments.

    :param app_config: Required path to the consumer's configuration file.
        All domain events that read or write configuration data use this path.
    :type app_config: str
    :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when
        ``None``.
    :type argv: Optional[List[str]]
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Resolve the session definition, using the built-in tiferet_cli
    # defaults when the consumer's config file does not define the session.
    app_session, _ = resolve_interface(
        'tiferet_cli',
        default_interfaces=[a.cli_app.DEFAULT_TIFERET_CLI_SESSION],
        app_config=app_config,
    )

    # Build the shared cache using the core blueprint (seeds errors, app service
    # dependencies, and bootstrap constants). This bridges the legacy path to the
    # core compose path; the cache is forwarded into realize_interface so
    # load_app_instance reuses it rather than creating a second one.
    # ++ todo: temporary cache creation; thread through the core compose path at FE1
    cache = build_cache()

    # Read default services from the seeded cache rather than calling load_default_services.
    default_services = get_default_app_services(cache)

    # Add CLI-specific services not already present in the defaults.
    existing_service_ids = {dep.service_id for dep in default_services}
    cli_service_deps = [
        AppServiceDependency.model_construct(
            service_id=sid,
            module_path=mp,
            class_name=cn,
            parameters=p or {},
        )
        for sid, mp, cn, p in a.cli_svc.DEFAULT_TIFERET_CLI_SERVICES
        if sid not in existing_service_ids
    ]
    all_services = default_services + cli_service_deps

    # Convert the merged service dependencies (framework defaults + CLI
    # services) into service configuration dicts for the feature-level DI
    # context. Keying each entry by its service_id registers every bootstrap
    # event (e.g. add_feature_evt) AND the repositories the events depend on
    # (e.g. feature_service), so each event's service dependency can be wired
    # even when the consumer's config file does not define them.
    default_configuration_dicts = [
        {
            'id': dep.service_id,
            'module_path': dep.module_path,
            'class_name': dep.class_name,
            'parameters': dep.parameters or {},
            'dependencies': [],
        }
        for dep in all_services
    ]

    # Build the bootstrap constants dict, pointing all config file keys at the
    # consumer's config file so every repo reads from and writes to that file.
    bootstrap_constants: Dict[str, Any] = {
        **a.app.CORE_DEFAULT_CONSTANTS,
        'app_config': app_config,
        'cli_config': app_config,
        'di_config': app_config,
        'error_config': app_config,
        'feature_config': app_config,
        'logging_config': app_config,
    }

    # Build the merged constants by starting from the defaults (the service
    # parameters and the placeholder config paths that GetAppSession seeds
    # onto the built-in interface), then updating with the bootstrap constants
    # so the consumer's app_config path wins for every config-file key.
    merged_constants: Dict[str, Any] = {
        k: v for dep in all_services for k, v in dep.parameters.items()
    }
    merged_constants.update(app_session.constants or {})
    merged_constants.update(bootstrap_constants)

    # Re-seed the session constants with the merged result so declarative
    # wiring during realization resolves repositories against the consumer's
    # app_config file rather than the seeded 'config.yml' placeholders.
    app_session.set_constants(merged_constants)

    # Realize the built-in CLI context. The session constants (re-seeded
    # above with the consumer's app_config) drive declarative service wiring,
    # and the bootstrap defaults are seeded onto the context and service
    # resolver so the bootstrap commands, features, and configurations resolve
    # even when they are not present in the consumer's config file.
    cli_context = realize_interface(
        app_session,
        'tiferet_cli',
        cache=cache,
        default_features=a.cli_feat.DEFAULT_TIFERET_CLI_FEATURES,
        default_commands=a.cli_cmd.DEFAULT_TIFERET_CLI_COMMANDS,
        default_configurations=default_configuration_dicts,
        default_constants=bootstrap_constants,
    )

    # Parse the CLI request through the context. The parser is built from the
    # seeded bootstrap commands (CliContext.get_commands() falls back to the
    # default command list); argparse exits with code 2 on invalid arguments.
    request = cli_context.parse_cli_request(argv)

    # Decode the management CLI's JSON-valued arguments before dispatch,
    # keeping the JSON concern in this blueprint rather than in CliContext.
    request.data = _decode_json_arguments(request.data)

    # Execute the feature via the context; on a TiferetAPIError, print the
    # message to stderr and exit with code 1.
    try:
        response = cli_context.run(
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


# ** blueprint: main
def main() -> None:
    '''
    Entry point for the ``tiferet`` console script.

    Parses ``--config`` from ``sys.argv`` before delegating to
    :func:`build_tiferet_cli`, enabling invocations of the form::

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

    # Delegate to build_tiferet_cli with the resolved config path.
    build_tiferet_cli(app_config=pre_args.config, argv=remaining)
