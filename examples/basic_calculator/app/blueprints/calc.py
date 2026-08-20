# *** imports

# ** app
from tiferet import TiferetError
from tiferet.blueprints import core
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from ..contexts.calc import CalculatorAppContext

# *** blueprints

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

    # Construct and return the calculator app context, wiring the five template-method handlers.
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

    # Build the bootstrap cache pre-seeded with all framework defaults.
    cache = core.build_cache()

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
