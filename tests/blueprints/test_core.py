"""Tiferet Core Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet import TiferetError, TiferetAPIError
from tiferet.blueprints.core import (
    build_cache,
    create_app_service,
    get_app_session,
    get_error,
    get_feature,
    build_app_service_container,
    parse_parameter,
    load_cache,
    create_request_context,
    create_feature_context,
    create_session_request,
    execute_feature_handler,
    raise_error_handler,
    response_handler,
    build_logging_context,
    build_app_session_context,
    build_app,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX, FeatureContext
from tiferet.contexts.logging import LoggingContext, LoggingSettings, LOGGING_CACHE_PREFIX
from tiferet.contexts.request import RequestContext
from tiferet.contexts.app import APP_SERVICE_CACHE_PREFIX, APP_CONSTANT_CACHE_PREFIX, AppSessionContext
from tiferet.domain import Error, Feature, AppSession, AppServiceDependency
from tiferet.utils.middleware import CacheMiddleware
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
    Test that core.build_cache seeds errors, app services, app constants, and
    logging settings into their respective namespaces.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert each namespace contains the expected number of entries.
    assert len(cache.get_by_prefix(*ERROR_CACHE_PREFIX)) == len(a.error.CORE_DEFAULT_ERRORS)
    assert len(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)) == len(a.app.CORE_DEFAULT_SERVICES)
    assert len(cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX)) == len(a.app.CORE_DEFAULT_CONSTANTS)

    # Assert the logging namespace contains the default LoggingSettings entry.
    assert isinstance(cache.get('default', *LOGGING_CACHE_PREFIX), LoggingSettings)


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


# ** test: get_app_session_returns_session
def test_get_app_session_returns_session(monkeypatch):
    '''
    Test that get_app_session returns the session resolved by the
    GetAppSession event, sourcing the app service from create_app_service.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a sample session and a mock app service that returns it.
    sample = AppSession(
        id='tiferet_app',
        name='Tiferet App',
    )
    app_service = mock.Mock()
    app_service.get.return_value = sample

    # Patch create_app_service so no real repository or config file is composed.
    monkeypatch.setattr(
        'tiferet.blueprints.core.create_app_service',
        lambda *args, **kwargs: app_service,
    )

    # Retrieve the session by id.
    result = get_app_session('tiferet_app')

    # Assert the session is returned and looked up by id via the app service.
    assert result is sample
    app_service.get.assert_called_once_with('tiferet_app')


# ** test: get_app_session_raises_when_absent
def test_get_app_session_raises_when_absent(monkeypatch):
    '''
    Test that get_app_session raises APP_SESSION_NOT_FOUND when the app
    service cannot resolve the requested session.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a mock app service that resolves no session.
    app_service = mock.Mock()
    app_service.get.return_value = None

    # Patch create_app_service to return the mock app service.
    monkeypatch.setattr(
        'tiferet.blueprints.core.create_app_service',
        lambda *args, **kwargs: app_service,
    )

    # Assert retrieval raises the not-found error.
    with pytest.raises(TiferetError) as exc_info:
        get_app_session('missing')

    # Assert the structured error code.
    assert exc_info.value.error_code == a.const.APP_SESSION_NOT_FOUND_ID


# ** test: build_app_service_container_exposes_core_services
def test_build_app_service_container_exposes_core_services():
    '''
    Test that build_app_service_container exposes every core service for an
    interface that adds no overrides.
    '''

    # Build the seeded cache and a minimal interface with no overrides.
    cache = build_cache()
    interface = AppSession(
        id='test',
        name='Test App',
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
    interface = AppSession(
        id='test',
        name='Test App',
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
    interface = AppSession(
        id='test',
        name='Test App',
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
    interface = AppSession(
        id='test',
        name='Test App',
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


# ** test: get_error_returns_callable
def test_get_error_returns_callable():
    '''
    Test that get_error returns a callable handler bound to the cache and resolver.
    '''

    # Build the handler with a fresh cache and a mock resolver.
    handler = get_error(CacheContext(), mock.Mock())

    # Assert the handler is callable.
    assert callable(handler)


# ** test: get_error_handler_cache_hit
def test_get_error_handler_cache_hit():
    '''
    Test that the get_error handler returns a cached error without invoking
    get_dependency.
    '''

    # Pre-seed the cache with an error under the error cache prefix.
    cache = CacheContext()
    cached_error = Error(id='CACHED_ERROR', name='Cached Error')
    cache.set('CACHED_ERROR', cached_error, *ERROR_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Build and invoke the handler.
    handler = get_error(cache, get_dependency)
    result = handler('CACHED_ERROR')

    # Assert the cached error is returned and get_dependency was not called.
    assert result is cached_error
    get_dependency.assert_not_called()


# ** test: get_error_handler_cache_miss_resolves_event
def test_get_error_handler_cache_miss_resolves_event():
    '''
    Test that the get_error handler resolves a GetError event from the app-scoped
    container and executes it on a cache miss.
    '''

    # Arrange a mock get_dependency that returns a mock GetError event.
    expected_error = Error(id='MISS_ERROR', name='Miss Error')
    get_error_evt = mock.Mock()
    get_error_evt.execute.return_value = expected_error
    get_dependency = mock.Mock(return_value=get_error_evt)

    # Build and invoke the handler against an empty cache.
    handler = get_error(CacheContext(), get_dependency)
    result = handler('MISS_ERROR')

    # Assert get_dependency was called with the correct service id and app flag.
    get_dependency.assert_called_once_with('get_error_evt', 'app')

    # Assert the event was executed with the error code.
    get_error_evt.execute.assert_called_once_with('MISS_ERROR')

    # Assert the resolved error is returned.
    assert result is expected_error


# ** test: get_error_handler_caches_result_after_miss
def test_get_error_handler_caches_result_after_miss():
    '''
    Test that the get_error handler caches the resolved error under ERROR_CACHE_PREFIX
    after a cache miss so subsequent calls hit the cache.
    '''

    # Arrange a mock event that returns a fresh error.
    expected_error = Error(id='NEW_ERROR', name='New Error')
    get_error_evt = mock.Mock()
    get_error_evt.execute.return_value = expected_error
    get_dependency = mock.Mock(return_value=get_error_evt)
    cache = CacheContext()

    # Invoke the handler to trigger a miss.
    handler = get_error(cache, get_dependency)
    handler('NEW_ERROR')

    # Assert the result is now cached under the error prefix.
    assert cache.get('NEW_ERROR', *ERROR_CACHE_PREFIX) is expected_error


# ** test: get_feature_returns_callable
def test_get_feature_returns_callable():
    '''
    Test that get_feature returns a callable handler bound to the cache and resolver.
    '''

    # Build the handler with a fresh cache and a mock resolver.
    handler = get_feature(CacheContext(), mock.Mock())

    # Assert the handler is callable.
    assert callable(handler)


# ** test: get_feature_handler_cache_hit
def test_get_feature_handler_cache_hit():
    '''
    Test that the get_feature handler returns a cached feature without invoking
    get_dependency.
    '''

    # Pre-seed the feature cache namespace with a feature.
    cache = CacheContext()
    cached_feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    cache.set('group.feat', cached_feature, *FEATURE_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Build and invoke the handler.
    handler = get_feature(cache, get_dependency)
    result = handler('group.feat')

    # Assert the cached feature is returned and get_dependency was not called.
    assert result is cached_feature
    get_dependency.assert_not_called()


# ** test: get_feature_handler_cache_miss_resolves_event
def test_get_feature_handler_cache_miss_resolves_event():
    '''
    Test that the get_feature handler resolves a GetFeature event from the app-scoped
    container and executes it with id=feature_id on a cache miss.
    '''

    # Arrange a mock get_dependency that returns a mock GetFeature event.
    expected_feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    get_feature_evt = mock.Mock()
    get_feature_evt.execute.return_value = expected_feature
    get_dependency = mock.Mock(return_value=get_feature_evt)

    # Build and invoke the handler against an empty cache.
    handler = get_feature(CacheContext(), get_dependency)
    result = handler('group.feat')

    # Assert get_dependency was called with the correct service id and app flag.
    get_dependency.assert_called_once_with('get_feature_evt', 'app')

    # Assert the event was executed with the feature id keyword argument.
    get_feature_evt.execute.assert_called_once_with(id='group.feat')

    # Assert the resolved feature is returned.
    assert result is expected_feature


# ** test: get_feature_handler_caches_result_after_miss
def test_get_feature_handler_caches_result_after_miss():
    '''
    Test that the get_feature handler caches the resolved feature under the
    feature cache prefix after a cache miss so subsequent calls hit the cache.
    '''

    # Arrange a mock event that returns a fresh feature.
    expected_feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    get_feature_evt = mock.Mock()
    get_feature_evt.execute.return_value = expected_feature
    get_dependency = mock.Mock(return_value=get_feature_evt)
    cache = CacheContext()

    # Invoke the handler to trigger a miss.
    handler = get_feature(cache, get_dependency)
    handler('group.feat')

    # Assert the result is now cached under the feature cache prefix.
    assert cache.get('group.feat', *FEATURE_CACHE_PREFIX) is expected_feature


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


# ** test: load_cache_returns_root_snapshot_callable
def test_load_cache_returns_root_snapshot_callable():
    '''
    Test that load_cache returns a zero-argument callable yielding the cache's
    root-namespace snapshot.
    '''

    # Seed the root namespace and a prefixed namespace on a fresh cache.
    cache = CacheContext()
    cache.set('root_key', 'root_value')
    cache.set('scoped', 'scoped_value', 'app', 'features')

    # Build the loader and invoke it.
    loader = load_cache(cache)
    snapshot = loader()

    # Assert the loader is callable and returns only the root-namespace entries.
    assert callable(loader)
    assert snapshot == {'root_key': 'root_value'}


# ** test: create_request_context_seeds_feature_id
def test_create_request_context_seeds_feature_id():
    '''
    Test that create_request_context builds a RequestContext seeded with the
    feature id and the supplied data and headers.
    '''

    # Build a feature and compose a request context around it.
    feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    request = create_request_context(
        feature,
        data={'a': 1},
        headers={'h': 'v'},
    )

    # Assert the request is shaped from the feature and inputs.
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'group.feat'
    assert request.data == {'a': 1}
    assert request.headers == {'h': 'v'}


# ** test: create_feature_context_with_preloaded_feature
def test_create_feature_context_with_preloaded_feature():
    '''
    Test that create_feature_context returns the given feature unchanged and a
    FeatureContext, without loading via get_dependency.
    '''

    # Arrange a pre-loaded feature and a resolver that must not be called for loading.
    feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    get_dependency = mock.Mock()
    cache = CacheContext()

    # Compose the feature context from the pre-loaded feature.
    loaded, feature_context = create_feature_context(
        get_dependency, cache, feature=feature
    )

    # Assert the same feature is returned with a wired FeatureContext.
    assert loaded is feature
    assert isinstance(feature_context, FeatureContext)
    assert feature_context.get_dependency is get_dependency
    assert feature_context.cache is cache
    get_dependency.assert_not_called()


# ** test: create_feature_context_loads_by_feature_id
def test_create_feature_context_loads_by_feature_id():
    '''
    Test that create_feature_context loads the feature via the get_feature
    handler when only a feature_id is supplied.
    '''

    # Arrange a resolver returning a GetFeature event that yields the feature.
    expected_feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    get_feature_evt = mock.Mock()
    get_feature_evt.execute.return_value = expected_feature
    get_dependency = mock.Mock(return_value=get_feature_evt)
    cache = CacheContext()

    # Compose the feature context by id.
    loaded, feature_context = create_feature_context(
        get_dependency, cache, feature_id='group.feat'
    )

    # Assert the feature was loaded via the app-scoped GetFeature event.
    assert loaded is expected_feature
    assert isinstance(feature_context, FeatureContext)
    get_dependency.assert_called_once_with('get_feature_evt', 'app')
    get_feature_evt.execute.assert_called_once_with(id='group.feat')


# ** test: create_session_request_builds_request_context
def test_create_session_request_builds_request_context():
    '''
    Test that create_session_request builds a RequestContext with interface_id
    injected into headers, feature_id set, and data wired.
    '''

    # Build the session request.
    request = create_session_request(
        interface_id='test_interface',
        feature_id='group.feat',
        headers={'h': 'v'},
        data={'a': 1},
    )

    # Assert the request is shaped correctly.
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'group.feat'
    assert request.headers.get('interface_id') == 'test_interface'
    assert request.headers.get('h') == 'v'
    assert request.data == {'a': 1}


# ** test: create_session_request_empty_headers_and_data
def test_create_session_request_empty_headers_and_data():
    '''
    Test that create_session_request handles None headers and data,
    producing a request with only interface_id in headers.
    '''

    # Build the session request with no headers or data.
    request = create_session_request(
        interface_id='iface',
        feature_id='g.f',
    )

    # Assert the interface_id is the only header and data defaults to an empty dict.
    assert request.headers == {'interface_id': 'iface'}
    assert request.data == {}


# ** test: execute_feature_handler_returns_callable
def test_execute_feature_handler_returns_callable():
    '''
    Test that execute_feature_handler returns a callable bound to the
    get_dependency and cache.
    '''

    # Build the handler with a mock resolver and fresh cache.
    handler = execute_feature_handler(mock.Mock(), CacheContext())

    # Assert the result is callable.
    assert callable(handler)


# ** test: execute_feature_handler_drives_feature_context
def test_execute_feature_handler_drives_feature_context(monkeypatch):
    '''
    Test that the callable returned by execute_feature_handler loads the
    feature via create_feature_context and drives FeatureContext.execute_feature.
    The handler is void — it does not call handle_response.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a feature and a stub feature context.
    feature = Feature(
        id='group.feat', group_id='group', feature_key='feat', name='Feat'
    )
    request = RequestContext(data={})
    feature_context = mock.Mock()

    # Patch create_feature_context to return the stubbed pair.
    monkeypatch.setattr(
        'tiferet.blueprints.core.create_feature_context',
        lambda *args, **kwargs: (feature, feature_context),
    )

    # Build the handler and invoke it with a flag.
    handler = execute_feature_handler(mock.Mock(), CacheContext())
    result = handler('group.feat', request, 'flag_a')

    # Assert the feature context was driven with the feature, request, and flag.
    feature_context.execute_feature.assert_called_once_with(feature, request, 'flag_a')

    # Assert the handler is void (returns None, not the response).
    assert result is None


# ** test: raise_error_handler_returns_callable
def test_raise_error_handler_returns_callable():
    '''
    Test that raise_error_handler returns a callable bound to the
    get_error_handler.
    '''

    # Build the handler with a mock error retrieval callable.
    handler = raise_error_handler(mock.Mock())

    # Assert the result is callable.
    assert callable(handler)


# ** test: raise_error_handler_raises_api_error_on_tiferet_error
def test_raise_error_handler_raises_api_error_on_tiferet_error(monkeypatch):
    '''
    Test that the callable returned by raise_error_handler raises
    TiferetAPIError when given a TiferetError input.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''
    from tiferet.contexts.error import ErrorContext
    from tiferet.domain import Error

    # Arrange an error domain object and a mock error context.
    error_domain = Error(id='TEST_ERROR', name='Test Error')
    get_error_mock = mock.Mock(return_value=error_domain)

    # Patch BaseContext.for_domain to return a mock error context class.
    error_context_instance = mock.Mock(spec=ErrorContext)
    error_context_instance.format_response.return_value = {
        'error_code': 'TEST_ERROR',
        'name': 'Test Error',
        'message': 'A test error occurred.',
    }
    monkeypatch.setattr(
        'tiferet.blueprints.core.BaseContext.for_domain',
        lambda domain_cls: (lambda **kwargs: error_context_instance),
    )

    # Build the handler and invoke it with a TiferetError.
    handler = raise_error_handler(get_error_mock)
    error = TiferetError('TEST_ERROR', 'A test error occurred.')

    with pytest.raises(TiferetAPIError) as exc_info:
        handler(error)

    # Assert the structured error was raised with the expected data.
    assert exc_info.value.error_code == 'TEST_ERROR'
    assert exc_info.value.name == 'Test Error'
    get_error_mock.assert_called_once_with('TEST_ERROR')


# ** test: raise_error_handler_wraps_plain_exception
def test_raise_error_handler_wraps_plain_exception(monkeypatch):
    '''
    Test that the callable returned by raise_error_handler wraps a plain
    Exception in a TiferetError with APP_ERROR code before formatting.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''
    from tiferet.contexts.error import ErrorContext
    from tiferet.domain import Error

    # Arrange an APP_ERROR domain object and a mock error context.
    error_domain = Error(id='APP_ERROR', name='App Error')
    get_error_mock = mock.Mock(return_value=error_domain)

    # Patch BaseContext.for_domain to return a mock error context class.
    error_context_instance = mock.Mock(spec=ErrorContext)
    error_context_instance.format_response.return_value = {
        'error_code': 'APP_ERROR',
        'name': 'App Error',
        'message': 'An error occurred: something went wrong',
    }
    monkeypatch.setattr(
        'tiferet.blueprints.core.BaseContext.for_domain',
        lambda domain_cls: (lambda **kwargs: error_context_instance),
    )

    # Build the handler and invoke it with a plain Exception.
    handler = raise_error_handler(get_error_mock)

    with pytest.raises(TiferetAPIError) as exc_info:
        handler(Exception('something went wrong'))

    # Assert the exception was wrapped and routed through APP_ERROR.
    assert exc_info.value.error_code == 'APP_ERROR'
    get_error_mock.assert_called_once_with('APP_ERROR')


# ** test: response_handler_delegates_to_request
def test_response_handler_delegates_to_request():
    '''
    Test that response_handler returns the result of request.handle_response().
    '''

    # Arrange a request with a known result.
    request = RequestContext(data={})
    request.set_result({'status': 'ok'})

    # Assert the handler returns the expected response.
    result = response_handler(request)
    assert result == {'status': 'ok'}


# ** test: build_app_service_container_wires_load_cache_into_cache_middleware
def test_build_app_service_container_wires_load_cache_into_cache_middleware():
    '''
    Test that build_app_service_container registers the load_cache constant and
    wires it into the CacheMiddleware singleton via constructor injection.
    '''

    # Build the seeded cache and a defaults-only container.
    cache = build_cache()
    container = build_app_service_container(cache)

    # Assert the load_cache constant resolves to a callable loader.
    loader = container.get_dependency('load_cache')
    assert callable(loader)

    # Assert the cache_middleware singleton composed with the loader wired in.
    middleware = container.get_dependency('cache_middleware')
    assert isinstance(middleware, CacheMiddleware)
    assert middleware.load_cache is loader


# ** test: build_logging_context_returns_logging_context
def test_build_logging_context_returns_logging_context():
    '''
    Test that build_logging_context returns a LoggingContext with the
    assembled LoggingSettings bound as its domain.
    '''

    # Arrange cache seeded with default logging settings.
    cache = build_cache()

    # Arrange a get_dependency that returns a mock logging_list_all_evt.
    logging_evt = mock.Mock()
    logging_evt.execute.return_value = ([], [], [])
    get_dependency = mock.Mock(return_value=logging_evt)

    # Build the logging context.
    result = build_logging_context(cache, get_dependency, logger_id='default')

    # Assert the result is a LoggingContext with a LoggingSettings domain.
    assert isinstance(result, LoggingContext)
    assert isinstance(result.domain, LoggingSettings)
    assert result.logger_id == 'default'


# ** test: build_logging_context_calls_evt_once
def test_build_logging_context_calls_evt_once():
    '''
    Test that build_logging_context resolves logging_list_all_evt from the
    app-scoped container and calls execute() exactly once.
    '''

    # Arrange cache and a mock event.
    cache = build_cache()
    logging_evt = mock.Mock()
    logging_evt.execute.return_value = ([], [], [])
    get_dependency = mock.Mock(return_value=logging_evt)

    # Build the logging context.
    build_logging_context(cache, get_dependency, logger_id='default')

    # Assert the event was resolved and called once.
    get_dependency.assert_called_once_with('logging_list_all_evt', 'app')
    logging_evt.execute.assert_called_once()


# ** test: build_logging_context_uses_defaults_when_evt_returns_empty
def test_build_logging_context_uses_defaults_when_evt_returns_empty():
    '''
    Test that build_logging_context falls back to cache-seeded defaults when
    the event returns empty sections.
    '''

    # Arrange cache and an event that returns all-empty sections.
    cache = build_cache()
    logging_evt = mock.Mock()
    logging_evt.execute.return_value = ([], [], [])
    get_dependency = mock.Mock(return_value=logging_evt)

    # Build the logging context.
    result = build_logging_context(cache, get_dependency, logger_id='default')

    # Assert the domain uses the cache-seeded defaults (non-empty).
    assert len(result.domain.formatters) > 0
    assert len(result.domain.handlers) > 0
    assert len(result.domain.loggers) > 0


# ** test: build_logging_context_uses_repo_data_when_provided
def test_build_logging_context_uses_repo_data_when_provided():
    '''
    Test that build_logging_context uses repo-supplied sections over cache
    defaults when the event returns non-empty data.
    '''
    from tiferet.domain.logging import Formatter, Handler, Logger

    # Arrange cache and an event that returns concrete domain objects.
    cache = build_cache()
    repo_formatter = Formatter(
        id='repo', name='Repo Formatter', format='%(message)s'
    )
    repo_handler = Handler(
        id='repo_h', name='Repo Handler',
        module_path='logging', class_name='NullHandler',
        level='INFO', formatter='repo',
    )
    repo_logger = Logger(
        id='root', name='Root',
        level='INFO', handlers=['repo_h'],
        is_root=True,
    )
    logging_evt = mock.Mock()
    logging_evt.execute.return_value = ([repo_formatter], [repo_handler], [repo_logger])
    get_dependency = mock.Mock(return_value=logging_evt)

    # Build the logging context.
    result = build_logging_context(cache, get_dependency, logger_id='default')

    # Assert the domain uses the repo-supplied data, not the defaults.
    assert result.domain.formatters == [repo_formatter]
    assert result.domain.handlers == [repo_handler]
    assert result.domain.loggers == [repo_logger]


# ** test: build_app_session_context_returns_app_session_context
def test_build_app_session_context_returns_app_session_context(monkeypatch):
    '''
    Test that build_app_session_context returns a fully wired AppSessionContext
    with the domain bound, the resolver handler, and a logging context injected.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a mock app container with no collaborators.
    app_container = mock.Mock()
    app_container.has_dependency.return_value = False
    app_container.get_dependency.return_value = mock.Mock()

    # Arrange a mock resolver.
    resolver = mock.Mock()

    # Arrange a mock logging context.
    logging_ctx = mock.Mock(spec=LoggingContext)

    # Patch build_app_service_container, build_service_resolver, and build_logging_context.
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_app_service_container',
        lambda *a, **kw: app_container,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_service_resolver',
        lambda *a, **kw: resolver,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_logging_context',
        lambda *a, **kw: logging_ctx,
    )

    # Build a minimal app session.
    app_session = AppSession(
        id='test_app',
        name='Test App',
    )
    cache = CacheContext()

    # Build the session context.
    result = build_app_session_context(app_session, cache)

    # Assert the result is an AppSessionContext with domain, resolver, and logging wired.
    assert isinstance(result, AppSessionContext)
    assert result.domain is app_session
    assert result.get_dependency is resolver.get_dependency
    assert result.cache is cache
    assert result._logging is logging_ctx


# ** test: build_app_session_context_injects_logging_context_via_build_logging_context
def test_build_app_session_context_injects_logging_context_via_build_logging_context(monkeypatch):
    '''
    Test that build_app_session_context calls build_logging_context and passes
    its result as logging_context to the constructed AppSessionContext.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange stubs.
    app_container = mock.Mock()
    app_container.has_dependency.return_value = False
    app_container.get_dependency.return_value = mock.Mock()

    logging_ctx = mock.Mock(spec=LoggingContext)
    build_logging_ctx_mock = mock.Mock(return_value=logging_ctx)

    monkeypatch.setattr(
        'tiferet.blueprints.core.build_app_service_container',
        lambda *a, **kw: app_container,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_service_resolver',
        lambda *a, **kw: mock.Mock(),
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_logging_context',
        build_logging_ctx_mock,
    )

    # Build the context.
    app_session = AppSession(
        id='test_app',
        name='Test App',
    )
    result = build_app_session_context(app_session, CacheContext())

    # Assert build_logging_context was called and the result is wired.
    build_logging_ctx_mock.assert_called_once()
    assert result._logging is logging_ctx


# ** test: build_app_session_context_wires_four_fe4_handlers
def test_build_app_session_context_wires_four_fe4_handlers(monkeypatch):
    '''
    Test that build_app_session_context wires all four FE4 template-method
    handler callables onto the resulting hub.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange an app container with no additional collaborators.
    app_container = mock.Mock()
    app_container.has_dependency.return_value = False
    app_container.get_dependency.return_value = mock.Mock()

    # Patch the three builders.
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_app_service_container',
        lambda *a, **kw: app_container,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_service_resolver',
        lambda *a, **kw: mock.Mock(),
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_logging_context',
        lambda *a, **kw: mock.Mock(spec=LoggingContext),
    )

    # Build the context.
    app_session = AppSession(
        id='test_app',
        name='Test App',
    )
    result = build_app_session_context(app_session, CacheContext())

    # Assert all four FE4 handler attributes are callable.
    assert callable(result._execute_feature)
    assert callable(result._create_request)
    assert callable(result._raise_error)
    assert callable(result._build_response)


# ** test: build_app_success
def test_build_app_success(monkeypatch):
    '''
    Test that build_app resolves the session via get_app_session and returns
    the AppSessionContext composed by build_app_session_context.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a resolved session and a spec'd context that passes validation.
    app_session = AppSession(
        id='test_calc',
        name='Test Calculator',
    )
    app_context = mock.Mock(spec=AppSessionContext)

    # Patch session resolution and the core compose path.
    get_session = mock.Mock(return_value=app_session)
    compose = mock.Mock(return_value=app_context)
    monkeypatch.setattr('tiferet.blueprints.core.get_app_session', get_session)
    monkeypatch.setattr('tiferet.blueprints.core.build_app_session_context', compose)

    # Build the app.
    result = build_app('test_calc', app_config='config.yml')

    # Assert the composed context is returned and the session was resolved by id.
    assert result is app_context
    assert get_session.call_args[0][0] == 'test_calc'
    compose.assert_called_once()


# ** test: build_app_invalid_context
def test_build_app_invalid_context(monkeypatch):
    '''
    Test that build_app raises INVALID_APP_SESSION_TYPE when the composed
    context is not an AppSessionContext.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a resolved session and an invalid (non-context) compose result.
    app_session = AppSession(
        id='invalid_interface',
        name='Invalid',
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.get_app_session',
        lambda *args, **kwargs: app_session,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_app_session_context',
        lambda *args, **kwargs: object(),
    )

    # Assert an invalid composed context raises the expected error.
    with pytest.raises(TiferetError) as exc_info:
        build_app('invalid_interface', app_config='config.yml')

    # Assert the structured error code and interface id.
    assert exc_info.value.error_code == a.const.INVALID_APP_SESSION_TYPE_ID
    assert 'invalid_interface' in str(exc_info.value)


# ** test: build_app_missing_session_propagates_not_found
def test_build_app_missing_session_propagates_not_found(monkeypatch):
    '''
    Test that build_app propagates the GetAppSession APP_SESSION_NOT_FOUND
    error when the session is absent — the core path has no fallback.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Patch get_app_session to raise the not-found error the event would raise.
    def _raise(*args, **kwargs):
        raise TiferetError(a.const.APP_SESSION_NOT_FOUND_ID, interface_id='missing')

    monkeypatch.setattr('tiferet.blueprints.core.get_app_session', _raise)

    # Assert the not-found error propagates unhandled.
    with pytest.raises(TiferetError) as exc_info:
        build_app('missing', app_config='config.yml')

    # Assert the structured error code.
    assert exc_info.value.error_code == a.const.APP_SESSION_NOT_FOUND_ID


# ** test: app_alias_is_core_build_app
def test_app_alias_is_core_build_app():
    '''
    Test that the top-level App alias resolves to core.build_app.
    '''

    # Import the public App alias.
    from tiferet import App

    # Assert it is the core build_app entry point.
    assert App is build_app
