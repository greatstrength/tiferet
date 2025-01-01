# *** imports

# ** app
from ..configs import *


# *** contexts

# ** context: cache_context
class CacheContext(Model):
    '''
    A context for managing cache operations within Tiferet applications.
    '''

    # * attribute: cache
    cache = DictType(
        StringType(),
        default={},
        metadata=dict(
            description='The cache storage.'
        )
    )

    # * method: init
    def __init__(self, initial_cache: Dict[str, Any] = None):
        '''
        Initialize the CacheContext.

        :param initial_cache: An optional initial state for the cache.
        :type initial_cache: dict
        '''
        super().__init__(dict(cache=initial_cache or {}))

    # * method: get
    def get(self, key: str) -> Any:
        '''
        Retrieve an item from the cache.

        :param key: The key of the item to retrieve.
        :type key: str
        :return: The cached item or None if not found.
        :rtype: Any
        '''

        # Return the item from the cache.
        return self.cache.get(key)

    # * method: set
    def set(self, key: str, value: Any):
        '''
        Store an item in the cache.

        :param key: The key to store the value under.
        :type key: str
        :param value: The value to store.
        :type value: Any
        '''

        # Store the value in the cache.
        self.cache[key] = value

    # * method: delete
    def delete(self, key: str):
        '''
        Remove an item from the cache.

        :param key: The key of the item to remove.
        :type key: str
        '''

        # Remove the item from the cache.
        self.cache.pop(key, None)

    # * method: clear
    def clear(self):
        '''
        Clear all items from the cache.
        '''

        # Clear the cache.
        self.cache.clear()