"""Tiferet App Context Tests"""

# *** imports

# ** core
import logging

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetError, TiferetAPIError
from tiferet.domain import Feature, Error
from tiferet.mappers import AppInterfaceAggregate
from tiferet.contexts.app import (
    BaseContext,
    FeatureContext,
    ErrorContext,
    LoggingContext,
    RequestContext,
    AppInterfaceContext,
)

# *** fixtures

# ** fixture: app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create an AppInterfaceAggregate instance.

    :return: An AppInterfaceAggregate instance.
    :rtype: AppInterfaceAggregate
    '''

    # Create a test AppInterfaceAggregate instance.
    return AppInterfaceAggregate(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
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
    Fixture to create an AppInterfaceContext hub bound to the test interface.
    The logging context is injected via its lazy cache; feature and error
    contexts are provided by patching the on-demand registry resolver.

    :return: An AppInterfaceContext instance.
    :rtype: AppInterfaceContext
    """

    # Construct the hub declaratively from the loaded interface with mock events.
    context = AppInterfaceContext.from_domain(
        app_interface,
        get_feature_evt=mock.Mock(),
        get_error_evt=mock.Mock(),
        di_list_all_configs_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
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

# ** test: app_interface_context_parse_request
def test_app_interface_context_parse_request(app_interface_context):
    """
    Test parsing a request using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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
    Test executing a feature using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

# ** test: app_interface_context_handle_error
def test_app_interface_context_handle_error(app_interface_context, error_context):
    """
    Test handling an error using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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
    Test handling an invalid error using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

# ** test: app_interface_context_handle_response
def test_app_interface_context_handle_response(app_interface_context):
    """
    Test handling a response using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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
    Test running the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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
    Test running the AppInterfaceContext with an invalid feature.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
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
