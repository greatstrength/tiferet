"""Tiferet Standard App Blueprint Tests"""

# *** imports

# ** core
import pathlib
import textwrap

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetError
from tiferet.blueprints.app import build_app_session_context, build_app
from tiferet.blueprints.core import create_session_request, response_handler
from tiferet.contexts.app import add_default_app_services, AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.domain import AppSession
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
         mock.patch('tiferet.blueprints.app.build_app_session_context') as mock_build_ctx:
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
         mock.patch('tiferet.blueprints.app.build_app_session_context') as mock_build_ctx:
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
