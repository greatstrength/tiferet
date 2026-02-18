"""Tiferet App Context Tests"""

# *** imports

# ** core
import logging

# ** infra
import pytest
from unittest import mock

# ** app
from ...entities import (
    ModelObject,
    AppInterface,
    AppAttribute,
)
from ...contracts import AppService
from ..app import (
    FeatureContext,
    ErrorContext,
    LoggingContext,
    RequestContext,
    AppInterfaceContext,
    AppManagerContext,
)
from ...assets import TiferetError, TiferetAPIError
from ...assets.constants import (
    DEFAULT_ATTRIBUTES,
    DEFAULT_APP_SERVICE_MODULE_PATH,
    DEFAULT_APP_SERVICE_CLASS_NAME,
)
from ...entities import (
    ModelObject,
    AppInterface,
    AppAttribute,
)
from ...contracts import AppService
from ...repos.config.app import AppConfigurationRepository

# *** fixtures

# ** fixture: settings
@pytest.fixture
def settings():
    """Fixture to provide application settings for a custom app service.

    Uses the AppConfigurationRepository as the backing AppService.
    """

    return {
        'app_repo_module_path': 'tiferet.repos.config.app',
        'app_repo_class_name': 'AppConfigurationRepository',
        'app_repo_params': {
            'app_config_file': 'tiferet/configs/tests/test.yml',
        },
    }

# ** app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create a mock AppInterface instance.

    :return: A mock instance of AppInterface.
    :rtype: AppInterface
    '''
    # Create a test AppInterface instance.
    return ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        description='The test app.',
        feature_flag='test',
        data_flag='test',
        attributes=[],
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

    # Mock the handle_error method to return a specific formatted message.
    error_context.handle_error.return_value = dict(
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
    Fixture to create a mock AppInterfaceContext instance.

    :return: A mock instance of AppInterfaceContext.
    :rtype: AppInterfaceContext
    """

    # Create a mock AppInterfaceContext instance.
    return AppInterfaceContext(
        interface_id=app_interface.id,
        features=feature_context,
        errors=error_context,
        logging=logging_context,
    )

# ** fixture: app_manager_context
@pytest.fixture
def app_manager_context():
    """
    Fixture to provide an AppManagerContext instance.

    :return: An instance of AppManagerContext.
    :rtype: AppManagerContext
    """

    # Return the AppManagerContext instance using test settings with AppConfigurationRepository
    # and a test-specific configuration file.
    return AppManagerContext(
        dict(
            app_repo_params=dict(
                app_config_file='tiferet/configs/tests/test_calc.yml',
            ),
        ),
    )

# ** fixture: features
@pytest.fixture
def features():
    return [
        ModelObject.new(
            Feature,
            **TEST_FEATURE,
        )
    ]

# ** fixture: container_attributes
@pytest.fixture
def container_attributes():
    return [
        ModelObject.new(
            ContainerAttribute,
            **TEST_SERVICE_COMMAND_ATTRIBUTE
        )
    ]

# ** fixture: errors
@pytest.fixture
def errors():
    return [
        ModelObject.new(
            Error,
            **TEST_ERROR
        )
    ]


# ** fixture: app_context_interface
@pytest.fixture
def app_context_interface(app_context, app_interface, features, container_attributes, errors):
    return app_context.load_interface(app_interface.id,
        dependencies={
            'features': features,
            'attributes': container_attributes,
            'errors': errors,
        })


# *** tests

# ** test: app_manager_context_load_app_repo_defaults
def test_app_manager_context_load_app_repo_defaults():
    """Validate that AppManagerContext defaults to AppConfigurationRepository.

    This ensures that when no custom repository settings are provided, the
    app repository is loaded using the configuration-backed implementation.
    """

    # Instantiate the AppManagerContext with default settings.
    context = AppManagerContext()

    # Load the app repository and assert that the default repository type is used.
    repo = context.load_app_repo()

    assert isinstance(repo, AppConfigurationRepository)

# ** test: app_manager_context_load_interface
def test_app_manager_context_load_interface(app_manager_context):
    """
    Test the load_interface method of AppManagerContext.

    :param app_manager_context: The AppManagerContext instance.
    :type app_manager_context: AppManagerContext
    :param app_interface: The AppInterface instance.
    :type app_interface: AppInterface
    """

    # Load the app interface using the app context.
    result = app_manager_context.load_interface('test_calc')

    # Assert that the result is an instance of AppInterfaceContext.
    assert result
    assert isinstance(result, AppInterfaceContext)

# ** test: app_manager_context_load_interface_invalid
def test_app_manager_context_load_interface_invalid(app_manager_context, app_interface):
    """
    Test loading an invalid app interface.

    :param app_manager_context: The AppManagerContext instance.
    :type app_manager_context: AppManagerContext
    """

    # Create invalid app interface context.
    class InvalidContext(object):
        def __init__(self, *args, **kwargs):
            pass

    # Create a fake app service that always returns the provided app_interface,
    # regardless of interface_id. This bypasses the APP_INTERFACE_NOT_FOUND path
    # so we can exercise the "invalid app interface context" error instead.
    fake_service = mock.Mock(spec=AppService)
    fake_service.get.return_value = app_interface

    # Mock the load_app_repo method to return the fake service.
    app_manager_context.load_app_repo = mock.Mock(return_value=fake_service)

    # Mock the load_app_instance method to return an invalid app interface context.
    app_manager_context.load_app_instance = mock.Mock(return_value=InvalidContext())

    # Attempt to load an invalid interface and assert that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        app_manager_context.load_interface('invalid_interface_id')

    # Assert that the error message is as expected.
    assert exc_info.value.error_code == 'APP_INTERFACE_INVALID'
    assert 'App context for interface is not valid: invalid_interface_id' in str(exc_info.value)
    assert exc_info.value.kwargs.get('interface_id') == 'invalid_interface_id'

# ** test: app_interface_context_parse_request
def test_app_interface_context_parse_request(app_interface_context):
    """
    Test parsing a request using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
    """

    # Parse the request using the app interface context.
    request = app_interface_context.parse_request(headers={
        'Content-Type': 'application/json',
    },
    data={
        'key': 'value',
        'param': 'test_param'
    },
    feature_id='test_group.test_feature')

    # Assert that the parsed request is not None and has the expected attributes.
    assert request is not None
    assert isinstance(request, RequestContext)
    assert request.headers.get('interface_id') == app_interface_context.interface_id
    assert request.data.get('key') == 'value'
    assert request.data.get('param') == 'test_param'
    request.feature_id == 'test_group.test_feature'

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
            'interface_id': app_interface_context.interface_id
        },
        data={"key": "value"}
    )

    # Execute a feature using the app interface context.
    app_interface_context.execute_feature('test_group.test_feature', request)

    # Assert that the feature id is set correctly to the request headers.
    assert request.headers.get('feature_id') == 'test_group.test_feature'

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
    error_context.handle_error.return_value = {
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
    error_context.handle_error.return_value = {
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

    # Handle the response using the app interface context.
    response = app_interface_context.handle_response(request)

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
    app_interface_context.run('test_group.test_feature', 
        headers={
            'Content-Type': 'application/json',
            'interface_id': app_interface_context.interface_id
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
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """

    # Mock the execute_feature method to raise an error for an invalid feature.
    feature_context.execute_feature.side_effect = TiferetError(
        error_code='FEATURE_NOT_FOUND',
        message='Feature not found: invalid_group.invalid_feature.'
    )

    # Mock the ErrorContext to handle the error and return a formatted message.
    error_context.handle_error.return_value = {
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
                'interface_id': app_interface_context.interface_id
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

    # Mock the ErrorContext to handle the error.
    error_context.handle_error.return_value = {
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
