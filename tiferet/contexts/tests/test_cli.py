# *** imports

# ** core
import logging

# ** infra
import pytest
from unittest import mock

# ** app
from ..cli import CliContext, CliService
from ..app import FeatureContext, ErrorContext, LoggingContext, TiferetError, RequestContext
from ...entities.cli import *

# *** fixtures

# ** fixture: cli_commands
@pytest.fixture
def cli_commands():
    """
    Fixture to create a list of mock CLI commands.
    """
    return {
        'test-group': [
            CliCommand.new(
                group_key='test-group',
                key='test-feature',
                name='Test Feature Command',
                description='A test feature command.',
                arguments=[
                    ModelObject.new(
                        CliArgument,
                        name_or_flags=['--arg1', '-a'],
                        description='Test argument 1',
                        required=True,
                        type='str',
                        default='default_value',
                    )
                ]
            )
        ]
    }

# ** fixture: cli_service
@pytest.fixture
def cli_service(cli_commands):
    """
    Fixture to create a mock CLI service.
    """
    cli_service = mock.create_autospec(CliService)
    cli_service.get_commands.return_value = cli_commands
    cli_service.parse_arguments.return_value = dict(
        group='test-group',
        command='test-feature',
        arg1='default_value'
    )
    return cli_service

# ** fixture: feature_context
@pytest.fixture
def feature_context():
    """
    Fixture to create a mock feature context.
    """
    feature_context = mock.Mock(spec=FeatureContext)
    feature_context.execute_feature.return_value = None
    return feature_context

# ** fixture: error_context
@pytest.fixture
def error_context():
    """
    Fixture to create a mock error context.
    """
    return mock.Mock(spec=ErrorContext)

# ** fixture: logging_context
@pytest.fixture
def logging_context():
    """
    Fixture to create a mock logging context.

    :return: A mock instance of LoggingContext.
    :rtype: LoggingContext
    """
    logging_context = mock.Mock(spec=LoggingContext)
    logging_context.build_logger.return_value = mock.Mock(spec=logging.Logger)
    return logging_context

# ** fixture: cli_context
@pytest.fixture
def cli_context(cli_service, feature_context, error_context, logging_context):
    """
    Fixture to create a CLI context with the provided CLI service, feature context, error context, and logging context.
    """
    return CliContext(
        interface_id='test_cli',
        features=feature_context,
        errors=error_context,
        cli_service=cli_service,
        logging=logging_context
    )

# *** tests

# ** test: cli_context_parse_request
def test_cli_context_parse_request(cli_context):
    """
    Test the parse_request method of the CLI context.
    """
    # Parse the request.
    request = cli_context.parse_request()

    # Check the request type.
    assert isinstance(request, RequestContext)

    # Check the command group and key.
    assert request.feature_id == 'test_group.test_feature'

    # Check the parsed data.
    assert request.data['arg1'] == 'default_value'

    # Check the headers.
    assert request.headers['interface_id'] == 'test_cli'
    assert request.headers['command_group'] == 'test-group'
    assert request.headers['command_key'] == 'test-feature'

# ** test: cli_context_run
def test_cli_context_run(cli_context, logging_context):
    """
    Test the run method of the CLI context.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """
    # Run the CLI context.
    result = cli_context.run()

    # Check that the feature was executed.
    cli_context.features.execute_feature.assert_called_once()

    # Check that the result is None (as per the mock).
    assert result is None

    # Check that no errors were logged.
    cli_context.errors.handle_error.assert_not_called()

    # Assert that the logger was created and used. -- new
    logging_context.build_logger.assert_called_once()
    logger = logging_context.build_logger.return_value
    logger.debug.assert_called()
    logger.info.assert_called_once_with('Executing feature for CLI request: test_group.test_feature')
    logger.error.assert_not_called()

# ** test: cli_context_run_with_parse_request_error
def test_cli_context_run_with_parse_request_error(cli_context, cli_service, logging_context):
    """
    Test the run method of the CLI context when there is an error in parsing the request.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    :param cli_service: The mock CliService instance.
    :type cli_service: CliService
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """
    # Mock the parse_arguments method to raise an exception.
    cli_service.parse_arguments.side_effect = Exception("Parsing error")

    # Run the CLI context and capture the output.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run()

    # Check that the exit code is 2 (as per the error handling).
    assert exc_info.value.code == 2

    # Assert that the logger was created and used for error logging. -- new
    logging_context.build_logger.assert_called_once()
    logger = logging_context.build_logger.return_value
    logger.debug.assert_called_once_with('Parsing CLI request...')
    logger.error.assert_called_once_with('Error parsing CLI request: Parsing error')

# ** test: cli_context_run_with_feature_error
def test_cli_context_run_with_feature_error(cli_context, feature_context, error_context, logging_context):
    """
    Test the run method of the CLI context when there is an error in executing the feature.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    :param feature_context: The mock FeatureContext instance.
    :type feature_context: FeatureContext
    :param error_context: The mock ErrorContext instance.
    :type error_context: ErrorContext
    :param logging_context: The mock LoggingContext instance.
    :type logging_context: LoggingContext
    """
    # Mock the execute_feature method to raise a TiferetError.
    feature_context.execute_feature.side_effect = TiferetError(
        'FEATURE_EXECUTION_FAILED',
        'Feature execution failed'
    )

    # Mock the ErrorContext to return a properly formatted error dict.
    error_context.handle_error.return_value = {
        'error_code': 'FEATURE_EXECUTION_FAILED',
        'name': 'Feature Execution Failed',
        'message': 'Feature execution failed'
    }

    # Run the CLI context and capture the output.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run()

    # Check that the exit code is 1 (as per the error handling).
    assert exc_info.value.code == 1

    # Assert that the logger was created and used for error logging. -- new
    logging_context.build_logger.assert_called_once()
    logger = logging_context.build_logger.return_value
    logger.debug.assert_called()
    logger.info.assert_called_once_with('Executing feature for CLI request: test_group.test_feature')
    logger.error.assert_called_once_with(
        'Error executing CLI feature test_group.test_feature: {"error_code": "FEATURE_EXECUTION_FAILED", "message": "Feature execution failed"}'
    )
