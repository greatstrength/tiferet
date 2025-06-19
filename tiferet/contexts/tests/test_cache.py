# *** imports

# ** infra
import pytest
# ** app
from ..cache import *

# *** fixtures

# ** fixture: initial_cache
@pytest.fixture
def initial_cache():
    return {"key1": "value1", "key2": "value2"}

# ** fixture: cache_context
@pytest.fixture
def cache_context():
    """Fixture to provide a fresh CacheContext instance for each test."""
    return CacheContext()


# *** tests

# ** test: test_init_with_initial_cache
def test_init_with_initial_cache(initial_cache):
    cache = CacheContext(initial_cache)
    assert cache._cache == initial_cache, "Cache should initialize with given data"

# ** test: test_init_without_initial_cache
def test_init_without_initial_cache(cache_context):
    assert cache_context.cache == {}, "Cache should initialize empty if no data provided"

# ** test: test_get_existing_key
def test_get_existing_key(cache_context):
    cache_context.set("test_key", "test_value")
    assert cache_context.get("test_key") == "test_value", "Should return the correct value"

# ** test: test_get_non_existent_key
def test_get_non_existent_key(cache_context):
    assert cache_context.get("non_existent_key") is None, "Should return None for non-existent key"

# ** test: test_set
def test_set(cache_context):
    cache_context.set("new_key", "new_value")
    assert cache_context.get("new_key") == "new_value", "Should set the key-value in cache"

# ** test: test_set_existing_key
def test_delete_existing_key(cache_context):
    cache_context.set("to_delete", "value")
    cache_context.delete("to_delete")
    assert "to_delete" not in cache_context.cache, "Key should be deleted from cache"

# ** test: test_delete_non_existent_key
def test_delete_non_existent_key(cache_context):
    cache_context.delete("non_existent_key")
    assert "non_existent_key" not in cache_context.cache, "Deleting non-existent key should do nothing"

# ** test: test_clear
def test_clear(cache_context):
    cache_context.set("key1", "value1")
    cache_context.set("key2", "value2")
    cache_context.clear()
    assert cache_context.cache == {}, "Cache should be empty after clear"

# ** test: test_clear_empty_cache
def test_multiple_operations(cache_context):
    # Test a sequence of operations
    cache_context.set("a", 1)
    cache_context.set("b", 2)
    assert cache_context.get("a") == 1
    assert cache_context.get("b") == 2
    cache_context.delete("a")
    assert cache_context.get("a") is None
    assert cache_context.get("b") == 2
    cache_context.clear()
    assert cache_context.get("b") is None