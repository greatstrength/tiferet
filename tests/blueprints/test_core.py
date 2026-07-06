"""Tiferet Core Blueprint Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet import assets as a
from tiferet.blueprints.core import build_cache
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import error_cache_key
from tiferet.contexts.app import app_service_cache_key, app_constant_cache_key
from tiferet.domain import Error, AppServiceDependency

# *** tests

# ** test: build_cache_returns_cache_context
def test_build_cache_returns_cache_context():
    '''
    Test that core.build_cache returns a CacheContext instance.
    '''

    # Invoke build_cache with no arguments.
    result = build_cache()

    # Assert the result is a CacheContext.
    assert isinstance(result, CacheContext)


# ** test: build_cache_seeds_all_three_catalogs
def test_build_cache_seeds_all_three_catalogs():
    '''
    Test that core.build_cache seeds errors, app services, and app constants,
    totalling the combined size of the three catalogs.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert the cache size equals the sum of the three seeded catalogs.
    expected = (
        len(a.error.CORE_DEFAULT_ERRORS)
        + len(a.app.CORE_DEFAULT_SERVICES)
        + len(a.app.CORE_DEFAULT_CONSTANTS)
    )
    assert len(cache._cache) == expected


# ** test: build_cache_seeds_typed_entries_per_catalog
def test_build_cache_seeds_typed_entries_per_catalog():
    '''
    Test that each catalog is seeded with the expected value type: errors as
    Error domain objects, services as AppServiceDependency, constants as scalars.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert each error is an Error domain object under its prefixed key.
    for error_id in a.error.CORE_DEFAULT_ERRORS:
        assert isinstance(cache.get(error_cache_key(error_id)), Error)

    # Assert each service is an AppServiceDependency under its prefixed key.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert isinstance(
            cache.get(app_service_cache_key(service_id)),
            AppServiceDependency,
        )

    # Assert each constant is its scalar value under its prefixed key.
    for name, value in a.app.CORE_DEFAULT_CONSTANTS.items():
        assert cache.get(app_constant_cache_key(name)) == value


# ** test: build_cache_specific_service_and_constant_retrievable
def test_build_cache_specific_service_and_constant_retrievable():
    '''
    Test that a known service (di_service) and constant (cli_config) are
    retrievable from the pre-seeded cache via their prefixed cache keys.
    '''

    # Build the cache.
    cache = build_cache()

    # Retrieve the di_service dependency by its prefixed key.
    service = cache.get(app_service_cache_key('di_service'))
    assert isinstance(service, AppServiceDependency)
    assert service.service_id == 'di_service'

    # Retrieve the cli_config constant by its prefixed key.
    assert cache.get(app_constant_cache_key('cli_config')) == 'config.yml'
