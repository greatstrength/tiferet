"""Tiferet Core Blueprint Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet import assets as a
from tiferet.blueprints.core import (
    build_cache,
    build_app_service_container,
    parse_parameter,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import error_cache_key
from tiferet.contexts.app import app_service_cache_key, app_constant_cache_key
from tiferet.domain import Error, AppInterface, AppServiceDependency
from tiferet.repos.di import DIConfigRepository

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


# ** test: build_app_service_container_exposes_core_services
def test_build_app_service_container_exposes_core_services():
    '''
    Test that build_app_service_container exposes every core service for an
    interface that adds no overrides.
    '''

    # Build the seeded cache and a minimal interface with no overrides.
    cache = build_cache()
    interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
    )

    # Build the app service container.
    container = build_app_service_container(cache, interface)

    # Assert every core service id resolves to a concrete instance.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert container.get_dependency(service_id) is not None


# ** test: build_app_service_container_interface_service_override
def test_build_app_service_container_interface_service_override():
    '''
    Test that an interface-provided service overrides the default by service id.
    '''

    # Build the seeded cache and an interface that overrides error_service.
    cache = build_cache()
    interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[
            AppServiceDependency(
                service_id='error_service',
                module_path='tiferet.repos.di',
                class_name='DIConfigRepository',
            ),
        ],
    )

    # Build the app service container.
    container = build_app_service_container(cache, interface)

    # Assert the interface override replaced the default error_service type.
    assert isinstance(container.get_dependency('error_service'), DIConfigRepository)


# ** test: build_app_service_container_interface_constant_override
def test_build_app_service_container_interface_constant_override():
    '''
    Test that an interface-provided constant overrides the default by name.
    '''

    # Build the seeded cache and an interface that overrides the error_config constant.
    cache = build_cache()
    interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        constants={'error_config': 'override.yml'},
    )

    # Build the app service container.
    container = build_app_service_container(cache, interface)

    # Assert the interface constant override wins over the default.
    assert container.get_dependency('error_config') == 'override.yml'


# ** test: parse_parameter_literal_passthrough
def test_parse_parameter_literal_passthrough():
    '''
    Test that parse_parameter passes a literal value through unchanged.
    '''

    # Assert a plain literal is returned as-is.
    assert parse_parameter('plain_value') == 'plain_value'


# ** test: parse_parameter_resolves_env
def test_parse_parameter_resolves_env(monkeypatch):
    '''
    Test that parse_parameter resolves an $env. reference from the environment.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Set an environment variable and assert the $env. reference resolves to it.
    monkeypatch.setenv('TIFERET_TEST_VAR', 'resolved_value')
    assert parse_parameter('$env.TIFERET_TEST_VAR') == 'resolved_value'
