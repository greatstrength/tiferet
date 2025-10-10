"""Tiferet App Context Tests"""

# *** imports

# ** core
import logging

# ** infra
import pytest
from unittest import mock

# ** app
from ..app import (
    AppRepository,
    FeatureContext,
    ErrorContext,
    LoggingContext,
    RequestContext,
    AppInterfaceContext,
    AppManagerContext,
    TiferetError,
    AppService,
)
from ...models import (
    ModelObject,
    AppInterface,
    AppAttribute,
)

# *** fixtures

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
        attributes=[
            ModelObject.new(
                AppAttribute,
                attribute_id='test_attribute',
                module_path='test_module_path',
                class_name='test_class_name',
            ),
        ],
    )

# ** fixture: app_repo
@pytest.fixture
def app_repo(app_interface):
    """
    Fixture to create a mock AppRepository instance.

    :return: A mock instance of AppRepository.
    :rtype: AppRepository
    """

    # Create a mock AppRepository instance.
    app_repo = mock.Mock(spec=AppRepository)

    # Set the return value for the get_interface method.
    app_repo.get_interface.return_value = app_interface

    # Return the mock AppRepository instance.
    return app_repo

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

# ** fixture: app_service
@pytest.fixture
def app_service(app_repo, app_interface_context):
    """Fixture to provide a mock app service."""

    # Create a mock app service.
    service = mock.Mock(spec=AppService)

    # Set the return value for the load_app_repository method.
    service.load_app_repository.return_value = app_repo

    # Set the return value for the load_app_instance method.
    service.load_app_instance.return_value = app_interface_context

    # Return the mock app service.
    return service

# ** fixture: app_manager_context
@pytest.fixture
def app_manager_context(app_service):
    """
    Fixture to provide an AppManagerContext instance.

    :param app_service: The mock app service.
    :type app_service: AppService
    :return: An instance of AppManagerContext.
    :rtype: AppManagerContext
    """

    # Return the AppManagerContext instance.
    return AppManagerContext(
        dict(
            app_repo_module_path='tiferet.proxies.yaml.app',
            app_repo_class_name='AppYamlProxy',
            app_repo_params=dict(
                app_config_file='tiferet/configs/app.yaml',
            )
        ),
        app_service
    )

# *** tests

# ** test: app_manager_context_load_interface
def test_app_manager_context_load_interface(app_manager_context, app_interface):
    """
    Test the load_interface method of AppManagerContext.

    :param app_manager_context: The AppManagerContext instance.
    :type app_manager_context: AppManagerContext
    :param app_interface: The AppInterface instance.
    :type app_interface: AppInterface
    """

    # Load the app interface using the app context.
    result = app_manager_context.load_interface(app_interface.id)

    # Assert that the result is an instance of AppInterfaceContext.
    assert result
    assert isinstance(result, AppInterfaceContext)

# ** test: app_manager_context_load_interface_invalid
def test_app_manager_context_load_interface_invalid(app_manager_context, app_service):
    """
    Test loading an invalid app interface.

    :param app_manager_context: The AppManagerContext instance.
    :type app_manager_context: AppManagerContext
    :param app_service: The mock app service.
    :type app_service: AppService
    """

    # Create invalid app interface context.
    class InvalidContext(object):
        def __init__(self, *args, **kwargs):
            pass

    # Mock the load_app_instance method to return an invalid app interface context.
    app_service.load_app_instance.return_value = InvalidContext()

    # Attempt to load an invalid interface and assert that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        app_manager_context.load_interface('invalid_interface_id')

    # Assert that the error message is as expected.
    assert exc_info.value.error_code == 'APP_INTERFACE_INVALID'
    assert 'App context for interface is not valid: invalid_interface_id' in str(exc_info.value)

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

    # Handle an error using the app interface context.
    error_response = app_interface_context.errors.handle_error(
        error
    )

    # Assert that the error response contains the expected error code and message.
    assert error_response['error_code'] == 'TEST_ERROR'
    assert error_response['message'] == 'This is a test error message.'

# ** test: app_interface_context_handle_error_invalid
def test_app_interface_context_handle_error_invalid(app_interface_context, error_context):
    """
    Test handling an invalid error using the AppInterfaceContext.

    :param app_interface_context: The AppInterfaceContext instance.
    :type app_interface_context: AppInterfaceContext
    """

    # Create an invalid error object.
    invalid_error = Exception("This is an invalid error.")

    # Mock the ErrorContext to raise a TiferetError when handling an invalid error.
    error_context.handle_error.return_value = {
        'error_code': 'APP_ERROR',
        'message': 'An error occurred in the app: This is an invalid error.'
    }

    # Handle the invalid error using the app interface context.
    error_response = app_interface_context.handle_error(invalid_error)

    # Assert that the error response contains a generic error code and message.
    assert error_response['error_code'] == 'APP_ERROR'
    assert 'An error occurred in the app' in error_response['message']

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

    # Assert that the logger was created and used. -- new
    logging_context.build_logger()
    logger = logging_context.build_logger.return_value
    # logger.debug.assert_called_with('Parsing request for feature: test_group.test_feature')
    logger.info.assert_called_with('Executing feature: test_group.test_feature')
    logger.debug.assert_called()

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
        'message': 'Feature not found: invalid_group.invalid_feature.'
    }

    # Attempt to run an invalid feature and assert that it raises an error.
    response = app_interface_context.run(
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

    # Assert that the formatted error message is as expected.
    assert response['error_code'] == 'FEATURE_NOT_FOUND'
    assert 'Feature not found: invalid_group.invalid_feature.' in response['message']

    # Assert that the logger was created and used for error logging. -- new
    logging_context.build_logger.assert_called_once()
    logger = logging_context.build_logger.return_value
    logger.error.assert_called_with(
        'Error executing feature invalid_group.invalid_feature: {"error_code": "FEATURE_NOT_FOUND", "message": "Feature not found: invalid_group.invalid_feature."}'
    )