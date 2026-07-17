"""Tiferet Admin Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List

# ** app
from ..assets import RaiseError
from . import core
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..contexts.feature import add_default_features
from ..contexts.app import (
    AppSession,
    AppSessionContext,
    AppServiceDependency,
    add_default_admin_services,
    add_default_admin_constants,
    get_default_admin_services,
    get_default_admin_constants,
)
from ..di import injectable_parameter_names
from ..di.dependency_injector import DIAppServiceContainer, DIDynamicServiceResolver
from ..di.core import ServiceResolver
from .. import assets as a

# *** blueprints

# ** blueprint: build_cache
@add_default_admin_services(a.app.ADMIN_DEFAULT_SERVICES)
@add_default_admin_constants(a.app.ADMIN_DEFAULT_CONSTANTS)
@add_default_features(a.feat.ADMIN_DEFAULT_FEATURES)
@add_default_errors(a.error.ADMIN_DEFAULT_ERRORS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build an admin cache context pre-seeded with the full admin catalog.

    Stacks admin-layer seeding decorators on top of the core blueprint's
    ``build_cache``: admin errors (merged set), admin service dependencies,
    admin bootstrap constants, and admin feature definitions. The resulting
    cache gives the admin blueprints everything needed to build admin session
    contexts without touching a consumer config file.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized cache context seeded with the full admin catalog.
    :rtype: CacheContext
    '''

    # Delegate to the core blueprint to obtain the core-seeded cache.
    return core.build_cache(cache=cache)

# ** blueprint: build_admin_service_resolver
def build_admin_service_resolver(
    app_container: DIAppServiceContainer,
    cache: CacheContext,
    parse_parameter: Callable = core.parse_parameter,
) -> ServiceResolver:
    '''
    Build the feature-level service resolver with admin services alongside the
    standard app container.

    Parallel to :func:`core.build_service_resolver` but adds a second
    ``DIAppServiceContainer`` built from the admin service catalog seeded on
    the shared cache.  The admin container is registered under the ``'admin'``
    flag and also as the **default** (empty-flag) container so feature steps
    that specify no flag resolve admin events without requiring explicit flag
    annotations in the feature definition.

    :param app_container: The pre-built app-scoped service container.
    :type app_container: DIAppServiceContainer
    :param cache: The shared cache context pre-seeded with admin services and
        constants.
    :type cache: CacheContext
    :param parse_parameter: The parameter parser injected into the resolver;
        defaults to the blueprint parser.
    :type parse_parameter: Callable
    :return: The composed feature-level service resolver.
    :rtype: ServiceResolver
    '''

    # Resolve the DI service registration from the app service container.
    di_service = app_container.get_dependency('di_service')

    # Build the admin container from cache-seeded admin services and constants.
    admin_constants = {
        **get_default_admin_constants(cache),
        'load_cache': core.load_cache(cache),
    }
    admin_container = DIAppServiceContainer.from_dependencies(
        services=get_default_admin_services(cache),
        constants=admin_constants,
    )

    # Compose the concrete per-flag feature resolver.
    resolver = DIDynamicServiceResolver(
        di_service=di_service,
        parse_parameter=parse_parameter,
    )

    # Register the core app container under the 'app' flag.
    resolver.add_container(app_container, 'app')

    # Register the admin container under the 'admin' flag and as the
    # default (empty-flag) container so admin events resolve without flags.
    resolver.add_container(admin_container, 'admin')
    resolver.add_container(admin_container)  # default — empty flags

    # Return the composed service resolver.
    return resolver

# ** blueprint: build_admin_app_session_context
def build_admin_app_session_context(
    app_session: AppSession,
    cache: CacheContext,
    **context_kwargs,
) -> AppSessionContext:
    '''
    Build a fully wired admin app session context from a resolved app session.

    Parallel to :func:`core.build_app_session_context` but uses
    :func:`build_admin_service_resolver` in place of
    :func:`core.build_service_resolver`, so the feature-level resolver carries
    the admin service catalog alongside the standard app container.  In every
    other respect the construction is identical.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context seeded with the full admin
        catalog.
    :type cache: CacheContext
    :param context_kwargs: Additional keyword arguments forwarded to the context
        constructor.
    :type context_kwargs: dict
    :return: The wired admin app session context.
    :rtype: AppSessionContext
    '''

    # Build the app service container from defaults and interface overrides.
    app_container = core.build_app_service_container(cache, app_session)

    # Build the feature-level resolver using the admin resolver (adds admin container).
    resolver = build_admin_service_resolver(app_container, cache)

    # Hardcode the context class; the admin app path always uses AppSessionContext.
    context_cls = AppSessionContext

    # Resolve the context's collaborators from the app container by id.
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
        execute_feature_handler=core.execute_feature_handler(resolver.get_dependency, cache),
        create_request_handler=core.create_session_request,
        raise_error_handler=core.raise_error_handler(core.get_error(cache, resolver.get_dependency)),
        response_handler=core.response_handler,
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

# ** blueprint: build_admin_app
def build_admin_app(
    interface_id: str = 'tiferet_app',
    **parameters: Any,
) -> AppSessionContext:
    '''
    Build a fully wired admin app session context in a single call.

    Parallel to :func:`core.build_app` but uses the admin cache (seeded with
    the full admin catalog) and :func:`build_admin_app_session_context` so the
    feature-level resolver carries the admin service catalog.  When
    ``interface_id`` is not found in the consumer's config file, the function
    falls back to :data:`~tiferet.assets.app.DEFAULT_ADMIN_APP_SESSION` so the
    built-in admin interface is always available without a config entry.

    :param interface_id: The session ID to load; defaults to ``'tiferet_app'``.
    :type interface_id: str
    :param parameters: Additional parameters forwarded to the app service
        constructor (e.g. ``app_config='config.yml'``).
    :type parameters: dict
    :return: The fully prepared admin application session context.
    :rtype: AppSessionContext
    '''

    # Build the admin cache (seeded with errors, services, constants, and features).
    cache = build_cache()

    # Resolve the session; built-in sessions are cache-seeded so no fallback needed.
    app_session = core.get_app_session(interface_id, cache, **parameters)

    # Compose the wired admin app session context.
    app_session_context = build_admin_app_session_context(app_session, cache)

    # Verify that the composed context is a valid app session context.
    if not isinstance(app_session_context, AppSessionContext):
        RaiseError.execute(
            a.error.INVALID_APP_SESSION_TYPE_ID,
            f'App context for session is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated admin app session context.
    return app_session_context

