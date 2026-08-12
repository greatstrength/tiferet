"""Tiferet DI Dependency Injector Container"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List

# ** infra
from dependency_injector import containers, providers

# ** app
from .core import ServiceContainer, ServiceResolver, injectable_parameter_names
from ..domain import ServiceDependency, AppServiceDependency
from ..interfaces.di import DIService
from ..interfaces.core import ServiceError

# *** constants

# ** constant: di_dependency_not_registered_id
DI_DEPENDENCY_NOT_REGISTERED_ID = 'DI_DEPENDENCY_NOT_REGISTERED'

# *** classes

# ** class: di_dynamic_service_container
class DIDynamicServiceContainer(ServiceContainer):
    '''
    A dependency-injector-backed DI container satisfying the core
    ServiceContainer ABC via a DynamicContainer engine.

    Services are registered as Factory providers (a new instance per
    resolution); constants are registered as Object providers. Constants
    are always registered before services so that scalar parameter values
    are available when factory kwargs are wired.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Initialize the dynamic service container.

        :param services: The initial service id-to-dependency mapping.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: The initial constant id-to-value mapping.
        :type constants: Dict[str, Any] | None
        '''

        # Create the underlying DynamicContainer.
        self.container = containers.DynamicContainer()

        # Bulk-load the container from the provided services and constants.
        self.load_container(services=services, constants=constants)

    # * method: add_service
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency in the container as a Factory provider.

        :param service_id: The service identifier.
        :type service_id: str
        :param service: The core service dependency.
        :type service: ServiceDependency
        '''

        # Register the dependency's declared parameters as constants first.
        for name, value in (service.parameters or {}).items():
            self.add_constant(name, value)

        # Resolve the concrete service type and build the Factory.
        service_type = service.get_service_type()
        factory = self.build_factory(service_type)

        # Register the Factory provider on the container.
        self.container.set_provider(service_id, factory)

    # * method: add_constant
    def add_constant(self, constant_id: str, value: Any):
        '''
        Register a constant value in the container as an Object provider.

        :param constant_id: The constant identifier.
        :type constant_id: str
        :param value: The constant value.
        :type value: Any
        '''

        # Register the value as an Object provider for scalar pass-through.
        self.container.set_provider(constant_id, providers.Object(value))

    # * method: get_dependency
    def get_dependency(self, dependency_id: str) -> Any:
        '''
        Resolve a registered dependency by identifier.

        A missing provider raises a ServiceError; a failing provider raises
        a raw exception, leaving structured error handling to callers with
        event access.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: The resolved instance or value.
        :rtype: Any
        '''

        # Look up the provider, guarding against an unregistered dependency.
        provider = self.container.providers.get(dependency_id)
        if provider is None:
            ServiceError.raise_for(
                self,
                DI_DEPENDENCY_NOT_REGISTERED_ID,
                f'No dependency is registered under the id: {dependency_id}.',
                dependency_id=dependency_id,
            )

        # Invoke the resolved provider.
        return provider()

    # * method: has_dependency
    def has_dependency(self, dependency_id: str) -> bool:
        '''
        Return True when a dependency is registered under the given identifier.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: True when registered, False otherwise.
        :rtype: bool
        '''

        # Check the underlying container's provider registry.
        return self.container.providers.get(dependency_id) is not None

    # * method: remove_dependency
    def remove_dependency(self, dependency_id: str):
        '''
        Remove a registered dependency from the container. Idempotent.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        '''

        # Remove the provider if it exists; no-op for nonexistent IDs.
        if self.has_dependency(dependency_id):
            delattr(self.container, dependency_id)

    # * method: load_container
    def load_container(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Bulk-load the container from service dependencies and constants.

        Registers all constants first, then all services, so scalar
        parameter values are available when factory kwargs are wired.

        :param services: A mapping of service id to core service dependency.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        '''

        # Normalize optional inputs.
        services = services if services else {}
        constants = constants if constants else {}

        # Register all constants first.
        for constant_id, value in constants.items():
            self.add_constant(constant_id, value)

        # Register all services second.
        for service_id, service in services.items():
            self.add_service(service_id, service)

    # * method: build_factory
    def build_factory(self, service_type: type) -> providers.Factory:
        '''
        Build a Factory provider with constructor kwargs wired to sibling providers.

        :param service_type: The service class to build a factory for.
        :type service_type: type
        :return: A Factory provider with cascading dependency resolution.
        :rtype: providers.Factory
        '''

        # Wire each injectable parameter to a registered sibling provider when one exists.
        kwargs = {}
        for name in injectable_parameter_names(service_type):
            sibling = self.container.providers.get(name)
            if sibling is not None:
                kwargs[name] = sibling

        # Return the Factory provider with wired kwargs.
        return providers.Factory(service_type, **kwargs)

# ** class: di_app_service_container
class DIAppServiceContainer(DIDynamicServiceContainer):
    '''
    A dependency-injector-backed DI container for the application's core
    service graph. Services are registered as Singleton providers so each
    service is shared across the application lifetime.
    '''

    # * method: add_service
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency in the container as a Singleton provider.

        :param service_id: The service identifier.
        :type service_id: str
        :param service: The core service dependency.
        :type service: ServiceDependency
        '''

        # Register the dependency's declared parameters as constants first.
        for name, value in (service.parameters or {}).items():
            self.add_constant(name, value)

        # Resolve the concrete service type and build the Singleton.
        service_type = service.get_service_type()
        singleton = self.build_singleton(service_type)

        # Register the Singleton provider on the container.
        self.container.set_provider(service_id, singleton)

    # * method: build_singleton
    def build_singleton(self, service_type: type) -> providers.Singleton:
        '''
        Build a Singleton provider with constructor kwargs wired to sibling providers.

        :param service_type: The service class to build a singleton for.
        :type service_type: type
        :return: A Singleton provider with cascading dependency resolution.
        :rtype: providers.Singleton
        '''

        # Wire each injectable parameter to a registered sibling provider when one exists.
        kwargs = {}
        for name in injectable_parameter_names(service_type):
            sibling = self.container.providers.get(name)
            if sibling is not None:
                kwargs[name] = sibling

        # Return the Singleton provider with wired kwargs.
        return providers.Singleton(service_type, **kwargs)

    # * method: from_dependencies (class)
    @classmethod
    def from_dependencies(cls,
            services: List[AppServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ) -> 'DIAppServiceContainer':
        '''
        Build a loaded app service container from a list of app service
        dependencies, keyed by their service_id.

        :param services: The application service dependencies.
        :type services: List[AppServiceDependency] | None
        :param constants: The constants to register alongside the services.
        :type constants: Dict[str, Any] | None
        :return: A loaded app service container.
        :rtype: DIAppServiceContainer
        '''

        # Key the app service dependencies by their service_id.
        services_by_id = {service.service_id: service for service in (services or [])}

        # Construct and return the loaded container.
        return cls(services=services_by_id, constants=constants)

# ** class: di_dynamic_service_resolver
class DIDynamicServiceResolver(ServiceResolver):
    '''
    A dependency-injector-backed service resolver satisfying the core
    ServiceResolver ABC. Builds a DIDynamicServiceContainer per unique
    flag set by reading registrations and constants from a DIService.
    '''

    # * attribute: di_service
    di_service: DIService

    # * attribute: parse_parameter
    parse_parameter: Callable

    # * init
    def __init__(self,
            di_service: DIService,
            parse_parameter: Callable = None,
        ):
        '''
        Initialize the dynamic service resolver.

        :param di_service: The DI service providing registrations and constants.
        :type di_service: DIService
        :param parse_parameter: Optional parameter parser; defaults to identity.
        :type parse_parameter: Callable | None
        '''

        # Initialize the per-flag container cache.
        super().__init__()

        # Assign the DI service.
        self.di_service = di_service

        # Default the parameter parser to identity to preserve the layering boundary.
        self.parse_parameter = parse_parameter if parse_parameter else lambda value: value

    # * method: build_container
    def build_container(self, flags: List[str] = None) -> DIDynamicServiceContainer:
        '''
        Build a new dynamic service container for the given normalized flag list.

        Registrations that resolve to no dependency for the given flags are
        excluded from the container.

        :param flags: The normalized flag list for this container.
        :type flags: List[str] | None
        :return: A new dynamic service container instance.
        :rtype: DIDynamicServiceContainer
        '''

        # Normalize optional flags.
        flags = flags if flags else []

        # Read the registrations and top-level constants from the DI service.
        registrations, constants = self.di_service.list_all()

        # Parse the top-level constants with the injected parser.
        parsed_constants = {key: self.parse_parameter(value) for key, value in constants.items()}

        # Resolve the effective service dependency for each registration.
        services = {}
        for registration in registrations:

            # Resolve the effective dependency for these flags; skip unresolved registrations.
            dependency = registration.resolve_service(*flags)
            if dependency is None:
                continue

            # Parse the resolved dependency's parameters and key it by registration id.
            services[registration.id] = ServiceDependency(
                module_path=dependency.module_path,
                class_name=dependency.class_name,
                parameters={
                    key: self.parse_parameter(value)
                    for key, value in (dependency.parameters or {}).items()
                },
            )

        # Return the loaded dynamic service container.
        return DIDynamicServiceContainer(services=services, constants=parsed_constants)
