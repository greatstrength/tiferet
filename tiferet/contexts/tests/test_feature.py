# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import *
from ...models.feature import *

# *** fixtures

# ** fixture: feature_service
@pytest.fixture
def feature_service():
    """Fixture to provide a mock feature service."""
    
    # Create a mock feature service.
    service = mock.Mock(spec=FeatureService)
    
    # Return the mock feature service.
    return service

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
def feature_context(feature_service, container_context):
    """Fixture to provide an instance of FeatureContext."""
    
    # Create an instance of FeatureContext with the mock feature service and container context.
    return FeatureContext(
        feature_service=feature_service, 
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
def test_feature_context_execute_feature(feature_context, feature_service, feature):

    # Create a standard feature command with no data key or pass on error.
    feature_command = ModelObject.new(
        FeatureCommand,
        attribute_id='test_command',
        name='Test Command'
    )

    # Add it to the feature and set as the feature service's return value.
    feature.add_command(feature_command)
    feature_service.get_feature.return_value = feature

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature using the feature context.
    feature_context.execute_feature(feature.id, request)

    # Assert that the request handled the response correctly.
    assert request.handle_response() == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_execute_feature_with_data_key_parameter
def test_feature_context_execute_feature_with_request_parameter(feature_context, feature_service, feature):
    """Test executing a feature with a request parameter in the FeatureContext."""
    
    # Create a standard feature command with a data key.
    feature_command = ModelObject.new(
        FeatureCommand,
        attribute_id='test_command',
        name='Test Command',
        parameters=dict(
            param='$r.key',
        ),
        data_key='response_data'
    )

    # Add it to the feature and set as the feature service's return value.
    feature.add_command(feature_command)
    feature_service.get_feature.return_value = feature
    feature_service.parse_parameter.return_value = 'value'

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature using the feature context with a data key.
    feature_context.cache.clear()  # Clear the cache to ensure fresh execution.
    feature_context.execute_feature(feature.id, request)

    # Assert that the response is stored in the request data under the specified key.
    assert request.data.get('response_data') == {"status": "success", "data": {"key": "value", "param": "value"}}

# ** test: feature_context_execute_feature_with_pass_on_error
def test_feature_context_execute_feature_with_pass_on_error(feature_context, feature_service, feature):
    """Test executing a feature with pass_on_error in the FeatureContext."""
    
    # Create a standard feature command with pass_on_error set to True.
    feature_command = ModelObject.new(
        FeatureCommand,
        attribute_id='test_command',
        name='Test Command',
        pass_on_error=True
    )

    # Add it to the feature and set as the feature service's return value.
    feature.add_command(feature_command)
    feature_service.get_feature.return_value = feature

    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})

    # Execute the feature using the feature context.
    feature_context.cache.clear()  # Clear the cache to ensure fresh execution.
    feature_context.execute_feature(feature.id, request)

    # Assert that the request handled the error without raising an exception.
    assert not request.handle_response()
