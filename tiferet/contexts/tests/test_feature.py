# *** imports

# ** core
from typing import Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import (
    ContainerContext,
    FeatureContext,
    RequestContext,
)
from ...commands.feature import GetFeature
from ...assets import TiferetError
from ...commands import Command
from ...commands.feature import GetFeature
from ...models import (
    ModelObject,
    Feature,
)

# *** fixtures

# ** fixture: get_feature_cmd
@pytest.fixture
def get_feature_cmd() -> GetFeature:
    """Fixture to provide a mock GetFeature command instance."""

    # Create a mock GetFeature command.
    cmd = mock.Mock(spec=GetFeature)

    # Return the mock command instance.
    return cmd

# ** fixture: container_context
@pytest.fixture
def container_context(test_command):
    """Fixture to provide a mock container context."""
    
    # Create a mock container context.
    container_context = mock.Mock(spec=ContainerContext)

    # Set the container service to return the test command when requested.
    container_context.get_dependency.return_value = test_command
    
    # Return the mock container context.
    return container_context

# ** fixture: feature_context
@pytest.fixture
def feature_context(get_feature_cmd, container_context):
    """Fixture to provide an instance of FeatureContext."""

    # Create an instance of FeatureContext with the mock GetFeature command and container context.
    return FeatureContext(
        get_feature_cmd=get_feature_cmd,
        container=container_context
    )

# ** fixture: test_command
@pytest.fixture
def test_command():

    class TestCommand(Command):
        """A mock command for testing purposes."""
        
        def execute(self, key: str, param: str = None, **kwargs) -> Any:
            """Mock execute method that returns a test response."""
            
            # Verify that the request exists.
            self.verify(key, 'KEY_NOT_FOUND', 'No key provided for command execution.')
            
            # Mock response data.
            if not param:
                return {"status": "success", "data": {"key": key}}
            return {"status": "success", "data": {"key": key, "param": param}}
        
    # Return an instance of the mock command.
    return TestCommand()

# ** fixture: feature
@pytest.fixture
def feature():

    return ModelObject.new(
        Feature,
        id='test_group.test_feature',
        group_id='test_group',
        feature_key='test_feature',
        name='Test Feature',
        description='A feature for testing purposes.',
        commands=[]
    )

# *** tests

# ** test: feature_context_parse_request_parameter_success
def test_feature_context_parse_request_parameter_success(feature_context):
    """Test parsing a request-backed parameter successfully."""

    # Create a mock request with data.
    request = RequestContext(data={"key": "value"})

    # Parse the parameter from the request.
    result = feature_context.parse_request_parameter('$r.key', request)

    # Assert that the parsed value is correct.
    assert result == 'value'

# ** test: feature_context_parse_request_parameter_request_not_found
def test_feature_context_parse_request_parameter_request_not_found(feature_context):
    """Test that an error is raised when request is None for a request-backed parameter."""

    from ...assets import TiferetError

    # Assert that an error is raised when request is None.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.parse_request_parameter('$r.key', None)

    assert exc_info.value.error_code == 'REQUEST_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.key'

# ** test: feature_context_parse_request_parameter_not_found
def test_feature_context_parse_request_parameter_not_found(feature_context):
    """Test that an error is raised when the parameter key is missing in request data."""

    from ...assets import TiferetError

    # Create a mock request without the expected key.
    request = RequestContext(data={})

    # Assert that an error is raised when the parameter is missing.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.parse_request_parameter('$r.missing', request)

    assert exc_info.value.error_code == 'PARAMETER_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.missing'

# ** test: feature_context_parse_request_parameter_delegates_to_parse_parameter
def test_feature_context_parse_request_parameter_delegates_to_parse_parameter(feature_context, monkeypatch):
    """Test that non-request parameters delegate to ParseParameter.execute."""

    from ...commands import static as static_commands

    called = {}

    def fake_execute(parameter: str):
        called['parameter'] = parameter
        return 'parsed-value'

    monkeypatch.setattr(static_commands.ParseParameter, 'execute', staticmethod(fake_execute))

    # Non-request parameter should be delegated to ParseParameter.execute.
    result = feature_context.parse_request_parameter('$env.MY_VAR', RequestContext(data={}))

    assert result == 'parsed-value'
    assert called['parameter'] == '$env.MY_VAR'

# ** test: feature_context_load_feature_command
def test_feature_context_load_feature_command(feature_context, test_command):
    """Test loading a feature command from the FeatureContext."""

    # Load the feature command using the feature context.
    command = feature_context.load_feature_command('test_command')
    
    # Assert that the loaded command is the same as the test command.
    assert command == test_command
    assert command.execute(key='value') == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_load_feature_command_failed
def test_feature_context_load_feature_command_failed(feature_context, container_context):
    """Test loading a feature command that does not exist in the FeatureContext."""
    
    # Add a side effect to the container context to raise an exception when trying to get a non-existent command.
    container_context.get_dependency.side_effect = TiferetError(
        'TEST_ERROR',
        'Feature command not found in container: non_existent_command',
    )

    # Attempt to load a non-existent feature command.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.load_feature_command('non_existent_command')
    
    # Assert that the exception message is as expected.
    assert exc_info.value.error_code == 'FEATURE_COMMAND_LOADING_FAILED'
    assert exc_info.value.kwargs.get('attribute_id') == 'non_existent_command'
    assert 'Failed to load feature command attribute: non_existent_command' in str(exc_info.value)

# ** test: feature_context_handle_command
def test_feature_context_handle_command(feature_context, test_command):
    """Test handling a command in the FeatureContext."""
    
    # Create a mock request.
    request = RequestContext(data={"key": "value"})
    
    # Handle the command using the feature context.
    feature_context.handle_command(test_command, request)
    response = request.handle_response()
    
    # Assert that the response matches the expected output.
    assert response == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_handle_command_with_error
def test_feature_context_handle_command_with_error(feature_context, test_command):
    """Test handling a command that raises an error in the FeatureContext."""
    
    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})
    
    # Attempt to handle the command and catch the raised error.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.handle_command(test_command, request)
    
    # Assert that the exception message is as expected.
    assert exc_info.value.error_code == 'KEY_NOT_FOUND'
    assert 'No key provided for command execution.' in str(exc_info.value)

# ** test: feature_context_handle_command_with_data_key
def test_feature_context_handle_command_with_data_key(feature_context, test_command):
    """Test handling a command with a data key in the FeatureContext."""
    
    # Create a mock request with a data key.
    request = RequestContext(data={"key": "value"})
    
    # Handle the command using the feature context.
    feature_context.handle_command(test_command, request, data_key="response_data")
    
    # Assert that the response matches the expected output.
    assert request.data.get('response_data') == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_handle_command_with_pass_on_error
def test_feature_context_handle_command_with_pass_on_error(feature_context, test_command):
    """Test handling a command with pass_on_error in the FeatureContext."""
    
    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})
    
    # Handle the command with pass_on_error set to True.
    feature_context.handle_command(test_command, request, pass_on_error=True)
    
    # Assert that the request handled the error without raising an exception.
    assert not request.handle_response()

# ** test: feature_context_execute_feature
def test_feature_context_execute_feature(feature_context, get_feature_cmd, feature):

    # Add a standard feature command with no data key or pass on error.
    feature.add_command(
        name='Test Command',
        attribute_id='test_command',
    )

    # Set the feature as the GetFeature command's return value.
    get_feature_cmd.execute.return_value = feature

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature using the feature context.
    feature_context.execute_feature(feature.id, request)

    # Assert that the request handled the response correctly.
    assert request.handle_response() == {"status": "success", "data": {"key": "value"}}

    # Assert that the GetFeature command was invoked once for this feature id.
    get_feature_cmd.execute.assert_called_once_with(id=feature.id)

# ** test: feature_context_execute_feature_with_request_parameter
def test_feature_context_execute_feature_with_request_parameter(feature_context, get_feature_cmd, feature):
    """Test executing a feature with a request parameter in the FeatureContext."""
    
    # Add a standard feature command with a data key.
    feature.add_command(
        name='Test Command',
        attribute_id='test_command',
        parameters=dict(
            param='$r.key',
        ),
        data_key='response_data',
    )

    # Set the feature as the GetFeature command's return value.
    get_feature_cmd.execute.return_value = feature

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature using the feature context with a data key.
    feature_context.cache.clear()  # Clear the cache to ensure fresh execution.
    feature_context.execute_feature(feature.id, request)

    # Assert that the response is stored in the request data under the specified key.
    assert request.data.get('response_data') == {"status": "success", "data": {"key": "value", "param": "value"}}

    # Assert that the GetFeature command was invoked once for this feature id.
    get_feature_cmd.execute.assert_called_once_with(id=feature.id)

# ** test: feature_context_execute_feature_with_pass_on_error
def test_feature_context_execute_feature_with_pass_on_error(feature_context, get_feature_cmd, feature):
    """Test executing a feature with pass_on_error in the FeatureContext."""
    
    # Add a standard feature command and enable pass_on_error.
    feature_command = feature.add_command(
        name='Test Command',
        attribute_id='test_command',
    )
    feature_command.pass_on_error = True

    # Set the feature as the GetFeature command's return value.
    get_feature_cmd.execute.return_value = feature

    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})

    # Execute the feature using the feature context.
    feature_context.cache.clear()  # Clear the cache to ensure fresh execution.
    feature_context.execute_feature(feature.id, request)

    # Assert that the request handled the error without raising an exception.
    assert not request.handle_response()

    # Assert that the GetFeature command was invoked once for this feature id.
    get_feature_cmd.execute.assert_called_once_with(id=feature.id)
