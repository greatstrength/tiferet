"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from .. import assets as a
from ..contexts.app import (
    AppSession,
    AppSessionContext,
    add_default_app_constants,
    add_default_app_services,
    add_default_app_sessions,
    get_default_app_constants,
    get_default_app_services,
    get_default_app_session,
)
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors, ERROR_CACHE_PREFIX
from ..contexts.feature import FEATURE_CACHE_PREFIX
from ..contexts.logging import LoggingContext, add_default_logging_settings, get_default_logging_settings
from ..di import DIAppServiceContainer, DIDynamicServiceContainer, DIDynamicServiceResolver
from ..di.core import ServiceResolver
from ..domain import LoggingSettings, ServiceDependency
from ..events import ParseParameter

# *** blueprints

# ** blueprint: parse_parameter
def parse_parameter(parameter: Any) -> Any:
    '''
    Thin, injectable wrapper over the ParseParameter static event.

    Passed as the injected parameter-parser to DIDynamicServiceResolver so the
    DI layer never imports from the events layer directly.

    :param parameter: The parameter to parse.
    :type parameter: Any
    :return: The parsed parameter.
    :rtype: Any
    '''

    # Delegate to the static parse parameter event.
    return ParseParameter.execute(parameter)

# ** blueprint: build_app_service_container
def build_app_service_container(cache,
        app_instance: AppSession = None,
        service_container: type = DIAppServiceContainer) -> DIAppServiceContainer:
    '''
    Build the singleton app service container from cache-seeded defaults
    merged with the session's own service and constant overrides.

    Session overrides are merged with the cache defaults before building the
    container (not layered afterward), so session constants reach all
    default services the session does not redeclare.

    :param cache: The bootstrap cache seeded with framework defaults.
    :type cache: CacheContext
    :param app_instance: The loaded app session whose own services and
        constants override the cache defaults.
    :type app_instance: AppSession
    :param service_container: The concrete DI app service container class.
    :type service_container: type
    :return: The built app service container.
    :rtype: DIAppServiceContainer
    '''

    # Retrieve the cache-seeded default services and constants.
    default_services = get_default_app_services(cache)
    default_constants = get_default_app_constants(cache)

    # Retrieve the session's own service and constant overrides.
    session_services = app_instance.services if app_instance is not None else []
    session_constants = app_instance.constants if app_instance is not None else {}

    # Merge session services over defaults, keyed by service_id.
    merged_services_by_id = {service.service_id: service for service in default_services}
    merged_services_by_id.update({service.service_id: service for service in session_services})

    # Merge session constants over defaults before building the container, and
    # register the shared cache-snapshot closure so services can read shared
    # bootstrap state without a direct cache reference.
    merged_constants = {**default_constants, **session_constants}
    merged_constants['load_cache'] = load_cache(cache)

    # Build and return the app service container from the merged dependencies.
    return service_container.from_dependencies(
        services=list(merged_services_by_id.values()),
        constants=merged_constants,
    )

# ** blueprint: build_service_resolver
def build_service_resolver(app_service_container: DIAppServiceContainer,
        parse_parameter: Callable = parse_parameter) -> ServiceResolver:
    '''
    Compose the feature-level service resolver, registering the app service
    container under the ``'app'`` flag for the hub's collaborators.

    :param app_service_container: The built app service container.
    :type app_service_container: DIAppServiceContainer
    :param parse_parameter: The parameter-parsing callable injected into the resolver.
    :type parse_parameter: Callable
    :return: The composed service resolver.
    :rtype: ServiceResolver
    '''

    # Resolve the DI repository service from the app container.
    di_service = app_service_container.get_dependency('di_service')

    # Construct the dynamic service resolver with the injected parameter parser.
    resolver = DIDynamicServiceResolver(di_service=di_service, parse_parameter=parse_parameter)

    # Register the app service container under the 'app' flag.
    resolver.add_container(app_service_container, 'app')

    # Return the composed resolver.
    return resolver

# ** blueprint: build_cache
@add_default_logging_settings(a.logging.CORE_DEFAULT_LOGGING_SETTINGS)
@add_default_app_sessions(a.app.CORE_DEFAULT_APP_SESSIONS)
@add_default_app_constants(a.app.CORE_DEFAULT_CONSTANTS)
@add_default_app_services(a.app.CORE_DEFAULT_SERVICES)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the bootstrap cache, pre-seeded with all framework default catalogs
    via the stacked decorator factories: errors, app services, app constants,
    app sessions, and logging settings.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The pre-seeded cache context.
    :rtype: CacheContext
    '''

    # Construct the base cache context; the stacked decorators seed it.
    return CacheContext(cache=cache)

# ** blueprint: load_cache
def load_cache(cache: CacheContext) -> Callable[[], Dict[str, Any]]:
    '''
    Build a zero-arg closure returning a root-namespace snapshot of the cache.

    Passed as a constant into the app service container so services can read
    shared bootstrap state without a direct cache reference.

    :param cache: The bootstrap cache to snapshot.
    :type cache: CacheContext
    :return: A zero-arg callable returning the root-namespace cache snapshot.
    :rtype: Callable[[], Dict[str, Any]]
    '''

    # Return the snapshot closure bound to the cache.
    def snapshot() -> Dict[str, Any]:
        return cache.get_by_prefix()

    # Return the closure.
    return snapshot

# ** blueprint: get_error
def get_error(cache: CacheContext, get_dependency: Callable) -> Callable:
    '''
    Build a handler closure that lazily resolves and caches Error domain objects.

    :param cache: The bootstrap cache used for lazy caching.
    :type cache: CacheContext
    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A handler closure resolving an Error by error code.
    :rtype: Callable
    '''

    # Return the handler closure bound to the cache and resolver.
    def handler(error_code: str) -> Any:

        # Return the cached error when already resolved.
        cached = cache.get(error_code, *ERROR_CACHE_PREFIX)
        if cached is not None:
            return cached

        # Resolve and execute the get_error event on a cache miss.
        get_error_evt = get_dependency('get_error_evt', 'app')
        error = get_error_evt.execute(id=error_code)

        # Cache the resolved error and return it.
        cache.set(error_code, error, *ERROR_CACHE_PREFIX)
        return error

    # Return the closure.
    return handler

# ** blueprint: get_feature
def get_feature(cache: CacheContext, get_dependency: Callable) -> Callable:
    '''
    Build a handler closure that lazily resolves and caches Feature domain objects.

    :param cache: The bootstrap cache used for lazy caching.
    :type cache: CacheContext
    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A handler closure resolving a Feature by feature id.
    :rtype: Callable
    '''

    # Return the handler closure bound to the cache and resolver.
    def handler(feature_id: str) -> Any:

        # Return the cached feature when already resolved.
        cached = cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        if cached is not None:
            return cached

        # Resolve and execute the get_feature event on a cache miss.
        get_feature_evt = get_dependency('get_feature_evt', 'app')
        feature = get_feature_evt.execute(id=feature_id)

        # Cache the resolved feature and return it.
        cache.set(feature_id, feature, *FEATURE_CACHE_PREFIX)
        return feature

    # Return the closure.
    return handler

# ** blueprint: build_logging_context
def build_logging_context(cache: CacheContext, get_dependency: Callable, logger_id: str) -> LoggingContext:
    '''
    Build the logging context from the merged default and repository-configured
    logging settings.

    :param cache: The bootstrap cache holding the default logging settings.
    :type cache: CacheContext
    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :param logger_id: The identifier of the logger configuration to bind.
    :type logger_id: str
    :return: The constructed logging context.
    :rtype: LoggingContext
    '''

    # Resolve and execute the logging list-all event to retrieve configured settings.
    list_all_evt = get_dependency('logging_list_all_evt', 'app')
    formatters, handlers, loggers = list_all_evt.execute()

    # Retrieve the cache-seeded default logging settings.
    default_settings = get_default_logging_settings(cache)
    default_formatters = default_settings.formatters if default_settings else []
    default_handlers = default_settings.handlers if default_settings else []
    default_loggers = default_settings.loggers if default_settings else []

    # Merge retrieved configs over the defaults, keyed by id (retrieved wins).
    merged_formatters = {formatter.id: formatter for formatter in default_formatters}
    merged_formatters.update({formatter.id: formatter for formatter in formatters})
    merged_handlers = {handler.id: handler for handler in default_handlers}
    merged_handlers.update({handler.id: handler for handler in handlers})
    merged_loggers = {logger.id: logger for logger in default_loggers}
    merged_loggers.update({logger.id: logger for logger in loggers})

    # Construct the merged logging settings and bind the logging context.
    settings = LoggingSettings(
        formatters=list(merged_formatters.values()),
        handlers=list(merged_handlers.values()),
        loggers=list(merged_loggers.values()),
    )
    return LoggingContext.from_domain(settings, logger_id=logger_id)

# ** blueprint: create_app_service
def create_app_service(module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
        service_container: type = DIDynamicServiceContainer) -> Any:
    '''
    Import and construct the app service used to resolve app sessions.

    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Optional constructor parameters for the app service.
    :type parameters: Dict[str, Any] | None
    :param service_container: The DI container class used to resolve the service.
    :type service_container: type
    :return: The constructed app service instance.
    :rtype: Any
    '''

    # Build a function-scoped container describing the single app service.
    container = service_container(services={
        'app_service': ServiceDependency(
            module_path=module_path,
            class_name=class_name,
            parameters=parameters or {},
        ),
    })

    # Resolve and return the constructed app service.
    return container.get_dependency('app_service')

# ** blueprint: get_app_session
def get_app_session(interface_id: str,
        cache: CacheContext = None,
        module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
        class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
        **parameters) -> AppSession:
    '''
    Resolve an app session, preferring a cache-seeded default before falling
    back to the configured app service.

    :param interface_id: The identifier of the app session to load.
    :type interface_id: str
    :param cache: The bootstrap cache checked for a seeded default session.
    :type cache: CacheContext | None
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Additional parameters for the app service constructor.
    :type parameters: dict
    :return: The resolved app session.
    :rtype: AppSession
    '''

    # Return a cache-seeded default session when present.
    if cache is not None:
        cached_session = get_default_app_session(cache, interface_id)
        if cached_session is not None:
            return cached_session

    # On a cache miss, compose the app service and load the session through it.
    app_service = create_app_service(module_path, class_name, parameters)
    return AppSessionContext.load(interface_id, app_service)
