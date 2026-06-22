"""Tiferet App Blueprints"""

# *** imports

# ** core
import inspect
from typing import Any, Dict, List

# ** app
from ..contexts.app import (
    AppInterfaceContext,
    resolve_default_interface,
)
from ..di import injectable_parameter_names
from .. import assets as a
from ..domain import (
    AppInterface,
    AppServiceDependency,
)
from ..events import (
    DomainEvent,
    ImportDependency,
    RaiseError,
)
from ..events.app import GetAppInterface
from ..events.blueprint import CreateServiceResolver

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
def build_wiring_constants(app_interface: AppInterface) -> Dict[str, Any]:
    '''
    Build the wiring-registry seed constants from an app interface.

    Combines the interface scalars (id, logger id) with the interface's
    declared constants into a single name-to-value mapping used to seed
    declarative service wiring.

    :param app_interface: The resolved app interface definition.
    :type app_interface: AppInterface
    :return: The seed constants keyed by name.
    :rtype: Dict[str, Any]
    '''

    # Combine interface scalars with the interface's declared constants.
    return {
        'interface_id': app_interface.id,
        'logger_id': getattr(app_interface, 'logger_id', None),
        **(app_interface.constants or {}),
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
    generic ``AppInterfaceContext`` still resolves only its original three.

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


# ** blueprint: load_app_service
def load_app_service(
    module_path: str = a.bps.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.bps.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters
) -> Any:
    '''
    Import and construct the application service.

    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The constructed app service instance.
    :rtype: Any
    '''

    # Import and construct the app service.
    service_cls = ImportDependency.execute(module_path, class_name)
    return service_cls(**parameters)


# ** blueprint: load_default_services
def load_default_services() -> List[AppServiceDependency]:
    '''
    Load the default app service dependencies from configuration constants.

    :return: A list of default app service dependencies.
    :rtype: List[AppServiceDependency]
    '''

    # Build domain dependency models from the default service configuration.
    return [
        AppServiceDependency.model_construct(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters or {},
        )
        for service_id, module_path, class_name, parameters in a.bps.DEFAULT_SERVICES
    ]


# ** blueprint: load_app_instance
def load_app_instance(
    app_interface: AppInterface,
    **context_kwargs,
) -> Any:
    '''
    Declaratively construct the app interface context from a loaded interface.

    The interface's service dependencies (repositories and events) are wired
    explicitly by importing each class and resolving its constructor arguments
    from a name-to-value registry of interface scalars, constants, and
    already-built services -- no app-level DI container is used. A
    ``ServiceResolver`` is built from the resolved ``di_service`` and its
    ``get_dependency`` handler is injected into the context.

    :param app_interface: The prepared app interface definition.
    :type app_interface: AppInterface
    :param context_kwargs: Additional keyword arguments forwarded to the context
        constructor (e.g. bootstrap defaults).
    :type context_kwargs: dict
    :return: The resolved app interface context.
    :rtype: Any
    '''

    # Seed the wiring registry with interface scalars and constants.
    constants = build_wiring_constants(app_interface)

    # Declaratively instantiate the interface's service dependencies.
    try:
        registry = wire_services(app_interface.services, constants)

    # Raise a structured error if declarative wiring fails.
    except Exception as e:
        RaiseError.execute(
            a.const.APP_SERVICE_IMPORT_FAILED_ID,
            exception=str(e),
        )

    # Compose the service resolver via the bootstrap event from the interface's
    # DI repository dependency, routing any bootstrap DI defaults (popped from
    # context kwargs) into it.
    resolver = DomainEvent.handle(
        CreateServiceResolver,
        dependencies={},
        app_interface=app_interface,
        default_configurations=context_kwargs.pop('default_configurations', None),
        default_constants=context_kwargs.pop('default_constants', None),
    )

    # Import the context class declared by the interface (supports custom contexts).
    context_cls = ImportDependency.execute(
        app_interface.module_path,
        app_interface.class_name,
    )

    # Resolve the context class's event collaborators by name from the registry.
    resolved = resolve_collaborators(context_cls, registry)

    # Construct the context declaratively, injecting the resolution handler.
    return context_cls.from_domain(
        app_interface,
        get_dependency=resolver.get_dependency,
        **resolved,
        **context_kwargs,
    )


# ** blueprint: resolve_interface
def resolve_interface(
    interface_id: str,
    module_path: str = a.bps.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.bps.DEFAULT_APP_SERVICE_CLASS_NAME,
    default_interfaces: List[Dict[str, Any]] = [],
    **parameters
) -> tuple:
    '''
    Load the app service and resolve the interface definition.

    Returns the resolved AppInterface and the default services list
    for downstream use by blueprint variants.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param default_interfaces: A list of interface definition dicts used as a
        fallback when the interface is not found in the repository.
    :type default_interfaces: List[Dict[str, Any]]
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: A tuple of (app_interface, default_services).
    :rtype: tuple
    '''

    # Load the app service.
    app_service = load_app_service(module_path, class_name, **parameters)

    # Load the default app service dependencies.
    default_services = load_default_services()

    # Retrieve the interface via the event, falling back to the bootstrap default
    # interface definitions (materialized by the context bootstrap helper) when
    # the consumer's config does not define it.
    try:
        app_interface = DomainEvent.handle(
            GetAppInterface,
            dependencies=dict(app_service=app_service),
            interface_id=interface_id,
        )
    except a.TiferetError:
        app_interface = resolve_default_interface(interface_id, default_interfaces)
        if app_interface is None:
            raise

    # Merge the framework default services and constants via the domain model.
    app_interface = app_interface.apply_defaults(
        default_services=default_services,
        default_constants=a.bps.DEFAULT_CONSTANTS,
    )

    # Return the resolved interface and default services.
    return app_interface, default_services


# ** blueprint: realize_interface
def realize_interface(
    app_interface: AppInterface,
    interface_id: str,
    **context_kwargs,
) -> AppInterfaceContext:
    '''
    Build and validate the concrete app interface context from a resolved interface.

    :param app_interface: The resolved app interface definition.
    :type app_interface: AppInterface
    :param interface_id: The interface ID (used in error messages).
    :type interface_id: str
    :param context_kwargs: Additional keyword arguments forwarded to the context
        constructor (e.g. bootstrap defaults).
    :type context_kwargs: dict
    :return: The validated app interface context.
    :rtype: AppInterfaceContext
    '''

    # Create the concrete app interface context.
    app_interface_context = load_app_instance(app_interface, **context_kwargs)

    # Verify that the resolved context is valid.
    if not isinstance(app_interface_context, AppInterfaceContext):
        RaiseError.execute(
            a.const.INVALID_APP_INTERFACE_TYPE_ID,
            f'App context for interface is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated app interface context.
    return app_interface_context


# ** blueprint: build_app
def build_app(
    interface_id: str,
    module_path: str = a.bps.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.bps.DEFAULT_APP_SERVICE_CLASS_NAME,
    default_interfaces: List[Dict[str, Any]] = [],
    **parameters
) -> AppInterfaceContext:
    '''
    Build a fully resolved application interface context in a single act.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param default_interfaces: A list of interface definition dicts used as a
        fallback when the interface is not found in the repository.
    :type default_interfaces: List[Dict[str, Any]]
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The fully prepared application interface context.
    :rtype: AppInterfaceContext
    '''

    # Resolve the interface definition, passing any provided interface defaults.
    app_interface, _ = resolve_interface(
        interface_id,
        module_path,
        class_name,
        default_interfaces=default_interfaces,
        **parameters,
    )

    # Realize and return the app interface context.
    return realize_interface(app_interface, interface_id)
