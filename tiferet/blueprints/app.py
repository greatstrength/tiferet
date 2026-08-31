"""Tiferet App Blueprints"""

# *** imports

# ** app
from ..assets import TiferetError
from . import core
from ..contexts.cache import CacheContext
from ..contexts.app import AppSession, AppSessionContext
from .. import a

# *** blueprints

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
    :param context_kwargs: Additional keyword arguments forwarded to the
        context constructor.
    :type context_kwargs: dict
    :return: The wired app session context.
    :rtype: AppSessionContext
    '''

    # Build the app service container from defaults and interface overrides.
    app_container = core.build_app_service_container(cache, app_session)

    # Build the feature-level resolver from the app container.
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
# >> see: @guides/blueprints.md#build-app
def build_app(
    interface_id: str,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters,
) -> AppSessionContext:
    '''
    The framework's single-call public entry point (exported as ``App``) —
    the thin orchestrator that turns an interface id into a fully wired,
    ready-to-run application session without the caller wiring DI, caching,
    or handler composition by hand.

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
    cache = core.build_cache()

    # Resolve the app session; GetAppSession raises APP_SESSION_NOT_FOUND when absent.
    app_session = core.get_app_session(interface_id, cache, module_path, class_name, **parameters)

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
