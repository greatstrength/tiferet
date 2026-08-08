"""Tiferet Core Blueprints"""

# *** imports

# ** core
import logging
import os
from typing import Any, Callable, Dict

# ** app
from ..assets import TiferetError, TiferetAPIError
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors, ERROR_CACHE_PREFIX, Error
from ..contexts.feature import (
    Feature,
    FeatureContext,
    FEATURE_CACHE_PREFIX,
)
from ..contexts.logging import (
    add_default_logging_settings,
    get_default_logging_settings,
    LoggingContext,
    LoggingSettings,
    LOGGER_CACHE_PREFIX,
)
from ..contexts.request import RequestContext
from ..contexts.core import BaseContext
from ..contexts.app import (
    AppSession,
    AppSessionContext,
    AppServiceDependency,
    add_default_app_services,
    add_default_app_constants,
    add_default_app_sessions,
    get_default_app_services,
    get_default_app_constants,
    get_default_app_session,
)
from ..di import DIAppServiceContainer, DIDynamicServiceContainer, injectable_parameter_names
from ..di.core import ServiceResolver
from ..di.dependency_injector import DIDynamicServiceResolver
from .. import assets as a

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
    parameters the session context builders supply explicitly
    (``RESERVED_CONTEXT_PARAMETERS``) and the bootstrap ``default_*``
    parameters. This is the seam that lets a context subclass declare extra
    collaborators and have them wired declaratively.

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
def merge_logging_settings(
    cache: CacheContext,
    formatters: list,
    handlers: list,
    loggers: list,
) -> LoggingSettings:
    '''
    Merge repository-supplied logging sections over cache-seeded defaults by id.

    Loads the cache-seeded ``LoggingSettings`` defaults (tolerating a cache with
    none seeded), then merges each retrieved section over its matching default
    section keyed by id, so a repository entry overrides only the default
    sharing its id while unmatched defaults survive.

    :param cache: The shared cache context pre-seeded with default LoggingSettings.
    :type cache: CacheContext
    :param formatters: The repository-supplied formatter definitions.
    :type formatters: list
    :param handlers: The repository-supplied handler definitions.
    :type handlers: list
    :param loggers: The repository-supplied logger definitions.
    :type loggers: list
    :return: The merged LoggingSettings domain object.
    :rtype: LoggingSettings
    '''

    # Load the cache-seeded defaults, tolerating a cache with none seeded.
    defaults = get_default_logging_settings(cache)
    default_formatters = defaults.formatters if defaults else []
    default_handlers = defaults.handlers if defaults else []
    default_loggers = defaults.loggers if defaults else []

    # Merge the retrieved configs over the defaults keyed by id, so a repository
    # entry overrides only the default sharing its id.
    merged_formatters = {formatter.id: formatter for formatter in default_formatters}
    merged_formatters.update({formatter.id: formatter for formatter in (formatters or [])})
    merged_handlers = {handler.id: handler for handler in default_handlers}
    merged_handlers.update({handler.id: handler for handler in (handlers or [])})
    merged_loggers = {logger.id: logger for logger in default_loggers}
    merged_loggers.update({logger.id: logger for logger in (loggers or [])})

    # Return the merged LoggingSettings domain object.
    return LoggingSettings(
        formatters=list(merged_formatters.values()),
        handlers=list(merged_handlers.values()),
        loggers=list(merged_loggers.values()),
    )

# *** blueprints

# ** blueprint: build_cache
@add_default_logging_settings(a.logging.CORE_DEFAULT_LOGGING_SETTINGS)
@add_default_app_sessions(a.app.CORE_DEFAULT_APP_SESSIONS)
@add_default_app_constants(a.app.CORE_DEFAULT_CONSTANTS)
@add_default_app_services(a.app.CORE_DEFAULT_SERVICES)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build a standalone cache context for managing in-memory cache operations.

    Constructs a ``CacheContext`` independently of any interface or service
    resolver, then pre-seeds it with the framework's built-in catalogs via the
    stacked seeding decorators: error domain objects (``add_default_errors``),
    app service dependency domain objects (``add_default_app_services``), and
    scalar bootstrap constants (``add_default_app_constants``). Each catalog is
    namespaced under its own cache-key prefix (``error_``, ``app_service_``,
    ``app_constant_``). Pass an existing dict to seed the cache with additional
    pre-populated values; omit it to start with a fresh empty cache.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized cache context seeded with errors, services, and constants.
    :rtype: CacheContext
    '''

    # Construct and return the cache context.
    return CacheContext(cache=cache)

# ** blueprint: create_app_service
def create_app_service(
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    parameters: Dict[str, Any] = None,
    service_container: type = DIDynamicServiceContainer,
) -> Any:
    '''
    Compose and return an app service instance via a single-use dynamic container.

    Describes the app service as a single id-keyed ``AppServiceDependency`` and
    resolves it through a function-scoped ``DIDynamicServiceContainer`` so its
    declared ``parameters`` are wired into the constructor by name (mirroring the
    legacy direct-import ``load_app_service``). When no parameters are supplied,
    the framework default (``a.app.DEFAULT_APP_SERVICE_PARAMETERS``) is used.

    :param module_path: The module path of the app service; defaults to the framework app repo.
    :type module_path: str
    :param class_name: The class name of the app service; defaults to AppConfigRepository.
    :type class_name: str
    :param parameters: The app service constructor parameters; defaults to the framework app service parameters.
    :type parameters: Dict[str, Any] | None
    :param service_container: The dynamic container class to compose with; defaults to DIDynamicServiceContainer.
    :type service_container: type
    :return: The composed app service instance.
    :rtype: Any
    '''

    # Fall back to the framework default parameters when none are supplied.
    parameters = parameters if parameters else a.app.DEFAULT_APP_SERVICE_PARAMETERS

    # Describe the app service as a single id-keyed dependency.
    service = AppServiceDependency(
        service_id='app_service',
        module_path=module_path,
        class_name=class_name,
        parameters=parameters,
    )

    # Build a single-use, function-scoped dynamic container to compose the app service.
    container = service_container(services={'app_service': service})

    # Resolve and return the composed app service instance.
    return container.get_dependency('app_service')

# ** blueprint: get_app_session
def get_app_session(
    interface_id: str,
    cache: CacheContext = None,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters,
):
    '''
    Retrieve an app session by id, checking the cache first then the config file.

    Checks the shared cache for a session seeded by the ``add_default_app_sessions``
    decorator (e.g. the built-in admin sessions).  When found, the cached
    ``AppSession`` is returned immediately without touching the config file.  When
    absent from the cache (or when no cache is provided), composes the
    ``app_service`` dependency via :func:`create_app_service` and retrieves the
    session through ``AppSessionContext.load``, which raises
    ``APP_SESSION_NOT_FOUND`` when the session is absent from the config file.
    Any keyword arguments are forwarded as the app service constructor parameters
    (e.g. ``app_config='config.yml'``).

    :param interface_id: The id of the app session to retrieve.
    :type interface_id: str
    :param cache: The shared cache context pre-seeded with default sessions.
    :type cache: CacheContext | None
    :param module_path: The module path of the app service; defaults to the framework app repo.
    :type module_path: str
    :param class_name: The class name of the app service; defaults to AppConfigRepository.
    :type class_name: str
    :param parameters: The app service constructor parameters.
    :type parameters: dict
    :return: The retrieved app session.
    :rtype: AppSession
    '''

    # Check the cache for a seeded default session (e.g. built-in admin sessions).
    if cache is not None:
        cached_session = get_default_app_session(cache, interface_id)
        if cached_session is not None:
            return cached_session

    # Compose the app service via a single-use container.
    app_service = create_app_service(module_path, class_name, parameters)

    # Retrieve the session from the config file via the AppSessionContext classmethod.
    return AppSessionContext.load(interface_id, app_service)

# ** blueprint: get_error
def get_error(
    cache: CacheContext,
    get_dependency: Callable,
) -> Callable:
    '''
    Build an error-retrieval handler with the shared cache and service
    resolver wired in.

    Returns a callable that, given an error code, first checks the shared
    cache under ``ERROR_CACHE_PREFIX``. On a miss, resolves a ``GetError``
    event instance from the app-scoped service container via
    ``get_dependency``, executes it to retrieve the ``Error`` domain
    object, caches the result under ``ERROR_CACHE_PREFIX``, and returns it.

    :param cache: The shared cache context pre-seeded with default errors.
    :type cache: CacheContext
    :param get_dependency: The service-resolution handler from the
        ServiceResolver.
    :type get_dependency: Callable
    :return: An error-retrieval callable bound to the cache and resolver.
    :rtype: Callable
    '''

    # Return the handler closure with cache and resolver wired in.
    def handler(error_code: str):

        # Try the shared cache first (pre-seeded with framework defaults).
        error = cache.get(error_code, *ERROR_CACHE_PREFIX)
        if error:
            return error

        # Resolve a GetError event instance from the app-scoped container.
        get_error_evt = get_dependency('get_error_evt', 'app')

        # Execute the event to retrieve the error domain object.
        error = get_error_evt.execute(error_code)

        # Cache the result under the error cache prefix.
        cache.set(error_code, error, *ERROR_CACHE_PREFIX)

        # Return the loaded error.
        return error

    return handler

# ** blueprint: get_feature
def get_feature(
    cache: CacheContext,
    get_dependency: Callable,
) -> Callable:
    '''
    Build a feature-retrieval handler with the shared cache and service
    resolver wired in.

    Returns a callable that, given a feature id, first checks the shared
    cache under ``FEATURE_CACHE_PREFIX``. On a miss, resolves a ``GetFeature``
    event instance from the app-scoped service container via
    ``get_dependency``, executes it to retrieve the ``Feature`` domain object,
    caches the result under ``FEATURE_CACHE_PREFIX``, and returns it.

    :param cache: The shared cache context.
    :type cache: CacheContext
    :param get_dependency: The service-resolution handler from the
        ServiceResolver.
    :type get_dependency: Callable
    :return: A feature-retrieval callable bound to the cache and resolver.
    :rtype: Callable
    '''

    # Return the handler closure with cache and resolver wired in.
    def handler(feature_id: str):

        # Try the shared cache first (under the feature cache prefix).
        feature = cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        if feature:
            return feature

        # Resolve a GetFeature event instance from the app-scoped container.
        get_feature_evt = get_dependency('get_feature_evt', 'app')

        # Execute the event to retrieve the feature domain object.
        feature = get_feature_evt.execute(id=feature_id)

        # Cache the result under the feature cache prefix.
        cache.set(feature_id, feature, *FEATURE_CACHE_PREFIX)

        # Return the loaded feature.
        return feature

    return handler

# ** blueprint: create_logging_context
def create_logging_context(
    settings: LoggingSettings,
    logger_id: str,
) -> LoggingContext:
    '''
    Construct a logging context from an already-assembled LoggingSettings.

    Pure factory with no cache or resolver dependency; merging repository
    configs over cache-seeded defaults is the caller's responsibility (see
    :func:`merge_logging_settings`).

    :param settings: The assembled logging settings domain object.
    :type settings: LoggingSettings
    :param logger_id: The ID of the logger to create for the session.
    :type logger_id: str
    :return: The constructed logging context bound to the given settings.
    :rtype: LoggingContext
    '''

    # Construct the LoggingContext via the BaseContext factory, injecting logger_id.
    return LoggingContext.from_domain(settings, logger_id=logger_id)

# ** blueprint: build_logger_handler
def build_logger_handler(
    cache: CacheContext,
    get_dependency: Callable,
) -> Callable:
    '''
    Build a logger-construction handler with the shared cache and service
    resolver wired in.

    Returns a callable that, given a logger id, first checks the shared cache
    under ``LOGGER_CACHE_PREFIX``. On a miss, resolves the
    ``logging_list_all_evt`` from the app-scoped service container, merges the
    retrieved sections over the cache-seeded defaults via
    :func:`merge_logging_settings`, builds the logger via
    :func:`create_logging_context`, caches the built logger under
    ``LOGGER_CACHE_PREFIX``, and returns it. The cache-first branch means
    ``dictConfig`` runs once per logger id per process rather than once per
    request.

    :param cache: The shared cache context pre-seeded with default LoggingSettings.
    :type cache: CacheContext
    :param get_dependency: The service-resolution handler from the
        ServiceResolver.
    :type get_dependency: Callable
    :return: A logger-construction callable bound to the cache and resolver.
    :rtype: Callable
    '''

    # Return the handler closure with cache and resolver wired in.
    def handler(logger_id: str) -> logging.Logger:

        # Try the shared cache first (under the logger cache prefix).
        logger = cache.get(logger_id, *LOGGER_CACHE_PREFIX)
        if logger:
            return logger

        # Resolve the list-all event from the app-scoped container.
        logging_list_all_evt = get_dependency('logging_list_all_evt', 'app')

        # Fetch repo configs and merge them over the cache-seeded defaults.
        formatters, handlers, loggers = logging_list_all_evt.execute()
        settings = merge_logging_settings(cache, formatters, handlers, loggers)

        # Build the logger and cache it under the logger cache prefix.
        logger = create_logging_context(settings, logger_id).build_logger()
        cache.set(logger_id, logger, *LOGGER_CACHE_PREFIX)

        # Return the built logger.
        return logger

    return handler

# ** blueprint: build_app_service_container
def build_app_service_container(
    cache: CacheContext,
    app_instance = None,
    service_container: type = DIAppServiceContainer,
) -> DIAppServiceContainer:
    '''
    Build the app-level service container from cache defaults merged with the
    interface's own constants and services.

    Merges the framework default services and constants seeded on the shared
    cache (by the app-context cache-key prefixes) with the ``app_instance``'s
    own constants and services (the interface wins), then builds the
    singleton-scoped container once from the merged result. Merging *before*
    the build — rather than layering overrides onto an already-built container
    — ensures every singleton, defaults included, wires to the final constant
    values, so an interface constant override reaches default services the
    interface does not redeclare (a constant swapped in after a singleton is
    built does not propagate to it; see the handoff wiring finding). The
    general-purpose cache loader is registered as the ``'load_cache'`` constant
    so ``build_singleton`` can wire it into ``CacheMiddleware`` via constructor
    inspection. When ``app_instance`` is ``None``, a defaults-only container is
    returned.

    :param cache: The shared cache context seeded with default services/constants.
    :type cache: CacheContext
    :param app_instance: The resolved application session definition, or None for defaults only.
    :type app_instance: AppSession | None
    :param service_container: The container class to build; defaults to DIAppServiceContainer.
    :type service_container: type
    :return: The loaded app service container.
    :rtype: DIAppServiceContainer
    '''

    # Merge default constants with the interface's own (interface wins), adding
    # the general-purpose cache loader so build_singleton can wire it into
    # CacheMiddleware by constructor inspection.
    constants = {
        **get_default_app_constants(cache),
        'load_cache': load_cache(cache),
    }
    if app_instance is not None:
        constants.update(app_instance.constants or {})

    # Merge default services with the interface's own, overriding defaults by
    # service id.
    services = {dep.service_id: dep for dep in get_default_app_services(cache)}
    if app_instance is not None:
        for service in (app_instance.services or []):
            services[service.service_id] = service

    # Build the singleton-scoped container once from the merged services and
    # constants. from_dependencies registers constants before services, so
    # every singleton wires to the final constant values.
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
    and injected into both the DI resolver and the FeatureContext, so neither
    reaches into the events layer to parse a parameter.

    :param parameter: The parameter value to parse.
    :type parameter: str
    :return: The parsed parameter value.
    :rtype: Any
    '''

    # Resolve the parameter, wrapping any failure in a structured error.
    try:

        # Resolve an environment reference from the process environment.
        if parameter.startswith('$env.'):
            result = os.getenv(parameter[5:])

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
def build_service_resolver(
    app_service_container: DIAppServiceContainer,
    parse_parameter: Callable = parse_parameter,
) -> ServiceResolver:
    '''
    Build the feature-level service resolver from a composed app service container.

    Resolves the DI service registration from the app service container, composes
    a concrete DIDynamicServiceResolver around it, then caches the same app
    service container on the resolver under the ``app`` flag so app-scoped
    services resolve through ``get_dependency(<id>, 'app')``.

    :param app_service_container: The composed app service container (defaults + interface overrides).
    :type app_service_container: DIAppServiceContainer
    :param parse_parameter: The parameter parser injected into the resolver; defaults to the blueprint parser.
    :type parse_parameter: Callable
    :return: The composed feature-level service resolver.
    :rtype: ServiceResolver
    '''

    # Resolve the DI service registration from the app service container.
    di_service = app_service_container.get_dependency('di_service')

    # Compose the concrete per-flag feature resolver, injecting the parameter parser.
    resolver = DIDynamicServiceResolver(
        di_service=di_service,
        parse_parameter=parse_parameter,
    )

    # Cache the app service container under the app flag so app-scoped
    # dependencies resolve through it.
    resolver.add_container(app_service_container, 'app')

    # Return the composed service resolver.
    return resolver

# ** blueprint: load_cache
def load_cache(cache: CacheContext) -> Callable[[], Dict[str, Any]]:
    '''
    Build a general-purpose cache-loader closure over the shared cache.

    Returns a zero-argument callable that yields a shallow snapshot of the
    cache's root namespace (``cache.get_by_prefix()``). The loader is
    general-purpose — not tied to any specific prefix — and is registered as
    the ``'load_cache'`` constant so it can be wired into ``CacheMiddleware``
    via constructor injection, keeping the utils layer decoupled from the
    cache context.

    :param cache: The shared cache context to snapshot on demand.
    :type cache: CacheContext
    :return: A zero-argument loader returning the root-namespace cache dict.
    :rtype: Callable[[], Dict[str, Any]]
    '''

    # Return a loader closure that snapshots the cache root namespace.
    def loader() -> Dict[str, Any]:

        # Return a shallow copy of the root-namespace cache dict.
        return cache.get_by_prefix()

    return loader

# ** blueprint: create_request_context
def create_request_context(
    interface_id: str,
    feature_id: str,
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None,
) -> RequestContext:
    '''
    Compose a request context for a feature execution.

    Pure, side-effect-free constructor that stamps the ``interface_id`` onto the
    request headers and seeds the request with the supplied ``feature_id`` and
    data. Takes string scalars so it can be called before the feature is
    loaded, matching the hub's construction order. Suitable as the hub's
    injected request-context factory.

    :param interface_id: The id of the app session issuing the request.
    :type interface_id: str
    :param feature_id: The id of the feature to execute.
    :type feature_id: str
    :param headers: Optional request headers to merge with the interface id.
    :type headers: Dict[str, str] | None
    :param data: Optional request data payload.
    :type data: Dict[str, Any] | None
    :return: The composed request context.
    :rtype: RequestContext
    '''

    # Compose and return the request context, stamping the interface id onto the headers.
    return RequestContext(
        headers={**(headers or {}), 'interface_id': interface_id},
        data=data or {},
        feature_id=feature_id,
    )

# ** blueprint: create_feature_context
def create_feature_context(
    get_dependency: Callable,
    cache: CacheContext,
    feature: Feature = None,
    feature_id: str = None,
) -> FeatureContext:
    '''
    Compose a feature context bound to its feature, loading the feature when
    only an id is given.

    Accepts either a pre-loaded ``Feature`` or a ``feature_id``; when only the
    id is supplied the feature is loaded via the ``get_feature`` handler bound
    to the shared cache and service resolver. The resolved feature is bound to
    the context as ``ctx.domain`` via ``FeatureContext.from_domain``, so callers
    reach it through the returned context rather than receiving it alongside.

    :param get_dependency: The service-resolution handler from the ServiceResolver.
    :type get_dependency: Callable
    :param cache: The shared cache context.
    :type cache: CacheContext
    :param feature: A pre-loaded feature domain object, if available.
    :type feature: Feature | None
    :param feature_id: The feature id to load when no feature is supplied.
    :type feature_id: str | None
    :return: The composed feature context with the feature bound as its domain.
    :rtype: FeatureContext
    '''

    # Load the feature via the get_feature handler when only an id is given.
    if feature is None:
        feature = get_feature(cache, get_dependency)(feature_id)

    # Compose the feature context via the registry factory, binding the resolved
    # feature as the context domain and wiring the resolver handler, shared
    # cache, and the blueprint-owned parameter parser.
    return FeatureContext.from_domain(
        feature,
        get_dependency=get_dependency,
        cache=cache,
        parse_parameter=parse_parameter,
    )

# ** blueprint: create_session_request
def create_session_request(
    interface_id: str,
    feature_id: str,
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None,
) -> RequestContext:
    '''
    Compose a session request context for the hub's ``run`` method.

    Backward-compatible alias for :func:`create_request_context`, retained as
    the name the hub's ``create_request_handler`` slot is wired to.

    :param interface_id: The interface id to inject into the request headers.
    :type interface_id: str
    :param feature_id: The feature id to seed on the request context.
    :type feature_id: str
    :param headers: Optional request headers to merge with the interface id.
    :type headers: Dict[str, str] | None
    :param data: Optional request data payload.
    :type data: Dict[str, Any] | None
    :return: The composed request context.
    :rtype: RequestContext
    '''

    # Delegate to the canonical request context factory.
    return create_request_context(interface_id, feature_id, headers, data)

# ** blueprint: execute_feature_handler
def execute_feature_handler(
    get_dependency: Callable,
    cache: CacheContext,
) -> Callable:
    '''
    Build the hub's feature-execution callable, bound to the service resolver
    and shared cache.

    Returns a void callable that composes a feature-bound context via
    :func:`create_feature_context` and drives
    ``FeatureContext.execute_feature``, accumulating the result on the
    request context. The handler is void — result extraction is the
    responsibility of the response step.

    :param get_dependency: The service-resolution handler from the ServiceResolver.
    :type get_dependency: Callable
    :param cache: The shared cache context.
    :type cache: CacheContext
    :return: A void execution callable bound to the resolver and cache.
    :rtype: Callable
    '''

    # Return the handler closure with the resolver and cache wired in.
    def handler(feature_id: str, request: RequestContext, *flags, **kwargs) -> None:

        # Compose the feature context with the loaded feature bound as its domain.
        feature_context = create_feature_context(
            get_dependency, cache, feature_id=feature_id
        )

        # Drive execution against the bound feature; the result is accumulated
        # on the request context.
        feature_context.execute_feature(request, *flags, **kwargs)

    return handler

# ** blueprint: raise_error_handler
def raise_error_handler(
    get_error_handler: Callable,
) -> Callable:
    '''
    Build an error-raising handler bound to an error-retrieval callable.

    Returns a callable that, given an error (``TiferetError`` or plain
    ``Exception``), retrieves the matching ``Error`` domain object via the
    supplied ``get_error_handler``, formats the response through an
    ``ErrorContext``, and raises ``TiferetAPIError``. Plain exceptions are
    wrapped in a ``TiferetError`` before formatting. The callable always
    raises — it never returns, echoing the ``TiferetError.raise_error`` convention.

    :param get_error_handler: An error-retrieval callable produced by
        :func:`get_error`.
    :type get_error_handler: Callable
    :return: An error-raising callable bound to the error retrieval handler.
    :rtype: Callable
    '''

    # Return the handler closure bound to the error retrieval handler.
    def handler(error: Exception, **kwargs) -> None:

        # Wrap plain exceptions in a TiferetError before formatting.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                a.error.APP_ERROR_ID,
                f'An error occurred: {str(error)}',
                error_message=str(error),
            )

        # Retrieve the error domain object via the error retrieval handler.
        error_domain = get_error_handler(error.error_code)

        # Resolve the error context class via the registry and format the response.
        error_context_cls = BaseContext.for_domain(Error)
        formatted_error = error_context_cls().format_response(error_domain, error)

        # Raise the API exception with the formatted payload.
        raise TiferetAPIError(**formatted_error)

    return handler

# ** blueprint: response_handler
def response_handler(request: RequestContext) -> Any:
    '''
    Extract the handled response from a completed request context.

    Pure, dependency-free function that delegates to
    ``request.handle_response()``. Stored directly on the hub as
    ``_build_response`` — no partial binding is needed. Subclasses override
    ``build_response`` to produce context-specific output (e.g. a
    ``CliContext`` serialises to stdout; a ``FlaskApiContext`` wraps in a JSON
    response).

    :param request: The completed request context.
    :type request: RequestContext
    :return: The handled feature response.
    :rtype: Any
    '''

    # Delegate to the request context's response handler.
    return request.handle_response()

# ** blueprint: build_app_session_context
def build_app_session_context(
    app_session: AppSession,
    cache: CacheContext,
    **context_kwargs,
) -> AppSessionContext:
    '''
    Build a fully wired app session context from a resolved app session.

    Chains the core building blocks to replace the legacy
    ``load_app_instance`` path: builds the app service container from defaults
    and interface overrides, composes the feature-level resolver, resolves any
    remaining event collaborators from the app container, wires the five
    template-method handlers, and constructs the context via the
    ``BaseContext.from_domain`` factory (inherited by any context subclass).

    ``logging_list_all_evt`` remains in ``CORE_DEFAULT_SERVICES`` but is not
    injected directly into the hub constructor; it is consumed lazily, on the
    first ``run()``, inside the ``build_logger_handler`` closure. Custom
    contexts (e.g. ``CliContext``) gain their additional collaborators via the
    same generic resolution loop.

    :param app_session: The resolved app session definition with defaults applied.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context (errors, services, constants, logging seeded).
    :type cache: CacheContext
    :param context_kwargs: Additional keyword arguments forwarded to the context constructor.
    :type context_kwargs: dict
    :return: The wired app session context.
    :rtype: AppSessionContext
    '''

    # Build the app service container from defaults and interface overrides.
    app_container = build_app_service_container(cache, app_session)

    # Build the feature-level resolver from the app container.
    resolver = build_service_resolver(app_container)

    # Hardcode the AppSessionContext class; blueprint functions are the declarative
    # owner of context class selection — the session's module_path / class_name
    # fields are no longer consulted at runtime (annotated obsolete).
    context_cls = AppSessionContext

    # Resolve the context's collaborators from the app container by id.
    collaborators = resolve_collaborators(context_cls, app_container)

    # Build the five template-method handlers.
    handlers = dict(
        build_logger_handler=build_logger_handler(cache, resolver.get_dependency),
        execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
        create_request_handler=create_session_request,
        raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
        response_handler=response_handler,
    )

    # Construct the context via from_domain, injecting the resolver handler,
    # cache, all collaborators, and the five handlers.
    return context_cls.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        **handlers,
        **collaborators,
        **context_kwargs,
    )

# ** blueprint: build_app
def build_app(
    interface_id: str,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters,
) -> AppSessionContext:
    '''
    Build a fully wired app session context in a single call.

    Orchestrates the core composition chain in fixed order: builds the shared
    cache (seeded with the framework default errors, services, and constants),
    resolves the requested app session via the ``GetAppSession`` event (which
    raises ``APP_SESSION_NOT_FOUND`` when the session is absent — the core path
    has no built-in default-session fallback), composes the wired
    ``AppSessionContext`` through :func:`build_app_session_context`, and
    validates the result type. All framework defaults come from the cache
    seeded by :func:`build_cache`; ``apply_defaults`` is never called here.
    This is the single-call entry point exported as ``App``.

    :param interface_id: The id of the app session to build.
    :type interface_id: str
    :param module_path: The module path of the app service; defaults to the framework app repo.
    :type module_path: str
    :param class_name: The class name of the app service; defaults to AppConfigRepository.
    :type class_name: str
    :param parameters: The app service constructor parameters (e.g. ``app_config='config.yml'``).
    :type parameters: dict
    :return: The fully wired app session context.
    :rtype: AppSessionContext
    '''

    # Build the shared cache (seeded with errors, services, and constants).
    cache = build_cache()

    # Resolve the app session; GetAppSession raises APP_SESSION_NOT_FOUND when absent.
    app_session = get_app_session(interface_id, cache, module_path, class_name, **parameters)

    # Compose the wired app session context via the core compose path.
    app_session_context = build_app_session_context(app_session, cache)

    # Verify that the composed context is a valid app session context.
    if not isinstance(app_session_context, AppSessionContext):
        TiferetError.raise_error(
            a.error.INVALID_APP_SESSION_TYPE_ID,
            f'App context for session is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated app session context.
    return app_session_context
