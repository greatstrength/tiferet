"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from ..assets import TiferetError, TiferetAPIError
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors, ERROR_CACHE_PREFIX
from ..contexts.feature import (
    Feature,
    FeatureContext,
    FEATURE_CACHE_PREFIX,
    add_default_features,
)
from ..contexts.request import RequestContext
from ..contexts.settings import BaseContext
from ..contexts.app import (
    AppSession,
    AppSessionContext,
    AppServiceDependency,
    add_default_app_services,
    add_default_app_constants,
    get_default_app_services,
    get_default_app_constants,
)
from ..domain import Error
from ..events import DomainEvent, ParseParameter, RaiseError
from ..events.app import GetAppSession
from ..di import DIAppServiceContainer, DIDynamicServiceContainer, injectable_parameter_names
from ..di.core import ServiceResolver
from ..di.dependency_injector import DIDynamicServiceResolver
from .. import assets as a

# *** blueprints

# ** blueprint: build_cache
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
# ++ todo: default app sessions are not yet cache-seeded; the `cache` param is a
#    seam for future default-session-from-cache resolution and to establish the
#    build ordering used by build_app.
def get_app_session(
    interface_id: str,
    cache: CacheContext = None,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters,
):
    '''
    Retrieve an app session by id, composing the app service dependency first.

    Composes the ``app_service`` dependency via :func:`create_app_service`, then
    retrieves the requested session through the ``GetAppSession`` domain event,
    which raises ``APP_SESSION_NOT_FOUND`` when the session is absent — so no
    built-in fallback belongs here. Any keyword arguments are forwarded as the
    app service constructor parameters (e.g. ``app_config='config.yml'``); when
    omitted, :func:`create_app_service` applies the framework default
    parameters. The ``cache`` argument is a build-ordering seam reserved for
    future default-session-from-cache resolution; it is not consumed yet.

    :param interface_id: The id of the app session to retrieve.
    :type interface_id: str
    :param cache: The shared cache context; a seam for future default-session resolution.
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

    # Compose the app service via a single-use container.
    app_service = create_app_service(module_path, class_name, parameters)

    # Retrieve the session via the GetAppSession event.
    return DomainEvent.handle(
        GetAppSession,
        dependencies=dict(app_service=app_service),
        interface_id=interface_id,
    )

# ** blueprint: get_app_interface (obsolete)
# -- obsolete: superseded by get_app_session; remove at v2.0.0 stable
get_app_interface = get_app_session

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

    Thin blueprint-layer wrapper over the ParseParameter static event so the DI
    resolver receives its parser from the blueprint layer rather than importing
    the event directly.

    :param parameter: The parameter value to parse.
    :type parameter: str
    :return: The parsed parameter value.
    :rtype: Any
    '''

    # Delegate to the ParseParameter static event.
    return ParseParameter.execute(parameter)

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
    feature: Feature,
    data: Dict[str, Any] = None,
    headers: Dict[str, str] = None,
    **kwargs,
) -> RequestContext:
    '''
    Compose a request context for a feature execution.

    Pure, side-effect-free constructor that seeds the request's ``feature_id``
    from the feature and wires in the supplied data and headers. Suitable as
    the hub's injected request-context factory.

    :param feature: The feature being executed; supplies the feature id.
    :type feature: Feature
    :param data: The request data payload.
    :type data: Dict[str, Any] | None
    :param headers: The request headers.
    :type headers: Dict[str, str] | None
    :param kwargs: Additional request context constructor arguments.
    :type kwargs: dict
    :return: The composed request context.
    :rtype: RequestContext
    '''

    # Compose and return the request context, seeding feature_id from the feature.
    return RequestContext(
        headers=headers,
        data=data,
        feature_id=feature.id,
        **kwargs,
    )

# ** blueprint: create_feature_context
def create_feature_context(
    get_dependency: Callable,
    cache: CacheContext,
    feature: Feature = None,
    feature_id: str = None,
) -> tuple[Feature, FeatureContext]:
    '''
    Compose a feature context, loading the feature when only an id is given.

    Accepts either a pre-loaded ``Feature`` or a ``feature_id``; when only the
    id is supplied the feature is loaded via the ``get_feature`` handler bound
    to the shared cache and service resolver. Returns the ``(feature,
    feature_context)`` pair so callers get both without knowing the loading
    internals.

    :param get_dependency: The service-resolution handler from the ServiceResolver.
    :type get_dependency: Callable
    :param cache: The shared cache context.
    :type cache: CacheContext
    :param feature: A pre-loaded feature domain object, if available.
    :type feature: Feature | None
    :param feature_id: The feature id to load when no feature is supplied.
    :type feature_id: str | None
    :return: The loaded feature and its composed feature context.
    :rtype: tuple[Feature, FeatureContext]
    '''

    # Load the feature via the get_feature handler when only an id is given.
    if feature is None:
        feature = get_feature(cache, get_dependency)(feature_id)

    # Compose the feature context with the resolver handler and shared cache.
    feature_context = FeatureContext(get_dependency=get_dependency, cache=cache)

    # Return the feature and its composed context.
    return feature, feature_context

# ** blueprint: create_session_request
def create_session_request(
    interface_id: str,
    feature_id: str,
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None,
) -> RequestContext:
    '''
    Compose a session request context for the hub's ``run`` method.

    Pure, side-effect-free constructor that enriches the supplied headers with
    the ``interface_id`` and constructs a ``RequestContext`` seeded with the
    ``feature_id``. Unlike :func:`create_request_context`, this variant takes
    string scalars so it can be called before the feature is loaded, matching
    the hub's current construction order.

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

    # Compose and return the request context, enriching headers with the interface id.
    return RequestContext(
        headers={**(headers or {}), 'interface_id': interface_id},
        data=data,
        feature_id=feature_id,
    )

# ** blueprint: execute_feature_handler
def execute_feature_handler(
    get_dependency: Callable,
    cache: CacheContext,
) -> Callable:
    '''
    Build the hub's feature-execution callable, bound to the service resolver
    and shared cache.

    Returns a void callable that loads the feature via
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

        # Load the feature and compose the feature context.
        feature, feature_context = create_feature_context(
            get_dependency, cache, feature_id=feature_id
        )

        # Drive execution; result is accumulated on the request context.
        feature_context.execute_feature(feature, request, *flags, **kwargs)

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
    raises — it never returns, echoing the ``RaiseError`` convention.

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
                'APP_ERROR',
                f'An error occurred: {str(error)}',
                error=str(error),
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
    and interface overrides, composes the feature-level resolver, imports the
    declared context class, resolves its event collaborators from the app
    container, wires the four FE4 template-method handlers, and constructs the
    context via the ``BaseContext.from_domain`` factory (inherited by any
    context subclass).

    All three hub event collaborators (``get_feature_evt``,
    ``get_error_evt``, ``logging_list_all_evt``) are in
    ``CORE_DEFAULT_SERVICES`` and are picked up automatically by the
    collaborator-resolution loop. Custom contexts (e.g. ``CliContext``) gain
    their additional collaborators the same way.

    :param app_session: The resolved app session definition with defaults applied.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context (errors, services, constants seeded).
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
    # Skip the explicitly supplied resolver, cache, handler params, and bootstrap defaults.
    reserved = {
        'get_dependency',
        'cache',
        'execute_feature_handler',
        'create_request_handler',
        'raise_error_handler',
        'response_handler',
    }
    collaborators = {
        name: app_container.get_dependency(name)
        for name in injectable_parameter_names(context_cls)
        if name not in reserved
        and not name.startswith('default_')
        and app_container.has_dependency(name)
    }

    # Build the four FE4 template-method handlers.
    handlers = dict(
        execute_feature_handler=execute_feature_handler(resolver.get_dependency, cache),
        create_request_handler=create_session_request,
        raise_error_handler=raise_error_handler(get_error(cache, resolver.get_dependency)),
        response_handler=response_handler,
    )

    # Construct the context via from_domain, injecting the resolver handler,
    # cache, all collaborators, and the four FE4 handlers.
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
        RaiseError.execute(
            a.const.INVALID_APP_SESSION_TYPE_ID,
            f'App context for session is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated app session context.
    return app_session_context
