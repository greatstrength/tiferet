# *** imports

# ** core
from typing import Any, List

# ** app
from .cache import CacheContext
from ..handlers.container import ContainerService
from ..commands import *
from ..commands.dependencies import *


# *** contexts

# ** contexts: container_context
class ContainerContext(Model):
    '''
    A container context is a class that is used to create a container object.
    '''

    # * attribute: cache
    cache: CacheContext

    # * attribute: container_service
    container_service: ContainerService


    # * method: init
    def __init__(self, container_service: ContainerService, cache: CacheContext = None):
        '''
        Initialize the container context.

        :param container_service: The container service to use for executing container requests.
        :type container_service: ContainerService
        :param cache: The cache context to use for caching container data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.container_service = container_service
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
            flags: List[str] = None,
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
        attributes, constants = self.container_service.list_all()

        # Load constants from the attributes.
        constants = self.container_service.load_constants(attributes, constants, flags)

        # Create the dependencies for the injector.
        dependencies = {}
        for attr in attributes:
            try:
                dependencies[attr.id] = self.container_service.get_dependency_type(attr, flags)
            except TiferetError as e:
                raise e
                    

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
