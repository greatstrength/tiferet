# *** imports

# ** core
from typing import Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import (
    DIContext,
    FeatureContext,
    RequestContext,
)
from ...assets import TiferetError
from ...events import DomainEvent
from ...domain import (
    DomainObject,
    Feature,
    FeatureEvent,
)

# *** fixtures

# ** fixture: get_feature_evt
@pytest.fixture
def get_feature_evt() -> DomainEvent:
    """Fixture to provide a mock GetFeature event instance."""

    # Create a mock GetFeature event.
    evt = mock.Mock(spec=DomainEvent)

    # Return the mock event instance.
    return evt

# ** fixture: services_context
@pytest.fixture
def services_context(test_command):
    """Fixture to provide a mock DI context."""

    # Create a mock DI context.
    services_context = mock.Mock(spec=DIContext)

    # Set the DI service to return the test command when requested.
    services_context.get_dependency.return_value = test_command

    # Return the mock DI context.
    return services_context

# ** fixture: feature_context
@pytest.fixture
def feature_context(get_feature_evt, services_context):
    """Fixture to provide an instance of FeatureContext."""

    # Create an instance of FeatureContext with the mock event and DI context.
    return FeatureContext(
        get_feature_evt=get_feature_evt,
        services=services_context
    )

# ** fixture: test_command
@pytest.fixture
def test_command():

    class TestEvent(DomainEvent):
        """A mock domain event for testing purposes."""

        def execute(self, key: str, param: str = None, **kwargs) -> Any:
            """Mock execute method that returns a test response."""

            # Verify that the request exists.
            self.verify(key, 'KEY_NOT_FOUND', 'No key provided for command execution.')

            # Mock response data.
            if not param:
                return {"status": "success", "data": {"key": key}}
            return {"status": "success", "data": {"key": key, "param": param}}

    # Return an instance of the mock event.
    return TestEvent()

# ** fixture: feature
@pytest.fixture
def feature():

    return DomainObject.new(
        Feature,
        id='test_group.test_feature',
        group_id='test_group',
        feature_key='test_feature',
        name='Test Feature',
        description='A feature for testing purposes.',
        steps=[]
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

    from ...events import static as static_events

    called = {}

    def fake_execute(parameter: str):
        called['parameter'] = parameter
        return 'parsed-value'

    monkeypatch.setattr(static_events.ParseParameter, 'execute', staticmethod(fake_execute))

    # Non-request parameter should be delegated to ParseParameter.execute.
    result = feature_context.parse_request_parameter('$env.MY_VAR', RequestContext(data={}))

    assert result == 'parsed-value'
    assert called['parameter'] == '$env.MY_VAR'

# ** test: feature_context_load_feature_step_with_combined_flags
def test_feature_context_load_feature_step_with_combined_flags(feature_context, services_context, test_command):
    """Test loading a feature step combining feature and step flags with correct priority."""

    feature_flags = ['feature_flag_1', 'feature_flag_2']

    feature_event: FeatureEvent = DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
        flags=['command_flag_1', 'command_flag_2'],
    )

    command = feature_context.load_feature_step(feature_event, feature_flags=feature_flags)

    assert command == test_command
    services_context.get_dependency.assert_called_once_with(
        'test_command',
        'feature_flag_1',
        'feature_flag_2',
        'command_flag_1',
        'command_flag_2'
    )


# ** test: feature_context_load_feature_step_only_feature_flags
def test_feature_context_load_feature_step_only_feature_flags(feature_context, services_context, test_command):
    """Test loading a feature step with only feature flags."""

    feature_flags = ['feature_flag']

    feature_event: FeatureEvent = DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
        flags=[],
    )

    command = feature_context.load_feature_step(feature_event, feature_flags=feature_flags)

    assert command == test_command
    services_context.get_dependency.assert_called_once_with('test_command', 'feature_flag')

# ** test: feature_context_load_feature_step_only_command_flags
def test_feature_context_load_feature_step_only_command_flags(feature_context, services_context, test_command):
    """Test loading a feature step with only step flags."""

    feature_event: FeatureEvent = DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
        flags=['command_flag'],
    )

    command = feature_context.load_feature_step(feature_event)

    assert command == test_command
    services_context.get_dependency.assert_called_once_with('test_command', 'command_flag')

# ** test: feature_context_load_feature_step_with_flags
def test_feature_context_load_feature_step_with_flags(feature_context, services_context, test_command):
    """Test loading a feature step that includes flags for dependency resolution."""

    feature_event: FeatureEvent = DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
        flags=['flag1', 'flag2'],
    )

    command = feature_context.load_feature_step(feature_event)

    assert command == test_command
    services_context.get_dependency.assert_called_once_with('test_command', 'flag1', 'flag2')


# ** test: feature_context_load_feature_step_without_flags
def test_feature_context_load_feature_step_without_flags(feature_context, services_context, test_command):
    """Test loading a feature step when no flags are configured."""

    feature_event: FeatureEvent = DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
    )

    command = feature_context.load_feature_step(feature_event)

    assert command == test_command
    services_context.get_dependency.assert_called_once_with('test_command')


# ** test: feature_context_load_feature_step_failed
def test_feature_context_load_feature_step_failed(feature_context, services_context):
    """Test loading a feature step that does not exist in the DIContext."""

    # Add a side effect to raise an exception when the service is not found.
    services_context.get_dependency.side_effect = TiferetError(
        'TEST_ERROR',
        'Feature command not found in services: non_existent_command',
    )

    feature_event: FeatureEvent = DomainObject.new(
        FeatureEvent,
        name='Missing Command',
        service_id='non_existent_command',
        flags=['flagX'],
    )

    with pytest.raises(TiferetError) as exc_info:
        feature_context.load_feature_step(feature_event)

    assert exc_info.value.error_code == 'FEATURE_COMMAND_LOADING_FAILED'
    assert exc_info.value.kwargs.get('service_id') == 'non_existent_command'
    assert 'Failed to load feature step attribute: non_existent_command' in str(exc_info.value)

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
def test_feature_context_execute_feature(feature_context, get_feature_evt, feature):

    # Add a standard feature step with no data key or pass on error.
    feature.steps.append(DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
    ))

    # Set the feature as the GetFeature event's return value.
    get_feature_evt.execute.return_value = feature

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature using the feature context.
    feature_context.execute_feature(feature.id, request)

    # Assert that the request handled the response correctly.
    assert request.handle_response() == {"status": "success", "data": {"key": "value"}}

    # Assert that the GetFeature event was invoked once for this feature id.
    get_feature_evt.execute.assert_called_once_with(id=feature.id)

# ** test: feature_context_execute_feature_with_request_parameter
def test_feature_context_execute_feature_with_request_parameter(feature_context, get_feature_evt, feature):
    """Test executing a feature with a request parameter in the FeatureContext."""

    # Add a feature step with a data key and request parameter.
    feature.steps.append(DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
        parameters=dict(
            param='$r.key',
        ),
        data_key='response_data',
    ))

    # Set the feature as the GetFeature event's return value.
    get_feature_evt.execute.return_value = feature

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature using the feature context with a data key.
    feature_context.cache.clear()
    feature_context.execute_feature(feature.id, request)

    # Assert that the response is stored in the request data under the specified key.
    assert request.data.get('response_data') == {"status": "success", "data": {"key": "value", "param": "value"}}

    # Assert that the GetFeature event was invoked once for this feature id.
    get_feature_evt.execute.assert_called_once_with(id=feature.id)

# ** test: feature_context_execute_feature_with_pass_on_error
def test_feature_context_execute_feature_with_pass_on_error(feature_context, get_feature_evt, feature):
    """Test executing a feature with pass_on_error in the FeatureContext."""

    # Add a feature step with pass_on_error enabled.
    feature.steps.append(DomainObject.new(
        FeatureEvent,
        name='Test Command',
        service_id='test_command',
        pass_on_error=True,
    ))

    # Set the feature as the GetFeature event's return value.
    get_feature_evt.execute.return_value = feature

    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})

    # Execute the feature using the feature context.
    feature_context.cache.clear()
    feature_context.execute_feature(feature.id, request)

    # Assert that the request handled the error without raising an exception.
    assert not request.handle_response()

    # Assert that the GetFeature event was invoked once for this feature id.
    get_feature_evt.execute.assert_called_once_with(id=feature.id)
