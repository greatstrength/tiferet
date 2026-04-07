# *** imports

# ** core
from typing import Callable, Any, List, Dict

# ** app
from .cache import CacheContext
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..domain import ServiceProvider, DependenciesServiceProvider
from ..domain.di import ServiceConfiguration
from ..events import DomainEvent, RaiseError, ImportDependency, ParseParameter


# *** contexts

# ** context: di_context
class DIContext(object):
    '''
    A context for managing dependency injection configuration and injector lifecycle.
    '''

    # * attribute: cache
    cache: CacheContext

    # * attribute: list_all_configs_handler
    list_all_configs_handler: Callable

    # * attribute: create_service_provider
    create_service_provider: Callable

    # * init
    def __init__(
        self,
        di_list_all_configs_evt: DomainEvent,
        create_service_provider: Callable = None,
        cache: CacheContext = None,
    ):
        '''
        Initialize the DI context.

        :param di_list_all_configs_evt: The event to list all service configurations and constants.
        :type di_list_all_configs_evt: DomainEvent
        :param create_service_provider: A callable factory that creates a service provider (defaults to a simple provider for tests).
        :type create_service_provider: Callable
        :param cache: The cache context to use for caching service providers.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.list_all_configs_handler = di_list_all_configs_evt.execute
        self.create_service_provider = create_service_provider or self._default_service_provider
        self.cache = cache if cache is not None else CacheContext()

    # * method: _default_service_provider (static)
    @staticmethod
    def _default_service_provider(type_map: Dict[str, type] = None, **constants) -> ServiceProvider:
        '''
        Default service provider factory used in tests when none is supplied.
        '''

        # Create and return a simple dependencies service provider with the provided type map and constants.
        provider = DependenciesServiceProvider(services=type_map or {})
        provider.add_constants(constants)
        return provider

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
        if not flags:
            return "feature_services"
        return f"feature_services_{'_'.join(flags)}"

    # * method: build_service_provider
    def build_service_provider(self, flags: List[str] = None) -> Any:
        '''
        Build the service provider for dependency injection.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The service provider instance.
        :rtype: Any
        '''

        flags = flags or []

        # Create the cache key for the service provider from the flags.
        cache_key = self.create_cache_key(flags)

        # Check if the service provider is already cached.
        cached_provider = self.cache.get(cache_key)
        if cached_provider is not None:
            return cached_provider

        # Get all service configurations and constants from the DI service.
        configurations, constants = self.list_all_configs_handler()

        # Load constants from the service configurations (flags take precedence).
        constants = self.load_constants(configurations, constants, flags)

        # Create the type map for the service provider.
        type_map = {}
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

            # Otherwise, add the dependency to the type map.
            type_map[config.id] = dep_type

        # Create the service provider with the type map and constants.
        provider = self.create_service_provider(
            type_map=type_map,
            **constants,
        )

        # Cache the service provider.
        self.cache.set(cache_key, provider)

        # Return the service provider.
        return provider

    # * method: get_dependency
    def get_dependency(self, configuration_id: str, flags: List[str] = None) -> Any:
        '''
        Get an injector dependency by its service configuration ID.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The resolved dependency.
        :rtype: Any
        '''

        flags = flags or []

        # Get the cached service provider.
        provider = self.build_service_provider(flags)

        # Get the dependency from the service provider.
        dependency = provider.get_service(configuration_id)

        # Return the dependency.
        return dependency

    # * method: get_configuration_type
    def get_configuration_type(self, configuration: ServiceConfiguration, *flags) -> type | None:
        '''
        Gets the type of a service configuration based on the provided flags.

        Checks flagged dependencies first (in flag priority order), then
        falls back to the configuration's default module_path/class_name.

        :param configuration: The service configuration to resolve.
        :type configuration: ServiceConfiguration
        :param flags: The flags for the flagged dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the service configuration or None.
        :rtype: type | None
        '''

        # Check the flagged dependencies for the type first.
        for flag in flags:
            dependency = configuration.get_dependency(flag)
            if dependency:
                return ImportDependency.execute(
                    dependency.module_path,
                    dependency.class_name,
                )

        # Otherwise defer to an available default type.
        if configuration.module_path and configuration.class_name:
            return ImportDependency.execute(
                configuration.module_path,
                configuration.class_name,
            )

        # Return None if no type is found.
        return None

    # * method: load_constants
    def load_constants(
        self,
        configurations: List[ServiceConfiguration] = None,
        constants: Dict[str, Any] = None,
        flags: List[str] = None,
    ) -> Dict[str, Any]:
        '''
        Load constants from the service configurations.

        Flagged dependencies take precedence over base configuration parameters.

        :param configurations: The list of service configurations.
        :type configurations: List[ServiceConfiguration]
        :param constants: The dictionary of constants.
        :type constants: Dict[str, Any]
        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: A dictionary of constants.
        :rtype: Dict[str, Any]
        '''

        configurations = configurations or []
        constants = dict(constants) if constants else {}  # copy
        flags = flags or []

        # Parse top-level constants.
        constants = {k: ParseParameter.execute(v) for k, v in constants.items()}

        # Iterate through each service configuration.
        for config in configurations:
            # Flags take precedence.
            dependency = config.get_dependency(*flags) if flags else None

            if dependency and dependency.parameters:
                parsed = {k: ParseParameter.execute(v) for k, v in dependency.parameters.items()}
                constants.update(parsed)
            elif config.parameters:
                parsed = {k: ParseParameter.execute(v) for k, v in config.parameters.items()}
                constants.update(parsed)

        # Return the updated constants dictionary.
        return constants