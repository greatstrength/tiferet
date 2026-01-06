# *** imports

# ** core
from typing import Callable, Any, List

# ** app
from .cache import CacheContext
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..models import ContainerAttribute
from ..commands import RaiseError, ParseParameter
from ..commands.dependencies import *
from ..commands.container import ListAllSettings

# *** contexts

# ** contexts: container_context
class ContainerContext(object):
    '''
    A container context is a class that is used to create a container object.
    '''

    # * attribute: cache
    cache: CacheContext

    # * attribute: list_all_handler
    list_all_handler: Callable

    # * method: init
    def __init__(self, container_list_all_cmd: ListAllSettings, cache: CacheContext = None):
        '''
        Initialize the container context.

        :param container_list_all_cmd: The command to list all container attributes.
        :type container_list_all_cmd: ListAllSettings
        :param cache: The cache context to use for caching container data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.list_all_handler = container_list_all_cmd.execute
        self.cache = cache if cache else CacheContext()

    # * method: create_cache_key
    def create_cache_key(self, flags: List[str] = None) -> str:
        '''
        Create a cache key for the container.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The cache key.
        :rtype: str
        '''

        # Create the cache key from the flags.
        return f"feature_container{'_' + '_'.join(flags) if flags else ''}"

    # * method: build_injector
    def build_injector(self,
            flags: List[str] = [],
        ) -> Injector:
        '''
        Build the container injector.

        :param flags: The feature or data flags to use.
        :type flags: List[str]
        :return: The container injector object.
        :rtype: Injector
        '''

        # Create the cache key for the injector from the flags.
        cache_key = self.create_cache_key(flags)

        # Check if the injector is already cached.
        cached_injector = self.cache.get(cache_key)
        if cached_injector:
            return cached_injector

        # Get all attributes and constants from the container service.
        attributes, constants = self.list_all_handler()

        # Load constants from the attributes.
        constants = self.load_constants(attributes, constants, flags)

        # Create the dependencies for the injector.
        dependencies = {}
        for attr in attributes:
            
            # Get the dependency type based on the flags.
            dep_type = attr.get_type(attr, *flags)

            # If no type is found, raise an error.
            if not dep_type:
                RaiseError.execute(
                    DEPENDENCY_TYPE_NOT_FOUND_ID,
                    f'No dependency type found for attribute {attr.id} with flags {flags}.',
                    attribute_id=attr.id,
                    flags=flags
                )

            # Otherwise, add the dependency to the dependencies dictionary.
            dependencies[attr.id] = dep_type
            
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
    def get_dependency(self, attribute_id: str, flags: List[str] = []) -> Any:
        '''
        Get an injector dependency by its attribute ID.

        :return: The container attribute.
        :rtype: Any
        '''

        # Get the cached injector.
        injector = self.build_injector(flags)

        # Get the dependency from the injector.
        dependency = get_dependency.execute(
            injector=injector,
            dependency_name=attribute_id,
        )

        # Return the dependency.
        return dependency
    
    # * method: load_constants
    def load_constants(self, attributes: List[ContainerAttribute] = [], constants: Dict[str, str] = {}, flags: List[str] = []) -> Dict[str, str]:
        '''
        Load constants from the container attributes.

        :param attributes: The list of container attributes.
        :type attributes: List[ContainerAttribute]
        :param constants: The dictionary of constants.
        :type constants: Dict[str, str]
        :return: A dictionary of constants.
        :rtype: Dict[str, str]
        '''

        # If constants are provided, clean the parameters using the parse_parameter command.
        constants = {k: ParseParameter.execute(v) for k, v in constants.items()}

        # Iterate through each attribute.
        for attr in attributes:

            # If flags are provided, check for dependencies with those flags.
            dependency = attr.get_dependency(*flags)

            # Update the constants dictionary with the parsed parameters from the dependency or the attribute itself.
            if dependency:
                constants.update({k: ParseParameter.execute(v) for k, v in dependency.parameters.items()})

            # If no dependency is found, use the attribute's parameters.
            else:
                constants.update({k: ParseParameter.execute(v) for k, v in attr.parameters.items()})

        # Return the updated constants dictionary.
        return constants
