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
from .main import (
    create_service_provider,
    load_default_services,
    resolve_interface,
    realize_interface,
)
from .cli import (
    build_parser,
    parse_argv,
    derive_feature_request,
)

# *** blueprints

# ** blueprint: _build_tiferet_command_map
def _build_tiferet_command_map() -> Dict[str, List]:
    '''
    Build a CLI command map directly from ``DEFAULT_TIFERET_CLI_COMMANDS``,
    bypassing the CLI config repository.

    :return: A dict mapping group keys to lists of ``CliCommandAggregate`` instances.
    :rtype: Dict[str, List]
    '''

    from ..mappers import CliCommandAggregate

    # Build the command map from the bootstrap command dicts.
    command_map: Dict[str, List] = {}
    for cmd_data in a.cli_cmd.DEFAULT_TIFERET_CLI_COMMANDS:
        cmd = CliCommandAggregate(**cmd_data)
        if cmd.group_key not in command_map:
            command_map[cmd.group_key] = [cmd]
        else:
            command_map[cmd.group_key].append(cmd)

    # Return the grouped command map.
    return command_map


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

    :param app_config: Required path to the consumer's configuration file.
        All domain events that read or write configuration data use this path.
    :type app_config: str
    :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when
        ``None``.
    :type argv: Optional[List[str]]
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Build the CLI command map directly from bootstrap defaults, bypassing
    # the CLI config repository entirely for parser construction.
    cli_command_map = _build_tiferet_command_map()

    # Build the argparse parser from the bootstrapped command map.
    parser = build_parser(cli_command_map, [])

    # Parse CLI arguments from argv (or sys.argv[1:] when None).
    parsed = parse_argv(parser, argv)

    # Derive the feature ID and request headers from the parsed arguments.
    feature_id, headers = derive_feature_request(parsed)

    # Resolve the interface definition, using the built-in tiferet_cli
    # defaults when the consumer's config file does not define the interface.
    app_interface, _ = resolve_interface(
        'tiferet_cli',
        default_interfaces=[a.cli_app.DEFAULT_TIFERET_CLI_INTERFACE],
        app_config=app_config,
    )

    # Load the framework's default services and add CLI-specific services,
    # avoiding duplicates of service IDs already present in the defaults.
    default_services = load_default_services()
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
        **a.bps.DEFAULT_CONSTANTS,
        'app_config': app_config,
        'cli_config': app_config,
        'di_config': app_config,
        'error_config': app_config,
        'feature_config': app_config,
        'logging_config': app_config,
    }

    # Build the merged constants by starting from the defaults (the service
    # parameters and the placeholder config paths that GetAppInterface seeds
    # onto the built-in interface), then updating with the bootstrap constants
    # so the consumer's app_config path wins for every config-file key.
    merged_constants: Dict[str, Any] = {
        k: v for dep in all_services for k, v in dep.parameters.items()
    }
    merged_constants.update(app_interface.constants or {})
    merged_constants.update(bootstrap_constants)

    # Re-seed the interface constants with the merged result so the constants
    # re-registered during realization (AppInterface.get_service_type_mapping)
    # also resolve to the consumer's app_config file rather than the seeded
    # 'config.yml' placeholders.
    app_interface.set_constants(merged_constants)

    # Build the service provider seeded with all service types and constants.
    service_provider = create_service_provider(
        type_map={dep.service_id: dep.get_service_type() for dep in all_services},
        **merged_constants,
    )

    # Realize the app interface context, passing the pre-built provider so that
    # all bootstrap constants are already wired before service construction, and
    # seeding the bootstrap defaults directly onto the hub initializer so the
    # bootstrap events resolve features, configurations, and commands that are
    # not present in the consumer's config file.
    interface_context = realize_interface(
        app_interface,
        'tiferet_cli',
        service_provider,
        default_features=a.cli_feat.DEFAULT_TIFERET_CLI_FEATURES,
        default_commands=a.cli_cmd.DEFAULT_TIFERET_CLI_COMMANDS,
        default_configurations=default_configuration_dicts,
        default_constants=bootstrap_constants,
    )

    # Decode JSON-valued CLI arguments before dispatching to the feature.
    parsed = _decode_json_arguments(parsed)

    # Execute the feature via the interface context; on API error, exit 1.
    try:
        response = interface_context.run(
            feature_id=feature_id,
            headers=headers,
            data=parsed,
        )

    # On a TiferetAPIError, print the message to stderr and exit with code 1.
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
