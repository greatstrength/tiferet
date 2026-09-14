"""Tiferet Standard App Blueprint"""

# *** imports

# ** app
from .. import a
from ..assets import TiferetError
from ..contexts.app import AppSession, AppSessionContext
from ..contexts.cache import CacheContext
from . import core

# *** blueprints

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
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)

    # Delegate handler wiring, collaborator resolution, and construction.
    return core.compose_session_context(
        AppSessionContext,
        app_session,
        cache,
        app_container,
        resolver,
        create_request_handler=core.create_session_request,
        response_handler=core.response_handler,
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
    cache = core.build_cache()

    # Resolve the app session, preferring a cache-seeded default.
    app_session = core.get_app_session(interface_id, cache, module_path=module_path, class_name=class_name, **parameters)

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
