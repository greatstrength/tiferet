"""Tiferet DI Settings"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List, Tuple

# ** infra
from dependency_injector import containers, providers

# ** app
from ..domain import ServiceRegistration
from ..interfaces.di import DIService
from .core import injectable_parameter_names

# *** functions

# ** function: normalize_flags
def normalize_flags(*flags) -> List[str]:
    '''
    Flatten a mixed sequence of strings, lists, and tuples into a flat list of strings.

    :param flags: The flags to normalize (strings, lists, or tuples).
    :type flags: Tuple[Any, ...]
    :return: A flat list of flag strings.
    :rtype: List[str]
    '''

    # Flatten one level of lists/tuples into a single flag list, stringifying every flag.
    normalized = []
    for flag in flags:

        # Expand nested list/tuple flag groups, coercing each member to a string.
        if isinstance(flag, (list, tuple)):
            normalized.extend(str(f) for f in flag)

        # Append scalar flags coerced to strings.
        else:
            normalized.append(str(flag))

    # Return the flattened flag list.
    return normalized

# ** function: create_cache_key
def create_cache_key(flags: List[str] = None) -> str:
    '''
    Create a cache key for a per-flag service container.

    :param flags: The feature or data flags to encode in the key.
    :type flags: List[str] | None
    :return: The cache key, with flags appended when present.
    :rtype: str
    '''

    # Build the cache key, appending underscore-joined flags when present.
    return f"feature_services{'_' + '_'.join(flags) if flags else ''}"

# ** function: merge_settings
def merge_settings(
        configs: List[ServiceRegistration] = None,
        constants: Dict[str, Any] = None,
        default_config_index: Dict[str, ServiceRegistration] = None,
        default_constants: Dict[str, Any] = None,
    ) -> Tuple[List[ServiceRegistration], Dict[str, Any]]:
    '''
    Merge repository service registrations and constants with bootstrap defaults.

    Default-index entries are appended for any service id not already present,
    and default constants are merged beneath repository constants (repository
    values win).

    :param configs: The repository service registrations.
    :type configs: List[ServiceRegistration] | None
    :param constants: The repository constants.
    :type constants: Dict[str, Any] | None
    :param default_config_index: The default service registrations keyed by id.
    :type default_config_index: Dict[str, ServiceRegistration] | None
    :param default_constants: The default constants.
    :type default_constants: Dict[str, Any] | None
    :return: The merged registrations and constants.
    :rtype: Tuple[List[ServiceRegistration], Dict[str, Any]]
    '''

    # Normalize optional inputs.
    configs = list(configs) if configs else []
    constants = dict(constants) if constants else {}
    default_config_index = default_config_index if default_config_index else {}
    default_constants = default_constants if default_constants else {}

    # Append default-index entries for any service id not already present.
    existing_ids = {config.id for config in configs}
    for config_id, config in default_config_index.items():
        if config_id not in existing_ids:
            configs.append(config)

    # Merge default constants beneath repository constants (repository wins).
    merged_constants = {**default_constants, **constants}

    # Return the merged registrations and constants.
    return configs, merged_constants

# *** classes

# ** class: service_container
class ServiceContainer(object):
    '''
    The low-level dependency-injection engine for the framework. It registers
    service types and constants and instantiates services with their
    constructor parameters wired to sibling registrations, backed by the
    dependency_injector DynamicContainer.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        '''
        Initialize the service container.

        :param services: Initial service ID-to-type mapping.
        :type services: Dict[str, type]
        '''

        # Create the underlying DynamicContainer.
        self.container = containers.DynamicContainer()

        # Register initial services if provided.
        if services:
            self.add_services(services)

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        '''
        Add a service dependency to the container.

        :param service_id: The ID of the service to add.
        :type service_id: str
        :param service_type: The type of the service to add.
        :type service_type: type
        '''

        # Build a Factory provider with constructor kwargs wired to sibling providers.
        factory = self.build_factory(service_type)

        # Register the provider on the container.
        self.container.set_provider(service_id, factory)

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        '''
        Add multiple service dependencies to the container.

        Class types are registered as Factory providers (new instance per
        resolution). Non-type values (scalars, callables, etc.) are registered
        as Object providers (pass-through).

        Registration is performed in two passes: scalars first, then types.
        This ensures all parameter values are available in the container
        when Factory providers are built and their kwargs are wired.

        :param services: A dictionary of service IDs and their corresponding types or values.
        :type services: Dict[str, type]
        '''

        # Pass 1: Register all scalar/non-type values first so they are
        # available when Factory providers are built.
        for service_id, value in services.items():
            if not isinstance(value, type):
                self.container.set_provider(service_id, providers.Object(value))

        # Pass 2: Register all class types as Factory providers.
        for service_id, value in services.items():
            if isinstance(value, type):
                self.add_service(service_id, value)

    # * method: add_constants
    def add_constants(self, constants: Dict[str, Any]):
        '''
        Add constant dependencies to the container.

        :param constants: A dictionary of constant names and their corresponding values.
        :type constants: Dict[str, Any]
        '''

        # Register each constant as an Object provider for scalar pass-through.
        for name, value in constants.items():
            self.container.set_provider(name, providers.Object(value))

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        '''
        Get a service dependency by its ID.

        :param service_id: The service ID.
        :type service_id: str
        :return: The resolved service dependency instance.
        :rtype: Any
        '''

        # Look up the provider and invoke it to resolve the dependency. A
        # missing or failing provider raises a raw exception for the caller
        # (which has event access) to convert into a structured error.
        provider = self.container.providers.get(service_id)
        return provider()

    # * method: remove_service
    def remove_service(self, service_id: str):
        '''
        Remove a service dependency from the container.

        :param service_id: The service ID to remove.
        :type service_id: str
        '''

        pass

# ** class: service_container
class ServiceContainer(object):
    '''
    A low-level dependency-injection engine backed by the dependency_injector
    DynamicContainer. Registers service types and constants and instantiates
    services with their constructor parameters wired to sibling registrations.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        '''
        Initialize the service container.

        :param services: Initial service ID-to-type mapping.
        :type services: Dict[str, type] | None
        '''

        # Create the underlying DynamicContainer.
        self.container = containers.DynamicContainer()

        # Register initial services if provided.
        if services:
            self.add_services(services)

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        '''
        Add a service dependency to the container.

        :param service_id: The ID of the service to add.
        :type service_id: str
        :param service_type: The type of the service to add.
        :type service_type: type
        '''

        # Build a Factory provider with constructor kwargs wired to sibling providers.
        factory = self.build_factory(service_type)

        # Register the provider on the container.
        self.container.set_provider(service_id, factory)

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        '''
        Add multiple service dependencies to the container.

        Registration happens in two passes: non-type values are registered as
        Object providers first, then class types are registered as Factory
        providers, so scalar parameter values are available when factory kwargs
        are wired.

        :param services: A dictionary of service IDs and their corresponding types or values.
        :type services: Dict[str, type]
        '''

        # First pass: register non-type values as Object providers.
        for service_id, value in services.items():
            if not isinstance(value, type):
                self.container.set_provider(service_id, providers.Object(value))

        # Second pass: register class types as Factory providers.
        for service_id, value in services.items():
            if isinstance(value, type):
                self.add_service(service_id, value)

    # * method: add_constants
    def add_constants(self, constants: Dict[str, Any]):
        '''
        Add constant dependencies to the container.

        :param constants: A dictionary of constant names and their corresponding values.
        :type constants: Dict[str, Any]
        '''

        # Register each constant as an Object provider for scalar pass-through.
        for name, value in constants.items():
            self.container.set_provider(name, providers.Object(value))

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        '''
        Get a service dependency by its ID.

        A missing or failing provider raises a raw exception, leaving structured
        error handling to the caller (which has event access).

        :param service_id: The service ID.
        :type service_id: str
        :return: The resolved service dependency instance.
        :rtype: Any
        '''

        # Look up the provider and invoke it; a missing provider raises a raw error.
        provider = self.container.providers.get(service_id)
        return provider()

    # * method: remove_service
    def remove_service(self, service_id: str):
        '''
        Remove a service dependency from the container.

        :param service_id: The service ID to remove.
        :type service_id: str
        '''

        # Remove the provider if it exists; no-op for nonexistent IDs.
        if service_id in self.container.providers:
            delattr(self.container, service_id)

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

# ** class: service_resolver
class ServiceResolver(object):
    '''
    The application service provider. Reads service registrations and constants
    from a DIService, merges typed bootstrap defaults beneath the repository's
    settings, and builds and caches a per-flag ServiceContainer.
    '''

    # * attribute: di_service
    di_service: DIService

    # * attribute: parse_parameter
    parse_parameter: Callable

    # * attribute: default_config_index
    default_config_index: Dict[str, ServiceRegistration]

    # * attribute: default_di_constants
    default_di_constants: Dict[str, Any]

    # * init
    def __init__(self,
            di_service: DIService,
            parse_parameter: Callable = None,
            default_config_index: Dict[str, ServiceRegistration] = None,
            default_di_constants: Dict[str, Any] = None,
        ):
        '''
        Initialize the service resolver.

        :param di_service: The DI service providing registrations and constants.
        :type di_service: DIService
        :param parse_parameter: Optional parameter parser; defaults to identity so the DI layer never imports the parameter-parsing event.
        :type parse_parameter: Callable | None
        :param default_config_index: Default service registrations keyed by id.
        :type default_config_index: Dict[str, ServiceRegistration] | None
        :param default_di_constants: Default DI constants.
        :type default_di_constants: Dict[str, Any] | None
        '''

        # Assign the DI service.
        self.di_service = di_service

        # Default the parameter parser to identity to preserve the layering boundary.
        self.parse_parameter = parse_parameter if parse_parameter else lambda value: value

        # Coerce optional default collections to empty dicts.
        self.default_config_index = default_config_index if default_config_index is not None else {}
        self.default_di_constants = default_di_constants if default_di_constants is not None else {}

        # Initialize the per-flag container cache.
        self._containers: Dict[str, ServiceContainer] = {}

    # * method: normalize_flags (static)
    @staticmethod
    def normalize_flags(*flags) -> List[str]:
        '''
        Flatten a mixed sequence of flags into a flat list of strings.

        :param flags: The flags to normalize.
        :type flags: Tuple[Any, ...]
        :return: A flat list of flag strings.
        :rtype: List[str]
        '''

        # Delegate to the module-level helper.
        return normalize_flags(*flags)

    # * method: create_cache_key
    def create_cache_key(self, flags: List[str] = None) -> str:
        '''
        Create a cache key for the given flags.

        :param flags: The feature or data flags to encode.
        :type flags: List[str] | None
        :return: The cache key.
        :rtype: str
        '''

        # Delegate to the module-level helper.
        return create_cache_key(flags)

    # * method: list_all_settings
    def list_all_settings(self) -> Tuple[List[ServiceRegistration], Dict[str, Any]]:
        '''
        List all service registrations and constants, merged with bootstrap defaults.

        :return: The merged registrations and constants.
        :rtype: Tuple[List[ServiceRegistration], Dict[str, Any]]
        '''

        # Read the registrations and constants from the DI service.
        configurations, constants = self.di_service.list_all()

        # Merge in the bootstrap defaults beneath the repository settings.
        return merge_settings(
            configs=configurations,
            constants=constants,
            default_config_index=self.default_config_index,
            default_constants=self.default_di_constants,
        )

    # * method: load_constants
    def load_constants(self,
            configurations: List[ServiceRegistration] = None,
            constants: Dict[str, Any] = None,
            flags: List[str] = None,
        ) -> Dict[str, Any]:
        '''
        Build the constants dict by parsing top-level constants and per-configuration parameters.

        :param configurations: The list of service registrations.
        :type configurations: List[ServiceRegistration] | None
        :param constants: The top-level constants dictionary.
        :type constants: Dict[str, Any] | None
        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: A dictionary of parsed constants.
        :rtype: Dict[str, Any]
        '''

        # Normalize optional inputs.
        configurations = configurations if configurations else []
        constants = constants if constants else {}
        flags = flags if flags else []

        # Parse the top-level constants with the injected parser.
        constants = {key: self.parse_parameter(value) for key, value in constants.items()}

        # Merge in per-configuration parameters (flagged or default).
        for configuration in configurations:

            # Check for a flagged dependency matching any of the provided flags.
            dependency = configuration.get_dependency(*flags)

            # Use flagged parameters when matched; otherwise use the default parameters.
            if dependency:
                constants.update({key: self.parse_parameter(value) for key, value in dependency.parameters.items()})
            else:
                constants.update({key: self.parse_parameter(value) for key, value in configuration.parameters.items()})

        # Return the merged constants dictionary.
        return constants

    # * method: build_type_map
    def build_type_map(self,
            configurations: List[ServiceRegistration] = None,
            flags: List[str] = None,
        ) -> Dict[str, type]:
        '''
        Resolve service types for each registration based on the provided flags.

        Registrations that resolve to no type are skipped (left unregistered) so
        an unresolved service later surfaces as a raw resolution error at a layer
        with event access.

        :param configurations: The list of service registrations.
        :type configurations: List[ServiceRegistration] | None
        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: A mapping of registration IDs to resolved service types.
        :rtype: Dict[str, type]
        '''

        # Normalize optional inputs.
        configurations = configurations if configurations else []
        flags = flags if flags else []

        # Resolve each registration's service type from the flags.
        type_map = {}
        for configuration in configurations:

            # Resolve the service type for the registration.
            service_type = configuration.get_service_type(*flags)

            # Skip registrations that resolve to no type (left unregistered).
            if not service_type:
                continue

            # Add the resolved type to the type map.
            type_map[configuration.id] = service_type

        # Return the resolved type map.
        return type_map

    # * method: build_container
    def build_container(self, flags: List[str] = None) -> ServiceContainer:
        '''
        Build and cache a service container for the given flags.

        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: The service container instance.
        :rtype: ServiceContainer
        '''

        # Normalize optional flags.
        flags = flags if flags else []

        # Return the cached container for the flag key if present.
        cache_key = self.create_cache_key(flags)
        cached_container = self._containers.get(cache_key)
        if cached_container:
            return cached_container

        # Load and merge the registrations and constants.
        configurations, constants = self.list_all_settings()

        # Parse the constants from configurations and the top-level constants dict.
        constants = self.load_constants(
            configurations=configurations,
            constants=constants,
            flags=flags,
        )

        # Build the service type map from the configurations.
        type_map = self.build_type_map(configurations=configurations, flags=flags)

        # Construct the container, registering constants then services.
        container = ServiceContainer()
        container.add_constants(constants)
        if type_map:
            container.add_services(type_map)

        # Cache and return the container.
        self._containers[cache_key] = container
        return container

    # * method: get_dependency
    def get_dependency(self, registration_id: str, *flags) -> Any:
        '''
        Get a resolved service by its registration ID.

        :param registration_id: The service registration identifier.
        :type registration_id: str
        :param flags: The feature or data flags to use.
        :type flags: Tuple[Any, ...]
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Normalize the provided flags.
        normalized_flags = self.normalize_flags(*flags)

        # Build (or retrieve) the container for these flags.
        container = self.build_container(normalized_flags)

        # Return the resolved service from the container.
        return container.get_service(registration_id)
