# *** imports

# ** core
from typing import Callable, Any, List, Dict

# ** app
from .cache import CacheContext
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..di import ServiceProvider, DependenciesServiceProvider
from ..domain.di import ServiceConfiguration
from ..events import DomainEvent, RaiseError, ImportDependency, ParseParameter
from ..events.builder import *

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

    # * init
    def __init__(self, di_list_all_configs_evt: DomainEvent, cache: CacheContext = None):
        '''
        Initialize the DI context.

        :param di_list_all_configs_evt: The event to list all service configurations and constants.
        :type di_list_all_configs_evt: DomainEvent
        :param cache: The cache context to use for caching injector data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.list_all_configs_handler = di_list_all_configs_evt.execute
        self.cache = cache if cache else CacheContext()

    # * method: create_cache_key
    def create_cache_key(self, flags: List[str] = None) -> str:
        '''
        Create a cache key for the injector.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The cache key.
        :rtype: str
        '''

        # Create the cache key from the flags.
        return f"feature_services{'_' + '_'.join(flags) if flags else ''}"

    # * method: build_injector
    def build_injector(self,
            flags: List[str] = [],
        ) -> Injector:
        '''
        Build the dependency injector.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The injector object.
        :rtype: Injector
        '''

        # Create the cache key for the injector from the flags.
        cache_key = self.create_cache_key(flags)

        # Check if the injector is already cached.
        cached_injector = self.cache.get(cache_key)
        if cached_injector:
            return cached_injector

        # Get all service configurations and constants from the DI service.
        configurations, constants = self.list_all_configs_handler()

        # Load constants from the service configurations.
        constants = self.load_constants(configurations, constants, flags)

        # Create the dependencies for the injector.
        dependencies = {}
        for config in configurations:

            # Get the dependency type based on the flags.
            dep_type = self.get_configuration_type(config, *flags)

            # If no type is found, raise an error.
            if not dep_type:
                RaiseError.execute(
                    DEPENDENCY_TYPE_NOT_FOUND_ID,
                    f'No dependency type found for service configuration {config.id} with flags {flags}.',
                    configuration_id=config.id,
                    flags=flags
                )

            # Otherwise, add the dependency to the dependencies dictionary.
            dependencies[config.id] = dep_type

        # Create the injector with the dependencies and constants.
        injector = create_injector.execute(
            cache_key,
            dependencies=dependencies,
            **constants
        )

        # Cache the injector.
        self.cache.set(cache_key, injector)

        # Return the injector.
        return injector

    # * method: get_dependency
    def get_dependency(self, configuration_id: str, flags: List[str] = []) -> Any:
        '''
        Get an injector dependency by its service configuration ID.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The resolved dependency.
        :rtype: Any
        '''

        # Get the cached injector.
        injector = self.build_injector(flags)

        # Get the dependency from the injector.
        dependency = get_dependency.execute(
            injector=injector,
            dependency_name=configuration_id,
        )

        # Return the dependency.
        return dependency

    # * method: get_configuration_type
    def get_configuration_type(self, configuration: ServiceConfiguration, *flags) -> type:
        '''
        Gets the type of a service configuration based on the provided flags.

        Checks flagged dependencies first (in flag priority order), then
        falls back to the configuration's default module_path/class_name.

        :param configuration: The service configuration to resolve.
        :type configuration: ServiceConfiguration
        :param flags: The flags for the flagged dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the service configuration.
        :rtype: type
        '''

        # Check the flagged dependencies for the type first.
        for flag in flags:
            dependency = configuration.get_dependency(flag)
            if dependency:
                return ImportDependency.execute(
                    dependency.module_path,
                    dependency.class_name
                )

        # Otherwise defer to an available default type.
        if configuration.module_path and configuration.class_name:
            return ImportDependency.execute(
                configuration.module_path,
                configuration.class_name
            )

        # Return None if no type is found.
        return None

    # * method: load_constants
    def load_constants(self, configurations: List[ServiceConfiguration] = [], constants: Dict[str, str] = {}, flags: List[str] = []) -> Dict[str, str]:
        '''
        Load constants from the service configurations.

        :param configurations: The list of service configurations.
        :type configurations: List[ServiceConfiguration]
        :param constants: The dictionary of constants.
        :type constants: Dict[str, str]
        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: A dictionary of constants.
        :rtype: Dict[str, str]
        '''

        # If constants are provided, clean the parameters using the parse_parameter command.
        constants = {k: ParseParameter.execute(v) for k, v in constants.items()}

        # Iterate through each service configuration.
        for config in configurations:

            # If flags are provided, check for dependencies with those flags.
            dependency = config.get_dependency(*flags)

            # Update the constants dictionary with the parsed parameters from the dependency or the configuration itself.
            if dependency:
                constants.update({k: ParseParameter.execute(v) for k, v in dependency.parameters.items()})

            # If no dependency is found, use the configuration's parameters.
            else:
                constants.update({k: ParseParameter.execute(v) for k, v in config.parameters.items()})

        # Return the updated constants dictionary.
        return constants
