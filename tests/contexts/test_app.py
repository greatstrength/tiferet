"""Tiferet App Context Tests"""

# *** imports

# ** core
import logging
from typing import Callable

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetError, TiferetAPIError
from tiferet.assets.error import APP_ERROR_ID
from tiferet.contexts.app import (
    AppSessionContext,
    add_default_app_services,
    get_default_app_services,
    add_default_app_constants,
    get_default_app_constants,
    add_default_admin_services,
    get_default_admin_services,
    add_default_admin_constants,
    get_default_admin_constants,
    add_default_app_sessions,
    get_default_app_session,
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
from tiferet.interfaces import AppService

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
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.repos.app',
            'class_name': 'AppConfigRepository',
        },
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

# ** test: app_session_context_load
def test_app_session_context_load():
    '''
    Test that load invokes GetAppSession with the correct kwargs and returns the session.
    '''

    # Configure a mock AppService that returns a session on get.
    session = AppSession(id='test.session', name='Test Session')
    service = mock.Mock(spec=AppService)
    service.get.return_value = session

    # Load the session via the classmethod.
    result = AppSessionContext.load('test.session', service)

    # Assert the session was retrieved by id and returned unchanged.
    assert result is session
    service.get.assert_called_once_with('test.session')

# ** test: app_session_context_load_not_found
def test_app_session_context_load_not_found():
    '''
    Test that load raises APP_SESSION_NOT_FOUND_ID when the session is missing.
    '''

    # Configure a mock AppService that returns no session.
    service = mock.Mock(spec=AppService)
    service.get.return_value = None

    # Attempt to load a non-existent session.
    with pytest.raises(TiferetError) as exc_info:
        AppSessionContext.load('missing.session', service)

    # Assert the structured not-found error is raised.
    assert exc_info.value.error_code == 'APP_SESSION_NOT_FOUND'

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

# ** test: add_default_app_services_seeds_cache
def test_add_default_app_services_seeds_cache(sample_services: dict, base_cache_builder: Callable):
    '''
    Test that add_default_app_services seeds AppServiceDependency objects under the correct prefix.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped()

    # Assert the service is cached as an AppServiceDependency under the correct prefix.
    cached = cache.get('svc1', *APP_SERVICE_CACHE_PREFIX)
    assert isinstance(cached, AppServiceDependency)
    assert cached.service_id == 'svc1'
    assert APP_SERVICE_CACHE_PREFIX == ('app', 'services')

# ** test: get_default_app_services_returns_list
def test_get_default_app_services_returns_list(sample_services: dict, base_cache_builder: Callable):
    '''
    Test that get_default_app_services returns the list of cached app service dependencies.
    '''

    # Seed the cache and retrieve the services list.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped()
    services = get_default_app_services(cache)

    # Assert the seeded service is present in the returned list.
    assert len(services) == 1
    assert isinstance(services[0], AppServiceDependency)
    assert services[0].service_id == 'svc1'

# ** test: add_default_app_constants_seeds_cache
def test_add_default_app_constants_seeds_cache(base_cache_builder: Callable):
    '''
    Test that add_default_app_constants seeds scalars under the correct prefix.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_constants({'FOO': 'bar'})(base_cache_builder)
    cache = wrapped()

    # Assert the constant is cached under the correct prefix.
    assert cache.get('FOO', *APP_CONSTANT_CACHE_PREFIX) == 'bar'
    assert APP_CONSTANT_CACHE_PREFIX == ('app', 'constants')

# ** test: get_default_app_constants_returns_dict
def test_get_default_app_constants_returns_dict(base_cache_builder: Callable):
    '''
    Test that get_default_app_constants returns the mapping of cached constants.
    '''

    # Seed the cache and retrieve the constants mapping.
    wrapped = add_default_app_constants({'FOO': 'bar'})(base_cache_builder)
    cache = wrapped()

    # Assert the returned mapping matches the seeded constants.
    assert get_default_app_constants(cache) == {'FOO': 'bar'}

# ** test: add_default_admin_services_seeds_cache
def test_add_default_admin_services_seeds_cache(sample_services: dict, base_cache_builder: Callable):
    '''
    Test that add_default_admin_services seeds AppServiceDependency objects under the correct prefix.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_admin_services(sample_services)(base_cache_builder)
    cache = wrapped()

    # Assert the service is cached under the admin prefix.
    cached = cache.get('svc1', *ADMIN_SERVICE_CACHE_PREFIX)
    assert isinstance(cached, AppServiceDependency)
    assert ADMIN_SERVICE_CACHE_PREFIX == ('admin', 'services')

# ** test: get_default_admin_services_returns_list
def test_get_default_admin_services_returns_list(sample_services: dict, base_cache_builder: Callable):
    '''
    Test that get_default_admin_services returns the list of cached admin service dependencies.
    '''

    # Seed the cache and retrieve the admin services list.
    wrapped = add_default_admin_services(sample_services)(base_cache_builder)
    cache = wrapped()
    services = get_default_admin_services(cache)

    # Assert the seeded service is present in the returned list.
    assert len(services) == 1
    assert services[0].service_id == 'svc1'

# ** test: add_default_admin_constants_seeds_cache
def test_add_default_admin_constants_seeds_cache(base_cache_builder: Callable):
    '''
    Test that add_default_admin_constants seeds scalars under the correct prefix.
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_admin_constants({'FOO': 'bar'})(base_cache_builder)
    cache = wrapped()

    # Assert the constant is cached under the admin prefix.
    assert cache.get('FOO', *ADMIN_CONSTANT_CACHE_PREFIX) == 'bar'
    assert ADMIN_CONSTANT_CACHE_PREFIX == ('admin', 'constants')

# ** test: get_default_admin_constants_returns_dict
def test_get_default_admin_constants_returns_dict(base_cache_builder: Callable):
    '''
    Test that get_default_admin_constants returns the mapping of cached admin constants.
    '''

    # Seed the cache and retrieve the admin constants mapping.
    wrapped = add_default_admin_constants({'FOO': 'bar'})(base_cache_builder)
    cache = wrapped()

    # Assert the returned mapping matches the seeded constants.
    assert get_default_admin_constants(cache) == {'FOO': 'bar'}

# ** test: add_default_app_sessions_seeds_cache
def test_add_default_app_sessions_seeds_cache(base_cache_builder: Callable):
    '''
    Test that add_default_app_sessions seeds AppSession objects under the correct prefix.
    '''

    # Wrap the builder and invoke it.
    sessions = {'test.session': {'id': 'test.session', 'name': 'Test Session'}}
    wrapped = add_default_app_sessions(sessions)(base_cache_builder)
    cache = wrapped()

    # Assert the session is cached as an AppSession under the correct prefix.
    cached = cache.get('test.session', *APP_SESSION_CACHE_PREFIX)
    assert isinstance(cached, AppSession)
    assert cached.id == 'test.session'
    assert APP_SESSION_CACHE_PREFIX == ('app', 'sessions')

# ** test: get_default_app_session_returns_seeded
def test_get_default_app_session_returns_seeded(base_cache_builder: Callable):
    '''
    Test that get_default_app_session returns the seeded session by id.
    '''

    # Seed the cache and retrieve the session by id.
    sessions = {'test.session': {'id': 'test.session', 'name': 'Test Session'}}
    wrapped = add_default_app_sessions(sessions)(base_cache_builder)
    cache = wrapped()

    # Assert the seeded session is returned.
    result = get_default_app_session(cache, 'test.session')
    assert isinstance(result, AppSession)
    assert result.id == 'test.session'

# ** test: get_default_app_session_returns_none_when_absent
def test_get_default_app_session_returns_none_when_absent():
    '''
    Test that get_default_app_session returns None for an empty cache.
    '''

    # Assert an empty cache yields no default session.
    assert get_default_app_session(CacheContext(), 'missing.session') is None
