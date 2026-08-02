"""Tiferet Core Blueprints Tests"""

# *** imports

# ** infra
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.blueprints.core import (
    parse_parameter,
    build_app_service_container,
    build_service_resolver,
    build_cache,
    load_cache,
    get_error,
    get_feature,
    build_logging_context,
    create_app_service,
    get_app_session,
)
from tiferet.contexts.app import (
    add_default_app_services,
    add_default_app_constants,
    add_default_app_sessions,
    AppSessionContext,
    APP_SERVICE_CACHE_PREFIX,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX
from tiferet.contexts.logging import LoggingContext, add_default_logging_settings, get_default_logging_settings
from tiferet.contexts.request import RequestContext
from tiferet.di import DIAppServiceContainer, DIDynamicServiceResolver
from tiferet.domain import AppSession, AppServiceDependency, Error, Feature, LoggingSettings
from tiferet.events import ParseParameter
from tiferet.repos.app import AppConfigRepository

# *** tests

# ** test: parse_parameter_delegates_to_parse_parameter_event
def test_parse_parameter_delegates_to_parse_parameter_event():
    '''
    Test that parse_parameter delegates to ParseParameter.execute.
    '''

    # Patch the static event and invoke the blueprint wrapper.
    with mock.patch.object(ParseParameter, 'execute', return_value='parsed') as mock_execute:
        result = parse_parameter('raw')

    # Assert the wrapper delegated to the event with the same argument.
    mock_execute.assert_called_once_with('raw')
    assert result == 'parsed'

# ** test: build_app_service_container_merges_defaults
def test_build_app_service_container_merges_defaults():
    '''
    Test that session constants override cache defaults and the result is a DIAppServiceContainer.
    '''

    # Seed the cache with a default constant.
    cache = add_default_app_constants({'FOO': 'default_value'})(lambda: CacheContext())()

    # Build the app instance with a session-level constant override.
    app_instance = AppSession(id='test.session', name='Test Session', constants={'FOO': 'session_value'})

    # Build the app service container.
    container = build_app_service_container(cache, app_instance)

    # Assert the result type and the session override taking precedence.
    assert isinstance(container, DIAppServiceContainer)
    assert container.get_dependency('FOO') == 'session_value'

# ** test: build_app_service_container_session_wins
def test_build_app_service_container_session_wins():
    '''
    Test that a service present in both the cache defaults and the session
    resolves to the session's definition.
    '''

    # Seed the cache with a default service pointing at CacheContext.
    cache = add_default_app_services({
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()

    # Build the app instance with a session-level override for the same service_id.
    app_instance = AppSession(
        id='test.session',
        name='Test Session',
        services=[
            AppServiceDependency(
                service_id='svc1',
                module_path='tiferet.contexts.request',
                class_name='RequestContext',
            ),
        ],
    )

    # Build the app service container.
    container = build_app_service_container(cache, app_instance)

    # Assert the session's service definition took precedence.
    assert isinstance(container.get_dependency('svc1'), RequestContext)

# ** test: build_service_resolver_returns_resolver
def test_build_service_resolver_returns_resolver():
    '''
    Test that build_service_resolver returns a resolver that resolves from the app container.
    '''

    # Seed the cache with a default service and build the app container. A
    # 'di_service' entry is also required so build_service_resolver can
    # resolve the DI repository dependency.
    cache = add_default_app_services({
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    container = build_app_service_container(cache, AppSession(id='test.session', name='Test Session'))

    # Build the service resolver.
    resolver = build_service_resolver(container)

    # Assert the resolver resolves the service from the registered app container.
    assert isinstance(resolver, DIDynamicServiceResolver)
    assert isinstance(resolver.get_dependency('svc1', 'app'), CacheContext)

# ** test: build_service_resolver_registers_app_flag
def test_build_service_resolver_registers_app_flag():
    '''
    Test that the app container is cached under the 'app' flag and reused on subsequent calls.
    '''

    # Build a minimal app container and resolver.
    cache = add_default_app_services({
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    container = build_app_service_container(cache, AppSession(id='test.session', name='Test Session'))
    resolver = build_service_resolver(container)

    # Assert the same container instance is returned by get_container on repeated calls.
    assert resolver.get_container('app') is container
    assert resolver.get_container('app') is container

# ** test: build_cache_returns_cache_context
def test_build_cache_returns_cache_context():
    '''
    Test that build_cache returns a CacheContext instance.
    '''

    # Assert the built cache is a CacheContext.
    assert isinstance(build_cache(), CacheContext)

# ** test: build_cache_seeds_errors
def test_build_cache_seeds_errors():
    '''
    Test that build_cache seeds default errors under ERROR_CACHE_PREFIX.
    '''

    # Assert a well-known default error is accessible under the error prefix.
    cache = build_cache()
    cached = cache.get(a.error.APP_SESSION_NOT_FOUND_ID, *ERROR_CACHE_PREFIX)
    assert isinstance(cached, Error)

# ** test: build_cache_seeds_app_services
def test_build_cache_seeds_app_services():
    '''
    Test that build_cache seeds default app services under APP_SERVICE_CACHE_PREFIX.
    '''

    # Assert the default di_service is accessible under the app service prefix.
    cache = build_cache()
    cached = cache.get('di_service', *APP_SERVICE_CACHE_PREFIX)
    assert isinstance(cached, AppServiceDependency)

# ** test: build_cache_seeds_logging_settings
def test_build_cache_seeds_logging_settings():
    '''
    Test that build_cache seeds default logging settings.
    '''

    # Assert the default logging settings are seeded and retrievable.
    cache = build_cache()
    settings = get_default_logging_settings(cache)
    assert isinstance(settings, LoggingSettings)
    assert len(settings.formatters) > 0

# ** test: load_cache_returns_root_snapshot
def test_load_cache_returns_root_snapshot():
    '''
    Test that load_cache returns a closure yielding the root-namespace cache snapshot.
    '''

    # Seed a root-namespace entry directly on the cache.
    cache = CacheContext()
    cache.set('key', 'value')

    # Assert the closure returns the root-namespace snapshot.
    snapshot = load_cache(cache)
    assert snapshot() == {'key': 'value'}

# ** test: get_error_returns_cached
def test_get_error_returns_cached():
    '''
    Test that get_error returns the cached Error without re-executing the event on a second call.
    '''

    # Seed the cache with an Error and build the handler with a get_dependency that would fail if called.
    cache = CacheContext()
    error = Error(id='TEST_ERROR', name='Test Error', message=[{'lang': 'en_US', 'text': 'Test.'}])
    cache.set('TEST_ERROR', error, *ERROR_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Assert the cached error is returned without invoking the resolver.
    handler = get_error(cache, get_dependency)
    assert handler('TEST_ERROR') is error
    get_dependency.assert_not_called()

# ** test: get_error_calls_event_on_miss
def test_get_error_calls_event_on_miss():
    '''
    Test that get_error resolves and executes get_error_evt on a cache miss, then caches the result.
    '''

    # Configure a mock resolver returning a mock get_error event.
    cache = CacheContext()
    error = Error(id='TEST_ERROR', name='Test Error', message=[{'lang': 'en_US', 'text': 'Test.'}])
    mock_event = mock.Mock()
    mock_event.execute.return_value = error
    get_dependency = mock.Mock(return_value=mock_event)

    # Assert the event is resolved and executed, and the result is cached.
    handler = get_error(cache, get_dependency)
    result = handler('TEST_ERROR')
    assert result is error
    get_dependency.assert_called_once_with('get_error_evt', 'app')
    mock_event.execute.assert_called_once_with(id='TEST_ERROR')
    assert cache.get('TEST_ERROR', *ERROR_CACHE_PREFIX) is error

# ** test: get_feature_returns_cached
def test_get_feature_returns_cached():
    '''
    Test that get_feature returns the cached Feature without re-executing the event on a second call.
    '''

    # Seed the cache with a Feature and build the handler with a get_dependency that would fail if called.
    cache = CacheContext()
    feature = Feature(id='test.feature', name='Test Feature')
    cache.set('test.feature', feature, *FEATURE_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Assert the cached feature is returned without invoking the resolver.
    handler = get_feature(cache, get_dependency)
    assert handler('test.feature') is feature
    get_dependency.assert_not_called()

# ** test: build_logging_context_returns_logging_context
def test_build_logging_context_returns_logging_context():
    '''
    Test that build_logging_context returns a LoggingContext bound to a merged LoggingSettings.
    '''

    # Seed the cache with default logging settings.
    cache = add_default_logging_settings({
        'formatters': [{'id': 'default', 'name': 'Default', 'format': '%(message)s'}],
        'handlers': [],
        'loggers': [],
    })(lambda: CacheContext())()

    # Configure a mock resolver returning empty repository-configured settings.
    mock_event = mock.Mock()
    mock_event.execute.return_value = ([], [], [])
    get_dependency = mock.Mock(return_value=mock_event)

    # Build the logging context and assert it is bound to the merged settings.
    logging_context = build_logging_context(cache, get_dependency, 'root')
    assert isinstance(logging_context, LoggingContext)
    assert isinstance(logging_context.domain, LoggingSettings)
    assert len(logging_context.domain.formatters) == 1
    get_dependency.assert_called_once_with('logging_list_all_evt', 'app')

# ** test: create_app_service_default
def test_create_app_service_default():
    '''
    Test that create_app_service constructs and resolves an AppConfigRepository.
    '''

    # Construct the app service via the default module path and class name.
    app_service = create_app_service(
        a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
        a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
        a.app.DEFAULT_APP_SERVICE_PARAMETERS,
    )

    # Assert the resolved service is the expected repository type.
    assert isinstance(app_service, AppConfigRepository)

# ** test: get_app_session_from_cache
def test_get_app_session_from_cache():
    '''
    Test that get_app_session returns a cache-seeded session without calling AppSessionContext.load.
    '''

    # Seed the cache with a default app session.
    cache = add_default_app_sessions({
        'test.session': {'id': 'test.session', 'name': 'Test Session'},
    })(lambda: CacheContext())()

    # Assert the cached session is returned without invoking AppSessionContext.load.
    with mock.patch.object(AppSessionContext, 'load') as mock_load:
        result = get_app_session('test.session', cache)
    assert isinstance(result, AppSession)
    assert result.id == 'test.session'
    mock_load.assert_not_called()

# ** test: get_app_session_from_config
def test_get_app_session_from_config():
    '''
    Test that get_app_session delegates to AppSessionContext.load on a cache miss.
    '''

    # Use an empty cache so the seeded-session lookup misses.
    cache = CacheContext()
    session = AppSession(id='test.session', name='Test Session')

    # Patch AppSessionContext.load to avoid touching the filesystem.
    with mock.patch.object(AppSessionContext, 'load', return_value=session) as mock_load:
        result = get_app_session(
            'test.session',
            cache,
            module_path=a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
            class_name=a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
            **a.app.DEFAULT_APP_SERVICE_PARAMETERS,
        )

    # Assert the session was loaded via the classmethod.
    assert result is session
    mock_load.assert_called_once()
    assert mock_load.call_args.args[0] == 'test.session'
    assert isinstance(mock_load.call_args.args[1], AppConfigRepository)
