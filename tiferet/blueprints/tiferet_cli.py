"""Tiferet CLI Blueprint — Built-in CLI Management Interface

-- obsolete: superseded by blueprints/admin_cli.py; remove at v2.0.0 stable
"""

# *** imports

# ** core
import inspect
import json
import sys
from typing import Any, Dict, List, Optional

# ** app
from ..assets import TiferetAPIError
from .. import assets as a
from ..contexts.app import (
    AppSessionContext,
    get_default_app_services,
    resolve_default_interface,
)
from ..contexts.cache import CacheContext
from ..domain import AppServiceDependency, AppSession
from ..di import injectable_parameter_names
from ..events import DomainEvent, ImportDependency, RaiseError
from ..events.blueprint import CreateServiceResolver
from .core import (
    build_cache,
    get_app_session,
    execute_feature_handler,
    raise_error_handler,
    create_session_request,
    response_handler,
    get_error,
)

# *** functions

# ** function: _resolve_ctor_kwargs
def _resolve_ctor_kwargs(service_type: type, registry: Dict[str, Any]) -> Dict[str, Any] | None:
    '''
    Resolve constructor keyword arguments for a service type from the registry.

    Returns the resolved kwargs, or ``None`` when a required constructor
    parameter is not yet available so the caller can defer instantiation.

    :param service_type: The service class to inspect.
    :type service_type: type
    :param registry: The name-to-value registry of constants and built services.
    :type registry: Dict[str, Any]
    :return: The resolved kwargs, or None when a required parameter is missing.
    :rtype: Dict[str, Any] | None
    '''

    # Inspect the constructor signature; treat uninspectable types as no-arg.
    try:
        sig = inspect.signature(service_type.__init__)
    except (ValueError, TypeError):
        return {}

    # Match each injectable constructor parameter (sourced from the shared DI
    # helper so the skip rules live in one place) to a registry entry,
    # deferring on any missing required parameter.
    kwargs: Dict[str, Any] = {}
    for name in injectable_parameter_names(service_type):

        # Wire from the registry, or defer when a required value is absent.
        if name in registry:
            kwargs[name] = registry[name]
        elif sig.parameters[name].default is inspect.Parameter.empty:
            return None

    # Return the resolved constructor kwargs.
    return kwargs


# ** function: _build_wiring_constants
def _build_wiring_constants(app_session: AppSession) -> Dict[str, Any]:
    '''
    Build the wiring-registry seed constants from an app session.

    Combines the session scalars (id, logger id) with the session's declared
    constants into a single name-to-value mapping used to seed declarative
    service wiring.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :return: The seed constants keyed by name.
    :rtype: Dict[str, Any]
    '''

    # Combine session scalars with the session's declared constants.
    return {
        'interface_id': app_session.id,
        'logger_id': getattr(app_session, 'logger_id', None),
        **(app_session.constants or {}),
    }


# ** function: _resolve_collaborators
def _resolve_collaborators(context_cls: type, registry: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Resolve a context class's event collaborators by name from a wiring registry.

    Inspects the context class's own injectable constructor parameters and
    pulls each matching id from the registry, skipping the arguments that
    ``_load_app_instance`` supplies explicitly (``get_dependency``, ``cache``)
    and the bootstrap ``default_*`` kwargs forwarded via ``context_kwargs``.
    This injects the CLI events for a ``CliContext`` and supports any custom
    context's collaborators without hard-coding collaborator names, while the
    generic ``AppSessionContext`` still resolves only its original three.

    :param context_cls: The context class whose collaborators are resolved.
    :type context_cls: type
    :param registry: The name-to-value registry of constants and built services.
    :type registry: Dict[str, Any]
    :return: The resolved collaborators keyed by constructor parameter name.
    :rtype: Dict[str, Any]
    '''

    # Arguments supplied explicitly during construction are never collaborators.
    reserved = {'get_dependency', 'cache'}

    # Match each injectable constructor parameter to a registry entry, skipping
    # the explicitly-supplied args and the bootstrap default_* kwargs.
    return {
        name: registry[name]
        for name in injectable_parameter_names(context_cls)
        if name not in reserved
        and not name.startswith('default_')
        and name in registry
    }


# *** blueprints

# ** blueprint: _wire_services
def _wire_services(
    services: List[AppServiceDependency],
    constants: Dict[str, Any],
) -> Dict[str, Any]:
    '''
    Declaratively instantiate service dependencies into a name-to-value registry.

    Seeds the registry with the provided constants and each dependency's
    parameters, then iteratively instantiates services whose constructor
    arguments are all resolvable, wiring events to the repositories they depend
    on without an app-level DI container.

    :param services: The service dependencies to instantiate.
    :type services: List[AppServiceDependency]
    :param constants: The seed constants (interface scalars, config values, etc.).
    :type constants: Dict[str, Any]
    :return: The registry of constants and instantiated services keyed by id.
    :rtype: Dict[str, Any]
    '''

    # Seed the registry with constants, then service parameters at lower priority.
    registry: Dict[str, Any] = dict(constants)
    for dep in services:
        for key, value in (dep.parameters or {}).items():
            registry.setdefault(key, value)

    # Iteratively instantiate services until none remain or no progress is made.
    pending = list(services)
    while pending:
        still_pending: List[AppServiceDependency] = []
        progressed = False

        # Attempt to instantiate each pending dependency.
        for dep in pending:
            service_type = dep.get_service_type()
            kwargs = _resolve_ctor_kwargs(service_type, registry)

            # Defer when constructor arguments are not yet fully resolvable.
            if kwargs is None:
                still_pending.append(dep)
                continue

            # Instantiate and register the service under its id.
            registry[dep.service_id] = service_type(**kwargs)
            progressed = True

        # Fail when remaining services cannot be resolved.
        if not progressed and still_pending:
            RaiseError.execute(
                a.const.APP_SERVICE_IMPORT_FAILED_ID,
                exception='Unresolvable service dependencies: {}'.format(
                    [dep.service_id for dep in still_pending]
                ),
            )

        # Continue with the still-pending dependencies.
        pending = still_pending

    # Return the populated registry.
    return registry


# ** blueprint: _load_app_instance
def _load_app_instance(
    app_session: AppSession,
    **context_kwargs,
) -> Any:
    '''
    Declaratively construct the app session context from a loaded session.

    The session's service dependencies (repositories and events) are wired
    explicitly by importing each class and resolving its constructor arguments
    from a name-to-value registry of session scalars, constants, and
    already-built services -- no app-level DI container is used. A
    ``ServiceResolver`` is built from the resolved ``di_service`` and its
    ``get_dependency`` handler is injected into the context.

    This is the relocated legacy feature-DI bootstrap path retained for
    ``build_tiferet_cli``; the standard app/CLI entrypoints use
    ``core.build_app`` instead.

    :param app_session: The prepared app session definition.
    :type app_session: AppSession
    :param context_kwargs: Additional keyword arguments forwarded to the context
        constructor (e.g. bootstrap defaults).
    :type context_kwargs: dict
    :return: The resolved app session context.
    :rtype: Any
    '''

    # Seed the wiring registry with session scalars and constants.
    constants = _build_wiring_constants(app_session)

    # Declaratively instantiate the session's service dependencies.
    try:
        registry = _wire_services(app_session.services, constants)

    # Raise a structured error if declarative wiring fails.
    except Exception as e:
        RaiseError.execute(
            a.const.APP_SERVICE_IMPORT_FAILED_ID,
            exception=str(e),
        )

    # Compose the service resolver via the bootstrap event from the session's
    # DI repository dependency, routing any bootstrap DI defaults (popped from
    # context kwargs) into it.
    resolver = DomainEvent.handle(
        CreateServiceResolver,
        dependencies={},
        app_interface=app_session,
        default_configurations=context_kwargs.pop('default_configurations', None),
        default_constants=context_kwargs.pop('default_constants', None),
    )

    # Import the context class declared by the session (supports custom contexts).
    context_cls = ImportDependency.execute(
        app_session.module_path,
        app_session.class_name,
    )

    # Resolve the context class's event collaborators by name from the registry.
    resolved = _resolve_collaborators(context_cls, registry)

    # Use a pre-built cache forwarded via context_kwargs (build_tiferet_cli always provides one).
    cache = context_kwargs.pop('cache', None) or build_cache()

    # Construct the context declaratively, injecting the resolution handler, cache,
    # and all four FE4 template-method handler callables.
    return context_cls.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
        create_request_handler=create_session_request,
        raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
        response_handler=response_handler,
        **resolved,
        **context_kwargs,
    )


# ** blueprint: _resolve_bootstrap_session
def _resolve_bootstrap_session(
    interface_id: str,
    cache: CacheContext,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    default_interfaces: List[Dict[str, Any]] = [],
    **parameters,
) -> AppSession:
    '''
    Resolve a built-in app session, falling back to bootstrap defaults.

    Shared by the built-in bootstrappers (``build_tiferet_app`` /
    ``build_tiferet_cli``) whose target session is not defined in the
    consumer's configuration file. Loads the session via ``get_app_session``
    and, when the app service cannot find it, falls back to the matching
    ``default_interfaces`` definition (re-raising when no default matches).
    The framework default services and constants are then merged onto the
    session via ``AppSession.apply_defaults``.

    This is downstream bootstrap machinery relocated from the retired
    ``main.resolve_interface`` to preserve behavior; the core path
    (``core.build_app``) reads defaults from the cache instead.

    :param interface_id: The id of the built-in session to resolve.
    :type interface_id: str
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param default_interfaces: Session definition dicts used as a fallback when
        the session is not found in the repository.
    :type default_interfaces: List[Dict[str, Any]]
    :param parameters: Additional parameters passed to the app service constructor.
    :type parameters: dict
    :return: The resolved, defaults-applied app session.
    :rtype: AppSession
    '''

    # Retrieve the session via the core blueprint, falling back to the bootstrap
    # default session definitions when the config does not define it.
    try:
        app_session = get_app_session(interface_id, cache, module_path, class_name, **parameters)
    except a.TiferetError:
        app_session = resolve_default_interface(interface_id, default_interfaces)
        if app_session is None:
            raise

    # Merge the framework default services and constants via the domain model.
    app_session = app_session.apply_defaults(
        default_services=[
            AppServiceDependency.model_validate(r)
            for r in a.app.CORE_DEFAULT_SERVICES.values()
        ],
        default_constants=a.app.CORE_DEFAULT_CONSTANTS,
    )

    # Return the resolved, defaults-applied session.
    return app_session


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


# ** blueprint: build_tiferet_cli (obsolete)
# -- obsolete: superseded by admin_cli.build_admin_cli; remove at v2.0.0 stable
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

    # Build the shared cache first (seeds errors, app service dependencies, and
    # bootstrap constants); it is threaded through the bootstrap resolver and
    # the relocated legacy wiring path.
    cache = build_cache()

    # Resolve the session definition, using the built-in tiferet_cli defaults
    # when the consumer's config file does not define the session.
    app_session = _resolve_bootstrap_session(
        'tiferet_cli',
        cache,
        default_interfaces=[a.cli_app.DEFAULT_TIFERET_CLI_SESSION],
        app_config=app_config,
    )

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

    # Realize the built-in CLI context via the relocated legacy feature-DI
    # bootstrap path (the core compose path cannot yet replace it). The session
    # constants (re-seeded above with the consumer's app_config) drive
    # declarative service wiring, and the bootstrap defaults are seeded onto the
    # context and service resolver so the bootstrap commands, features, and
    # configurations resolve even when absent from the consumer's config file.
    cli_context = _load_app_instance(
        app_session,
        cache=cache,
        default_features=a.cli_feat.DEFAULT_TIFERET_CLI_FEATURES,
        default_commands=a.cli_cmd.DEFAULT_TIFERET_CLI_COMMANDS,
        default_configurations=default_configuration_dicts,
        default_constants=bootstrap_constants,
    )

    # Validate the realized context type (the check realize_interface performed).
    if not isinstance(cli_context, AppSessionContext):
        RaiseError.execute(
            a.const.INVALID_APP_SESSION_TYPE_ID,
            'App context for session is not valid: tiferet_cli.',
            interface_id='tiferet_cli',
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
