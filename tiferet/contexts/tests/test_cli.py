# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..cli import CliContext, CliService
from ..app import FeatureContext, ErrorContext, TiferetError
from ...models.cli import *

# *** fixtures

# ** fixture: cli_commands
@pytest.fixture
def cli_commands():
    '''
    Fixture to create a list of mock CLI commands.
    '''
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
                        default='default_value'
                    )
                ]
            )
        ]
    }

# ** fixture: cli_service
@pytest.fixture
def cli_service(cli_commands):
    '''
    Fixture to create a mock CLI service.
    '''
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
    '''
    Fixture to create a mock feature context.
    '''
    feature_context = mock.Mock(spec=FeatureContext)
    feature_context.execute_feature.return_value = None
    return feature_context

# ** fixture: error_context
@pytest.fixture
def error_context():
    '''
    Fixture to create a mock error context.
    '''
    return mock.Mock(spec=ErrorContext)

# ** fixture: cli_context
@pytest.fixture
def cli_context(cli_service, feature_context, error_context):
    '''
    Fixture to create a CLI context with the provided CLI service, feature context, and error context.
    '''
    return CliContext(
        interface_id='test_cli',
        features=feature_context,
        errors=error_context,
        cli_service=cli_service
    )

# *** tests

# ** test: cli_context_parse_request
def test_cli_context_parse_request(cli_context):
    '''
    Test the parse_request method of the CLI context.
    '''
    # Parse the request.
    request = cli_context.parse_request()
    
    # Check the request type.
    assert isinstance(request, CliRequest)
    
    # Check the command group and key.
    assert request.command_group == 'test-group'
    assert request.command_key == 'test-feature'
    
    # Check the parsed data.
    assert request.data['arg1'] == 'default_value'
    
    # Check the headers.
    assert request.headers['interface_id'] == 'test_cli'

# ** test: cli_context_run
def test_cli_context_run(cli_context):
    '''
    Test the run method of the CLI context.
    '''
    # Run the CLI context.
    result = cli_context.run()
    
    # Check that the feature was executed.
    cli_context.features.execute_feature.assert_called_once()
    
    # Check that the result is None (as per the mock).
    assert result is None
    
    # Check that no errors were logged.
    cli_context.errors.handle_error.assert_not_called()

# ** test: cli_context_run_with_parse_request_error
def test_cli_context_run_with_parse_request_error(cli_context, cli_service):
    '''
    Test the run method of the CLI context when there is an error in parsing the request.
    '''
    # Mock the parse_arguments method to raise an exception.
    cli_service.parse_arguments.side_effect = Exception("Parsing error")
    
    # Run the CLI context and capture the output.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run()
    
    # Check that the exit code is 2 (as per the error handling).
    assert exc_info.value.code == 2

# ** test: cli_context_run_with_feature_error
def test_cli_context_run_with_feature_error(cli_context, feature_context):
    '''
    Test the run method of the CLI context when there is an error in executing the feature.
    '''
    # Mock the execute_feature method to raise a TiferetError.
    feature_context.execute_feature.side_effect = TiferetError(
        'FEATURE_EXECUTION_FAILED',
        'Feature execution failed'
    )
    
    # Run the CLI context and capture the output.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run()
    
    # Check that the exit code is 1 (as per the error handling).
    assert exc_info.value.code == 1