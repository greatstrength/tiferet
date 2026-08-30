"""Tiferet Core Blueprints Tests"""

# *** imports

# ** core
import pathlib
import textwrap

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
    build_app_session_context,
    build_app,
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
from tiferet.utils.core import CacheMiddleware

# *** fixtures

# ** fixture: session_config_file
@pytest.fixture
def session_config_file(tmp_path) -> str:
    '''
    Write a real single-file session configuration and return its path.

    The session declares constants repointing every configuration repository at
    this same file, so the composed build_app path resolves the full default
    service catalog against real configuration rather than mocks.

    :param tmp_path: The pytest temporary directory fixture.
    :type tmp_path: pathlib.Path
    :return: The path to the written configuration file.
    :rtype: str
    '''

    # Resolve the target configuration file path.
    config_path = tmp_path / 'config.yml'

    # Write a minimal but complete configuration declaring one session.
    config_path.write_text(textwrap.dedent(f'''
        sessions:
          test_session:
            name: Test Session
            description: End-to-end composition test session
            logger_id: default
            constants:
              app_config: {config_path}
              cli_config: {config_path}
              di_config: {config_path}
              error_config: {config_path}
              feature_config: {config_path}
              logging_config: {config_path}
        services: {{}}
        features: {{}}
        errors: {{}}
        logging:
          formatters:
            default:
              name: Default Formatter
              format: '%(message)s'
          handlers:
            default:
              name: Default Handler
              module_path: logging
              class_name: StreamHandler
              level: CRITICAL
              formatter: default
              stream: 'ext://sys.stderr'
          loggers:
            default:
              name: Default Logger
              level: CRITICAL
              handlers:
                - default
    '''))

    # Return the configuration file path.
    return str(config_path)

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

# ** test: build_app_session_context_wires_handlers
def test_build_app_session_context_wires_handlers():
    '''
    Test that build_app_session_context returns an AppSessionContext with all five handlers wired.
    '''

    # Seed the cache with a minimal di_service default.
    cache = add_default_app_services({
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    app_session = AppSession(id='test.session', name='Test Session')

    # Bypass the real logging pipeline; this test targets handler wiring only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    with mock.patch('tiferet.blueprints.core.build_logger_handler', return_value=fake_build_logger):
        context = build_app_session_context(app_session, cache)

    # Assert the context is fully wired with all five template-method handlers.
    assert isinstance(context, AppSessionContext)
    assert context._build_logger is fake_build_logger
    assert context._execute_feature is not None
    assert context._raise_error is not None
    assert context._build_response is response_handler
    assert context._create_request is create_session_request

# ** test: build_app_returns_app_session_context
def test_build_app_returns_app_session_context():
    '''
    Test that build_app returns a fully wired AppSessionContext.
    '''

    # Isolate build_app from the cache/session/context composition chain.
    with mock.patch('tiferet.blueprints.core.get_app_session') as mock_get_session, \
         mock.patch('tiferet.blueprints.core.build_app_session_context') as mock_build_ctx:
        mock_get_session.return_value = AppSession(id='test.session', name='Test Session')
        mock_ctx = mock.Mock(spec=AppSessionContext)
        mock_build_ctx.return_value = mock_ctx

        # Invoke build_app.
        result = build_app('test.session')

    # Assert the wired context is returned unchanged.
    assert result is mock_ctx

# ** test: build_app_invalid_type
def test_build_app_invalid_type():
    '''
    Test that build_app raises INVALID_APP_SESSION_TYPE_ID when the resolved context type is invalid.
    '''

    # Isolate build_app and force an invalid context type.
    with mock.patch('tiferet.blueprints.core.get_app_session') as mock_get_session, \
         mock.patch('tiferet.blueprints.core.build_app_session_context') as mock_build_ctx:
        mock_get_session.return_value = AppSession(id='test.session', name='Test Session')
        mock_build_ctx.return_value = object()

        # Invoke build_app and expect the structured type error.
        with pytest.raises(TiferetError) as exc_info:
            build_app('test.session')

    # Assert the structured invalid-type error is raised.
    assert exc_info.value.error_code == a.error.INVALID_APP_SESSION_TYPE_ID

# ** test: build_app_end_to_end_wires_session_context
def test_build_app_end_to_end_wires_session_context(session_config_file):
    '''
    Test that build_app composes a real AppSessionContext end to end, with no
    step of the composition chain patched out.
    '''

    # Build the app against the real session configuration file.
    context = build_app('test_session', app_config=session_config_file)

    # Assert the composed context is bound to the configured session.
    assert isinstance(context, AppSessionContext)
    assert context.domain.id == 'test_session'
    assert context.domain.name == 'Test Session'

    # Assert all five template-method handlers were wired by the composition chain.
    assert context._build_logger is not None
    assert context._execute_feature is not None
    assert context._raise_error is not None
    assert context._create_request is create_session_request
    assert context._build_response is response_handler

    # Assert the shared cache was composed for real.
    assert isinstance(context.cache, CacheContext)

# ** test: build_app_end_to_end_resolves_default_services
def test_build_app_end_to_end_resolves_default_services(session_config_file):
    '''
    Test that the composed context resolves the seeded default service catalog,
    including every middleware utility registered in CORE_DEFAULT_SERVICES.
    '''

    # Build the app against the real session configuration file.
    context = build_app('test_session', app_config=session_config_file)

    # Assert every default app service id resolves through the composed resolver.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert context.get_dependency(service_id, 'app') is not None

    # Assert the cache middleware resolves to the utility with its loader injected.
    cache_middleware = context.get_dependency(a.app.CACHE_MIDDLEWARE_ID, 'app')
    assert isinstance(cache_middleware, CacheMiddleware)
    assert cache_middleware.load_cache is not None

# ** test: build_app_end_to_end_defaults_app_service_parameters
def test_build_app_end_to_end_defaults_app_service_parameters(session_config_file, monkeypatch):
    '''
    Test that build_app falls back to the framework default app service
    parameters when no app_config is supplied by the caller.
    '''

    # Run from the config file's directory so the default 'config.yml' resolves.
    monkeypatch.chdir(str(pathlib.Path(session_config_file).parent))

    # Build the app without passing any app service parameters.
    context = build_app('test_session')

    # Assert the zero-config entry point resolved the configured session.
    assert isinstance(context, AppSessionContext)
    assert context.domain.id == 'test_session'
