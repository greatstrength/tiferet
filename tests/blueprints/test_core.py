"""Tiferet Core Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet import TiferetError
from tiferet.blueprints.core import (
    build_cache,
    create_app_service,
    get_app_interface,
    build_app_service_container,
    parse_parameter,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.app import APP_SERVICE_CACHE_PREFIX, APP_CONSTANT_CACHE_PREFIX
from tiferet.domain import Error, AppInterface, AppServiceDependency
from tiferet.repos.app import AppConfigRepository
from tiferet.repos.di import DIConfigRepository
from tiferet.repos.error import ErrorConfigRepository

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
    Test that core.build_cache seeds errors, app services, and app constants
    into their respective namespaces.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert each namespace contains the expected number of entries.
    assert len(cache.get_by_prefix(*ERROR_CACHE_PREFIX)) == len(a.error.CORE_DEFAULT_ERRORS)
    assert len(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)) == len(a.app.CORE_DEFAULT_SERVICES)
    assert len(cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX)) == len(a.app.CORE_DEFAULT_CONSTANTS)


# ** test: build_cache_seeds_typed_entries_per_catalog
def test_build_cache_seeds_typed_entries_per_catalog():
    '''
    Test that each catalog is seeded with the expected value type: errors as
    Error domain objects, services as AppServiceDependency, constants as scalars.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert each error is an Error domain object in the error namespace.
    for error_id in a.error.CORE_DEFAULT_ERRORS:
        assert isinstance(cache.get(error_id, *ERROR_CACHE_PREFIX), Error)

    # Assert each service is an AppServiceDependency in the services namespace.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert isinstance(
            cache.get(service_id, *APP_SERVICE_CACHE_PREFIX),
            AppServiceDependency,
        )

    # Assert each constant is its scalar value in the constants namespace.
    for name, value in a.app.CORE_DEFAULT_CONSTANTS.items():
        assert cache.get(name, *APP_CONSTANT_CACHE_PREFIX) == value


# ** test: build_cache_specific_service_and_constant_retrievable
def test_build_cache_specific_service_and_constant_retrievable():
    '''
    Test that a known service (di_service) and constant (cli_config) are
    retrievable from the pre-seeded cache via their prefixed cache keys.
    '''

    # Build the cache.
    cache = build_cache()

    # Retrieve the di_service dependency from the services namespace.
    service = cache.get('di_service', *APP_SERVICE_CACHE_PREFIX)
    assert isinstance(service, AppServiceDependency)
    assert service.service_id == 'di_service'

    # Retrieve the cli_config constant from the constants namespace.
    assert cache.get('cli_config', *APP_CONSTANT_CACHE_PREFIX) == 'config.yml'


# ** test: create_app_service_default_composes_app_config_repository
def test_create_app_service_default_composes_app_config_repository():
    '''
    Test that create_app_service composes the default app service
    (AppConfigRepository) wired to the default app config file.
    '''

    # Compose the default app service.
    service = create_app_service()

    # Assert it is the default app repository wired to the default config file.
    assert isinstance(service, AppConfigRepository)
    assert service.config_file == a.app.DEFAULT_APP_CONFIG_FILE


# ** test: create_app_service_default_parameters_fallback
def test_create_app_service_default_parameters_fallback():
    '''
    Test that create_app_service falls back to the framework default app
    service parameters when none are supplied, wiring app_config by name.
    '''

    # Compose the default app service with no explicit parameters.
    service = create_app_service()

    # Assert the app_config parameter resolved to the framework default.
    assert service.config_file == a.app.DEFAULT_APP_SERVICE_PARAMETERS['app_config']


# ** test: create_app_service_custom_parameter_wiring
def test_create_app_service_custom_parameter_wiring():
    '''
    Test that create_app_service wires an explicit app_config parameter into
    the composed app service constructor by name.
    '''

    # Compose the app service with an explicit app_config override.
    service = create_app_service(parameters={'app_config': 'custom.yml'})

    # Assert the explicit parameter was wired into the constructor.
    assert isinstance(service, AppConfigRepository)
    assert service.config_file == 'custom.yml'


# ** test: create_app_service_custom_service_type
def test_create_app_service_custom_service_type():
    '''
    Test that create_app_service composes a custom service type and wires its
    own declared parameter by name.
    '''

    # Compose a custom service (DIConfigRepository) with its di_config parameter.
    service = create_app_service(
        module_path='tiferet.repos.di',
        class_name='DIConfigRepository',
        parameters={'di_config': 'di_custom.yml'},
    )

    # Assert the custom service type composed with its wired parameter.
    assert isinstance(service, DIConfigRepository)
    assert service.config_file == 'di_custom.yml'


# ** test: get_app_interface_returns_interface
def test_get_app_interface_returns_interface(monkeypatch):
    '''
    Test that get_app_interface returns the interface resolved by the
    GetAppInterface event, sourcing the app service from create_app_service.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a sample interface and a mock app service that returns it.
    sample = AppInterface(
        id='tiferet_app',
        name='Tiferet App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
    )
    app_service = mock.Mock()
    app_service.get.return_value = sample

    # Patch create_app_service so no real repository or config file is composed.
    monkeypatch.setattr(
        'tiferet.blueprints.core.create_app_service',
        lambda *args, **kwargs: app_service,
    )

    # Retrieve the interface by id.
    result = get_app_interface('tiferet_app')

    # Assert the interface is returned and looked up by id via the app service.
    assert result is sample
    app_service.get.assert_called_once_with('tiferet_app')


# ** test: get_app_interface_raises_when_absent
def test_get_app_interface_raises_when_absent(monkeypatch):
    '''
    Test that get_app_interface raises APP_INTERFACE_NOT_FOUND when the app
    service cannot resolve the requested interface.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a mock app service that resolves no interface.
    app_service = mock.Mock()
    app_service.get.return_value = None

    # Patch create_app_service to return the mock app service.
    monkeypatch.setattr(
        'tiferet.blueprints.core.create_app_service',
        lambda *args, **kwargs: app_service,
    )

    # Assert retrieval raises the not-found error.
    with pytest.raises(TiferetError) as exc_info:
        get_app_interface('missing')

    # Assert the structured error code.
    assert exc_info.value.error_code == a.const.APP_INTERFACE_NOT_FOUND_ID


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


# ** test: build_app_service_container_defaults_only_when_no_interface
def test_build_app_service_container_defaults_only_when_no_interface():
    '''
    Test that build_app_service_container returns a defaults-only container when
    no interface is provided, exposing every core service and constant.
    '''

    # Build the container from cache defaults with no interface.
    cache = build_cache()
    container = build_app_service_container(cache)

    # Assert every core service id resolves to a concrete instance.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert container.get_dependency(service_id) is not None

    # Assert every core constant resolves to its default value.
    for name, value in a.app.CORE_DEFAULT_CONSTANTS.items():
        assert container.get_dependency(name) == value


# ** test: build_app_service_container_constant_override_propagates_to_redeclared_service
def test_build_app_service_container_constant_override_propagates_to_redeclared_service():
    '''
    Test that a constant override layered by the interface propagates to a
    service the interface redeclares, guarding the constants-before-services
    ordering (see handoff §4).
    '''

    # Build a seeded cache and an interface that overrides the error_config
    # constant and redeclares error_service with its default definition.
    cache = build_cache()
    interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        constants={'error_config': 'override.yml'},
        services=[
            AppServiceDependency(
                service_id='error_service',
                module_path='tiferet.repos.error',
                class_name='ErrorConfigRepository',
            ),
        ],
    )

    # Build the app service container.
    container = build_app_service_container(cache, interface)

    # Assert the redeclared service was rebuilt against the overridden constant.
    error_service = container.get_dependency('error_service')
    assert isinstance(error_service, ErrorConfigRepository)
    assert error_service.config_file == 'override.yml'


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
