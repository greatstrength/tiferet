# *** imports

# ** app
from tiferet import TiferetError
from tiferet.blueprints import core
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from ..contexts.fluent import CalculatorFluentContext
from .calc import build_calculator_cache, record_run_handler, register_calc_container

# *** blueprints

# ** blueprint: build_calculator_fluent_context
def build_calculator_fluent_context(app_session: AppSession, cache: CacheContext) -> CalculatorFluentContext:
    '''
    Compose a fully wired CalculatorFluentContext from a resolved app session.

    Mirrors build_calculator_app_context exactly, but realizes
    CalculatorFluentContext -- the fluent chain's own AppSessionContext
    subclass -- instead of the plain client.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :return: The wired calculator fluent context.
    :rtype: CalculatorFluentContext
    '''

    # Build the app service container and compose the feature-level resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)

    # Register the calculator's own dedicated 'calc'-flagged container.
    register_calc_container(resolver, cache)

    # Resolve any remaining injectable collaborators the context class declares.
    collaborators = core.resolve_collaborators(CalculatorFluentContext, app_container)

    # Construct and return the calculator fluent context, wiring the six template-method handlers.
    return CalculatorFluentContext.from_domain(
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

# ** blueprint: create_calculator_fluent
def create_calculator_fluent(interface_id: str = 'calc_fluent', config_file: str = 'config.yml') -> CalculatorFluentContext:
    '''
    Build a fully resolved CalculatorFluentContext in a single call.

    :param interface_id: The interface identifier to load from config.yml.
    :type interface_id: str
    :param config_file: The configuration file path.
    :type config_file: str
    :return: The fully wired calculator fluent context.
    :rtype: CalculatorFluentContext
    '''

    # Build the bootstrap cache pre-seeded with framework defaults plus the
    # calculator's own arithmetic bounded-context defaults.
    cache = build_calculator_cache()

    # Resolve the app session for the fluent calculator interface.
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)

    # Build the fully wired calculator fluent context.
    context = build_calculator_fluent_context(app_session, cache)

    # Verify the resolved context is a valid CalculatorFluentContext.
    if not isinstance(context, CalculatorFluentContext):
        TiferetError.raise_error(
            'APP_ERROR',
            interface_id=interface_id,
        )

    # Return the validated calculator fluent context.
    return context
