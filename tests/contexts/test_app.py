"""Tiferet App Context Tests"""

# *** imports

# ** core
import logging

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetError, TiferetAPIError
from tiferet.domain import AppSession, AppServiceDependency, Feature, CliCommand, Error
from tiferet.mappers import AppSessionAggregate
from tiferet.contexts.app import (
    BaseContext,
    FeatureContext,
    LoggingContext,
    RequestContext,
    AppSessionContext,
    resolve_default_interface,
    add_default_app_services,
    add_default_app_constants,
    get_default_app_services,
    get_default_app_constants,
    APP_SERVICE_CACHE_PREFIX,
    APP_CONSTANT_CACHE_PREFIX,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import ErrorContext, ERROR_CACHE_PREFIX

# *** fixtures

# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder():
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Return a minimal cache-builder that mirrors the unwrapped build_cache.
    def _build(cache=None):
        return CacheContext(cache=cache)

    return _build

# ** fixture: sample_services
@pytest.fixture
def sample_services() -> dict:
    '''
    Fixture providing a small subset of default service definitions for decorator tests.

    :return: A dict of service id to raw service dependency dict.
    :rtype: dict
    '''

    # Return a representative slice of the default service catalog.
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
    Fixture providing a small subset of bootstrap constants for decorator tests.

    :return: A dict of constant name to scalar value.
    :rtype: dict
    '''

    # Return a representative slice of the default constant catalog.
    return {
        'cli_config': 'config.yml',
        'di_config': 'config.yml',
    }

# ** fixture: app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create an AppSessionAggregate instance.

    :return: An AppSessionAggregate instance.
    :rtype: AppSessionAggregate
    '''

    # Create a test AppSessionAggregate instance.
    return AppSessionAggregate(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppSessionContext',
        description='The test app.',
        flags=['test'],
        services=[],
    )

# ** fixture: feature_context
@pytest.fixture
def feature_context():
    """
    Fixture to create a mock FeatureContext instance.

    :return: A mock instance of FeatureContext.
    :rtype: FeatureContext
    """

    # Create a mock FeatureContext instance.
    feature_context = mock.Mock(spec=FeatureContext)

    # Mock the execute_feature method to return a specific response.
    feature_context.execute_feature.return_value = None

    # Return the mock FeatureContext instance.
    return feature_context

# ** fixture: error_context
@pytest.fixture
def error_context():
    """
    Fixture to create a mock ErrorContext instance.

    :return: A mock instance of ErrorContext.
    :rtype: ErrorContext
    """

    # Create a mock ErrorContext instance.
    error_context = mock.Mock(spec=ErrorContext)

    # Mock the format_response method to return a specific formatted message.
    error_context.format_response.return_value = dict(
        error_code='TEST_ERROR',
        message='This is a test error message.',
    )

    # Return the mock ErrorContext instance.
    return error_context

# ** fixture: logging_context
@pytest.fixture
def logging_context():
    """
    Fixture to create a mock LoggingContext instance.

    :return: A mock instance of LoggingContext.
    :rtype: LoggingContext
    """

    # Create a mock LoggingContext instance.
    logging_context = mock.Mock(spec=LoggingContext)

    # Mock the build_logger method to return a mock logger.
    logging_context.build_logger.return_value = mock.Mock(spec=logging.Logger)

    # Return the mock LoggingContext instance.
    return logging_context

# ** fixture: app_interface_context
@pytest.fixture
def app_interface_context(app_interface, feature_context, error_context, logging_context):
    """
    Fixture to create an AppSessionContext hub bound to the test interface,
    with FE4 handlers wired to the mock feature and error contexts.

    :return: An AppSessionContext instance.
    :rtype: AppSessionContext
    """

    # Build execute_feature_handler that delegates to the mock feature_context.
    def _execute_feature_handler(feature_id, request, **kwargs):
        feature = Feature(
            id=feature_id,
            group_id=feature_id.split('.')[0],
            feature_key=feature_id.split('.')[-1],
            name='Test Feature',
            is_async=False,
        )
        feature_context.execute_feature(feature, request, **kwargs)

    # Build raise_error_handler that delegates to the mock error_context.
    def _raise_error_handler(error, **kwargs):
        error_domain = mock.Mock()
        formatted = error_context.format_response(error_domain, error)
        raise TiferetAPIError(**formatted)

    # Construct the hub declaratively from the loaded interface with FE4 handlers.
    context = AppSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        execute_feature_handler=_execute_feature_handler,
        raise_error_handler=_raise_error_handler,
    )

    # Inject the mock logging context via its lazy cache.
    context._logging = logging_context

    # Return the hub.
    return context


# *** tests

# ** test: app_service_cache_prefix_value
def test_app_service_cache_prefix_value():
    '''
    Test that APP_SERVICE_CACHE_PREFIX is the expected namespace tuple.
    '''

    # Assert the prefix constant has the correct value.
    assert APP_SERVICE_CACHE_PREFIX == ('app', 'services')

# ** test: app_constant_cache_prefix_value
def test_app_constant_cache_prefix_value():
    '''
    Test that APP_CONSTANT_CACHE_PREFIX is the expected namespace tuple.
    '''

    # Assert the prefix constant has the correct value.
    assert APP_CONSTANT_CACHE_PREFIX == ('app', 'constants')

# ** test: add_default_app_services_returns_callable
def test_add_default_app_services_returns_callable(sample_services, base_cache_builder):
    '''
    Test that add_default_app_services returns a decorator that produces a callable.

    :param sample_services: A small sample of service definitions.
    :type sample_services: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Apply the decorator.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)

    # Assert the result is callable.
    assert callable(wrapped)

# ** test: add_default_app_services_seeds_cache_with_domain_objects
def test_add_default_app_services_seeds_cache_with_domain_objects(sample_services, base_cache_builder):
    '''
    Test that the decorated builder stores AppServiceDependency objects in the cache.

    :param sample_services: A small sample of service definitions.
    :type sample_services: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped()

    # Assert each service id maps to an AppServiceDependency in the services namespace.
    for service_id in sample_services:
        cached = cache.get(service_id, *APP_SERVICE_CACHE_PREFIX)
        assert isinstance(cached, AppServiceDependency)
        assert cached.service_id == service_id

# ** test: add_default_app_services_preserves_initial_cache_values
def test_add_default_app_services_preserves_initial_cache_values(sample_services, base_cache_builder):
    '''
    Test that pre-seeded services do not overwrite an initial cache dict.

    :param sample_services: A small sample of service definitions.
    :type sample_services: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke with a pre-populated initial dict.
    wrapped = add_default_app_services(sample_services)(base_cache_builder)
    cache = wrapped(cache={'existing_key': 'existing_value'})

    # Assert the pre-existing entry is still accessible.
    assert cache.get('existing_key') == 'existing_value'

    # Assert the service entries are also present in the services namespace.
    for service_id in sample_services:
        assert isinstance(cache.get(service_id, *APP_SERVICE_CACHE_PREFIX), AppServiceDependency)

# ** test: add_default_app_services_empty_dict_leaves_cache_clean
def test_add_default_app_services_empty_dict_leaves_cache_clean(base_cache_builder):
    '''
    Test that wrapping with an empty services dict results in an empty cache.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap with an empty services dict.
    wrapped = add_default_app_services({})(base_cache_builder)
    cache = wrapped()

    # Assert the cache contains no entries.
    assert cache._cache == {}

# ** test: add_default_app_constants_returns_callable
def test_add_default_app_constants_returns_callable(sample_constants, base_cache_builder):
    '''
    Test that add_default_app_constants returns a decorator that produces a callable.

    :param sample_constants: A small sample of bootstrap constants.
    :type sample_constants: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Apply the decorator.
    wrapped = add_default_app_constants(sample_constants)(base_cache_builder)

    # Assert the result is callable.
    assert callable(wrapped)

# ** test: add_default_app_constants_seeds_cache_with_scalars
def test_add_default_app_constants_seeds_cache_with_scalars(sample_constants, base_cache_builder):
    '''
    Test that the decorated builder stores scalar constant values in the cache.

    :param sample_constants: A small sample of bootstrap constants.
    :type sample_constants: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_app_constants(sample_constants)(base_cache_builder)
    cache = wrapped()

    # Assert each constant name maps to its scalar value in the constants namespace.
    for name, value in sample_constants.items():
        assert cache.get(name, *APP_CONSTANT_CACHE_PREFIX) == value

# ** test: add_default_app_constants_preserves_initial_cache_values
def test_add_default_app_constants_preserves_initial_cache_values(sample_constants, base_cache_builder):
    '''
    Test that pre-seeded constants do not overwrite an initial cache dict.

    :param sample_constants: A small sample of bootstrap constants.
    :type sample_constants: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke with a pre-populated initial dict.
    wrapped = add_default_app_constants(sample_constants)(base_cache_builder)
    cache = wrapped(cache={'existing_key': 'existing_value'})

    # Assert the pre-existing entry is still accessible.
    assert cache.get('existing_key') == 'existing_value'

    # Assert the constant entries are also present in the constants namespace.
    for name, value in sample_constants.items():
        assert cache.get(name, *APP_CONSTANT_CACHE_PREFIX) == value

# ** test: add_default_app_constants_empty_dict_leaves_cache_clean
def test_add_default_app_constants_empty_dict_leaves_cache_clean(base_cache_builder):
    '''
    Test that wrapping with an empty constants dict results in an empty cache.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap with an empty constants dict.
    wrapped = add_default_app_constants({})(base_cache_builder)
    cache = wrapped()

    # Assert the cache contains no entries.
    assert cache._cache == {}

# ** test: resolve_default_interface_match
def test_resolve_default_interface_match():
    '''
    Test that resolve_default_interface builds an interface from a matching default.
    '''

    # Resolve a default interface whose id matches.
    interface = resolve_default_interface(
        'tiferet_cli',
        [{'id': 'tiferet_cli', 'name': 'Tiferet CLI', 'module_path': 'tiferet.contexts.cli', 'class_name': 'CliContext'}],
    )

    # Assert an interface is built from the matching default.
    assert isinstance(interface, AppSession)
    assert interface.id == 'tiferet_cli'
    assert interface.name == 'Tiferet CLI'

# ** test: resolve_default_interface_no_match
def test_resolve_default_interface_no_match():
    '''
    Test that resolve_default_interface returns None when no default matches.
    '''

    # Assert no match yields None for both empty and non-matching defaults.
    assert resolve_default_interface('missing', []) is None
    assert resolve_default_interface(
        'missing',
        [{'id': 'other', 'name': 'Other', 'module_path': 'm', 'class_name': 'C'}],
    ) is None

# ** test: app_interface_context_execute_feature
def test_app_interface_context_execute_feature(app_interface_context, feature_context):
    """
    Test that execute_feature via the injected handler delegates to the mock feature context.

    :param app_interface_context: The AppSessionContext instance (FE4 handlers wired).
    :type app_interface_context: AppSessionContext
    :param feature_context: The mock FeatureContext instance.
    :type feature_context: FeatureContext
    """

    # Create a new request object.
    request = RequestContext(
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'}
    )

    # Execute a feature using the app interface context.
    app_interface_context.execute_feature('test_group.test_feature', request)

    # Assert the feature context was delegated to by the injected handler.
    feature_context.execute_feature.assert_called_once()

# ** test: app_interface_context_handle_error
def test_app_interface_context_handle_error(app_interface_context, error_context):
    """
    Test that handle_error via the injected handler delegates to the mock error context.

    :param app_interface_context: The AppSessionContext instance (FE4 handlers wired).
    :type app_interface_context: AppSessionContext
    :param error_context: The mock ErrorContext instance.
    :type error_context: ErrorContext
    """

    # Create a new Tiferet Error object.
    error = TiferetError(
        error_code='TEST_ERROR',
        message='This is a test error message.'
    )

    # Mock the ErrorContext to return the formatted error dict.
    error_context.format_response.return_value = {
        'error_code': 'TEST_ERROR',
        'name': 'Test Error',
        'message': 'This is a test error message.'
    }

    # Handle an error using the app interface context and verify it raises TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        app_interface_context.handle_error(error)

    # Assert that the raised exception contains the expected error data.
    assert exc_info.value.error_code == 'TEST_ERROR'
    assert exc_info.value.name == 'Test Error'
    assert exc_info.value.message == 'This is a test error message.'

# ** test: app_session_context_build_request_delegates_to_create_request_handler
def test_app_session_context_build_request_delegates_to_create_request_handler(app_interface):
    """
    Test that build_request delegates to the injected _create_request callable
    when create_request_handler is wired, bypassing the legacy construction path.

    :param app_interface: The test AppSessionAggregate.
    :type app_interface: AppSessionAggregate
    """

    # Arrange a mock create_request_handler returning a known request.
    expected_request = RequestContext(data={'k': 'v'})
    mock_handler = mock.Mock(return_value=expected_request)

    # Construct the hub with the injected handler.
    context = AppSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        create_request_handler=mock_handler,
    )

    # Invoke build_request.
    result = context.build_request('group.feat', {'h': 'v'}, {'d': 1})

    # Assert the injected handler was called with interface_id, feature_id, headers, data.
    assert result is expected_request
    mock_handler.assert_called_once_with(app_interface.id, 'group.feat', {'h': 'v'}, {'d': 1})


# ** test: app_session_context_execute_feature_delegates_to_handler
def test_app_session_context_execute_feature_delegates_to_handler(app_interface):
    """
    Test that execute_feature delegates to the injected _execute_feature callable
    when execute_feature_handler is wired, bypassing the legacy path.

    :param app_interface: The test AppSessionAggregate.
    :type app_interface: AppSessionAggregate
    """

    # Arrange a mock execute_feature_handler (void callable).
    execute_mock = mock.Mock()
    request = RequestContext(data={})

    # Construct the hub with the injected handler.
    context = AppSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        execute_feature_handler=execute_mock,
    )

    # Invoke execute_feature.
    context.execute_feature('group.feat', request)

    # Assert the injected handler was called with the feature_id and request.
    execute_mock.assert_called_once_with('group.feat', request)


# ** test: app_session_context_handle_error_delegates_to_raise_error_handler
def test_app_session_context_handle_error_delegates_to_raise_error_handler(app_interface):
    """
    Test that handle_error delegates to the injected _raise_error callable when
    raise_error_handler is wired, bypassing the legacy error path.

    :param app_interface: The test AppSessionAggregate.
    :type app_interface: AppSessionAggregate
    """
    from tiferet.assets import TiferetAPIError

    # Arrange a raise_error_handler that raises a TiferetAPIError.
    api_error = TiferetAPIError(
        error_code='INJECTED_ERROR',
        name='Injected Error',
        message='Injected error message.',
    )
    raise_mock = mock.Mock(side_effect=api_error)

    # Construct the hub with the injected handler.
    context = AppSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        raise_error_handler=raise_mock,
    )

    # Invoke handle_error and assert the injected handler is called.
    error = TiferetError('INJECTED_ERROR', 'injected')
    with pytest.raises(TiferetAPIError):
        context.handle_error(error)

    raise_mock.assert_called_once_with(error)


# ** test: app_session_context_build_response_delegates_to_response_handler
def test_app_session_context_build_response_delegates_to_response_handler(app_interface):
    """
    Test that build_response delegates to the injected _build_response callable
    when response_handler is wired.

    :param app_interface: The test AppSessionAggregate.
    :type app_interface: AppSessionAggregate
    """

    # Arrange a response_handler that returns a known result.
    expected_result = {'status': 'ok'}
    response_mock = mock.Mock(return_value=expected_result)

    # Construct the hub with the injected handler.
    context = AppSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        response_handler=response_mock,
    )

    # Invoke build_response.
    request = RequestContext(data={})
    result = context.build_response(request)

    # Assert the injected handler was called and its result returned.
    assert result is expected_result
    response_mock.assert_called_once_with(request)


# ** test: app_session_context_build_response_fallback
def test_app_session_context_build_response_fallback(app_interface):
    """
    Test that build_response falls back to request.handle_response() when no
    response_handler is wired.

    :param app_interface: The test AppSessionAggregate.
    :type app_interface: AppSessionAggregate
    """

    # Construct the hub without a response_handler.
    context = AppSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
    )

    # Arrange a request with a known result.
    request = RequestContext(data={})
    request.set_result('the_result')

    # Assert build_response returns the request's handled response.
    result = context.build_response(request)
    assert result == 'the_result'


# ** test: app_interface_context_handle_response
def test_app_interface_context_handle_response(app_interface_context):
    """
    Test handling a response using the AppSessionContext.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    """

    # Create a mock request with a response data.
    request = RequestContext(
        headers={'Content-Type': 'application/json'},
        data={"key": "value"}
    )

    # Set the request result to simulate a successful response.
    request.result = {
        'status': 'success',
        'data': {"key": "value"}
    }

    # Handle the response directly via the request context.
    response = request.handle_response()

    # Assert that the response is not None and has the expected attributes.
    assert response is not None
    assert isinstance(response, dict)
    assert response.get('status') == 'success'
    assert response.get('data') == {"key": "value"}

# ** test: app_interface_context_run
def test_app_interface_context_run(app_interface_context, logging_context: LoggingContext):
    """
    Test running the AppSessionContext.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Run the app interface context.
    app_interface_context.run(
        'test_group.test_feature',
        headers={
            'Content-Type': 'application/json',
            'interface_id': app_interface_context.domain.id
        },
        data={
            'key': 'value',
            'param': 'test_param'
        }
    )

    # Assert that the logger was created and used.
    logging_context.build_logger()
    logger = logging_context.build_logger.return_value

    # Verify that debug calls were made but no pre-execution INFO log exists.
    logger.debug.assert_called()

    # Verify that the final INFO log contains duration in parentheses.
    info_calls = [call for call in logger.info.call_args_list]
    assert len(info_calls) == 1
    final_log = info_calls[0][0][0]
    assert final_log.startswith('Executed Feature - test_group.test_feature')
    assert '(ms)' in final_log or 'ms)' in final_log

# ** test: app_interface_context_run_invalid
def test_app_interface_context_run_invalid(app_interface_context, feature_context, error_context, logging_context):
    """
    Test running the AppSessionContext with an invalid feature.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param feature_context: The mock FeatureContext instance.
    :type feature_context: FeatureContext
    :param error_context: The mock ErrorContext instance.
    :type error_context: ErrorContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Mock the execute_feature method to raise an error for an invalid feature.
    feature_context.execute_feature.side_effect = TiferetError(
        error_code='FEATURE_NOT_FOUND',
        message='Feature not found: invalid_group.invalid_feature.'
    )

    # Mock the ErrorContext to format the error and return a formatted message.
    error_context.format_response.return_value = {
        'error_code': 'FEATURE_NOT_FOUND',
        'name': 'Feature Not Found',
        'message': 'Feature not found: invalid_group.invalid_feature.'
    }

    # Attempt to run an invalid feature and assert that it raises TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        app_interface_context.run(
            'invalid_group.invalid_feature',
            headers={
                'Content-Type': 'application/json',
                'interface_id': app_interface_context.domain.id
            },
            data={
                'key': 'value',
                'param': 'test_param'
            }
        )

    # Assert that the raised exception contains the expected error data.
    assert exc_info.value.error_code == 'FEATURE_NOT_FOUND'
    assert exc_info.value.name == 'Feature Not Found'
    assert 'Feature not found: invalid_group.invalid_feature.' in exc_info.value.message

    # Assert that the logger was created and used for error logging.
    logging_context.build_logger.assert_called_once()
    logger = logging_context.build_logger.return_value
    logger.error.assert_called_once()


# ** test: app_interface_context_run_timing_success
def test_app_interface_context_run_timing_success(app_interface_context, logging_context):
    """
    Test that successful execution logs duration in final INFO message.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Run the app interface context.
    app_interface_context.run(
        'test_group.test_feature',
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'}
    )

    # Get the logger mock.
    logger = logging_context.build_logger.return_value

    # Extract all INFO log calls.
    info_calls = [call[0][0] for call in logger.info.call_args_list]

    # Assert only one INFO log exists.
    assert len(info_calls) == 1

    # Assert the final INFO log follows the expected format: "Executed Feature - {feature_id} ({X}ms)".
    final_log = info_calls[0]
    assert final_log.startswith('Executed Feature - test_group.test_feature (')
    assert final_log.endswith('ms)')

    # Extract duration and verify it's a positive integer.
    import re
    match = re.search(r'\((\d+)ms\)', final_log)
    assert match is not None
    duration_ms = int(match.group(1))
    assert duration_ms >= 0


# ** test: app_interface_context_run_timing_no_pre_execution_log
def test_app_interface_context_run_timing_no_pre_execution_log(app_interface_context, logging_context):
    """
    Test that pre-execution INFO log is removed.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Run the app interface context.
    app_interface_context.run(
        'test_group.test_feature',
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'}
    )

    # Get the logger mock.
    logger = logging_context.build_logger.return_value

    # Extract all INFO log calls.
    info_calls = [call[0][0] for call in logger.info.call_args_list]

    # Assert that no pre-execution "Executing feature..." INFO log appears.
    pre_execution_logs = [log for log in info_calls if log.startswith('Executing feature:')]
    assert len(pre_execution_logs) == 0


# ** test: app_interface_context_run_timing_error_path
def test_app_interface_context_run_timing_error_path(app_interface_context, feature_context, error_context, logging_context):
    """
    Test that no duration is logged on error paths.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param feature_context: The mock FeatureContext instance.
    :type feature_context: FeatureContext
    :param error_context: The mock ErrorContext instance.
    :type error_context: ErrorContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Mock the execute_feature method to raise an error.
    feature_context.execute_feature.side_effect = TiferetError(
        error_code='TEST_ERROR',
        message='Test error occurred.'
    )

    # Mock the ErrorContext to format the error.
    error_context.format_response.return_value = {
        'error_code': 'TEST_ERROR',
        'name': 'Test Error',
        'message': 'Test error occurred.'
    }

    # Run the app interface context and expect TiferetAPIError to be raised.
    with pytest.raises(TiferetAPIError) as exc_info:
        app_interface_context.run(
            'test_group.test_feature',
            headers={'Content-Type': 'application/json'},
            data={'key': 'value'}
        )

    # Assert that the raised exception contains the expected error data.
    assert exc_info.value.error_code == 'TEST_ERROR'
    assert exc_info.value.name == 'Test Error'
    assert exc_info.value.message == 'Test error occurred.'

    # Get the logger mock.
    logger = logging_context.build_logger.return_value

    # Extract all INFO log calls.
    info_calls = [call[0][0] for call in logger.info.call_args_list]

    # Assert no INFO logs contain duration (no success log).
    duration_logs = [log for log in info_calls if 'ms)' in log]
    assert len(duration_logs) == 0

    # Assert error was logged.
    logger.error.assert_called_once()


# ** test: app_interface_context_run_timing_zero_duration
def test_app_interface_context_run_timing_zero_duration(app_interface_context, logging_context):
    """
    Test edge case where execution is extremely fast (0ms).

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Mock time.perf_counter to simulate zero duration.
    with mock.patch('time.perf_counter', side_effect=[0.0, 0.0]):
        # Run the app interface context.
        app_interface_context.run(
            'test_group.test_feature',
            headers={'Content-Type': 'application/json'},
            data={'key': 'value'}
        )

        # Get the logger mock.
        logger = logging_context.build_logger.return_value

        # Extract all INFO log calls.
        info_calls = [call[0][0] for call in logger.info.call_args_list]

        # Assert the final log contains (0ms).
        assert len(info_calls) == 1
        assert '(0ms)' in info_calls[0]


# ** test: app_interface_context_run_timing_long_execution
def test_app_interface_context_run_timing_long_execution(app_interface_context, logging_context):
    """
    Test that long execution durations are logged correctly.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Mock time.perf_counter to simulate 1.5 second duration.
    with mock.patch('time.perf_counter', side_effect=[0.0, 1.5]):
        # Run the app interface context.
        app_interface_context.run(
            'test_group.test_feature',
            headers={'Content-Type': 'application/json'},
            data={'key': 'value'}
        )

        # Get the logger mock.
        logger = logging_context.build_logger.return_value

        # Extract all INFO log calls.
        info_calls = [call[0][0] for call in logger.info.call_args_list]

        # Assert the final log contains (1500ms).
        assert len(info_calls) == 1
        assert '(1500ms)' in info_calls[0]

# ** test: get_default_app_services_returns_seeded
def test_get_default_app_services_returns_seeded(base_cache_builder, sample_services):
    '''
    Test that get_default_app_services returns the seeded AppServiceDependency objects.

    :param base_cache_builder: The plain cache-builder fixture.
    :type base_cache_builder: Callable
    :param sample_services: The sample service definitions fixture.
    :type sample_services: dict
    '''

    # Seed a cache with the sample services via the seeding decorator.
    build = add_default_app_services(sample_services)(base_cache_builder)
    cache = build()

    # Read the services back via the getter.
    services = get_default_app_services(cache)

    # Assert each seeded service is returned as an AppServiceDependency keyed by service_id.
    assert len(services) == len(sample_services)
    assert all(isinstance(service, AppServiceDependency) for service in services)
    assert {service.service_id for service in services} == set(sample_services)

# ** test: get_default_app_constants_strips_prefix
def test_get_default_app_constants_strips_prefix(base_cache_builder, sample_constants):
    '''
    Test that get_default_app_constants returns the seeded constants with the prefix stripped.

    :param base_cache_builder: The plain cache-builder fixture.
    :type base_cache_builder: Callable
    :param sample_constants: The sample constants fixture.
    :type sample_constants: dict
    '''

    # Seed a cache with the sample constants via the seeding decorator.
    build = add_default_app_constants(sample_constants)(base_cache_builder)
    cache = build()

    # Read the constants back via the getter and assert the prefix is stripped.
    constants = get_default_app_constants(cache)
    assert constants == sample_constants
