"""Tiferet DI Settings"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List, Tuple
import inspect

# ** infra
from dependency_injector import containers, providers

# ** app
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..domain import ServiceConfiguration
from ..events import RaiseError, ParseParameter
from ..interfaces.di import DIService


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

        # Attempt to retrieve and invoke the provider from the container.
        try:
            provider = self.container.providers.get(service_id)

            # If no provider was found, raise an error.
            if provider is None:
                RaiseError.execute(
                    'INVALID_DEPENDENCY_ERROR',
                    f'Dependency {service_id} could not be resolved: not registered.',
                    dependency_name=service_id,
                    exception=f'No provider registered for {service_id}.',
                )

            # Invoke the provider to resolve the dependency.
            return provider()

        # Re-raise TiferetErrors without wrapping.
        except Exception as e:
            from ..assets.exceptions import TiferetError
            if isinstance(e, TiferetError):
                raise

            # Wrap unexpected resolution errors in a structured error.
            RaiseError.execute(
                'INVALID_DEPENDENCY_ERROR',
                f'Dependency {service_id} could not be resolved: {str(e)}',
                dependency_name=service_id,
                exception=str(e),
            )

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

        # Inspect the constructor signature to identify injectable parameters.
        try:
            sig = inspect.signature(service_type.__init__)
        except (ValueError, TypeError):
            return providers.Factory(service_type)

        # Build kwargs mapping from constructor parameter names to sibling providers.
        kwargs = {}
        for param_name, param in sig.parameters.items():

            # Skip self and variadic parameters.
            if param_name == 'self':
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            # Wire the parameter to a sibling provider if one exists.
            sibling = self.container.providers.get(param_name)
            if sibling is not None:
                kwargs[param_name] = sibling

        # Return the Factory provider with wired kwargs.
        return providers.Factory(service_type, **kwargs)

# ** class: service_resolver
class ServiceResolver(object):
    '''
    The application's service provider. It takes a DIService as a direct
    dependency (in the spirit of a domain event), reads service configurations
    and constants, assembles a per-flag type map and constant set, and builds
    and caches a ServiceContainer engine per flag set to resolve dependencies.
    '''

    # * attribute: di_service
    di_service: DIService

    # * attribute: container_factory
    container_factory: Callable

    # * attribute: default_config_index
    default_config_index: Dict[str, ServiceConfiguration]

    # * attribute: default_di_constants
    default_di_constants: Dict[str, Any]

    # * init
    def __init__(self,
            di_service: DIService,
            container_factory: Callable = None,
            default_config_index: Dict[str, ServiceConfiguration] = None,
            default_di_constants: Dict[str, Any] = None,
        ):
        '''
        Initialize the service resolver.

        :param di_service: The DI service (repository) supplying service configurations and constants.
        :type di_service: DIService
        :param container_factory: Optional factory for creating the internal service container.
        :type container_factory: Callable | None
        :param default_config_index: Optional typed default service configuration index,
            keyed by id, merged beneath the repository's configurations.
        :type default_config_index: Dict[str, ServiceConfiguration] | None
        :param default_di_constants: Optional default constants merged beneath the
            repository's constants at lower priority.
        :type default_di_constants: Dict[str, Any] | None
        '''

        # Set the DI repository dependency.
        self.di_service = di_service

        # Assign the container factory, defaulting to the built-in one.
        self.container_factory = container_factory if container_factory else self.default_container

        # Store the typed bootstrap defaults, defaulting to empty containers.
        self.default_config_index = default_config_index if default_config_index is not None else {}
        self.default_di_constants = default_di_constants if default_di_constants is not None else {}

        # Initialize the per-flag service container cache.
        self._containers: Dict[str, ServiceContainer] = {}

    # * method: default_container (static)
    @staticmethod
    def default_container(type_map: Dict[str, type] = None, **constants) -> ServiceContainer:
        '''
        Create the default service container for dependency resolution.

        :param type_map: Mapping of service IDs to dependency types.
        :type type_map: Dict[str, type]
        :param constants: Constant values to register in the container.
        :type constants: dict
        :return: A configured service container.
        :rtype: ServiceContainer
        '''

        # Create an empty container and register constants first
        # so Factory providers can wire constructor parameters.
        container = ServiceContainer()
        container.add_constants(constants)

        # Add service types after constants are available.
        if type_map:
            container.add_services(type_map)

        # Return the configured container.
        return container

    # * method: normalize_flags (static)
    @staticmethod
    def normalize_flags(*flags) -> List[str]:
        '''
        Normalize a mixed sequence of flag arguments into a flat list of strings.

        Accepts individual strings, lists, tuples, or any combination thereof.

        :param flags: The flags to normalize.
        :type flags: str | list | tuple
        :return: A flat list of flag strings.
        :rtype: List[str]
        '''

        # Flatten the flags into a single list.
        result: List[str] = []
        for flag in flags:
            if isinstance(flag, (list, tuple)):
                result.extend(str(f) for f in flag)
            else:
                result.append(str(flag))

        # Return the flattened list.
        return result

    # * method: create_cache_key
    def create_cache_key(self, flags: List[str] = None) -> str:
        '''
        Create a cache key for the service container.

        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: The cache key.
        :rtype: str
        '''

        # Create the cache key from the flags.
        return f"feature_services{'_' + '_'.join(flags) if flags else ''}"

    # * method: list_all_settings
    def list_all_settings(self) -> Tuple[List[ServiceConfiguration], Dict[str, Any]]:
        '''
        List all service configurations and constants from the DI service,
        merging the bootstrap defaults for any service ID or constant not
        present in the repository.

        :return: Merged list of service configurations and constants.
        :rtype: Tuple[List[ServiceConfiguration], Dict[str, Any]]
        '''

        # Retrieve configurations and constants from the DI service.
        configs, constants = self.di_service.list_all()

        # Build the set of existing service IDs for deduplication.
        existing_ids = {c.id for c in (configs or [])}

        # Merge default-index entries for any service ID not already present.
        default_configs = [
            config
            for config_id, config in (self.default_config_index or {}).items()
            if config_id not in existing_ids
        ]

        # Merge constants: defaults are lower priority than repository constants.
        merged_constants = {**(self.default_di_constants or {}), **(constants or {})}

        # Return the merged configurations and constants.
        return list(configs or []) + default_configs, merged_constants

    # * method: load_constants
    def load_constants(self,
            configurations: List[ServiceConfiguration] = None,
            constants: Dict[str, Any] = None,
            flags: List[str] = None,
        ) -> Dict[str, Any]:
        '''
        Build the constants dict by parsing top-level constants and per-configuration parameters.

        :param configurations: The list of service configurations.
        :type configurations: List[ServiceConfiguration] | None
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

        # Parse the top-level constants.
        constants = {k: ParseParameter.execute(v) for k, v in constants.items()}

        # Merge in per-configuration parameters (flagged or default).
        for config in configurations:

            # Check for a flagged dependency matching any of the provided flags.
            dependency = config.get_dependency(*flags)

            # Use flagged parameters if available; otherwise use the default parameters.
            if dependency:
                constants.update({k: ParseParameter.execute(v) for k, v in dependency.parameters.items()})
            else:
                constants.update({k: ParseParameter.execute(v) for k, v in config.parameters.items()})

        # Return the merged constants dictionary.
        return constants

    # * method: build_type_map
    def build_type_map(self,
            configurations: List[ServiceConfiguration] = None,
            flags: List[str] = None,
        ) -> Dict[str, type]:
        '''
        Resolve the service type for each configuration based on the provided flags.

        :param configurations: The list of service configurations.
        :type configurations: List[ServiceConfiguration] | None
        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: A mapping of service configuration IDs to their resolved types.
        :rtype: Dict[str, type]
        '''

        # Normalize optional inputs.
        configurations = configurations if configurations else []
        flags = flags if flags else []

        # Resolve service types from configurations.
        type_map: Dict[str, type] = {}
        for config in configurations:

            # Get the dependency type based on the flags.
            dep_type = config.get_service_type(*flags)

            # If no type is found, raise an error.
            if not dep_type:
                RaiseError.execute(
                    DEPENDENCY_TYPE_NOT_FOUND_ID,
                    f'No dependency type found for service configuration {config.id} with flags {flags}.',
                    configuration_id=config.id,
                    flags=flags,
                )

            # Add the resolved type to the service type mapping.
            type_map[config.id] = dep_type

        # Return the resolved type mapping.
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

        # Create the cache key from the flags.
        cache_key = self.create_cache_key(flags)

        # Return the cached container if available.
        cached_container = self._containers.get(cache_key)
        if cached_container:
            return cached_container

        # Get all service configurations and constants, merging bootstrap defaults.
        configurations, constants = self.list_all_settings()

        # Load and parse constants from configurations and the top-level constants dict.
        constants = self.load_constants(
            configurations=configurations,
            constants=constants,
            flags=flags,
        )

        # Resolve service types from configurations.
        type_map = self.build_type_map(
            configurations=configurations,
            flags=flags,
        )

        # Build the service container using the configured factory.
        container = self.container_factory(
            type_map=type_map,
            **constants,
        )

        # Cache and return the container.
        self._containers[cache_key] = container
        return container

    # * method: get_dependency
    def get_dependency(self, configuration_id: str, *flags) -> Any:
        '''
        Get a resolved service by its configuration ID.

        Accepts flags as individual strings, lists, or tuples in any combination.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flags: The feature or data flags to use.
        :type flags: str | list | tuple
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Normalize the flags into a flat list.
        normalized = self.normalize_flags(*flags) if flags else []

        # Build (or retrieve) the service container for these flags.
        container = self.build_container(normalized)

        # Return the resolved service from the container.
        return container.get_service(configuration_id)
