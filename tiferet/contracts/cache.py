# *** imports

# ** core
from abc import abstractmethod
from typing import Any

# ** app
from .settings import Service


# ** contracts

# ** contract: cache_service
class CacheService(Service):
    '''
    A contract for cache services in Tiferet applications.
    '''

    # * method: get
    @abstractmethod
    def get(self, key: str) -> Any:
        '''
        Retrieve an item from the cache.

        :param key: The key of the item to retrieve.
        :type key: str
        :return: The cached item or None if not found.
        :rtype: Any
        '''
        raise NotImplementedError(
            'The get method must be implemented by the cache service.'
        )

    # * method: set
    @abstractmethod
    def set(self, key: str, value: Any):
        '''
        Store an item in the cache.

        :param key: The key to store the value under.
        :type key: str
        :param value: The value to store.
        :type value: Any
        '''
        raise NotImplementedError(
            'The set method must be implemented by the cache service.'
        )

    # * method: delete
    @abstractmethod
    def delete(self, key: str):
        '''
        Delete an item from the cache.

        :param key: The key of the item to delete.
        :type key: str
        '''
        raise NotImplementedError(
            'The delete method must be implemented by the cache service.'
        )

    # * method: clear
    @abstractmethod
    def clear(self):
        '''
        Clear the entire cache.
        '''
        raise NotImplementedError(
            'The clear method must be implemented by the cache service.'
        )