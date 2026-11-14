# *** imports

# ** core
from typing import Any, Callable, Dict, List, Optional

# ** app
from tiferet import TiferetError
from tiferet.blueprints import app as app_bp
from tiferet.blueprints import core
from tiferet.blueprints import cli as cli_bp
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import add_default_errors
from tiferet.contexts.request import RequestContext
from tiferet.di import DIDynamicServiceContainer, ServiceResolver
from .. import assets as a
from ..contexts.calc import (
    CalculatorAppContext,
    add_default_calc_features,
    add_default_calc_services,
    get_default_calc_services,
)

# *** blueprints

# ** blueprint: build_calculator_cache
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_calc_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_calc_services(a.di.CALC_DEFAULT_SERVICES)
def build_calculator_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the bootstrap cache pre-seeded with the framework's own core
    defaults plus the calculator's arithmetic bounded-context defaults.

    Mirrors tiferet.blueprints.app.build_cache's stacked-decorator shape,
    scoped to the calculator's own arithmetic operators instead of the
    framework core, so calc.add/subtract/multiply/divide/exp/sqrt resolve
    regardless of what config.yml declares.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The pre-seeded cache context.
    :rtype: CacheContext
    '''

    # Delegate to the framework's standard app cache builder; the stacked
    # decorators above layer the calculator's own defaults on top.
    return app_bp.build_cache(cache)

# ** blueprint: build_calculator_cli_cache
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_calc_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_calc_services(a.di.CALC_DEFAULT_SERVICES)
def build_calculator_cli_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the bootstrap cache for the CLI entry point, pre-seeded with the
    built-in CLI command catalog plus the calculator's arithmetic
    bounded-context defaults.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The pre-seeded cache context.
    :rtype: CacheContext
    '''

    # Delegate to the CLI blueprint's own cache builder; the stacked
    # decorators above layer the calculator's own defaults on top.
    return cli_bp.build_cli_cache(cache)

# ** blueprint: build_calc_service_container
def build_calc_service_container(cache: CacheContext) -> DIDynamicServiceContainer:
    '''
    Build the calculator's own dynamic service container from its
    cache-seeded default services, keyed by service id.

    A plain DIDynamicServiceContainer, not a DIAppServiceContainer: the
    arithmetic events are ordinary feature-step services that happen to ship
    as defaults, not app-level infrastructure, so they get Factory scope --
    a new instance per resolution -- exactly as they would if config.yml had
    declared them directly.

    :param cache: The bootstrap cache seeded with the calculator's defaults.
    :type cache: CacheContext
    :return: The built calc service container.
    :rtype: DIDynamicServiceContainer
    '''

    # Key the calculator's default service dependencies by service id.
    services_by_id = {service.service_id: service for service in get_default_calc_services(cache)}

    # Build and return the dynamic service container.
    return DIDynamicServiceContainer(services=services_by_id)

# ** blueprint: register_calc_container
def register_calc_container(resolver: ServiceResolver, cache: CacheContext) -> None:
    '''
    Register the calculator's own dynamic service container on the resolver
    under the 'calc' flag.

    calc.* feature steps are tagged flags=['calc'] by add_default_calc_
    features, so they resolve their arithmetic events from this dedicated
    container -- a real bounded-context namespace, not the framework's own
    'app' container.

    :param resolver: The feature-level service resolver to register against.
    :type resolver: ServiceResolver
    :param cache: The bootstrap cache seeded with the calculator's defaults.
    :type cache: CacheContext
    '''

    # Build and register the calc container under the 'calc' flag.
    resolver.add_container(build_calc_service_container(cache), 'calc')

# ** blueprint: record_run_handler
def record_run_handler(get_dependency: Callable) -> Callable:
    '''
    Build the record-run handler closure.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A handler closure recording a completed feature run.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(feature_id: str, request: RequestContext) -> None:

        # Resolve and execute the record-run event; non-arithmetic runs no-op.
        # request.result carries the final response; request.data keeps the raw operands.
        record_run_evt = get_dependency(a.core.RECORD_RUN_EVT_ID, 'app')
        record_run_evt.execute(feature_id=feature_id, result=request.result, **request.data)

    # Return the closure.
    return handler

# ** blueprint: build_calculator_app_context
def build_calculator_app_context(app_session: AppSession, cache: CacheContext) -> CalculatorAppContext:
    '''
    Compose a fully wired CalculatorAppContext from a resolved app session.

    Parallel to tiferet.blueprints.app.build_app_session_context, but dedicated to the fluent
    calculator path: it selects CalculatorAppContext at the blueprint level
    directly, since App(...) has no dynamic module_path/class_name
    resolution of a custom high-level context.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :return: The wired calculator app context.
    :rtype: CalculatorAppContext
    '''

    # Build the app service container and compose the feature-level resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)

    # Register the calculator's own dedicated 'calc'-flagged container.
    register_calc_container(resolver, cache)

    # Delegate handler wiring and construction, adding the calculator's own slots.
    return core.compose_session_context(
        CalculatorAppContext,
        app_session,
        cache,
        resolver,
        create_request_handler=core.create_request_context,
        response_handler=core.response_handler,
        record_run_handler=record_run_handler(resolver.get_dependency),
    )

# ** blueprint: create_calculator_app
def create_calculator_app(interface_id: str = 'calc_client', config_file: str = 'config.yml') -> CalculatorAppContext:
    '''
    Build a fully resolved CalculatorAppContext in a single call.

    Builds the plain, non-fluent client. See app.blueprints.fluent for the
    chainable CalculatorFluentContext (calc_fluent).

    :param interface_id: The interface identifier to load from config.yml.
    :type interface_id: str
    :param config_file: The configuration file path.
    :type config_file: str
    :return: The fully wired calculator app context.
    :rtype: CalculatorAppContext
    '''

    # Build the bootstrap cache pre-seeded with framework defaults plus the
    # calculator's own arithmetic bounded-context defaults.
    cache = build_calculator_cache()

    # Resolve the app session for the fluent calculator interface.
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)

    # Build the fully wired calculator app context.
    context = build_calculator_app_context(app_session, cache)

    # Verify the resolved context is a valid CalculatorAppContext.
    if not isinstance(context, CalculatorAppContext):
        TiferetError.raise_error(
            'APP_ERROR',
            interface_id=interface_id,
        )

    # Return the validated calculator app context.
    return context

# ** blueprint: build_calculator_cli_session_context
def build_calculator_cli_session_context(app_session: AppSession, cache: CacheContext) -> Any:
    '''
    Compose a fully wired CLI session context, mirroring
    tiferet.blueprints.cli.build_cli_session_context exactly, with one
    addition: registering the calculator's own dedicated 'calc'-flagged
    container so CLI-dispatched features resolve the same bounded-context
    defaults as calc_client.py/calc_fluent.py. A calculator-local copy is
    needed because the framework's own builder has no hook to register an
    extra container -- it builds and consumes its resolver internally.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :return: The wired CLI session context.
    :rtype: Any
    '''

    # Build the app service container and compose the feature-level resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)

    # Register the calculator's own dedicated 'calc'-flagged container.
    register_calc_container(resolver, cache)

    # Build the CLI handlers without resolving events during construction.
    commands_handler = cli_bp.list_commands_handler(cache, resolver.get_dependency)
    parent_args_handler = cli_bp.get_parent_args_handler(resolver.get_dependency)
    parse_cli_args = cli_bp.parse_cli_args_handler(
        list_commands=commands_handler,
        get_parent_args=parent_args_handler,
    )

    # Delegate handler wiring and construction.
    return core.compose_session_context(
        cli_bp.CliSessionContext,
        app_session,
        cache,
        resolver,
        create_request_handler=cli_bp.create_cli_request_context,
        response_handler=core.response_handler,
        parse_cli_args=parse_cli_args,
        list_commands_handler=commands_handler,
        get_parent_args_handler=parent_args_handler,
    )

# ** blueprint: create_calculator_cli
def create_calculator_cli(interface_id: str = 'calc_cli',
        argv: Optional[List[str]] = None,
        config_file: str = 'config.yml') -> Any:
    '''
    Build the calculator's CLI session context and dispatch argv through it.

    Mirrors tiferet.blueprints.cli.build_app, but seeds the cache via
    build_calculator_cli_cache and composes the session via
    build_calculator_cli_session_context, so the arithmetic bounded-context
    defaults are available to CLI commands exactly as they are to
    calc_client/calc_fluent.

    :param interface_id: The CLI interface identifier.
    :type interface_id: str
    :param argv: The argument list; defaults to sys.argv[1:] when None.
    :type argv: Optional[List[str]]
    :param config_file: The configuration file path.
    :type config_file: str
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Build the calculator CLI cache: core + CLI commands + calc defaults.
    cache = build_calculator_cli_cache()

    # Resolve the app session for the CLI interface.
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)

    # Compose the wired CLI session context.
    cli_context = build_calculator_cli_session_context(app_session, cache)

    # Dispatch argv through the CLI session context.
    return cli_context.run(argv)
