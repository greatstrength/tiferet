"""Tiferet App Blueprints"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..contexts.app import AppInterfaceContext
from ..di import ServiceProvider, DynamicServiceProvider
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

# *** blueprints

# ** blueprint: create_service_provider
def create_service_provider(
    provider_type: type = DynamicServiceProvider,
    type_map: Dict[str, type] = None,
    **constants
) -> ServiceProvider:
    '''
    Create a service provider from a type map and constants.

    :param provider_type: The concrete provider class to instantiate.
    :type provider_type: type
    :param type_map: A dictionary mapping service IDs to their types.
    :type type_map: Dict[str, type]
    :param constants: Constant parameters to register in the provider.
    :type constants: dict
    :return: The configured service provider instance.
    :rtype: ServiceProvider
    '''

    # Create the provider and register constants first so that
    # Factory providers built during add_services can resolve them.
    provider = provider_type()
    if constants:
        provider.add_constants(constants)
    if type_map:
        provider.add_services(type_map)

    # Return the configured service provider.
    return provider


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
    service_provider: ServiceProvider = None,
) -> Any:
    '''
    Load the concrete app interface context instance.

    :param app_interface: The prepared app interface definition.
    :type app_interface: AppInterface
    :param service_provider: The service provider to use for resolution.
        When None, a fresh provider is created.
    :type service_provider: ServiceProvider
    :return: The resolved app interface context.
    :rtype: Any
    '''

    # Create a default service provider if none is given.
    if service_provider is None:
        service_provider = create_service_provider()

    # Build the app interface dependencies map.
    try:
        dependencies = app_interface.get_service_type_mapping()

    # Raise a structured error if dependency mapping fails.
    except Exception as e:
        RaiseError.execute(
            a.const.APP_SERVICE_IMPORT_FAILED_ID,
            exception=str(e),
        )

    # Register the create_service_provider callable for downstream contexts.
    dependencies['create_service_provider'] = create_service_provider

    # Add dependencies to the service provider.
    service_provider.add_services(dependencies)

    # Resolve and return the app interface context.
    return service_provider.get_service('app_context')


# ** blueprint: resolve_interface
def resolve_interface(
    interface_id: str,
    module_path: str = a.bps.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.bps.DEFAULT_APP_SERVICE_CLASS_NAME,
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
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: A tuple of (app_interface, default_services).
    :rtype: tuple
    '''

    # Load the app service.
    app_service = load_app_service(module_path, class_name, **parameters)

    # Load the default app service dependencies.
    default_services = load_default_services()

    # Get the app interface via the event.
    app_interface = DomainEvent.handle(
        GetAppInterface,
        dependencies=dict(app_service=app_service),
        interface_id=interface_id,
        default_services=default_services,
        default_constants=a.bps.DEFAULT_CONSTANTS,
    )

    # Return the resolved interface and default services.
    return app_interface, default_services


# ** blueprint: realize_interface
def realize_interface(
    app_interface: AppInterface,
    interface_id: str,
    service_provider: ServiceProvider = None,
) -> AppInterfaceContext:
    '''
    Build and validate the concrete app interface context from a resolved interface.

    :param app_interface: The resolved app interface definition.
    :type app_interface: AppInterface
    :param interface_id: The interface ID (used in error messages).
    :type interface_id: str
    :param service_provider: Optional service provider; a fresh one is created if None.
    :type service_provider: ServiceProvider
    :return: The validated app interface context.
    :rtype: AppInterfaceContext
    '''

    # Create the concrete app interface context.
    app_interface_context = load_app_instance(app_interface, service_provider)

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
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The fully prepared application interface context.
    :rtype: AppInterfaceContext
    '''

    # Resolve the interface definition.
    app_interface, _ = resolve_interface(interface_id, module_path, class_name, **parameters)

    # Realize and return the app interface context.
    return realize_interface(app_interface, interface_id)
