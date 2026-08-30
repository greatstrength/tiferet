"""Tiferet Admin Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from .. import assets as a
from ..assets import TiferetError
from ..contexts.app import (
    ADMIN_CONSTANT_CACHE_PREFIX,
    ADMIN_SERVICE_CACHE_PREFIX,
    AppSession,
    AppSessionContext,
    add_default_admin_constants,
    add_default_admin_services,
)
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..contexts.feature import add_default_features
from ..di import DIAppServiceContainer, DIDynamicServiceResolver
from ..di.core import ServiceResolver
from . import core

# *** blueprints

# ** blueprint: build_cache
@add_default_admin_services(a.app.ADMIN_DEFAULT_SERVICES)
@add_default_admin_constants(a.app.ADMIN_DEFAULT_CONSTANTS)
@add_default_features(a.feat.ADMIN_DEFAULT_FEATURES)
@add_default_errors(a.error.ADMIN_DEFAULT_ERRORS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the admin bootstrap cache, pre-seeded with admin catalogs over the
    core framework defaults.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any] | None
    :return: The pre-seeded admin cache context.
    :rtype: CacheContext
    '''

    # Delegate to the core cache builder; stacked decorators seed admin catalogs.
    return core.build_cache(cache=cache)

# ** blueprint: build_admin_service_resolver
def build_admin_service_resolver(app_container: DIAppServiceContainer,
        cache: CacheContext,
        parse_parameter: Callable = core.parse_parameter) -> ServiceResolver:
    '''
    Compose the admin feature-level service resolver.

    Registers the app service container under the ``'app'`` flag and the admin
    container under both the ``'admin'`` flag and as the empty-flag default so
    admin-scoped feature steps resolve without an explicit flag.

    :param app_container: The built app service container.
    :type app_container: DIAppServiceContainer
    :param cache: The admin bootstrap cache holding admin services and constants.
    :type cache: CacheContext
    :param parse_parameter: The parameter-parsing callable injected into the resolver.
    :type parse_parameter: Callable
    :return: The composed admin service resolver.
    :rtype: ServiceResolver
    '''

    # Resolve the DI repository service from the app container.
    di_service = app_container.get_dependency('di_service')

    # Build the admin container from cache-seeded admin services and constants.
    admin_container = DIAppServiceContainer.from_dependencies(
        services=list(cache.get_by_prefix(*ADMIN_SERVICE_CACHE_PREFIX).values()),
        constants={
            **cache.get_by_prefix(*ADMIN_CONSTANT_CACHE_PREFIX),
            'load_cache': core.load_cache(cache),
        },
    )

    # Construct the dynamic service resolver with the injected parameter parser.
    resolver = DIDynamicServiceResolver(
        di_service=di_service,
        parse_parameter=parse_parameter,
    )

    # Register the app service container under the 'app' flag.
    resolver.add_container(app_container, 'app')

    # Register the admin container under the 'admin' flag and as the default.
    resolver.add_container(admin_container, 'admin')
    resolver.add_container(admin_container)

    # Return the composed resolver.
    return resolver

# ** blueprint: build_admin_app_session_context
def build_admin_app_session_context(app_session: AppSession,
        cache: CacheContext,
        **context_kwargs) -> AppSessionContext:
    '''
    Compose a fully wired admin AppSessionContext from a loaded app session.

    Mirrors core.build_app_session_context, substituting the admin service
    resolver so feature steps resolve from the admin container by default.

    :param app_session: The loaded app session domain object.
    :type app_session: AppSession
    :param cache: The admin bootstrap cache.
    :type cache: CacheContext
    :param context_kwargs: Additional keyword arguments forwarded to the context constructor.
    :type context_kwargs: dict
    :return: The fully wired admin app session context.
    :rtype: AppSessionContext
    '''

    # Build the app service container and compose the admin service resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = build_admin_service_resolver(app_container, cache)

    # Build the five template-method handlers.
    handlers = dict(
        build_logger_handler=core.build_logger_handler(cache, resolver.get_dependency),
        execute_feature_handler=core.execute_feature_handler(resolver.get_dependency, cache),
        raise_error_handler=core.raise_error_handler(core.get_error(cache, resolver.get_dependency)),
        response_handler=core.response_handler,
        create_request_handler=core.create_session_request,
    )

    # Resolve any remaining injectable collaborators the context class declares.
    collaborators = core.resolve_collaborators(AppSessionContext, app_container)

    # Construct and return the wired admin app session context.
    return AppSessionContext.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        **handlers,
        **collaborators,
        **context_kwargs,
    )

# ** blueprint: build_admin_app
def build_admin_app(interface_id: str = a.app.TIFERET_ADMIN_ID,
        **parameters: Any) -> AppSessionContext:
    '''
    Build a fully resolved admin application session context in a single call.

    The built-in admin session is cache-seeded by CORE_DEFAULT_APP_SESSIONS, so
    no consumer config entry is required for the default interface id.

    :param interface_id: The interface identifier to load; defaults to the admin session id.
    :type interface_id: str
    :param parameters: Additional parameters forwarded to get_app_session.
    :type parameters: dict
    :return: The fully wired admin application session context.
    :rtype: AppSessionContext
    '''

    # Build the admin bootstrap cache pre-seeded with admin and core defaults.
    cache = build_cache()

    # Resolve the app session, preferring a cache-seeded default.
    app_session = core.get_app_session(interface_id, cache, **parameters)

    # Build the fully wired admin app session context.
    app_session_context = build_admin_app_session_context(app_session, cache)

    # Verify the resolved context is a valid AppSessionContext.
    if not isinstance(app_session_context, AppSessionContext):
        TiferetError.raise_error(
            a.error.INVALID_APP_SESSION_TYPE_ID,
            f'App context for session is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated admin app session context.
    return app_session_context

# ** blueprint: admin_app (alias)
AdminApp = build_admin_app
