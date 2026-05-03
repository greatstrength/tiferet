# *** imports

# ** core
from typing import Callable, Any, List, Dict

# ** app
from .cache import CacheContext
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..di import ServiceProvider, DependenciesServiceProvider
from ..domain import ServiceConfiguration
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

    # * attribute: create_service_provider
    create_service_provider: Callable

    # * init
    def __init__(self,
            di_list_all_configs_evt: DomainEvent,
            cache: CacheContext = None,
            create_service_provider: Callable = None,
        ):
        '''
        Initialize the DI context.

        :param di_list_all_configs_evt: The event to list all service configurations and constants.
        :type di_list_all_configs_evt: DomainEvent
        :param cache: The cache context to use for caching service providers.
        :type cache: CacheContext
        :param create_service_provider: Optional factory for creating service providers.
        :type create_service_provider: Callable | None
        '''

        # Assign the attributes.
        self.list_all_configs_handler = di_list_all_configs_evt.execute
        self.cache = cache if cache else CacheContext()
        self.create_service_provider = create_service_provider if create_service_provider else self._default_service_provider

    # * method: _default_service_provider (static)
    @staticmethod
    def _default_service_provider(type_map: Dict[str, type] = None, **constants) -> ServiceProvider:
        '''
        Create the default service provider for DI context resolution.

        :param type_map: Mapping of service IDs to dependency types.
        :type type_map: Dict[str, type]
        :param constants: Constant values to register in the provider.
        :type constants: dict
        :return: A configured service provider.
        :rtype: ServiceProvider
        '''

        # Create a provider seeded with service dependency types.
        provider = DependenciesServiceProvider(services=type_map or {})

        # Add constants to the provider for constructor injection.
        provider.add_constants(constants)

        # Return the configured provider.
        return provider

    # * method: create_cache_key
    def create_cache_key(self, flags: List[str] = None) -> str:
        '''
        Create a cache key for the service provider.

        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: The cache key.
        :rtype: str
        '''

        # Create the cache key from the flags.
        return f"feature_services{'_' + '_'.join(flags) if flags else ''}"

    # * method: build_service_provider
    def build_service_provider(self, flags: List[str] = None) -> ServiceProvider:
        '''
        Build and cache a service provider for the given flags.

        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: The service provider instance.
        :rtype: ServiceProvider
        '''
        # Normalize optional flags.
        flags = flags if flags else []

        # Create the cache key from the flags.
        cache_key = self.create_cache_key(flags)

        # Return the cached provider if available.
        cached_provider = self.cache.get(cache_key)
        if cached_provider:
            return cached_provider

        # Get all service configurations and constants from the DI service.
        configurations, constants = self.list_all_configs_handler()

        # Load and parse constants from configurations and the top-level constants dict.
        constants = self.load_constants(
            configurations=configurations,
            constants=constants,
            flags=flags,
        )

        # Resolve service types from configurations.
        type_map = {}
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

        # Build the service provider using the configured factory.
        provider = self.create_service_provider(
            type_map=type_map,
            **constants,
        )

        # Cache and return the provider.
        self.cache.set(cache_key, provider)
        return provider

    # * method: get_dependency
    def get_dependency(self, configuration_id: str, flags: List[str] = None) -> Any:
        '''
        Get a resolved service by its configuration ID.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flags: The feature or data flags to use.
        :type flags: List[str] | None
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Build (or retrieve) the service provider for these flags.
        provider = self.build_service_provider(flags)

        # Return the resolved service from the provider.
        return provider.get_service(configuration_id)

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
