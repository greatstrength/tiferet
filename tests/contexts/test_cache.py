# *** imports

# ** infra
import pytest

# ** app
from tiferet.contexts.cache import CacheContext

# *** fixtures

# ** fixture: initial_cache
@pytest.fixture
def initial_cache():
    '''
    Fixture providing a flat dict for root-namespace pre-seeding.

    :return: A small key-value dict.
    :rtype: dict
    '''

    # Return a representative flat dict.
    return {"key1": "value1", "key2": "value2"}


# ** fixture: cache_context
@pytest.fixture
def cache_context():
    '''
    Fixture to provide a fresh CacheContext instance for each test.

    :return: A new, empty CacheContext.
    :rtype: CacheContext
    '''

    # Return a fresh, empty cache context.
    return CacheContext()

# *** tests

# ** test: test_init_with_initial_cache
def test_init_with_initial_cache(initial_cache):
    '''
    Test that a flat dict passed to the constructor is placed in the root namespace.
    '''

    # Construct the cache with a pre-seeded flat dict.
    cache = CacheContext(initial_cache)

    # Assert the flat dict is stored in the root namespace.
    assert cache._cache.get(()) == initial_cache


# ** test: test_init_without_initial_cache
def test_init_without_initial_cache(cache_context):
    '''
    Test that omitting the initial dict produces an empty namespace store.
    '''

    # Assert the namespace store is completely empty.
    assert cache_context._cache == {}


# ** test: test_get_existing_key
def test_get_existing_key(cache_context):
    '''
    Test that get returns the stored value for an existing root-namespace key.
    '''

    # Store and retrieve a root-namespace item.
    cache_context.set("test_key", "test_value")
    assert cache_context.get("test_key") == "test_value"


# ** test: test_get_existing_key_with_prefix
def test_get_existing_key_with_prefix(cache_context):
    '''
    Test that get returns the stored value for an existing prefixed-namespace key.
    '''

    # Store under a namespace prefix and retrieve with the same prefix.
    cache_context.set("my_error", "err_val", 'app', 'errors')
    assert cache_context.get("my_error", 'app', 'errors') == "err_val"


# ** test: test_get_non_existent_key
def test_get_non_existent_key(cache_context):
    '''
    Test that get returns None for a missing key.
    '''

    # Assert a missing key returns None.
    assert cache_context.get("non_existent_key") is None


# ** test: test_get_non_existent_namespace
def test_get_non_existent_namespace(cache_context):
    '''
    Test that get returns None when the namespace has never been written to.
    '''

    # Assert a key in a missing namespace returns None.
    assert cache_context.get("any_key", 'missing', 'namespace') is None


# ** test: test_set
def test_set(cache_context):
    '''
    Test that set stores a value retrievable by the same key and root namespace.
    '''

    # Store and verify a root-namespace item.
    cache_context.set("new_key", "new_value")
    assert cache_context.get("new_key") == "new_value"


# ** test: test_set_with_prefix
def test_set_with_prefix(cache_context):
    '''
    Test that set stores a value in the correct namespace.
    '''

    # Store under a two-element prefix and verify isolation from root namespace.
    cache_context.set("svc", "val", 'app', 'services')
    assert cache_context.get("svc", 'app', 'services') == "val"
    assert cache_context.get("svc") is None


# ** test: test_delete_existing_key
def test_delete_existing_key(cache_context):
    '''
    Test that delete removes an existing root-namespace key.
    '''

    # Store, delete, and verify the key is gone.
    cache_context.set("to_delete", "value")
    cache_context.delete("to_delete")
    assert cache_context.get("to_delete") is None


# ** test: test_delete_existing_key_with_prefix
def test_delete_existing_key_with_prefix(cache_context):
    '''
    Test that delete removes a key from a prefixed namespace without affecting siblings.
    '''

    # Populate a namespace with two keys, delete one, verify isolation.
    cache_context.set("a", 1, 'app', 'errors')
    cache_context.set("b", 2, 'app', 'errors')
    cache_context.delete("a", 'app', 'errors')
    assert cache_context.get("a", 'app', 'errors') is None
    assert cache_context.get("b", 'app', 'errors') == 2


# ** test: test_delete_non_existent_key
def test_delete_non_existent_key(cache_context):
    '''
    Test that deleting a missing key is a no-op.
    '''

    # Deleting a key that was never set should not raise.
    cache_context.delete("non_existent_key")
    assert cache_context.get("non_existent_key") is None


# ** test: test_delete_non_existent_namespace
def test_delete_non_existent_namespace(cache_context):
    '''
    Test that deleting a key from a missing namespace is a no-op.
    '''

    # Deleting from a namespace that was never written to should not raise.
    cache_context.delete("key", 'missing', 'ns')
    assert cache_context._cache == {}


# ** test: test_clear
def test_clear(cache_context):
    '''
    Test that clear removes all namespaces and items.
    '''

    # Populate multiple namespaces, then clear.
    cache_context.set("key1", "value1")
    cache_context.set("key2", "value2", 'app', 'errors')
    cache_context.clear()
    assert cache_context._cache == {}


# ** test: test_multiple_operations
def test_multiple_operations(cache_context):
    '''
    Test a sequence of set, get, delete, and clear operations across namespaces.
    '''

    # Populate root and a named namespace.
    cache_context.set("a", 1)
    cache_context.set("b", 2)
    assert cache_context.get("a") == 1
    assert cache_context.get("b") == 2

    # Delete from root; sibling key must survive.
    cache_context.delete("a")
    assert cache_context.get("a") is None
    assert cache_context.get("b") == 2

    # Clear everything.
    cache_context.clear()
    assert cache_context.get("b") is None


# ** test: test_get_by_prefix_matches
def test_get_by_prefix_matches(cache_context):
    '''
    Test that get_by_prefix returns only the items in the requested namespace.
    '''

    # Populate two namespaces.
    cache_context.set("di", "svc1", 'app', 'services')
    cache_context.set("error", "svc2", 'app', 'services')
    cache_context.set("cli", "const", 'app', 'constants')

    # Only the services namespace should be returned.
    result = cache_context.get_by_prefix('app', 'services')
    assert result == {"di": "svc1", "error": "svc2"}


# ** test: test_get_by_prefix_no_match
def test_get_by_prefix_no_match(cache_context):
    '''
    Test that get_by_prefix returns an empty dict for an unknown namespace.
    '''

    # An item in a different namespace must not appear.
    cache_context.set("other", "value")
    assert cache_context.get_by_prefix('app', 'services') == {}


# ** test: test_get_by_prefix_root
def test_get_by_prefix_root(cache_context):
    '''
    Test that get_by_prefix with no args returns the root namespace.
    '''

    # Items stored without a prefix live in the root namespace.
    cache_context.set("r1", "v1")
    cache_context.set("r2", "v2")
    result = cache_context.get_by_prefix()
    assert result == {"r1": "v1", "r2": "v2"}
