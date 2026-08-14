"""Tiferet Core Blueprints"""

# *** imports

# ** core
import os
from typing import Any, Callable, Dict

# ** app
from .. import assets as a
from ..assets import TiferetAPIError, TiferetError
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
from ..contexts.core import BaseContext
from ..contexts.error import add_default_errors, ERROR_CACHE_PREFIX
from ..contexts.feature import FeatureContext, FEATURE_CACHE_PREFIX
from ..contexts.logging import (
    LOGGER_CACHE_PREFIX,
    LoggingContext,
    add_default_logging_settings,
    get_default_logging_settings,
)
from ..contexts.request import RequestContext
from ..di import DIAppServiceContainer, DIDynamicServiceContainer, DIDynamicServiceResolver
from ..di.core import ServiceResolver, injectable_parameter_names
from ..domain import Error, Feature, LoggingSettings, ServiceDependency

# *** constants

# ** constant: reserved_context_parameters
# Constructor parameters supplied explicitly by the session context builders,
# and therefore excluded from generic collaborator resolution.
RESERVED_CONTEXT_PARAMETERS = (
    'get_dependency',
    'cache',
    'build_logger_handler',
    'parse_cli_args',
    'execute_feature_handler',
    'create_request_handler',
    'raise_error_handler',
    'response_handler',
)

# *** functions

# ** function: resolve_collaborators
def resolve_collaborators(context_cls: type, app_container: DIAppServiceContainer) -> Dict[str, Any]:
    '''
    Resolve a context class's remaining injectable collaborators from the app container.

    Inspects the realized context class's constructor and resolves every
    injectable parameter that is registered on the app container, skipping the
    parameters build_app_session_context supplies explicitly and the bootstrap
    ``default_*`` parameters. This is the seam that lets a context subclass
    declare extra collaborators and have them wired declaratively.

    :param context_cls: The realized context class to inspect.
    :type context_cls: type
    :param app_container: The built app service container to resolve against.
    :type app_container: DIAppServiceContainer
    :return: A mapping of collaborator name to resolved instance.
    :rtype: Dict[str, Any]
    '''

    # Resolve each injectable parameter that is neither reserved nor a bootstrap default.
    return {
        name: app_container.get_dependency(name)
        for name in injectable_parameter_names(context_cls)
        if name not in RESERVED_CONTEXT_PARAMETERS
        and not name.startswith('default_')
        and app_container.has_dependency(name)
    }

# ** function: merge_logging_settings
def merge_logging_settings(cache: CacheContext,
        formatters: list,
        handlers: list,
        loggers: list) -> LoggingSettings:
    '''
    Merge repository-configured logging sections over cache-seeded defaults.

    Each section is keyed by ``.id``; repository entries override the default
    sharing their id, and unmatched defaults survive. Tolerates a cache with
    no seeded defaults.

    :param cache: The bootstrap cache holding default logging settings.
    :type cache: CacheContext
    :param formatters: Repository-configured formatters.
    :type formatters: list
    :param handlers: Repository-configured handlers.
    :type handlers: list
    :param loggers: Repository-configured loggers.
    :type loggers: list
    :return: The merged logging settings value object.
    :rtype: LoggingSettings
    '''

    # Retrieve the cache-seeded default logging settings, tolerating none.
    defaults = get_default_logging_settings(cache)
    default_formatters = defaults.formatters if defaults else []
    default_handlers = defaults.handlers if defaults else []
    default_loggers = defaults.loggers if defaults else []

    # Merge retrieved configs over the defaults, keyed by id (retrieved wins).
    merged_formatters = {formatter.id: formatter for formatter in default_formatters}
    merged_formatters.update({formatter.id: formatter for formatter in formatters})
    merged_handlers = {handler.id: handler for handler in default_handlers}
    merged_handlers.update({handler.id: handler for handler in handlers})
    merged_loggers = {logger.id: logger for logger in default_loggers}
    merged_loggers.update({logger.id: logger for logger in loggers})

    # Return the merged logging settings value object.
    return LoggingSettings(
        formatters=list(merged_formatters.values()),
        handlers=list(merged_handlers.values()),
        loggers=list(merged_loggers.values()),
    )

# *** blueprints

# ** blueprint: parse_parameter
def parse_parameter(parameter: Any) -> Any:
    '''
    Parse a configuration parameter value, resolving environment references.

    Resolves ``$env.``-prefixed values from the process environment and returns
    any other value unchanged. Parameter parsing is owned by the blueprint layer
    and injected into both the DI resolver and FeatureContext.

    :param parameter: The parameter value to parse.
    :type parameter: Any
    :return: The parsed parameter value.
    :rtype: Any
    '''

    # Resolve the parameter, wrapping any failure in a structured error.
    try:

        # Resolve an environment reference from the process environment.
        if isinstance(parameter, str) and parameter.startswith(a.core.ENV_VAR_PREFIX):
            result = os.getenv(parameter[len(a.core.ENV_VAR_PREFIX):])

            # Treat an unset or empty environment variable as a failure.
            if not result:
                raise Exception('Environment variable not found.')

            # Return the resolved environment value.
            return result

        # Return any non-environment parameter unchanged.
        return parameter

    # Raise a structured error when parsing fails.
    except Exception as e:
        TiferetError.raise_error(
            a.error.PARAMETER_PARSING_FAILED_ID,
            parameter=parameter,
            exception=str(e),
        )

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

# ** blueprint: build_logger_handler
def build_logger_handler(cache: CacheContext, get_dependency: Callable) -> Callable:
    '''
    Build a logger-construction handler that caches loggers by logger id.

    On a cache hit under ``LOGGER_CACHE_PREFIX``, the previously built logger
    is returned. On a miss, repository logging configs are listed, merged over
    cache-seeded defaults, applied via ``LoggingContext``, and cached so
    ``dictConfig`` runs once per logger id per process.

    :param cache: The bootstrap cache used for lazy logger caching.
    :type cache: CacheContext
    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A handler closure resolving a logger by logger id.
    :rtype: Callable
    '''

    # Return the handler closure bound to the cache and resolver.
    def handler(logger_id: str):

        # Return the cached logger when already built for this id.
        cached = cache.get(logger_id, *LOGGER_CACHE_PREFIX)
        if cached is not None:
            return cached

        # Resolve and execute the logging list-all event on a cache miss.
        list_all_evt = get_dependency('logging_list_all_evt', 'app')
        formatters, handlers, loggers = list_all_evt.execute()

        # Merge repository configs over cache-seeded defaults.
        settings = merge_logging_settings(cache, formatters, handlers, loggers)

        # Build the logger from the merged settings for the requested id.
        logger = LoggingContext.from_domain(settings, logger_id=logger_id).build_logger()

        # Cache the built logger and return it.
        cache.set(logger_id, logger, *LOGGER_CACHE_PREFIX)
        return logger

    # Return the closure.
    return handler

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
    :param parameters: Optional constructor parameters for the app service;
        defaults to the framework app service parameters when omitted.
    :type parameters: Dict[str, Any] | None
    :param service_container: The DI container class used to resolve the service.
    :type service_container: type
    :return: The constructed app service instance.
    :rtype: Any
    '''

    # Fall back to the framework default parameters when none are supplied.
    parameters = parameters if parameters else a.app.DEFAULT_APP_SERVICE_PARAMETERS

    # Build a function-scoped container describing the single app service.
    container = service_container(services={
        'app_service': ServiceDependency(
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
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

# ** blueprint: create_request_context
def create_request_context(interface_id: str,
        feature_id: str,
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None) -> RequestContext:
    '''
    Pure factory constructing a request context stamped with the interface id.

    :param interface_id: The identifier of the app session issuing the request.
    :type interface_id: str
    :param feature_id: The identifier of the feature to execute.
    :type feature_id: str
    :param headers: The request headers.
    :type headers: Dict[str, str] | None
    :param data: The request data.
    :type data: Dict[str, Any] | None
    :return: The constructed request context.
    :rtype: RequestContext
    '''

    # Construct the request context, stamping the interface id onto the headers.
    return RequestContext(
        headers={**(headers or {}), 'interface_id': interface_id},
        data=data or {},
        feature_id=feature_id,
    )

# ** blueprint: create_feature_context
def create_feature_context(get_dependency: Callable,
        cache: CacheContext,
        feature_id: str) -> FeatureContext:
    '''
    Resolve a Feature domain object and bind it to a fresh FeatureContext.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :param cache: The bootstrap cache used for lazy feature caching.
    :type cache: CacheContext
    :param feature_id: The identifier of the feature to resolve.
    :type feature_id: str
    :return: The feature context bound to the resolved feature domain object.
    :rtype: FeatureContext
    '''

    # Resolve the feature via the lazy-caching get_feature handler.
    feature = get_feature(cache, get_dependency)(feature_id)

    # Construct and return the feature context bound to the resolved feature.
    return FeatureContext.from_domain(
        feature,
        get_dependency=get_dependency,
        cache=cache,
        parse_parameter=parse_parameter,
    )

# ** blueprint: create_session_request
def create_session_request(interface_id: str,
        feature_id: str,
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None) -> RequestContext:
    '''
    Convenience alias for create_request_context, kept for backward compatibility.

    :param interface_id: The identifier of the app session issuing the request.
    :type interface_id: str
    :param feature_id: The identifier of the feature to execute.
    :type feature_id: str
    :param headers: The request headers.
    :type headers: Dict[str, str] | None
    :param data: The request data.
    :type data: Dict[str, Any] | None
    :return: The constructed request context.
    :rtype: RequestContext
    '''

    # Delegate to the request context factory.
    return create_request_context(interface_id, feature_id, headers, data)

# ** blueprint: execute_feature_handler
def execute_feature_handler(get_dependency: Callable, cache: CacheContext) -> Callable:
    '''
    Build the feature-execution handler closure.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :param cache: The bootstrap cache used for lazy feature caching.
    :type cache: CacheContext
    :return: A void handler closure executing a feature against a request.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver and cache.
    def handler(feature_id: str, request: RequestContext, *flags, **kwargs) -> None:

        # Resolve the feature-bound context.
        feature_context = create_feature_context(get_dependency, cache, feature_id)

        # Drive execution; the result is accumulated on the request context and
        # result extraction is the responsibility of the response step.
        feature_context.execute_feature(request, *flags, **kwargs)

    # Return the closure.
    return handler

# ** blueprint: raise_error_handler
def raise_error_handler(get_error_handler: Callable) -> Callable:
    '''
    Build the error-handling handler closure.

    :param get_error_handler: The lazy-caching error-resolution handler.
    :type get_error_handler: Callable
    :return: A handler closure formatting and raising a structured API error.
    :rtype: Callable
    '''

    # Return the handler closure bound to the error resolver.
    def handler(error: Exception, **kwargs) -> Any:

        # Wrap bare exceptions in a TiferetError before processing.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                'APP_ERROR',
                f'An error occurred in the app: {str(error)}',
                error=str(error),
            )

        # Resolve the Error domain object and the registered ErrorContext.
        error_domain = get_error_handler(error.error_code)
        error_context_cls = BaseContext.for_domain(Error)
        error_context = error_context_cls()

        # Format the structured response and raise the API error.
        formatted = error_context.format_response(error_domain, error)
        raise TiferetAPIError(**formatted)

    # Return the closure.
    return handler

# ** blueprint: response_handler
def response_handler(request: RequestContext) -> Any:
    '''
    Pure response-building function delegating to the request context.

    :param request: The request context object.
    :type request: RequestContext
    :return: The response.
    :rtype: Any
    '''

    # Delegate directly to the request context.
    return request.handle_response()

# ** blueprint: build_app_session_context
def build_app_session_context(app_session: AppSession, cache: CacheContext, **context_kwargs) -> AppSessionContext:
    '''
    Compose a fully wired AppSessionContext from a loaded app session.

    :param app_session: The loaded app session domain object.
    :type app_session: AppSession
    :param cache: The bootstrap cache.
    :type cache: CacheContext
    :param context_kwargs: Additional keyword arguments forwarded to the context constructor.
    :type context_kwargs: dict
    :return: The fully wired app session context.
    :rtype: AppSessionContext
    '''

    # Build the app service container and compose the service resolver.
    app_container = build_app_service_container(cache, app_session)
    resolver = build_service_resolver(app_container)

    # Build the five template-method handlers.
    handlers = dict(
        build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
        execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
        raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
        response_handler=response_handler,
        create_request_handler=create_session_request,
    )

    # Resolve any remaining injectable collaborators the context class declares.
    collaborators = resolve_collaborators(AppSessionContext, app_container)

    # Construct and return the wired app session context.
    return AppSessionContext.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        **handlers,
        **collaborators,
        **context_kwargs,
    )

# ** blueprint: build_app
def build_app(interface_id: str,
        module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
        class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
        **parameters) -> AppSessionContext:
    '''
    Build a fully resolved application session context in a single call.

    No apply_defaults call occurs on this path; all framework defaults come
    from the cache seeded by build_cache. Raises APP_SESSION_NOT_FOUND when
    the session is absent (via get_app_session), never resolve_default_interface.

    :param interface_id: The interface identifier to load.
    :type interface_id: str
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The fully wired application session context.
    :rtype: AppSessionContext
    '''

    # Build the bootstrap cache pre-seeded with all framework defaults.
    cache = build_cache()

    # Resolve the app session, preferring a cache-seeded default.
    app_session = get_app_session(interface_id, cache, module_path=module_path, class_name=class_name, **parameters)

    # Build the fully wired app session context.
    context = build_app_session_context(app_session, cache)

    # Verify the resolved context is a valid AppSessionContext.
    if not isinstance(context, AppSessionContext):
        TiferetError.raise_error(
            a.error.INVALID_APP_SESSION_TYPE_ID,
            interface_id=interface_id,
        )

    # Return the validated app session context.
    return context
