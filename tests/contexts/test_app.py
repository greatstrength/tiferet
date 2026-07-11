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
    ErrorContext,
    LoggingContext,
    RequestContext,
    AppSessionContext,
    build_feature_index,
    build_command_list,
    resolve_default_interface,
    add_default_app_services,
    add_default_app_constants,
    get_default_app_services,
    get_default_app_constants,
    APP_SERVICE_CACHE_PREFIX,
    APP_CONSTANT_CACHE_PREFIX,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import ERROR_CACHE_PREFIX

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
def app_interface_context(app_interface, feature_context, error_context, logging_context, monkeypatch):
    """
    Fixture to create an AppSessionContext hub bound to the test interface.
    The logging context is injected via its lazy cache; feature and error
    contexts are provided by patching the on-demand registry resolver.

    :return: An AppSessionContext instance.
    :rtype: AppSessionContext
    """

    # Build a get-feature event that returns a real (synchronous) Feature.
    # A bare Mock is truthy, so its `is_async` attribute would incorrectly
    # route every feature to the async branch; a real Feature avoids that.
    get_feature_evt = mock.Mock()
    get_feature_evt.execute.return_value = Feature(
        id='test_group.test_feature',
        group_id='test_group',
        feature_key='test_feature',
        name='Test Feature',
        is_async=False,
    )

    # Construct the hub declaratively from the loaded interface with mock events.
    context = AppSessionContext.from_domain(
        app_interface,
        get_feature_evt=get_feature_evt,
        get_error_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
    )

    # Inject the mock logging context via its lazy cache (still supported).
    context._logging = logging_context

    # Feature and error contexts are now built on demand via the registry, so
    # patch the resolver to return the mock contexts for those domain types.
    original_for_domain = BaseContext.for_domain

    def fake_for_domain(domain_cls):
        if domain_cls is Feature:
            return lambda **kwargs: feature_context
        if domain_cls is Error:
            return lambda **kwargs: error_context
        return original_for_domain(domain_cls)

    monkeypatch.setattr(
        'tiferet.contexts.app.BaseContext.for_domain',
        staticmethod(fake_for_domain),
    )

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

# ** test: build_feature_index_materializes_typed_features
def test_build_feature_index_materializes_typed_features():
    '''
    Test that build_feature_index materializes an id-keyed mapping into typed
    Feature objects keyed by id.
    '''

    # Materialize a small id-keyed feature mapping (records minus id).
    index = build_feature_index({
        'group.add': {'group_id': 'group', 'feature_key': 'add', 'name': 'Add'},
    })

    # Assert the record is materialized into a typed Feature keyed by id.
    assert set(index.keys()) == {'group.add'}
    assert isinstance(index['group.add'], Feature)
    assert index['group.add'].id == 'group.add'
    assert index['group.add'].name == 'Add'

# ** test: build_feature_index_empty
def test_build_feature_index_empty():
    '''
    Test that build_feature_index returns an empty index for None or empty input.
    '''

    # Assert both None and empty mappings yield an empty index.
    assert build_feature_index() == {}
    assert build_feature_index({}) == {}

# ** test: build_command_list_materializes_typed_commands
def test_build_command_list_materializes_typed_commands():
    '''
    Test that build_command_list materializes an id-keyed mapping into a list of
    typed CliCommand objects with ids drawn from the keys.
    '''

    # Materialize a small id-keyed command mapping (records minus id).
    commands = build_command_list({
        'sys.boot': {'name': 'Boot', 'key': 'boot', 'group_key': 'sys'},
    })

    # Assert the record is materialized into a typed CliCommand keyed by id.
    assert len(commands) == 1
    assert isinstance(commands[0], CliCommand)
    assert commands[0].id == 'sys.boot'
    assert commands[0].key == 'boot'

# ** test: build_command_list_empty
def test_build_command_list_empty():
    '''
    Test that build_command_list returns an empty list for None or empty input.
    '''

    # Assert both None and empty mappings yield an empty list.
    assert build_command_list() == []
    assert build_command_list({}) == []

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

# ** test: app_interface_context_parse_request
def test_app_interface_context_parse_request(app_interface_context):
    """
    Test parsing a request using the AppSessionContext.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    """

    # Parse the request using the app interface context.
    request = app_interface_context.parse_request(
        headers={
            'Content-Type': 'application/json',
        },
        data={
            'key': 'value',
            'param': 'test_param'
        },
        feature_id='test_group.test_feature'
    )

    # Assert that the parsed request is not None and has the expected attributes.
    assert request is not None
    assert isinstance(request, RequestContext)
    assert request.headers.get('interface_id') == app_interface_context.domain.id
    assert request.data.get('key') == 'value'
    assert request.data.get('param') == 'test_param'
    assert request.feature_id == 'test_group.test_feature'

# ** test: app_interface_context_execute_feature
def test_app_interface_context_execute_feature(app_interface_context, feature_context):
    """
    Test executing a feature using the AppSessionContext.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    :param feature_context: The mock FeatureContext instance.
    :type feature_context: FeatureContext
    """

    # Create a new request object.
    request = RequestContext(
        headers={
            'Content-Type': 'application/json',
            'interface_id': app_interface_context.domain.id
        },
        data={"key": "value"}
    )

    # Execute a feature using the app interface context.
    app_interface_context.execute_feature('test_group.test_feature', request)

    # Assert that the feature id is set correctly to the request headers.
    assert request.headers.get('feature_id') == 'test_group.test_feature'

    # Assert the feature context was delegated to with the loaded domain feature.
    feature_context.execute_feature.assert_called_once()

# ** test: app_interface_context_execute_feature_async
def test_app_interface_context_execute_feature_async(app_interface_context, monkeypatch):
    """
    Test that an is_async feature is routed to AsyncFeatureContext and its
    execute_feature_async coroutine is driven to completion.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    """

    # Arrange the loaded feature to be async.
    app_interface_context.get_feature_evt.execute.return_value = Feature(
        id='test_group.async_feature',
        group_id='test_group',
        feature_key='async_feature',
        name='Async Feature',
        is_async=True,
    )

    # Capture construction and execution of the async feature context.
    calls = {}

    class FakeAsyncFeatureContext:
        def __init__(self, **kwargs):
            calls['init_kwargs'] = kwargs

        async def execute_feature_async(self, feature, request, **kwargs):
            calls['feature'] = feature
            calls['request'] = request

    # Patch the async context referenced by the app module.
    monkeypatch.setattr(
        'tiferet.contexts.app.AsyncFeatureContext',
        FakeAsyncFeatureContext,
    )

    # Create a request and execute the async feature.
    request = RequestContext(data={'key': 'value'})
    app_interface_context.execute_feature('test_group.async_feature', request)

    # Assert the async context was constructed and its coroutine was driven.
    assert 'init_kwargs' in calls
    assert calls['feature'].is_async is True
    assert calls['request'] is request
    assert request.headers.get('feature_id') == 'test_group.async_feature'

# ** test: app_interface_context_handle_error
def test_app_interface_context_handle_error(app_interface_context, error_context):
    """
    Test handling an error using the AppSessionContext.

    :param app_interface_context: The AppSessionContext instance.
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

# ** test: app_interface_context_handle_error_invalid
def test_app_interface_context_handle_error_invalid(app_interface_context, error_context):
    """
    Test handling an invalid error using the AppSessionContext.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    """

    # Create an invalid error object.
    invalid_error = Exception("This is an invalid error.")

    # Mock the ErrorContext to return the formatted error dict.
    error_context.format_response.return_value = {
        'error_code': 'APP_ERROR',
        'name': 'App Error',
        'message': 'An error occurred in the app: This is an invalid error.'
    }

    # Handle the invalid error using the app interface context and verify it raises TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        app_interface_context.handle_error(invalid_error)

    # Assert that the raised exception contains a generic error code and message.
    assert exc_info.value.error_code == 'APP_ERROR'
    assert 'An error occurred in the app' in exc_info.value.message

# ** test: app_interface_context_get_error_cache_hit
def test_app_interface_context_get_error_cache_hit(app_interface_context):
    """
    Test that get_error returns a cached error without invoking the get-error event.

    :param app_interface_context: The AppSessionContext instance.
    :type app_interface_context: AppSessionContext
    """

    # Pre-seed the shared cache with an error in the error namespace.
    cached_error = Error(id='CACHED_ERROR', name='Cached Error')
    app_interface_context.cache.set('CACHED_ERROR', cached_error, *ERROR_CACHE_PREFIX)

    # Retrieve the error by its code.
    result = app_interface_context.get_error('CACHED_ERROR')

    # Assert the cached error is returned and the event was not invoked.
    assert result is cached_error
    app_interface_context.get_error_evt.execute.assert_not_called()

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
    logger.error.assert_called_with(
        'Error executing feature invalid_group.invalid_feature: {"error_code": "FEATURE_NOT_FOUND", "message": "Feature not found: invalid_group.invalid_feature."}'
    )


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
