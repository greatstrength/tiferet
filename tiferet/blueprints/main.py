"""Tiferet App Blueprints"""

# *** imports

# ** core
import inspect
from typing import Any, Dict, List

# ** app
from ..contexts.app import (
    AppSessionContext,
    AppInterfaceContext,
    resolve_default_interface,
)
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..di import injectable_parameter_names
from .. import assets as a
from ..domain import (
    AppSession,
    AppInterface,
    AppServiceDependency,
)
from ..events import (
    DomainEvent,
    ImportDependency,
    RaiseError,
)
from ..events.blueprint import CreateServiceResolver
from .core import get_app_session

# *** functions

# ** function: resolve_ctor_kwargs
def resolve_ctor_kwargs(service_type: type, registry: Dict[str, Any]) -> Dict[str, Any] | None:
    '''
    Resolve constructor keyword arguments for a service type from the registry.

    Returns the resolved kwargs, or ``None`` when a required constructor
    parameter is not yet available so the caller can defer instantiation.

    :param service_type: The service class to inspect.
    :type service_type: type
    :param registry: The name-to-value registry of constants and built services.
    :type registry: Dict[str, Any]
    :return: The resolved kwargs, or None when a required parameter is missing.
    :rtype: Dict[str, Any] | None
    '''

    # Inspect the constructor signature; treat uninspectable types as no-arg.
    try:
        sig = inspect.signature(service_type.__init__)
    except (ValueError, TypeError):
        return {}

    # Match each injectable constructor parameter (sourced from the shared DI
    # helper so the skip rules live in one place) to a registry entry,
    # deferring on any missing required parameter.
    kwargs: Dict[str, Any] = {}
    for name in injectable_parameter_names(service_type):

        # Wire from the registry, or defer when a required value is absent.
        if name in registry:
            kwargs[name] = registry[name]
        elif sig.parameters[name].default is inspect.Parameter.empty:
            return None

    # Return the resolved constructor kwargs.
    return kwargs


# ** function: build_wiring_constants
def build_wiring_constants(app_session: AppSession) -> Dict[str, Any]:
    '''
    Build the wiring-registry seed constants from an app interface.

    Combines the interface scalars (id, logger id) with the interface's
    declared constants into a single name-to-value mapping used to seed
    declarative service wiring.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :return: The seed constants keyed by name.
    :rtype: Dict[str, Any]
    '''

    # Combine session scalars with the session's declared constants.
    return {
        'interface_id': app_session.id,
        'logger_id': getattr(app_session, 'logger_id', None),
        **(app_session.constants or {}),
    }


# ** function: resolve_collaborators
def resolve_collaborators(context_cls: type, registry: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Resolve a context class's event collaborators by name from a wiring registry.

    Inspects the context class's own injectable constructor parameters and
    pulls each matching id from the registry, skipping the arguments that
    ``load_app_instance`` supplies explicitly (``get_dependency``, ``cache``)
    and the bootstrap ``default_*`` kwargs forwarded via ``context_kwargs``.
    This injects the CLI events for a ``CliContext`` and supports any custom
    context's collaborators without hard-coding collaborator names, while the
    generic ``AppSessionContext`` still resolves only its original three.

    :param context_cls: The context class whose collaborators are resolved.
    :type context_cls: type
    :param registry: The name-to-value registry of constants and built services.
    :type registry: Dict[str, Any]
    :return: The resolved collaborators keyed by constructor parameter name.
    :rtype: Dict[str, Any]
    '''

    # Arguments supplied explicitly during construction are never collaborators.
    reserved = {'get_dependency', 'cache'}

    # Match each injectable constructor parameter to a registry entry, skipping
    # the explicitly-supplied args and the bootstrap default_* kwargs.
    return {
        name: registry[name]
        for name in injectable_parameter_names(context_cls)
        if name not in reserved
        and not name.startswith('default_')
        and name in registry
    }


# *** blueprints

# ** blueprint: build_cache
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build a standalone cache context for managing in-memory cache operations.

    Constructs a ``CacheContext`` independently of any interface or service
    resolver, then pre-seeds it with the framework's built-in error domain
    objects via the ``add_default_errors`` decorator. Pass an existing dict
    to seed the cache with additional pre-populated values; omit it to start
    with a fresh empty cache.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized and error-seeded cache context.
    :rtype: CacheContext
    '''

    # Construct and return the cache context.
    return CacheContext(cache=cache)


# ** blueprint: wire_services
def wire_services(
    services: List[AppServiceDependency],
    constants: Dict[str, Any],
) -> Dict[str, Any]:
    '''
    Declaratively instantiate service dependencies into a name-to-value registry.

    Seeds the registry with the provided constants and each dependency's
    parameters, then iteratively instantiates services whose constructor
    arguments are all resolvable, wiring events to the repositories they depend
    on without an app-level DI container.

    :param services: The service dependencies to instantiate.
    :type services: List[AppServiceDependency]
    :param constants: The seed constants (interface scalars, config values, etc.).
    :type constants: Dict[str, Any]
    :return: The registry of constants and instantiated services keyed by id.
    :rtype: Dict[str, Any]
    '''

    # Seed the registry with constants, then service parameters at lower priority.
    registry: Dict[str, Any] = dict(constants)
    for dep in services:
        for key, value in (dep.parameters or {}).items():
            registry.setdefault(key, value)

    # Iteratively instantiate services until none remain or no progress is made.
    pending = list(services)
    while pending:
        still_pending: List[AppServiceDependency] = []
        progressed = False

        # Attempt to instantiate each pending dependency.
        for dep in pending:
            service_type = dep.get_service_type()
            kwargs = resolve_ctor_kwargs(service_type, registry)

            # Defer when constructor arguments are not yet fully resolvable.
            if kwargs is None:
                still_pending.append(dep)
                continue

            # Instantiate and register the service under its id.
            registry[dep.service_id] = service_type(**kwargs)
            progressed = True

        # Fail when remaining services cannot be resolved.
        if not progressed and still_pending:
            RaiseError.execute(
                a.const.APP_SERVICE_IMPORT_FAILED_ID,
                exception='Unresolvable service dependencies: {}'.format(
                    [dep.service_id for dep in still_pending]
                ),
            )

        # Continue with the still-pending dependencies.
        pending = still_pending

    # Return the populated registry.
    return registry


# ** blueprint: load_app_instance
def load_app_instance(
    app_session: AppSession,
    **context_kwargs,
) -> Any:
    '''
    Declaratively construct the app session context from a loaded session.

    The session's service dependencies (repositories and events) are wired
    explicitly by importing each class and resolving its constructor arguments
    from a name-to-value registry of session scalars, constants, and
    already-built services -- no app-level DI container is used. A
    ``ServiceResolver`` is built from the resolved ``di_service`` and its
    ``get_dependency`` handler is injected into the context.

    :param app_session: The prepared app session definition.
    :type app_session: AppSession
    :param context_kwargs: Additional keyword arguments forwarded to the context
        constructor (e.g. bootstrap defaults).
    :type context_kwargs: dict
    :return: The resolved app session context.
    :rtype: Any
    '''

    # Seed the wiring registry with session scalars and constants.
    constants = build_wiring_constants(app_session)

    # Declaratively instantiate the session's service dependencies.
    try:
        registry = wire_services(app_session.services, constants)

    # Raise a structured error if declarative wiring fails.
    except Exception as e:
        RaiseError.execute(
            a.const.APP_SERVICE_IMPORT_FAILED_ID,
            exception=str(e),
        )

    # Compose the service resolver via the bootstrap event from the session's
    # DI repository dependency, routing any bootstrap DI defaults (popped from
    # context kwargs) into it.
    resolver = DomainEvent.handle(
        CreateServiceResolver,
        dependencies={},
        app_interface=app_session,
        default_configurations=context_kwargs.pop('default_configurations', None),
        default_constants=context_kwargs.pop('default_constants', None),
    )

    # Import the context class declared by the session (supports custom contexts).
    context_cls = ImportDependency.execute(
        app_session.module_path,
        app_session.class_name,
    )

    # Resolve the context class's event collaborators by name from the registry.
    resolved = resolve_collaborators(context_cls, registry)

    # Use a pre-built cache if forwarded via context_kwargs, otherwise build fresh.
    # ++ todo: remove fallback when the core compose path is wired at N2/FE1
    cache = context_kwargs.pop('cache', None) or build_cache()

    # Construct the context declaratively, injecting the resolution handler and cache.
    return context_cls.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        **resolved,
        **context_kwargs,
    )


# ** blueprint: resolve_interface
def resolve_interface(
    interface_id: str,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    default_interfaces: List[Dict[str, Any]] = [],
    **parameters
) -> tuple:
    '''
    Load the app service and resolve the session definition.

    Returns the resolved AppSession. The second tuple element is vestigial
    (all callers discard it with ``_``) and will be removed when
    ``resolve_interface`` retires at N6.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param default_interfaces: A list of session definition dicts used as a
        fallback when the session is not found in the repository.
    :type default_interfaces: List[Dict[str, Any]]
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: A tuple of (app_session, []).
    :rtype: tuple
    '''

    # Retrieve the session via the core blueprint, falling back to the bootstrap
    # default session definitions when the config does not define it.
    try:
        app_session = get_app_session(interface_id, module_path, class_name, **parameters)
    except a.TiferetError:
        app_session = resolve_default_interface(interface_id, default_interfaces)
        if app_session is None:
            raise

    # Merge the framework default services and constants via the domain model.
    app_session = app_session.apply_defaults(
        default_services=[
            AppServiceDependency.model_validate(r)
            for r in a.app.CORE_DEFAULT_SERVICES.values()
        ],
        default_constants=a.app.CORE_DEFAULT_CONSTANTS,
    )

    # Return the resolved session. The second element is vestigial; callers
    # discard it with _ and it will be removed when resolve_interface retires at N6.
    # ++ todo: simplify to single return value at N6
    return app_session, []


# ** blueprint: realize_interface
def realize_interface(
    app_session: AppSession,
    interface_id: str,
    **context_kwargs,
) -> AppSessionContext:
    '''
    Build and validate the concrete app session context from a resolved session.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param interface_id: The session ID (used in error messages).
    :type interface_id: str
    :param context_kwargs: Additional keyword arguments forwarded to the context
        constructor (e.g. bootstrap defaults).
    :type context_kwargs: dict
    :return: The validated app session context.
    :rtype: AppSessionContext
    '''

    # Create the concrete app session context.
    app_session_context = load_app_instance(app_session, **context_kwargs)

    # Verify that the resolved context is valid.
    if not isinstance(app_session_context, AppSessionContext):
        RaiseError.execute(
            a.const.INVALID_APP_SESSION_TYPE_ID,
            f'App context for session is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated app session context.
    return app_session_context


# ** blueprint: build_app
def build_app(
    interface_id: str,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    default_interfaces: List[Dict[str, Any]] = [],
    **parameters
) -> AppSessionContext:
    '''
    Build a fully resolved application session context in a single act.

    :param interface_id: The session ID to load.
    :type interface_id: str
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param default_interfaces: A list of session definition dicts used as a
        fallback when the session is not found in the repository.
    :type default_interfaces: List[Dict[str, Any]]
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The fully prepared application session context.
    :rtype: AppSessionContext
    '''

    # Resolve the session definition, passing any provided session defaults.
    app_session, _ = resolve_interface(
        interface_id,
        module_path,
        class_name,
        default_interfaces=default_interfaces,
        **parameters,
    )

    # Realize and return the app session context.
    return realize_interface(app_session, interface_id)
