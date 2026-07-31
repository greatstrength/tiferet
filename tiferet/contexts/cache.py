"""Tiferet Cache Contexts"""

# *** imports

# ** core
from typing import Any, Dict, Tuple

# *** contexts

# ** context: cache_context
class CacheContext(object):
    '''
    A context for managing namespaced cache operations within Tiferet applications.

    Items are stored in namespaces addressed by a prefix; omitting the prefix
    addresses the root namespace, preserving backward compatibility for callers
    that pass only a key.
    '''

    # * attribute: cache (private)
    _cache: Dict[Tuple[str, ...], Dict[str, Any]]

    # * method: init
    def __init__(self, cache: Dict[str, Any] = None) -> None:
        '''
        Initialize the cache context, pre-seeding the root namespace with any
        initial values provided.

        :param cache: An optional initial cache dictionary for the root namespace.
        :type cache: Dict[str, Any] | None
        '''

        # Initialize the namespace store with the root namespace, pre-seeded when provided.
        self._cache = {(): dict(cache) if cache else {}}

    # * method: get
    def get(self, key: str, *prefix: str) -> Any:
        '''
        Retrieve an item from the cache within the given namespace.

        :param key: The key of the item to retrieve.
        :type key: str
        :param prefix: The namespace prefix segments; defaults to the root namespace.
        :type prefix: str
        :return: The cached item or None if not found.
        :rtype: Any
        '''

        # Look up the namespace; return None when absent.
        namespace = self._cache.get(prefix)
        if namespace is None:
            return None

        # Return the item from the namespace.
        return namespace.get(key)

    # * method: set
    def set(self, key: str, value: Any, *prefix: str) -> None:
        '''
        Store an item in the cache within the given namespace, creating the
        namespace on first use.

        :param key: The key to store the value under.
        :type key: str
        :param value: The value to store.
        :type value: Any
        :param prefix: The namespace prefix segments; defaults to the root namespace.
        :type prefix: str
        '''

        # Create the namespace on first use.
        namespace = self._cache.setdefault(prefix, {})

        # Store the value in the namespace.
        namespace[key] = value

    # * method: delete
    def delete(self, key: str, *prefix: str) -> None:
        '''
        Remove an item from the cache within the given namespace. A no-op when
        the key or namespace is absent.

        :param key: The key of the item to remove.
        :type key: str
        :param prefix: The namespace prefix segments; defaults to the root namespace.
        :type prefix: str
        '''

        # Look up the namespace; no-op when absent.
        namespace = self._cache.get(prefix)
        if namespace is None:
            return

        # Remove the item from the namespace if present.
        namespace.pop(key, None)

    # * method: get_by_prefix
    def get_by_prefix(self, *prefix: str) -> Dict[str, Any]:
        '''
        Retrieve a shallow copy of all items stored under the given namespace.

        :param prefix: The namespace prefix segments; defaults to the root namespace.
        :type prefix: str
        :return: A shallow copy of the namespace's items, or an empty dict when absent.
        :rtype: Dict[str, Any]
        '''

        # Return a shallow copy of the namespace, or an empty dict when absent.
        return dict(self._cache.get(prefix, {}))

    # * method: clear
    def clear(self) -> None:
        '''
        Clear all namespaces from the cache, resetting to an empty root namespace.
        '''

        # Reset the cache to a single empty root namespace.
        self._cache = {(): {}}
