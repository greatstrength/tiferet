"""Tiferet App Context Tests"""

# *** imports

# ** core
import logging
from typing import Callable

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetError, TiferetAPIError
from tiferet.assets.error import APP_ERROR_ID
from tiferet.contexts.app import (
    AppSessionContext,
    add_default_app_services,
    add_default_app_constants,
    add_default_admin_services,
    add_default_admin_constants,
    add_default_app_sessions,
    APP_SERVICE_CACHE_PREFIX,
    APP_CONSTANT_CACHE_PREFIX,
    ADMIN_SERVICE_CACHE_PREFIX,
    ADMIN_CONSTANT_CACHE_PREFIX,
    APP_SESSION_CACHE_PREFIX,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import RequestContext
from tiferet.domain import AppSession, AppServiceDependency

# *** fixtures

# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder() -> Callable:
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Define a minimal cache-builder mirroring the unwrapped build_cache.
    def build_cache(cache: dict = None) -> CacheContext:
        return CacheContext(cache=cache)

    # Return the cache-builder.
    return build_cache

# ** fixture: sample_services
@pytest.fixture
def sample_services() -> dict:
    '''
    Fixture providing a small sample of raw app service dependency definitions.

    :return: A mapping of service id to raw definition dict.
    :rtype: dict
    '''

    # Return a small sample service catalog.
    return {
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.repos.di',
            'class_name': 'DIConfigRepository',
            'parameters': {},
        },
        'get_error_evt': {
            'service_id': 'get_error_evt',
            'module_path': 'tiferet.events.error',
            'class_name': 'GetError',
            'parameters': {},
        },
    }

# ** fixture: sample_constants
@pytest.fixture
def sample_constants() -> dict:
    '''
    Fixture providing a small sample of raw app constant definitions.

    :return: A mapping of constant id to scalar value.
    :rtype: dict
    '''

    # Return a small sample constant catalog.
    return {
        'cli_config': 'config.yml',
        'di_config': 'config.yml',
    }

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Fixture to create a sample AppSession domain object.

    :return: A sample app session.
    :rtype: AppSession
    '''

    # Build and return a minimal app session.
    return AppSession(id='test.session', name='Test Session')

# ** fixture: get_dependency
@pytest.fixture
def get_dependency() -> Callable:
    '''
    Fixture providing a mock DI resolution handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a plain mock callable.
    return mock.Mock()

# ** fixture: build_logger_handler
@pytest.fixture
def build_logger_handler() -> Callable:
    '''
    Fixture providing a mock logger-construction handler.

    :return: A mock callable that returns a mock logger.
    :rtype: Callable
    '''

    # Return a mock logger-construction handler.
    return mock.Mock(return_value=mock.Mock(spec=logging.Logger))

# ** fixture: execute_feature_handler
@pytest.fixture
def execute_feature_handler() -> Callable:
    '''
    Fixture providing a mock FE4 feature-execution handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock feature-execution handler.
    return mock.Mock(return_value=None)

# ** fixture: create_request_handler
@pytest.fixture
def create_request_handler() -> Callable:
    '''
    Fixture providing a mock FE4 request-construction handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock request-construction handler returning a real RequestContext.
    return mock.Mock(side_effect=lambda interface_id, feature_id, headers, data: RequestContext(
        headers={**(headers or {}), 'interface_id': interface_id},
        data=data,
        feature_id=feature_id,
    ))

# ** fixture: raise_error_handler
@pytest.fixture
def raise_error_handler() -> Callable:
    '''
    Fixture providing a mock FE4 error-handling handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock error-handling handler.
    return mock.Mock(return_value={'error_code': 'TEST_ERROR'})

# ** fixture: response_handler
@pytest.fixture
def response_handler() -> Callable:
    '''
    Fixture providing a mock FE4 response-building handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock response-building handler.
    return mock.Mock(return_value={'status': 'success'})

# ** fixture: app_session_context
@pytest.fixture
def app_session_context(
        app_session: AppSession,
        get_dependency: Callable,
        build_logger_handler: Callable,
        execute_feature_handler: Callable,
        create_request_handler: Callable,
        raise_error_handler: Callable,
        response_handler: Callable,
    ) -> AppSessionContext:
    '''
    Fixture to create a fully wired AppSessionContext instance.

    :return: A wired AppSessionContext bound to the sample app session.
    :rtype: AppSessionContext
    '''

    # Construct the context via the base factory, binding the session domain object.
    return AppSessionContext.from_domain(
        app_session,
        get_dependency=get_dependency,
        build_logger_handler=build_logger_handler,
        execute_feature_handler=execute_feature_handler,
        create_request_handler=create_request_handler,
        raise_error_handler=raise_error_handler,
        response_handler=response_handler,
    )

# *** tests

# ** test: app_session_context_init
def test_app_session_context_init(app_session_context: AppSessionContext,
        get_dependency: Callable,
        build_logger_handler: Callable,
        execute_feature_handler: Callable,
        create_request_handler: Callable,
        raise_error_handler: Callable,
        response_handler: Callable):
    '''
    Test that the constructor stores all fields correctly.
    '''

    # Assert all collaborators are stored.
    assert app_session_context.get_dependency is get_dependency
    assert app_session_context._build_logger is build_logger_handler
    assert app_session_context._execute_feature is execute_feature_handler
    assert app_session_context._create_request is create_request_handler
    assert app_session_context._raise_error is raise_error_handler
    assert app_session_context._build_response is response_handler
    assert not hasattr(app_session_context, '_logging')

# ** test: app_session_context_init_default_cache
def test_app_session_context_init_default_cache(get_dependency: Callable):
    '''
    Test that cache defaults to a new CacheContext when not provided.
    '''

    # Construct a context without a cache.
    context = AppSessionContext(get_dependency=get_dependency)

    # Assert a fresh CacheContext was created.
    assert isinstance(context.cache, CacheContext)

# ** test: app_session_context_domain_type
def test_app_session_context_domain_type():
    '''
    Test that AppSessionContext declares AppSession as its domain type.
    '''

    # Assert the domain type ClassVar is the AppSession domain object.
    assert AppSessionContext.domain_type is AppSession

# ** test: app_session_context_registered_for_app_session_domain
def test_app_session_context_registered_for_app_session_domain():
    '''
    Test that AppSessionContext is the context registered for the AppSession domain type.
    '''

    # Assert the registry resolves AppSessionContext for the AppSession domain type.
    assert BaseContext.for_domain(AppSession) is AppSessionContext

# ** test: app_session_context_build_logger_wired
def test_app_session_context_build_logger_wired(
        app_session_context: AppSessionContext,
        build_logger_handler: Callable,
    ):
    '''
    Test that build_logger delegates to the injected handler when wired.
    '''

    # Build the logger through the wired handler.
    logger = app_session_context.build_logger()

    # Assert the handler was invoked with the session logger id.
    build_logger_handler.assert_called_once_with(app_session_context.domain.logger_id)
    assert logger is build_logger_handler.return_value

# ** test: app_session_context_build_logger_unwired
def test_app_session_context_build_logger_unwired(app_session: AppSession, get_dependency: Callable):
    '''
    Test that build_logger raises APP_ERROR when the handler is unwired.
    '''

    # Construct a context without a logger-construction handler.
    context = AppSessionContext.from_domain(app_session, get_dependency=get_dependency)

    # Assert an unwired handler fails loudly with APP_ERROR.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.build_logger()

    # Assert the structured app error names the missing handler.
    assert exc_info.value.error_code == APP_ERROR_ID
    assert 'build_logger_handler' in exc_info.value.message

# ** test: app_session_context_build_logger_formats_tiferet_error
def test_app_session_context_build_logger_formats_tiferet_error(
        app_session: AppSession,
        get_dependency: Callable,
        raise_error_handler: Callable,
    ):
    '''
    Test that build_logger formats a TiferetError from the handler via handle_error.
    '''

    # Configure the logger handler to raise a domain error.
    domain_error = TiferetError('LOGGER_CREATION_FAILED', 'Logger failed.')
    build_logger = mock.Mock(side_effect=domain_error)

    # Construct a context with a failing logger handler and a wired error handler.
    context = AppSessionContext.from_domain(
        app_session,
        get_dependency=get_dependency,
        build_logger_handler=build_logger,
        raise_error_handler=raise_error_handler,
    )

    # Assert the domain error is formatted through handle_error.
    result = context.build_logger()
    raise_error_handler.assert_called_once_with(domain_error)
    assert result == {'error_code': 'TEST_ERROR'}

# ** test: app_session_context_build_request_wired
def test_app_session_context_build_request_wired(app_session_context: AppSessionContext, create_request_handler: Callable):
    '''
    Test that build_request delegates to the injected handler when wired.
    '''

    # Build the request through the wired handler.
    request = app_session_context.build_request('test.feature', headers={'X-Test': '1'}, data={'key': 'value'})

    # Assert the handler was invoked with the expected arguments.
    create_request_handler.assert_called_once_with(
        app_session_context.domain.id, 'test.feature', {'X-Test': '1'}, {'key': 'value'},
    )
    assert isinstance(request, RequestContext)
    assert request.headers.get('interface_id') == app_session_context.domain.id

# ** test: app_session_context_build_request_unwired
def test_app_session_context_build_request_unwired(app_session: AppSession, get_dependency: Callable):
    '''
    Test that build_request raises APP_ERROR when the handler is unwired.
    '''

    # Construct a context without a request-construction handler.
    context = AppSessionContext.from_domain(app_session, get_dependency=get_dependency)

    # Assert an unwired handler fails loudly with APP_ERROR.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.build_request('test.feature', headers={'X-Test': '1'}, data={'key': 'value'})

    # Assert the structured app error names the missing handler.
    assert exc_info.value.error_code == APP_ERROR_ID
    assert 'create_request_handler' in exc_info.value.message
    assert exc_info.value.kwargs.get('feature_id') == 'test.feature'

# ** test: app_session_context_execute_feature_wired
def test_app_session_context_execute_feature_wired(app_session_context: AppSessionContext, execute_feature_handler: Callable):
    '''
    Test that execute_feature delegates to the injected handler when wired.
    '''

    # Execute the feature through the wired handler.
    request = RequestContext(feature_id='test.feature')
    app_session_context.execute_feature('test.feature', request, logger=None)

    # Assert the handler was invoked with the expected arguments.
    execute_feature_handler.assert_called_once_with('test.feature', request, logger=None)

# ** test: app_session_context_execute_feature_unwired
def test_app_session_context_execute_feature_unwired(app_session: AppSession, get_dependency: Callable):
    '''
    Test that execute_feature raises APP_ERROR when the handler is unwired.
    '''

    # Construct a context without a feature-execution handler.
    context = AppSessionContext.from_domain(app_session, get_dependency=get_dependency)
    request = RequestContext(feature_id='test.feature')

    # Assert an unwired handler fails loudly with APP_ERROR.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.execute_feature('test.feature', request)

    # Assert the structured app error names the missing handler.
    assert exc_info.value.error_code == APP_ERROR_ID
    assert 'execute_feature_handler' in exc_info.value.message
    assert exc_info.value.kwargs.get('feature_id') == 'test.feature'

# ** test: app_session_context_handle_error_wired
def test_app_session_context_handle_error_wired(app_session_context: AppSessionContext, raise_error_handler: Callable):
    '''
    Test that handle_error delegates to the injected handler when wired.
    '''

    # Handle the error through the wired handler.
    error = TiferetError('TEST_ERROR', 'Test error message.')
    result = app_session_context.handle_error(error)

    # Assert the handler was invoked and its result returned.
    raise_error_handler.assert_called_once_with(error)
    assert result == {'error_code': 'TEST_ERROR'}

# ** test: app_session_context_handle_error_api_error_passthrough
def test_app_session_context_handle_error_api_error_passthrough(
        app_session_context: AppSessionContext,
        raise_error_handler: Callable,
    ):
    '''
    Test that handle_error re-raises an incoming TiferetAPIError verbatim.
    '''

    # Build an already-formatted API error.
    api_error = TiferetAPIError(
        error_code=APP_ERROR_ID,
        name='App Error',
        message='Already formatted.',
    )

    # Assert the same instance is re-raised without consulting the handler.
    with pytest.raises(TiferetAPIError) as exc_info:
        app_session_context.handle_error(api_error)

    assert exc_info.value is api_error
    raise_error_handler.assert_not_called()

# ** test: app_session_context_handle_error_unwired
def test_app_session_context_handle_error_unwired(app_session: AppSession, get_dependency: Callable):
    '''
    Test that handle_error raises APP_ERROR when the handler is unwired.
    '''

    # Construct a context without an error-handling handler.
    context = AppSessionContext.from_domain(app_session, get_dependency=get_dependency)

    # Handle a structured error with no wired handler.
    error = TiferetError('SOME_ERROR', 'Some error message.')
    with pytest.raises(TiferetAPIError) as exc_info:
        context.handle_error(error)

    # Assert the structured app error names the missing handler.
    assert exc_info.value.error_code == APP_ERROR_ID
    assert 'raise_error_handler' in exc_info.value.message
    assert exc_info.value.kwargs['original_error_code'] == 'SOME_ERROR'
    assert exc_info.value.kwargs['original_error_message'] == str(error)

# ** test: app_session_context_build_response_wired
def test_app_session_context_build_response_wired(app_session_context: AppSessionContext, response_handler: Callable):
    '''
    Test that build_response delegates to the injected handler when wired.
    '''

    # Build the response through the wired handler.
    request = RequestContext(feature_id='test.feature')
    result = app_session_context.build_response(request)

    # Assert the handler was invoked and its result returned.
    response_handler.assert_called_once_with(request)
    assert result == {'status': 'success'}

# ** test: app_session_context_build_response_unwired
def test_app_session_context_build_response_unwired(app_session: AppSession, get_dependency: Callable):
    '''
    Test that build_response raises APP_ERROR when the handler is unwired.
    '''

    # Construct a context without a response-building handler.
    context = AppSessionContext.from_domain(app_session, get_dependency=get_dependency)
    request = RequestContext(feature_id='test.feature')

    # Assert an unwired handler fails loudly with APP_ERROR.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.build_response(request)

    # Assert the structured app error names the missing handler.
    assert exc_info.value.error_code == APP_ERROR_ID
    assert 'response_handler' in exc_info.value.message

# ** test: app_session_context_execute_feature_unwired_handler_passes_through_run
def test_app_session_context_execute_feature_unwired_handler_passes_through_run(
        app_session: AppSession,
        get_dependency: Callable,
        build_logger_handler: Callable,
        create_request_handler: Callable,
        response_handler: Callable,
    ):
    '''
    Test that run surfaces the unwired execute handler without wrapping it.
    '''

    # Wire every handler except execute and raise.
    context = AppSessionContext.from_domain(
        app_session,
        get_dependency=get_dependency,
        build_logger_handler=build_logger_handler,
        create_request_handler=create_request_handler,
        response_handler=response_handler,
    )

    # Run and assert the execute-slot error passes through.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.run('group.feat')

    assert exc_info.value.error_code == APP_ERROR_ID
    assert 'execute_feature_handler' in exc_info.value.message
    assert 'raise_error_handler' not in exc_info.value.message
    assert exc_info.value.kwargs['feature_id'] == 'group.feat'
    assert 'An error occurred in the app' not in exc_info.value.message
    build_logger_handler.return_value.error.assert_called_once()

# ** test: app_session_context_run_success
def test_app_session_context_run_success(
        app_session_context: AppSessionContext,
        create_request_handler: Callable,
        execute_feature_handler: Callable,
        response_handler: Callable,
        build_logger_handler: Callable,
    ):
    '''
    Test that run calls build_logger, build_request, execute_feature, and build_response.
    '''

    # Run the app session context.
    result = app_session_context.run('test.feature', headers={'X-Test': '1'}, data={'key': 'value'})

    # Assert all five template methods were driven and the response returned.
    build_logger_handler.assert_called_once_with(app_session_context.domain.logger_id)
    create_request_handler.assert_called_once()
    execute_feature_handler.assert_called_once()
    response_handler.assert_called_once()
    assert result == {'status': 'success'}

    # Assert the logger logged the successful execution with duration.
    logger = build_logger_handler.return_value
    info_calls = [call[0][0] for call in logger.info.call_args_list]
    assert len(info_calls) == 1
    assert info_calls[0].startswith('Executed Feature - test.feature (')

# ** test: app_session_context_run_error
def test_app_session_context_run_error(
        app_session_context: AppSessionContext,
        execute_feature_handler: Callable,
        raise_error_handler: Callable,
        build_logger_handler: Callable,
    ):
    '''
    Test that a TiferetError during execute_feature triggers handle_error.
    '''

    # Configure the feature execution handler to raise a structured error.
    execute_feature_handler.side_effect = TiferetError('FEATURE_ERROR', 'Feature failed.')

    # Run the app session context.
    result = app_session_context.run('test.feature')

    # Assert the error handler was invoked and its result returned.
    raise_error_handler.assert_called_once()
    assert result == {'error_code': 'TEST_ERROR'}

    # Assert the logger logged the error.
    logger = build_logger_handler.return_value
    logger.error.assert_called_once()

# ** test: app_service_cache_prefix_value
def test_app_service_cache_prefix_value():
    '''
    Verify the context app service prefix equals and is the asset tuple.
    '''

    # Assert equality and identity with the asset prefix.
    assert APP_SERVICE_CACHE_PREFIX == ('app', 'services')
    assert APP_SERVICE_CACHE_PREFIX is a.app.APP_SERVICE_CACHE_PREFIX

# ** test: app_constant_cache_prefix_value
def test_app_constant_cache_prefix_value():
    '''
    Verify the context app constant prefix equals and is the asset tuple.
    '''

    # Assert equality and identity with the asset prefix.
    assert APP_CONSTANT_CACHE_PREFIX == ('app', 'constants')
    assert APP_CONSTANT_CACHE_PREFIX is a.app.APP_CONSTANT_CACHE_PREFIX

# ** test: add_default_app_services_returns_callable
def test_add_default_app_services_returns_callable(sample_services: dict, base_cache_builder: Callable):
    '''
    Verify add_default_app_services returns a callable cache builder.
    '''

    # Assert the wrapped builder is callable.
    assert callable(add_default_app_services(sample_services)(base_cache_builder))

# ** test: add_default_app_services_seeds_cache_with_domain_objects
def test_add_default_app_services_seeds_cache_with_domain_objects(sample_services: dict, base_cache_builder: Callable):
    '''
    Verify each seeded app service is an AppServiceDependency keyed by service id.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped()

    # Assert each service is cached as an AppServiceDependency under the prefix.
    for key in sample_services:
        cached = cache.get(key, *APP_SERVICE_CACHE_PREFIX)
        assert isinstance(cached, AppServiceDependency)
        assert cached.service_id == key

# ** test: add_default_app_services_preserves_initial_cache_values
def test_add_default_app_services_preserves_initial_cache_values(sample_services: dict, base_cache_builder: Callable):
    '''
    Verify an initial root cache key survives app service seeding.
    '''

    # Wrap the builder and invoke it with an initial root entry.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped(cache={'existing_key': 'existing_value'})

    # Assert the root entry remains and each service is seeded under the prefix.
    assert cache.get('existing_key') == 'existing_value'
    for key in sample_services:
        cached = cache.get(key, *APP_SERVICE_CACHE_PREFIX)
        assert isinstance(cached, AppServiceDependency)

# ** test: add_default_app_services_empty_dict_leaves_cache_clean
def test_add_default_app_services_empty_dict_leaves_cache_clean(base_cache_builder: Callable):
    '''
    Verify an empty app service catalog writes no prefix namespace.
    '''

    # Wrap the builder with an empty catalog and invoke it.
    wrapped = add_default_app_services({})(base_cache_builder)
    cache = wrapped()

    # Assert the prefix namespace is absent.
    assert cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX) == {}
    assert ('app', 'services') not in cache._cache

# ** test: add_default_app_constants_returns_callable
def test_add_default_app_constants_returns_callable(sample_constants: dict, base_cache_builder: Callable):
    '''
    Verify add_default_app_constants returns a callable cache builder.
    '''

    # Assert the wrapped builder is callable.
    assert callable(add_default_app_constants(sample_constants)(base_cache_builder))

# ** test: add_default_app_constants_seeds_cache_with_scalars
def test_add_default_app_constants_seeds_cache_with_scalars(sample_constants: dict, base_cache_builder: Callable):
    '''
    Verify each seeded app constant reads back as the fixture scalar.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_constants(sample_constants)(base_cache_builder)
    cache = wrapped()

    # Assert each constant reads back under the prefix.
    for name, value in sample_constants.items():
        assert cache.get(name, *APP_CONSTANT_CACHE_PREFIX) == value

# ** test: add_default_app_constants_preserves_initial_cache_values
def test_add_default_app_constants_preserves_initial_cache_values(sample_constants: dict, base_cache_builder: Callable):
    '''
    Verify an initial root cache key survives app constant seeding.
    '''

    # Wrap the builder and invoke it with an initial root entry.
    wrapped = add_default_app_constants(sample_constants)(base_cache_builder)
    cache = wrapped(cache={'existing_key': 'existing_value'})

    # Assert the root entry remains and each constant reads back under the prefix.
    assert cache.get('existing_key') == 'existing_value'
    for name, value in sample_constants.items():
        assert cache.get(name, *APP_CONSTANT_CACHE_PREFIX) == value

# ** test: add_default_app_constants_empty_dict_leaves_cache_clean
def test_add_default_app_constants_empty_dict_leaves_cache_clean(base_cache_builder: Callable):
    '''
    Verify an empty app constant catalog writes no prefix namespace.
    '''

    # Wrap the builder with an empty catalog and invoke it.
    wrapped = add_default_app_constants({})(base_cache_builder)
    cache = wrapped()

    # Assert the prefix namespace is absent.
    assert cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX) == {}
    assert ('app', 'constants') not in cache._cache

# ** test: app_session_cache_prefix_value
def test_app_session_cache_prefix_value():
    '''
    Verify the context app session prefix equals and is the asset tuple.
    '''

    # Assert equality and identity with the asset prefix.
    assert APP_SESSION_CACHE_PREFIX == ('app', 'sessions')
    assert APP_SESSION_CACHE_PREFIX is a.app.APP_SESSION_CACHE_PREFIX

# ** test: add_default_app_sessions_seeds_cache_with_domain_objects
def test_add_default_app_sessions_seeds_cache_with_domain_objects(base_cache_builder: Callable):
    '''
    Verify each seeded app session is an AppSession keyed by id.
    '''

    # Wrap the builder with the inline session catalog and invoke it.
    sessions = {
        'tiferet_app': {'id': 'tiferet_app', 'name': 'Admin App'},
        'tiferet_cli': {'id': 'tiferet_cli', 'name': 'Admin CLI'},
    }
    wrapped = add_default_app_sessions(sessions)(base_cache_builder)
    cache = wrapped()

    # Assert each session is cached as an AppSession under the prefix.
    for key in sessions:
        cached = cache.get(key, *APP_SESSION_CACHE_PREFIX)
        assert isinstance(cached, AppSession)
        assert cached.id == key

# ** test: add_default_app_sessions_absent_key_returns_none
def test_add_default_app_sessions_absent_key_returns_none(base_cache_builder: Callable):
    '''
    Verify a missing session id reads back as None after seeding.
    '''

    # Wrap the builder with one session and invoke it.
    sessions = {'tiferet_app': {'id': 'tiferet_app', 'name': 'Admin App'}}
    wrapped = add_default_app_sessions(sessions)(base_cache_builder)
    cache = wrapped()

    # Assert the seeded session exists and the missing id reads back as None.
    cached = cache.get('tiferet_app', *APP_SESSION_CACHE_PREFIX)
    assert isinstance(cached, AppSession)
    assert cached.id == 'tiferet_app'
    assert cache.get('missing.session', *APP_SESSION_CACHE_PREFIX) is None

# ** test: add_default_app_services_readable_via_cache_by_prefix
def test_add_default_app_services_readable_via_cache_by_prefix(sample_services: dict, base_cache_builder: Callable):
    '''
    Verify get_by_prefix returns every seeded AppServiceDependency.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped()

    # Assert the prefix namespace holds every seeded service.
    values = list(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX).values())
    assert len(values) == len(sample_services)
    assert all(isinstance(value, AppServiceDependency) for value in values)
    assert {value.service_id for value in values} == set(sample_services)

# ** test: add_default_app_constants_readable_via_cache_by_prefix
def test_add_default_app_constants_readable_via_cache_by_prefix(sample_constants: dict, base_cache_builder: Callable):
    '''
    Verify get_by_prefix returns the seeded constant mapping.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_constants(sample_constants)(base_cache_builder)
    cache = wrapped()

    # Assert the prefix namespace equals the fixture mapping.
    assert cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX) == sample_constants

# ** test: add_default_admin_services_seeds_cache
def test_add_default_admin_services_seeds_cache(sample_services: dict, base_cache_builder: Callable):
    '''
    Verify each seeded admin service is an AppServiceDependency under the admin prefix.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_admin_services(sample_services)(base_cache_builder)
    cache = wrapped()

    # Assert each service is cached under the admin prefix and the prefix is the asset tuple.
    for key in sample_services:
        cached = cache.get(key, *ADMIN_SERVICE_CACHE_PREFIX)
        assert isinstance(cached, AppServiceDependency)
        assert cached.service_id == key
    assert ADMIN_SERVICE_CACHE_PREFIX == ('admin', 'services')
    assert ADMIN_SERVICE_CACHE_PREFIX is a.app.ADMIN_SERVICE_CACHE_PREFIX

# ** test: add_default_admin_constants_seeds_cache
def test_add_default_admin_constants_seeds_cache(base_cache_builder: Callable):
    '''
    Verify add_default_admin_constants stores the scalar under the admin prefix.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_admin_constants({'FOO': 'bar'})(base_cache_builder)
    cache = wrapped()

    # Assert the scalar and the asset prefix identity.
    assert cache.get('FOO', *ADMIN_CONSTANT_CACHE_PREFIX) == 'bar'
    assert ADMIN_CONSTANT_CACHE_PREFIX == ('admin', 'constants')
    assert ADMIN_CONSTANT_CACHE_PREFIX is a.app.ADMIN_CONSTANT_CACHE_PREFIX
