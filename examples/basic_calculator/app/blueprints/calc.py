# *** imports

# ** core
from typing import Any, Callable, Dict, List, Optional

# ** app
from tiferet import TiferetError
from tiferet.blueprints import core
from tiferet.blueprints import cli as cli_bp
from tiferet.contexts.app import AppSession, add_default_app_services
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import add_default_errors
from tiferet.contexts.feature import add_default_features
from tiferet.contexts.request import RequestContext
from .. import assets as a
from ..contexts.calc import CalculatorAppContext

# *** blueprints

# ** blueprint: build_calculator_cache
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_app_services(a.core.CALC_DEFAULT_SERVICES)
def build_calculator_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the bootstrap cache pre-seeded with the framework's own core
    defaults plus the calculator's arithmetic bounded-context defaults.

    Mirrors tiferet.blueprints.core.build_cache's stacked-decorator shape,
    scoped to the calculator's own arithmetic operators instead of the
    framework core, so calc.add/subtract/multiply/divide/exp/sqrt resolve
    regardless of what config.yml declares.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The pre-seeded cache context.
    :rtype: CacheContext
    '''

    # Delegate to the framework's own core cache builder; the stacked
    # decorators above layer the calculator's own defaults on top.
    return core.build_cache(cache)

# ** blueprint: build_calculator_cli_cache
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_app_services(a.core.CALC_DEFAULT_SERVICES)
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
        # request.result (not request.data) carries the feature's final
        # response, since the default arithmetic features have no data_key
        # step to set it -- request.data still carries the raw a/b operands.
        record_run_evt = get_dependency(a.core.RECORD_RUN_EVT_ID, 'app')
        record_run_evt.execute(feature_id=feature_id, result=request.result, **request.data)

    # Return the closure.
    return handler

# ** blueprint: build_calculator_app_context
def build_calculator_app_context(app_session: AppSession, cache: CacheContext) -> CalculatorAppContext:
    '''
    Compose a fully wired CalculatorAppContext from a resolved app session.

    Parallel to core.build_app_session_context, but dedicated to the fluent
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

    # Resolve any remaining injectable collaborators the context class declares.
    collaborators = core.resolve_collaborators(CalculatorAppContext, app_container)

    # Construct and return the calculator app context, wiring the six template-method handlers.
    # The resolver itself (not just its bound get_dependency) is passed through so
    # future collaborators can resolve additional services without a signature change.
    return CalculatorAppContext.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        resolver=resolver,
        build_logger_handler=core.build_logger_handler(cache, resolver.get_dependency),
        execute_feature_handler=core.execute_feature_handler(resolver.get_dependency, cache),
        raise_error_handler=core.raise_error_handler(core.get_error(cache, resolver.get_dependency)),
        response_handler=core.response_handler,
        create_request_handler=core.create_session_request,
        record_run_handler=record_run_handler(resolver.get_dependency),
        **collaborators,
    )

# ** blueprint: create_calculator_app
def create_calculator_app(interface_id: str = 'calc_fluent', config_file: str = 'config.yml') -> CalculatorAppContext:
    '''
    Build a fully resolved CalculatorAppContext in a single call.

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

# ** blueprint: create_calculator_cli
def create_calculator_cli(interface_id: str = 'calc_cli',
        argv: Optional[List[str]] = None,
        config_file: str = 'config.yml') -> Any:
    '''
    Build the calculator's CLI session context and dispatch argv through it.

    Mirrors tiferet.blueprints.cli.build_app, but seeds the cache via
    build_calculator_cli_cache so the arithmetic bounded-context defaults are
    available to CLI commands exactly as they are to calc_client/calc_fluent.

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
    cli_context = cli_bp.build_cli_session_context(app_session, cache)

    # Dispatch argv through the CLI session context.
    return cli_context.run(argv)
