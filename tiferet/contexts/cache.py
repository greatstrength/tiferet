# *** imports

# ** core
from typing import Any, Dict, Tuple

# *** contexts

# ** context: cache_context
class CacheContext(object):
    '''
    A context for managing cache operations within Tiferet applications.

    Items are stored in named namespaces identified by prefix tuples
    (e.g. ``('app', 'errors')``). The root namespace, addressed by the
    empty prefix ``()``, holds items stored without any prefix. All
    item-level methods accept an optional ``*prefix`` variadic argument;
    omitting it addresses the root namespace, preserving backward
    compatibility for callers that pass only a key.
    '''

    # * attribute: _cache (private)
    _cache: Dict[Tuple[str, ...], Dict[str, Any]]

    # * init
    def __init__(self, cache: Dict[str, Any] = None):
        '''
        Initialize the cache context.

        :param cache: An optional flat dict used to pre-seed the root namespace.
        :type cache: Dict[str, Any] | None
        '''

        # Initialize the namespace store as an empty dict.
        self._cache = {}

        # Place any pre-seeded entries in the root namespace.
        if cache is not None:
            self._cache[()] = dict(cache)

    # * method: get
    def get(self, key: str, *prefix: str) -> Any:
        '''
        Retrieve an item from the cache.

        :param key: The key of the item to retrieve.
        :type key: str
        :param prefix: The namespace prefix tuple; omit for the root namespace.
        :type prefix: str
        :return: The cached item, or None if not found.
        :rtype: Any
        '''

        # Look up the namespace, then the key within it.
        namespace = self._cache.get(tuple(prefix))
        return namespace.get(key) if namespace is not None else None

    # * method: set
    def set(self, key: str, value: Any, *prefix: str):
        '''
        Store an item in the cache.

        :param key: The key to store the value under.
        :type key: str
        :param value: The value to store.
        :type value: Any
        :param prefix: The namespace prefix tuple; omit for the root namespace.
        :type prefix: str
        '''

        # Create the namespace on first use, then store the value.
        prefix_t = tuple(prefix)
        if prefix_t not in self._cache:
            self._cache[prefix_t] = {}
        self._cache[prefix_t][key] = value

    # * method: delete
    def delete(self, key: str, *prefix: str):
        '''
        Remove an item from the cache. No-op when the key is absent.

        :param key: The key of the item to remove.
        :type key: str
        :param prefix: The namespace prefix tuple; omit for the root namespace.
        :type prefix: str
        '''

        # Remove the key from the namespace; ignore missing keys or namespaces.
        namespace = self._cache.get(tuple(prefix))
        if namespace is not None:
            namespace.pop(key, None)

    # * method: get_by_prefix
    def get_by_prefix(self, *prefix: str) -> Dict[str, Any]:
        '''
        Return all items stored under the given namespace prefix.

        :param prefix: The namespace prefix tuple to retrieve.
        :type prefix: str
        :return: A shallow copy of the namespace mapping (key → value),
            or an empty dict when the namespace has no entries.
        :rtype: Dict[str, Any]
        '''

        # Return a copy of the namespace dict, defaulting to empty.
        return dict(self._cache.get(tuple(prefix), {}))

    # * method: clear
    def clear(self):
        '''
        Clear all namespaces and items from the cache.
        '''

        # Clear all namespaces.
        self._cache.clear()
