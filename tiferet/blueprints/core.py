"""Tiferet Core Blueprints"""

# *** imports

# ** core
import logging
import os
from typing import Any, Callable, Dict, Tuple

# ** app
from .. import a
from ..assets import TiferetAPIError, TiferetError
from ..contexts.app import (
    APP_CONSTANT_CACHE_PREFIX,
    APP_SERVICE_CACHE_PREFIX,
    APP_SESSION_CACHE_PREFIX,
    AppServiceDependency,
    AppSession,
)
from ..contexts.cache import CacheContext
from ..contexts.core import BaseContext
from ..contexts.error import Error, ERROR_CACHE_PREFIX
from ..contexts.feature import Feature, FeatureContext, FEATURE_CACHE_PREFIX
from ..contexts.logging import (
    LOGGER_CACHE_PREFIX,
    LoggingContext,
    LoggingSettings,
    get_default_logging_settings,
)
from ..contexts.request import RequestContext
from ..events import DomainEvent
from ..events.app import GetAppSession
from ..di import DIAppServiceContainer, DIDynamicServiceContainer, DIDynamicServiceResolver
from ..di.core import ServiceResolver

# *** functions

# ** function: compose_session_context
def compose_session_context(
        context_cls: type,
        app_session: AppSession,
        cache: CacheContext,
        resolver: ServiceResolver,
        create_request_handler: Callable,
        response_handler: Callable,
        **extra_kwargs) -> Any:
    '''
    Compose a session context from a pre-built resolver.

    Wires the three resolver-derived handlers (build_logger_handler,
    execute_feature_handler, raise_error_handler) plus the caller-supplied
    request/response handler pair, and constructs the context via from_domain.
    A new context slot is an explicit handler or extra_kwargs, not a
    constructor name matched to a service id.
    The caller supplies the pre-built resolver so this function stays
    agnostic to which resolver-composition strategy (core vs admin) produced
    it, and to which context class (AppSessionContext vs CliSessionContext)
    is being constructed.

    :param context_cls: The context class to construct (AppSessionContext or
        CliSessionContext).
    :type context_cls: type
    :param app_session: The loaded app session domain object.
    :type app_session: AppSession
    :param cache: The bootstrap cache.
    :type cache: CacheContext
    :param resolver: The composed service resolver (core or admin).
    :type resolver: ServiceResolver
    :param create_request_handler: The request-construction handler to wire.
    :type create_request_handler: Callable
    :param response_handler: The response-building handler to wire.
    :type response_handler: Callable
    :param extra_kwargs: Additional keyword arguments forwarded to the
        context constructor (e.g. parse_cli_args, or caller context_kwargs).
    :type extra_kwargs: dict
    :return: The fully wired session context.
    :rtype: Any
    '''

    # Construct and return the fully wired session context.
    return context_cls.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
        execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
        raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
        response_handler=response_handler,
        create_request_handler=create_request_handler,
        **extra_kwargs,
    )

# ** function: merge_logging_settings
def merge_logging_settings(cache: CacheContext,
        formatters: list,
        handlers: list,
        loggers: list) -> LoggingSettings:
    '''
    Merge repository-configured logging sections over cache-seeded defaults.

    Each section is keyed by ``.id``; repository entries override the default
    sharing their id, and unmatched defaults survive. A missing section is
    treated as empty. Tolerates a cache with no seeded defaults.

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

    # Treat a missing section as empty before merging by id.
    formatters = formatters or []
    handlers = handlers or []
    loggers = loggers or []

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

# ** function: add_default_catalog
def add_default_catalog(items: Dict[str, Any],
        prefix: Tuple[str, ...],
        model: type = None,
        id_field: str = None) -> Callable:
    '''
    Decorator factory that pre-seeds one catalog onto the cache the wrapped builder returns.

    Omitting model caches the raw value, and omitting id_field does not reinject the dict key.

    :param items: The catalog entries, keyed by cache id.
    :type items: Dict[str, Any]
    :param prefix: The cache prefix the entries are stored under.
    :type prefix: Tuple[str, ...]
    :param model: Optional model type. Omitting it caches the raw value.
    :type model: type
    :param id_field: Optional id field name. Omitting it does not reinject the dict key.
    :type id_field: str
    :return: A decorator wrapping a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then seed each catalog entry under the prefix.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Build the cache the wrapped builder returns.
            cache = build_fn(*args, **kwargs)

            # Seed each catalog entry, validating when a model is supplied.
            for key, data in items.items():
                if model is not None and id_field:
                    payload = {**data, id_field: key}
                    value = model.model_validate(payload)
                elif model is not None:
                    value = model.model_validate(data)
                else:
                    value = data

                cache.set(key, value, *prefix)

            # Return the seeded cache.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# *** blueprints

# ** blueprint: build_cache
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build a bare CacheContext, independent of an interface and of any default catalog.

    An optional dict pre-seeds the root namespace. Dialect builders stack their
    own catalog decorators.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The bare cache context.
    :rtype: CacheContext
    '''

    # Construct the bare cache context.
    return CacheContext(cache=cache)

# ** blueprint: create_app_service
def create_app_service(module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
        class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
        parameters: Dict[str, Any] = None,
        service_container: type = DIDynamicServiceContainer) -> Any:
    '''
    Import and construct the app service used to resolve app sessions.

    :param module_path: The module path of the app service implementation.
        Defaults to the framework app service module path.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
        Defaults to the framework app service class name.
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
        'app_service': AppServiceDependency(
            service_id='app_service',
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
    # Prefix names stay on the context module until the assets prefix slice lands.
    if cache is not None:
        cached_session = cache.get(interface_id, *APP_SESSION_CACHE_PREFIX)
        if cached_session is not None:
            return cached_session

    # On a cache miss, compose the app service and resolve the session through the event.
    app_service = create_app_service(module_path, class_name, parameters)
    return DomainEvent.handle(
        GetAppSession,
        dependencies=dict(app_service=app_service),
        id=interface_id,
    )

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

        # Return the cached error when already resolved. A falsy value is a miss.
        cached = cache.get(error_code, *ERROR_CACHE_PREFIX)
        if cached:
            return cached

        # Resolve and execute the get_error event on a cache miss.
        get_error_evt = get_dependency('get_error_evt', 'app')
        error = get_error_evt.execute(error_code)

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

        # Return the cached feature when already resolved. A falsy value is a miss.
        cached = cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        if cached:
            return cached

        # Resolve and execute the get_feature event on a cache miss.
        get_feature_evt = get_dependency('get_feature_evt', 'app')
        feature = get_feature_evt.execute(id=feature_id)

        # Cache the resolved feature and return it.
        cache.set(feature_id, feature, *FEATURE_CACHE_PREFIX)
        return feature

    # Return the closure.
    return handler

# ** blueprint: create_logging_context
def create_logging_context(settings: LoggingSettings, logger_id: str) -> LoggingContext:
    '''
    Pure factory for an already-assembled LoggingSettings. Merging is the caller's job.

    :param settings: The assembled logging settings.
    :type settings: LoggingSettings
    :param logger_id: The logger id to bind.
    :type logger_id: str
    :return: The logging context bound to the settings.
    :rtype: LoggingContext
    '''

    # Bind the settings without reading the cache or resolving a dependency.
    return LoggingContext.from_domain(settings, logger_id=logger_id)

# ** blueprint: build_logger_handler
def build_logger_handler(cache: CacheContext, get_dependency: Callable) -> Callable:
    '''
    Build a logger-construction handler that caches loggers by logger id.

    On a cache hit under ``LOGGER_CACHE_PREFIX``, the previously built logger
    is returned. On a miss, repository logging configs are listed, merged over
    cache-seeded defaults, applied via ``create_logging_context``, and cached
    so ``dictConfig`` runs once per logger id per process. A ``ServiceError``
    from the list-all lookup or its execute falls back to empty repository
    sections. Any other exception propagates.

    :param cache: The bootstrap cache used for lazy logger caching.
    :type cache: CacheContext
    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A handler closure resolving a logger by logger id.
    :rtype: Callable
    '''

    # Return the handler closure bound to the cache and resolver.
    def handler(logger_id: str) -> logging.Logger:

        # Return the cached logger when already built for this id.
        cached = cache.get(logger_id, *LOGGER_CACHE_PREFIX)
        if cached:
            return cached

        # List repository sections, falling back when the event is a ServiceError.
        formatters, handlers, loggers = [], [], []
        try:
            list_all_evt = get_dependency('logging_list_all_evt', 'app')
            formatters, handlers, loggers = list_all_evt.execute()

        # A ServiceError is a composition miss; any other exception propagates.
        except Exception as err:
            if type(err).__name__ != 'ServiceError':
                raise

        # Merge repository configs over cache-seeded defaults and build the logger.
        settings = merge_logging_settings(cache, formatters, handlers, loggers)
        logger = create_logging_context(settings, logger_id=logger_id).build_logger()

        # Cache the built logger and return it.
        cache.set(logger_id, logger, *LOGGER_CACHE_PREFIX)
        return logger

    # Return the closure.
    return handler

# ** blueprint: build_app_service_container
def build_app_service_container(cache,
        app_instance: AppSession = None,
        service_container: type = DIAppServiceContainer) -> DIAppServiceContainer:
    '''
    Build the singleton app service container from cache-seeded defaults
    merged with the session's own service and constant overrides.

    Session overrides are merged with the cache defaults before building the
    container (not layered afterward), so session constants reach all
    default services the session does not redeclare. A session constant may
    overwrite ``load_cache``.

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

    # Start from cache defaults and register the shared cache-snapshot closure.
    # Prefix names stay on the context module until the assets prefix slice lands.
    constants = {
        **cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX),
        'load_cache': load_cache(cache),
    }

    # Let session constants overwrite defaults, including load_cache.
    if app_instance is not None:
        constants.update(app_instance.constants or {})

    # Start from cache-seeded services, keyed by service id.
    services = {
        dep.service_id: dep
        for dep in cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX).values()
    }

    # Let each session service replace the entry with the same service id.
    if app_instance is not None:
        for dep in app_instance.services or []:
            services[dep.service_id] = dep

    # Build and return the app service container from the merged dependencies.
    return service_container.from_dependencies(
        services=list(services.values()),
        constants=constants,
    )

# ** blueprint: parse_parameter
def parse_parameter(parameter: str) -> Any:
    '''
    Parse a configuration parameter value, resolving environment references.

    Resolves ``$env.``-prefixed values from the process environment and returns
    any other value unchanged. Parameter parsing is owned by the blueprint layer
    and injected into both the DI resolver and FeatureContext.

    :param parameter: The parameter value to parse.
    :type parameter: str
    :return: The parsed parameter value.
    :rtype: Any
    '''

    # Resolve the parameter, wrapping any failure in a structured error.
    try:

        # Resolve an environment reference from the process environment.
        if parameter.startswith(a.core.ENV_VAR_PREFIX):
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
        feature: Feature = None,
        feature_id: str = None) -> FeatureContext:
    '''
    Resolve a Feature domain object and bind it to a fresh FeatureContext.

    A positional third argument is the feature, not the feature id. Callers
    that have only an id must pass feature_id as a keyword.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :param cache: The bootstrap cache used for lazy feature caching.
    :type cache: CacheContext
    :param feature: An already-loaded feature. Loaded by id when omitted.
    :type feature: Feature
    :param feature_id: The identifier of the feature to resolve when feature is omitted.
    :type feature_id: str
    :return: The feature context bound to the resolved feature domain object.
    :rtype: FeatureContext
    '''

    # Load the feature only when the caller did not pass one.
    if feature is None:
        feature = get_feature(cache, get_dependency)(feature_id)

    # Construct and return the feature context bound to the resolved feature.
    return FeatureContext.from_domain(
        feature,
        get_dependency=get_dependency,
        cache=cache,
        parse_parameter=parse_parameter,
    )

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

        # Resolve the feature-bound context by id.
        feature_context = create_feature_context(
            get_dependency,
            cache,
            feature_id=feature_id,
        )

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
    def handler(error: Exception, **kwargs) -> None:

        # Wrap bare exceptions in a TiferetError before processing.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                a.error.APP_ERROR_ID,
                f'An error occurred: {str(error)}',
                error_message=str(error),
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
