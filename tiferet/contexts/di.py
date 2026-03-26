# *** imports

# ** core
from typing import Callable, Any, List, Dict

# ** app
from .cache import CacheContext
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..di import ServiceProvider, DependenciesServiceProvider
from ..domain.di import ServiceConfiguration
from ..events import DomainEvent, RaiseError, ParseParameter


# *** contexts

# ** context: di_context
class DIContext(object):
    '''
    A context for managing dependency injection configuration and service provider lifecycle.
    '''

    # * attribute: cache
    cache: CacheContext

    # * attribute: list_all_configs_handler
    list_all_configs_handler: Callable

    # * init
    def __init__(self, di_list_all_configs_evt: DomainEvent, cache: CacheContext = None):
        '''
        Initialize the DI context.

        :param di_list_all_configs_evt: The event to list all service configurations and constants.
        :type di_list_all_configs_evt: DomainEvent
        :param cache: The cache context to use for caching service providers.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.list_all_configs_handler = di_list_all_configs_evt.execute
        self.cache = cache if cache else CacheContext()

    # * method: create_cache_key
    def create_cache_key(self, flags: List[str] = None) -> str:
        '''
        Create a cache key for the service provider.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The cache key.
        :rtype: str
        '''

        # Create the cache key from the flags.
        return f"feature_services{'_' + '_'.join(flags) if flags else ''}"

    # * method: build_provider
    def build_provider(self, flags: List[str] = []) -> ServiceProvider:
        '''
        Build and cache a service provider for the given flags.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The service provider instance.
        :rtype: ServiceProvider
        '''

        # Create the cache key from the flags.
        cache_key = self.create_cache_key(flags)

        # Return the cached provider if available.
        cached_provider = self.cache.get(cache_key)
        if cached_provider:
            return cached_provider

        # Get all service configurations and constants from the DI service.
        configurations, constants = self.list_all_configs_handler()

        # Load and parse constants from configurations and the top-level constants dict.
        constants = self.load_constants(configurations, constants, flags)

        # Resolve service types from configurations.
        services = {}
        for config in configurations:

            # Get the dependency type based on the flags.
            dep_type = self.get_configuration_type(config, *flags)

            # If no type is found, raise an error.
            if not dep_type:
                RaiseError.execute(
                    DEPENDENCY_TYPE_NOT_FOUND_ID,
                    f'No dependency type found for service configuration {config.id} with flags {flags}.',
                    configuration_id=config.id,
                    flags=flags,
                )

            # Add the resolved type to the services dictionary.
            services[config.id] = dep_type

        # Merge services and constants and build the provider.
        provider = DependenciesServiceProvider(
            services={**services, **constants},
            name=cache_key,
        )

        # Cache and return the provider.
        self.cache.set(cache_key, provider)
        return provider

    # * method: get_dependency
    def get_dependency(self, configuration_id: str, flags: List[str] = []) -> Any:
        '''
        Get a resolved service by its configuration ID.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Build (or retrieve) the service provider for these flags.
        provider = self.build_provider(flags)

        # Return the resolved service from the provider.
        return provider.get_service(configuration_id)

    # * method: get_configuration_type
    def get_configuration_type(self, configuration: ServiceConfiguration, *flags) -> type:
        '''
        Resolve the implementation type for a service configuration.

        Delegates to ServiceConfiguration.get_service_type() which checks
        flagged dependencies first, then falls back to the default type.

        :param configuration: The service configuration to resolve.
        :type configuration: ServiceConfiguration
        :param flags: The flags for the flagged dependency.
        :type flags: Tuple[str, ...]
        :return: The resolved type, or None.
        :rtype: type
        '''

        # Delegate to the domain method for type resolution.
        return configuration.get_service_type(*flags)

    # * method: load_constants
    def load_constants(self,
            configurations: List[ServiceConfiguration] = [],
            constants: Dict[str, str] = {},
            flags: List[str] = [],
        ) -> Dict[str, str]:
        '''
        Build the constants dict by parsing top-level constants and per-configuration parameters.

        :param configurations: The list of service configurations.
        :type configurations: List[ServiceConfiguration]
        :param constants: The top-level constants dictionary.
        :type constants: Dict[str, str]
        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: A dictionary of parsed constants.
        :rtype: Dict[str, str]
        '''

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
