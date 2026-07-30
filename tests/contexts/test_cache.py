"""Tiferet Cache Context Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.contexts.cache import CacheContext

# *** fixtures

# ** fixture: cache_context
@pytest.fixture
def cache_context() -> CacheContext:
    '''
    Fixture to provide a fresh CacheContext instance for each test.

    :return: A fresh CacheContext instance.
    :rtype: CacheContext
    '''

    # Return a fresh cache context.
    return CacheContext()

# *** tests

# ** test: test_cache_get_root_namespace
def test_cache_get_root_namespace(cache_context: CacheContext):
    '''
    Test that get(key) with no prefix returns a root-namespace value.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a value in the root namespace directly and retrieve it with no prefix.
    cache_context._cache[()]['key1'] = 'value1'
    assert cache_context.get('key1') == 'value1'

# ** test: test_cache_set_root_namespace
def test_cache_set_root_namespace(cache_context: CacheContext):
    '''
    Test that set(key, value) with no prefix stores the value in the root namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a value with no prefix and assert it is stored under the root namespace.
    cache_context.set('key1', 'value1')
    assert cache_context._cache[()]['key1'] == 'value1'

# ** test: test_cache_set_and_get_with_prefix
def test_cache_set_and_get_with_prefix(cache_context: CacheContext):
    '''
    Test that set/get round-trip a value under a namespace prefix.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a value under a namespace prefix and assert it round-trips.
    cache_context.set('key1', 'value1', 'app', 'errors')
    assert cache_context.get('key1', 'app', 'errors') == 'value1'

# ** test: test_cache_get_by_prefix_returns_all
def test_cache_get_by_prefix_returns_all(cache_context: CacheContext):
    '''
    Test that get_by_prefix returns all keys stored under a namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set multiple values under the same namespace prefix.
    cache_context.set('key1', 'value1', 'app', 'errors')
    cache_context.set('key2', 'value2', 'app', 'errors')

    # Assert get_by_prefix returns a shallow copy of all items under the namespace.
    assert cache_context.get_by_prefix('app', 'errors') == {
        'key1': 'value1',
        'key2': 'value2',
    }

# ** test: test_cache_get_by_prefix_empty
def test_cache_get_by_prefix_empty(cache_context: CacheContext):
    '''
    Test that get_by_prefix returns an empty dict for an absent namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Assert an absent namespace returns an empty dict.
    assert cache_context.get_by_prefix('absent', 'namespace') == {}

# ** test: test_cache_delete_with_prefix
def test_cache_delete_with_prefix(cache_context: CacheContext):
    '''
    Test that delete(key, *prefix) removes the key while the namespace remains.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a value under a namespace prefix, then delete it.
    cache_context.set('key1', 'value1', 'app', 'errors')
    cache_context.delete('key1', 'app', 'errors')

    # Assert the key is gone but the namespace still exists (empty).
    assert cache_context.get('key1', 'app', 'errors') is None
    assert cache_context.get_by_prefix('app', 'errors') == {}

# ** test: test_cache_delete_absent_key_no_op
def test_cache_delete_absent_key_no_op(cache_context: CacheContext):
    '''
    Test that deleting an absent key raises no error.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Deleting a key from an absent namespace should not raise.
    cache_context.delete('non_existent_key')
    cache_context.delete('non_existent_key', 'app', 'errors')

# ** test: test_cache_clear
def test_cache_clear(cache_context: CacheContext):
    '''
    Test that clear() empties all namespaces.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Populate the root namespace and a prefixed namespace.
    cache_context.set('key1', 'value1')
    cache_context.set('key2', 'value2', 'app', 'errors')

    # Clear the cache and assert all namespaces are empty.
    cache_context.clear()
    assert cache_context.get('key1') is None
    assert cache_context.get_by_prefix('app', 'errors') == {}

# ** test: test_cache_init_with_existing_values
def test_cache_init_with_existing_values():
    '''
    Test that the constructor seeds the root namespace with an initial cache dict.
    '''

    # Construct a cache context with an initial cache dict.
    cache_context = CacheContext(cache={'k': 'v'})

    # Assert the initial values are available in the root namespace.
    assert cache_context.get('k') == 'v'
