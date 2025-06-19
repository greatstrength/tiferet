# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..configs import *


# *** contexts

# ** context: cache_context
class CacheContext(object):
    '''
    A context for managing cache operations within Tiferet applications.
    '''
    
    # * attribute: cache (private)
    _cache = Dict[str, Any]

    # * method: init
    def __init__(self, cache: Dict[str, Any] = {}):
        '''
        Initialize the cache context.
        :param cache: An optional initial cache dictionary.
        :type cache: dict
        '''

        # Initialize the cache with the provided dictionary.
        self._cache = cache

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
        return self._cache.get(key)

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
        self._cache[key] = value

    # * method: delete
    def delete(self, key: str):
        '''
        Remove an item from the cache.
        :param key: The key of the item to remove.
        :type key: str
        '''

        # Remove the item from the cache.
        self._cache.pop(key, None)

    # * method: clear
    def clear(self):
        '''
        Clear all items from the cache.
        '''

        # Clear the cache.
        self._cache.clear()
