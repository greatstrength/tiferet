"""Tiferet Cache Context Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.contexts.cache import CacheContext

# *** fixtures

# ** fixture: initial_cache
@pytest.fixture
def initial_cache() -> dict:
    '''
    Fixture to provide a small flat dict for pre-seeding the root namespace.

    :return: The initial cache dict.
    :rtype: dict
    '''

    # Return the initial cache.
    return {
        'key1': 'value1',
        'key2': 'value2',
    }

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

# ** test: init_with_initial_cache
def test_init_with_initial_cache(initial_cache: dict):
    '''
    Test that the constructor seeds the root namespace with the initial cache.

    :param initial_cache: The initial cache fixture.
    :type initial_cache: dict
    '''

    # Construct a cache context pre-seeded with the initial cache.
    cache_context = CacheContext(cache=initial_cache)

    # Assert each seeded key is available in the root namespace.
    for key, value in initial_cache.items():
        assert cache_context.get(key) == value

    # Assert the root namespace holds exactly the seeded pairs.
    assert cache_context.get_by_prefix() == initial_cache

# ** test: get_existing_key
def test_get_existing_key(cache_context: CacheContext):
    '''
    Test that get returns a value set in the root namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a root value and retrieve it with no prefix.
    cache_context.set('test_key', 'test_value')
    assert cache_context.get('test_key') == 'test_value'

# ** test: get_existing_key_with_prefix
def test_get_existing_key_with_prefix(cache_context: CacheContext):
    '''
    Test that get returns a value set under a multi-segment prefix.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a value under the app errors namespace and retrieve it there.
    cache_context.set('my_error', 'err_val', 'app', 'errors')
    assert cache_context.get('my_error', 'app', 'errors') == 'err_val'

# ** test: get_non_existent_key
def test_get_non_existent_key(cache_context: CacheContext):
    '''
    Test that get returns None for an absent root key.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Assert an absent root key returns None.
    assert cache_context.get('non_existent_key') is None

# ** test: get_non_existent_namespace
def test_get_non_existent_namespace(cache_context: CacheContext):
    '''
    Test that get returns None for an absent namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Assert a key in an absent namespace returns None.
    assert cache_context.get('any_key', 'missing', 'namespace') is None

# ** test: set
def test_set(cache_context: CacheContext):
    '''
    Test that set stores a value in the root namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a root value and assert the root get returns it.
    cache_context.set('new_key', 'new_value')
    assert cache_context.get('new_key') == 'new_value'

# ** test: set_with_prefix
def test_set_with_prefix(cache_context: CacheContext):
    '''
    Test that set under a prefix creates that namespace and leaves the root untouched.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a value under the app services namespace.
    cache_context.set('svc', 'val', 'app', 'services')

    # Assert the prefixed get returns it and the root namespace does not.
    assert cache_context.get('svc', 'app', 'services') == 'val'
    assert cache_context.get('svc') is None

# ** test: delete_existing_key
def test_delete_existing_key(cache_context: CacheContext):
    '''
    Test that delete removes a root key.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a root value, then delete it.
    cache_context.set('del_key', 'del_value')
    cache_context.delete('del_key')

    # Assert the key is gone.
    assert cache_context.get('del_key') is None

# ** test: delete_existing_key_with_prefix
def test_delete_existing_key_with_prefix(cache_context: CacheContext):
    '''
    Test that delete under a prefix removes only the named key.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set two values under the app errors namespace, then delete one.
    cache_context.set('a', 1, 'app', 'errors')
    cache_context.set('b', 2, 'app', 'errors')
    cache_context.delete('a', 'app', 'errors')

    # Assert the deleted key is gone and its sibling remains.
    assert cache_context.get('a', 'app', 'errors') is None
    assert cache_context.get('b', 'app', 'errors') == 2

# ** test: delete_non_existent_key
def test_delete_non_existent_key(cache_context: CacheContext):
    '''
    Test that deleting an absent root key is a no-op.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Delete an absent key without raising.
    cache_context.delete('non_existent_key')

    # Assert the key is still absent.
    assert cache_context.get('non_existent_key') is None

# ** test: multiple_operations
def test_multiple_operations(cache_context: CacheContext):
    '''
    Test a sequence of set, get, delete, and clear on the root namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set two root values and retrieve both.
    cache_context.set('a', 1)
    cache_context.set('b', 2)
    assert cache_context.get('a') == 1
    assert cache_context.get('b') == 2

    # Delete one value; its sibling survives.
    cache_context.delete('a')
    assert cache_context.get('a') is None
    assert cache_context.get('b') == 2

    # Clear the cache; the surviving value is gone.
    cache_context.clear()
    assert cache_context.get('b') is None

# ** test: get_by_prefix_matches
def test_get_by_prefix_matches(cache_context: CacheContext):
    '''
    Test that get_by_prefix returns only the items in the exact namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set values under the app services and app constants namespaces.
    cache_context.set('di', 'svc1', 'app', 'services')
    cache_context.set('error', 'svc2', 'app', 'services')
    cache_context.set('cli', 'const1', 'app', 'constants')

    # Assert only the app services items are returned.
    assert cache_context.get_by_prefix('app', 'services') == {
        'di': 'svc1',
        'error': 'svc2',
    }

# ** test: get_by_prefix_no_match
def test_get_by_prefix_no_match(cache_context: CacheContext):
    '''
    Test that get_by_prefix returns an empty dict for an absent namespace.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set a root value only.
    cache_context.set('other', 'value')

    # Assert the absent app services namespace returns an empty dict.
    assert cache_context.get_by_prefix('app', 'services') == {}

# ** test: get_by_prefix_root
def test_get_by_prefix_root(cache_context: CacheContext):
    '''
    Test that get_by_prefix with no prefix returns the root namespace items.

    :param cache_context: The cache context fixture.
    :type cache_context: CacheContext
    '''

    # Set two root values.
    cache_context.set('r1', 'v1')
    cache_context.set('r2', 'v2')

    # Assert the root namespace items are returned.
    assert cache_context.get_by_prefix() == {
        'r1': 'v1',
        'r2': 'v2',
    }
