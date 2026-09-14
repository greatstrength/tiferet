"""Tiferet Core Blueprints Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetAPIError, TiferetError
from tiferet.blueprints.core import (
    parse_parameter,
    build_app_service_container,
    build_service_resolver,
    build_cache,
    load_cache,
    get_error,
    get_feature,
    merge_logging_settings,
    build_logger_handler,
    create_app_service,
    get_app_session,
    create_request_context,
    create_feature_context,
    create_session_request,
    execute_feature_handler,
    raise_error_handler,
    response_handler,
    compose_session_context,
)
from tiferet.contexts.app import (
    add_default_app_services,
    add_default_app_constants,
    add_default_app_sessions,
    APP_SERVICE_CACHE_PREFIX,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.feature import FeatureContext, FEATURE_CACHE_PREFIX
from tiferet.contexts.logging import (
    LOGGER_CACHE_PREFIX,
    add_default_logging_settings,
    get_default_logging_settings,
)
from tiferet.contexts.request import RequestContext
from tiferet.di import DIAppServiceContainer, DIDynamicServiceResolver
from tiferet.domain import AppSession, AppServiceDependency, Error, Feature, LoggingSettings, Formatter
from tiferet.events.app import GetAppSession
from tiferet.repos.app import AppConfigRepository

# *** tests

# ** test: parse_parameter_literal_passthrough
def test_parse_parameter_literal_passthrough():
    '''
    Test that parse_parameter passes through a plain string unchanged.
    '''

    # A non-$env. value is returned verbatim.
    assert parse_parameter('plain_value') == 'plain_value'


# ** test: parse_parameter_resolves_env
def test_parse_parameter_resolves_env(monkeypatch: pytest.MonkeyPatch):
    '''
    Test that parse_parameter resolves an existing $env. variable.
    '''

    # Arrange env and invoke.
    monkeypatch.setenv('TIFERET_TEST_VAR', 'hello_world')
    result = parse_parameter('$env.TIFERET_TEST_VAR')

    # Assert resolution.
    assert result == 'hello_world'


# ** test: parse_parameter_missing_env_raises
def test_parse_parameter_missing_env_raises(monkeypatch: pytest.MonkeyPatch):
    '''
    Test that parse_parameter raises PARAMETER_PARSING_FAILED for a missing env var.
    '''

    # Ensure absent.
    monkeypatch.delenv('TIFERET_NONEXISTENT_VAR', raising=False)

    # Call and assert structured error.
    with pytest.raises(TiferetError) as exc_info:
        parse_parameter('$env.TIFERET_NONEXISTENT_VAR')

    assert exc_info.value.error_code == a.error.PARAMETER_PARSING_FAILED_ID
    assert exc_info.value.kwargs.get('parameter') == '$env.TIFERET_NONEXISTENT_VAR'


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

# ** test: merge_logging_settings_overrides_by_id
def test_merge_logging_settings_overrides_by_id():
    '''
    Test that merge_logging_settings keeps unmatched defaults and overrides by id.
    '''

    # Seed the cache with a single default formatter.
    cache = add_default_logging_settings({
        'formatters': [{'id': 'default', 'name': 'Default', 'format': '%(message)s'}],
        'handlers': [],
        'loggers': [],
    })(lambda: CacheContext())()

    # Merge a repository formatter that overrides the default id plus a new one.
    override = Formatter(id='default', name='Override', format='%(levelname)s %(message)s')
    extra = Formatter(id='extra', name='Extra', format='%(message)s')
    settings = merge_logging_settings(cache, [override, extra], [], [])

    # Assert the merge result is a LoggingSettings with override and unmatched defaults preserved.
    assert isinstance(settings, LoggingSettings)
    formatters_by_id = {formatter.id: formatter for formatter in settings.formatters}
    assert formatters_by_id['default'].name == 'Override'
    assert formatters_by_id['extra'].name == 'Extra'

# ** test: merge_logging_settings_tolerates_empty_defaults
def test_merge_logging_settings_tolerates_empty_defaults():
    '''
    Test that merge_logging_settings accepts a cache with no seeded defaults.
    '''

    # Merge repository sections against an empty cache.
    formatter = Formatter(id='repo', name='Repo', format='%(message)s')
    settings = merge_logging_settings(CacheContext(), [formatter], [], [])

    # Assert the repository entry is the sole formatter.
    assert [item.id for item in settings.formatters] == ['repo']

# ** test: build_logger_handler_caches_by_logger_id
def test_build_logger_handler_caches_by_logger_id():
    '''
    Test that build_logger_handler builds once per logger id and returns the cache hit.
    '''

    # Seed the cache with default logging settings sufficient for dictConfig.
    cache = add_default_logging_settings({
        'formatters': [{'id': 'default', 'name': 'Default', 'format': '%(message)s'}],
        'handlers': [{
            'id': 'default',
            'name': 'Default',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'CRITICAL',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        }],
        'loggers': [{
            'id': 'default',
            'name': 'Default',
            'level': 'CRITICAL',
            'handlers': ['default'],
        }],
    })(lambda: CacheContext())()

    # Configure a mock resolver returning empty repository-configured settings.
    mock_event = mock.Mock()
    mock_event.execute.return_value = ([], [], [])
    get_dependency = mock.Mock(return_value=mock_event)

    # Build the handler and resolve the same logger id twice.
    handler = build_logger_handler(cache, get_dependency)
    first = handler('default')
    second = handler('default')

    # Assert the logger is cached and the list-all event ran only once.
    assert first is second
    assert cache.get('default', *LOGGER_CACHE_PREFIX) is first
    get_dependency.assert_called_once_with('logging_list_all_evt', 'app')
    mock_event.execute.assert_called_once_with()

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
    Test that get_app_session returns a cache-seeded session without invoking the GetAppSession event.
    '''

    # Seed the cache with a default app session.
    cache = add_default_app_sessions({
        'test.session': {'id': 'test.session', 'name': 'Test Session'},
    })(lambda: CacheContext())()

    # Assert the cached session is returned without invoking DomainEvent.handle.
    with mock.patch('tiferet.blueprints.core.DomainEvent.handle') as mock_handle:
        result = get_app_session('test.session', cache)
    assert isinstance(result, AppSession)
    assert result.id == 'test.session'
    mock_handle.assert_not_called()

# ** test: get_app_session_from_config
def test_get_app_session_from_config():
    '''
    Test that get_app_session resolves a cache miss via DomainEvent.handle(GetAppSession, ...).
    '''

    # Use an empty cache so the seeded-session lookup misses.
    cache = CacheContext()
    session = AppSession(id='test.session', name='Test Session')

    # Patch DomainEvent.handle to avoid touching the filesystem.
    with mock.patch('tiferet.blueprints.core.DomainEvent.handle', return_value=session) as mock_handle:
        result = get_app_session(
            'test.session',
            cache,
            module_path=a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
            class_name=a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
            **a.app.DEFAULT_APP_SERVICE_PARAMETERS,
        )

    # Assert the session was resolved via the GetAppSession domain event.
    assert result is session
    mock_handle.assert_called_once()
    assert mock_handle.call_args.args[0] is GetAppSession
    assert isinstance(mock_handle.call_args.kwargs['dependencies']['app_service'], AppConfigRepository)
    assert mock_handle.call_args.kwargs['id'] == 'test.session'

# ** test: create_request_context_sets_interface_id_header
def test_create_request_context_sets_interface_id_header():
    '''
    Test that create_request_context stamps the interface id onto the request headers.
    '''

    # Build the request context and assert the stamped fields.
    request = create_request_context('test.session', 'test.feature', headers={'X-Test': '1'}, data={'k': 'v'})
    assert request.headers.get('interface_id') == 'test.session'
    assert request.headers.get('X-Test') == '1'
    assert request.data == {'k': 'v'}
    assert request.feature_id == 'test.feature'

# ** test: create_feature_context_resolves_and_binds
def test_create_feature_context_resolves_and_binds():
    '''
    Test that create_feature_context returns a FeatureContext bound via from_domain.
    '''

    # Seed the cache with a Feature domain object.
    cache = CacheContext()
    feature = Feature(id='test.feature', name='Test Feature')
    cache.set('test.feature', feature, *FEATURE_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Resolve the bound feature context.
    feature_context = create_feature_context(get_dependency, cache, 'test.feature')

    # Assert a single FeatureContext is returned with the feature bound as domain.
    assert isinstance(feature_context, FeatureContext)
    assert feature_context.domain is feature

# ** test: create_session_request_sets_interface_id_header
def test_create_session_request_sets_interface_id_header():
    '''
    Test that create_session_request delegates to create_request_context.
    '''

    # Build the request via the alias and assert the stamped interface id.
    request = create_session_request('test.session', 'test.feature', headers={'X-Test': '1'}, data={'k': 'v'})
    assert request.headers.get('interface_id') == 'test.session'
    assert request.headers.get('X-Test') == '1'

# ** test: execute_feature_handler_drives_feature_context
def test_execute_feature_handler_drives_feature_context():
    '''
    Test that the execute_feature_handler closure calls FeatureContext.execute_feature without a feature arg.
    '''

    # Seed the cache with a Feature domain object.
    cache = CacheContext()
    feature = Feature(id='test.feature', name='Test Feature')
    cache.set('test.feature', feature, *FEATURE_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Build the handler and execute it against a request.
    handler = execute_feature_handler(get_dependency, cache)
    request = RequestContext(feature_id='test.feature')
    with mock.patch.object(FeatureContext, 'execute_feature') as mock_execute:
        result = handler('test.feature', request)

    # Assert the feature context was driven with the request only.
    mock_execute.assert_called_once_with(request)

    # Assert the handler is void; the result accrues on the request context.
    assert result is None

# ** test: execute_feature_handler_forwards_flags
def test_execute_feature_handler_forwards_flags():
    '''
    Test that the execute_feature_handler closure forwards execution flags to FeatureContext.execute_feature.
    '''

    # Seed the cache with a Feature domain object.
    cache = CacheContext()
    feature = Feature(id='test.feature', name='Test Feature')
    cache.set('test.feature', feature, *FEATURE_CACHE_PREFIX)
    get_dependency = mock.Mock()

    # Build the handler and execute it with execution flags.
    handler = execute_feature_handler(get_dependency, cache)
    request = RequestContext(feature_id='test.feature')
    with mock.patch.object(FeatureContext, 'execute_feature') as mock_execute:
        handler('test.feature', request, 'flag_one', 'flag_two', logger=None)

    # Assert the execution flags were forwarded positionally to the feature context.
    mock_execute.assert_called_once_with(request, 'flag_one', 'flag_two', logger=None)

# ** test: raise_error_handler_formats_and_raises
def test_raise_error_handler_formats_and_raises():
    '''
    Test that raise_error_handler formats a TiferetError into a TiferetAPIError with correct fields.
    '''

    # Build the error domain object and the lazy error resolver.
    error_domain = Error(
        id='SOME_CODE',
        name='Some Code',
        message=[{'lang': 'en_US', 'text': 'Something went wrong: {foo}.'}],
    )
    get_error_handler = mock.Mock(return_value=error_domain)

    # Build the handler and handle a structured error.
    handler = raise_error_handler(get_error_handler)
    exception = TiferetError('SOME_CODE', 'msg', foo='bar')
    with pytest.raises(TiferetAPIError) as exc_info:
        handler(exception)

    # Assert the error was resolved by code and the raised error is correctly formatted.
    get_error_handler.assert_called_once_with('SOME_CODE')
    assert exc_info.value.error_code == 'SOME_CODE'
    assert exc_info.value.name == 'Some Code'
    assert 'bar' in exc_info.value.message

# ** test: raise_error_handler_wraps_bare_exception
def test_raise_error_handler_wraps_bare_exception():
    '''
    Test that raise_error_handler wraps a bare Exception into a TiferetError before formatting.
    '''

    # Build the generic app error domain object and the lazy error resolver.
    error_domain = Error(
        id='APP_ERROR',
        name='App Error',
        message=[{'lang': 'en_US', 'text': 'An error occurred in the app: {error}.'}],
    )
    get_error_handler = mock.Mock(return_value=error_domain)

    # Build the handler and handle a bare exception.
    handler = raise_error_handler(get_error_handler)
    with pytest.raises(TiferetAPIError) as exc_info:
        handler(Exception('boom'))

    # Assert the bare exception was wrapped and resolved under the generic app error code.
    get_error_handler.assert_called_once_with('APP_ERROR')
    assert exc_info.value.error_code == 'APP_ERROR'

# ** test: compose_session_context_wires_five_handlers
def test_compose_session_context_wires_five_handlers():
    '''
    Test that compose_session_context wires all five template-method handlers
    onto the constructed context.
    '''

    # Define a fake session context that captures every wired constructor kwarg.
    class FakeSessionContext(BaseContext):
        def __init__(self,
                get_dependency=None,
                cache=None,
                build_logger_handler=None,
                execute_feature_handler=None,
                create_request_handler=None,
                raise_error_handler=None,
                response_handler=None,
                **kwargs):
            super().__init__()
            self.get_dependency = get_dependency
            self.cache = cache
            self.build_logger_handler = build_logger_handler
            self.execute_feature_handler = execute_feature_handler
            self.create_request_handler = create_request_handler
            self.raise_error_handler = raise_error_handler
            self.response_handler = response_handler
            self.extra_kwargs = kwargs

    # Seed a minimal di_service default and build the app container/resolver.
    cache = add_default_app_services({
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    app_session = AppSession(id='test.session', name='Test Session')
    app_container = build_app_service_container(cache, app_session)
    resolver = build_service_resolver(app_container)

    # Bypass the real logging pipeline; this test targets handler wiring only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    fake_create_request = mock.Mock(name='create_request_handler')
    with mock.patch('tiferet.blueprints.core.build_logger_handler', return_value=fake_build_logger):
        context = compose_session_context(
            FakeSessionContext,
            app_session,
            cache,
            app_container,
            resolver,
            create_request_handler=fake_create_request,
            response_handler=response_handler,
        )

    # Assert the constructed context is bound to the app session with all five handlers wired.
    assert isinstance(context, FakeSessionContext)
    assert context.domain is app_session
    assert context.get_dependency == resolver.get_dependency
    assert context.cache is cache
    assert context.build_logger_handler is fake_build_logger
    assert context.execute_feature_handler is not None
    assert context.raise_error_handler is not None
    assert context.create_request_handler is fake_create_request
    assert context.response_handler is response_handler

# ** test: compose_session_context_resolves_collaborators
def test_compose_session_context_resolves_collaborators():
    '''
    Test that compose_session_context resolves a context class's remaining
    injectable collaborators via resolve_collaborators.
    '''

    # Define a fake session context declaring one extra injectable collaborator.
    class FakeSessionContext(BaseContext):
        def __init__(self,
                get_dependency=None,
                cache=None,
                build_logger_handler=None,
                execute_feature_handler=None,
                create_request_handler=None,
                raise_error_handler=None,
                response_handler=None,
                extra_service=None,
                **kwargs):
            super().__init__()
            self.extra_service = extra_service

    # Seed di_service plus the extra collaborator service on the app container.
    cache = add_default_app_services({
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
        'extra_service': {
            'service_id': 'extra_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    app_session = AppSession(id='test.session', name='Test Session')
    app_container = build_app_service_container(cache, app_session)
    resolver = build_service_resolver(app_container)

    # Bypass the real logging pipeline; this test targets collaborator resolution only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    with mock.patch('tiferet.blueprints.core.build_logger_handler', return_value=fake_build_logger):
        context = compose_session_context(
            FakeSessionContext,
            app_session,
            cache,
            app_container,
            resolver,
            create_request_handler=create_session_request,
            response_handler=response_handler,
        )

    # Assert the extra collaborator was resolved from the app container.
    assert isinstance(context.extra_service, CacheContext)

# ** test: compose_session_context_forwards_extra_kwargs
def test_compose_session_context_forwards_extra_kwargs():
    '''
    Test that compose_session_context forwards extra_kwargs (e.g. a
    parse_cli_args-style closure) through to the constructed context.
    '''

    # Define a fake session context accepting a CLI-style extra kwarg.
    class FakeSessionContext(BaseContext):
        def __init__(self,
                get_dependency=None,
                cache=None,
                build_logger_handler=None,
                execute_feature_handler=None,
                create_request_handler=None,
                raise_error_handler=None,
                response_handler=None,
                parse_cli_args=None,
                **kwargs):
            super().__init__()
            self.parse_cli_args = parse_cli_args

    # Seed a minimal di_service default and build the app container/resolver.
    cache = add_default_app_services({
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    app_session = AppSession(id='test.session', name='Test Session')
    app_container = build_app_service_container(cache, app_session)
    resolver = build_service_resolver(app_container)
    fake_parse_cli_args = mock.Mock(name='parse_cli_args')

    # Bypass the real logging pipeline; this test targets extra_kwargs forwarding only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    with mock.patch('tiferet.blueprints.core.build_logger_handler', return_value=fake_build_logger):
        context = compose_session_context(
            FakeSessionContext,
            app_session,
            cache,
            app_container,
            resolver,
            create_request_handler=create_session_request,
            response_handler=response_handler,
            parse_cli_args=fake_parse_cli_args,
        )

    # Assert the extra kwarg was forwarded to the constructed context.
    assert context.parse_cli_args is fake_parse_cli_args

