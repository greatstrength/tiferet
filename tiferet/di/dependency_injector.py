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

# *** classes

# ** class: di_dynamic_service_container
class DIDynamicServiceContainer(ServiceContainer):
    '''
    A concrete ServiceContainer that adapts the framework's DI container
    contract to the third-party dependency_injector DynamicContainer. It
    registers services as Factory providers (wired to sibling providers) and
    constants as Object providers.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Initialize the container and load the provided services and constants.

        :param services: A mapping of service id to core service dependency.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        '''

        # Create the underlying DynamicContainer.
        self.container = containers.DynamicContainer()

        # Load the provided services and constants via the shared loader.
        self.load_container(services=services, constants=constants)

    # * method: add_service
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency as a Factory provider.

        Any parameters declared on the dependency are registered as constants
        first (reusing ``add_constant``) so they are wired into the factory and
        take precedence; a parameter overwrites an existing constant of the same
        name.

        :param service_id: The identifier under which to register the service.
        :type service_id: str
        :param service: The core service dependency describing the service.
        :type service: ServiceDependency
        '''

        # Register the dependency's declared parameters as constants first so
        # they take precedence over any existing constant of the same name.
        for name, value in (service.parameters or {}).items():
            self.add_constant(name, value)

        # Resolve the concrete service type from the core dependency model.
        service_type = service.get_service_type()

        # Build a Factory provider with constructor kwargs wired to siblings.
        factory = self.build_factory(service_type)

        # Register the provider on the container.
        self.container.set_provider(service_id, factory)

    # * method: add_constant
    def add_constant(self, constant_id: str, value: Any):
        '''
        Register a constant value as an Object provider.

        :param constant_id: The identifier under which to register the constant.
        :type constant_id: str
        :param value: The constant value.
        :type value: Any
        '''

        # Register the constant as an Object provider for scalar pass-through.
        self.container.set_provider(constant_id, providers.Object(value))

    # * method: get_dependency
    def get_dependency(self, dependency_id: str) -> Any:
        '''
        Resolve a registered dependency (service or constant) by its identifier.

        A missing or failing provider raises a raw exception, leaving structured
        error handling to the caller (which has event access).

        :param dependency_id: The identifier of the dependency to resolve.
        :type dependency_id: str
        :return: The resolved dependency instance or value.
        :rtype: Any
        '''

        # Look up the provider and invoke it; a missing provider raises a raw error.
        provider = self.container.providers.get(dependency_id)
        return provider()

    # * method: has_dependency
    def has_dependency(self, dependency_id: str) -> bool:
        '''
        Return True when a dependency is registered under the given identifier.

        :param dependency_id: The identifier of the dependency to check.
        :type dependency_id: str
        :return: True when the dependency is registered, False otherwise.
        :rtype: bool
        '''

        # Check the underlying container's provider registry.
        return self.container.providers.get(dependency_id) is not None

    # * method: remove_dependency
    def remove_dependency(self, dependency_id: str):
        '''
        Remove a registered dependency from the container. Idempotent.

        :param dependency_id: The identifier of the dependency to remove.
        :type dependency_id: str
        '''

        # Remove the provider if it exists; no-op for nonexistent IDs.
        if dependency_id in self.container.providers:
            delattr(self.container, dependency_id)

    # * method: load_container
    def load_container(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Bulk-load the container from service dependencies and constants.

        Constants are registered first so that service Factory providers can
        wire their constructor kwargs to them.

        :param services: A mapping of service id to core service dependency.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        '''

        # Normalize optional inputs.
        services = services if services else {}
        constants = constants if constants else {}

        # Register constants first so service factories can wire to them.
        for constant_id, value in constants.items():
            self.add_constant(constant_id, value)

        # Register services after constants.
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
    A concrete ServiceContainer for the application's core service graph. It
    mirrors DIDynamicServiceContainer but registers services as Singleton
    providers (one shared instance per app) and builds from AppServiceDependency
    objects keyed by service id.
    '''

    # * method: add_service
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency as a Singleton provider.

        :param service_id: The identifier under which to register the service.
        :type service_id: str
        :param service: The core service dependency describing the service.
        :type service: ServiceDependency
        '''

        # Register the dependency's declared parameters as constants first.
        for name, value in (service.parameters or {}).items():
            self.add_constant(name, value)

        # Resolve the concrete service type from the core dependency model.
        service_type = service.get_service_type()

        # Build a Singleton provider with constructor kwargs wired to siblings.
        singleton = self.build_singleton(service_type)

        # Register the provider on the container.
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
        Build an app service container from a list of app service dependencies.

        :param services: The app service dependencies (each carries a service_id).
        :type services: List[AppServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        :return: The loaded app service container.
        :rtype: DIAppServiceContainer
        '''

        # Key the app service dependencies by their service id.
        services_by_id = {service.service_id: service for service in (services or [])}

        # Construct and load the container (constants first, then services).
        return cls(services=services_by_id, constants=constants)

# ** class: di_dynamic_service_resolver
class DIDynamicServiceResolver(ServiceResolver):
    '''
    A concrete ServiceResolver that builds DIDynamicServiceContainers from the
    service registrations and constants provided by a DIService, resolving each
    registration to its effective service dependency for the requested flags.
    '''

    # * attribute: di_service
    di_service: DIService

    # * attribute: parse_parameter
    parse_parameter: Callable

    # * init
    def __init__(self, di_service: DIService, parse_parameter: Callable = None):
        '''
        Initialize the resolver with a DI service and a parameter parser.

        :param di_service: The DI service providing registrations and constants.
        :type di_service: DIService
        :param parse_parameter: The parameter parser; defaults to identity.
        :type parse_parameter: Callable | None
        '''

        # Initialize the base per-flag container cache.
        super().__init__()

        # Assign the DI service.
        self.di_service = di_service

        # Default the parameter parser to identity when none is provided.
        self.parse_parameter = parse_parameter if parse_parameter else lambda value: value

    # * method: build_container
    def build_container(self, flags: List[str] = None) -> ServiceContainer:
        '''
        Build a DIDynamicServiceContainer for the given flags.

        :param flags: The flags for which to build the container.
        :type flags: List[str] | None
        :return: The built service container.
        :rtype: ServiceContainer
        '''

        # Normalize optional flags.
        flags = flags if flags else []

        # Read the registrations and top-level constants from the DI service.
        registrations, constants = self.di_service.list_all()

        # Parse the top-level constants once.
        constants = {key: self.parse_parameter(value) for key, value in constants.items()}

        # Unpack each registration into an effective core ServiceDependency for these flags.
        services = {}
        for registration in registrations:

            # Resolve the effective dependency (flagged override -> default -> None).
            dependency = registration.resolve_service(*flags)

            # Skip registrations that resolve to no service.
            if dependency is None:
                continue

            # Register the parsed effective dependency by registration id.
            services[registration.id] = ServiceDependency(
                module_path=dependency.module_path,
                class_name=dependency.class_name,
                parameters={
                    key: self.parse_parameter(value)
                    for key, value in (dependency.parameters or {}).items()
                },
            )

        # Build and return the container (constants first, then services).
        return DIDynamicServiceContainer(services=services, constants=constants)
