# *** imports

# ** core
from typing import Any

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.contexts.feature import (
    DIContext,
    FeatureContext,
    RequestContext,
)
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent, AsyncDomainEvent
from tiferet.domain import (
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

    return Feature(
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

    from tiferet.assets import TiferetError

    # Assert that an error is raised when request is None.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.parse_request_parameter('$r.key', None)

    assert exc_info.value.error_code == 'REQUEST_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.key'

# ** test: feature_context_parse_request_parameter_not_found
def test_feature_context_parse_request_parameter_not_found(feature_context):
    """Test that an error is raised when the parameter key is missing in request data."""

    from tiferet.assets import TiferetError

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

    from tiferet.events import static as static_events

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

    feature_event: FeatureEvent = FeatureEvent(
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

    feature_event: FeatureEvent = FeatureEvent(
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

    feature_event: FeatureEvent = FeatureEvent(
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

    feature_event: FeatureEvent = FeatureEvent(
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

    feature_event: FeatureEvent = FeatureEvent(
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

    feature_event: FeatureEvent = FeatureEvent(
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
    feature.steps.append(FeatureEvent(
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
    feature.steps.append(FeatureEvent(
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

# ** test: feature_context_evaluate_condition_none_returns_true
def test_feature_context_evaluate_condition_none_returns_true(feature_context):
    """Test that evaluate_condition returns True when condition is None."""

    # Create a mock request.
    request = RequestContext(data={})

    # Assert that None condition evaluates to True.
    assert feature_context.evaluate_condition(None, request) is True

# ** test: feature_context_evaluate_condition_empty_returns_true
def test_feature_context_evaluate_condition_empty_returns_true(feature_context):
    """Test that evaluate_condition returns True when condition is empty."""

    # Create a mock request.
    request = RequestContext(data={})

    # Assert that empty string condition evaluates to True.
    assert feature_context.evaluate_condition('', request) is True
    assert feature_context.evaluate_condition('   ', request) is True

# ** test: feature_context_evaluate_condition_true_expression
def test_feature_context_evaluate_condition_true_expression(feature_context):
    """Test that evaluate_condition returns True when expression resolves to True."""

    # Create a request with data for the condition.
    request = RequestContext(data={'x': 5})

    # Assert that the condition evaluates to True.
    assert feature_context.evaluate_condition('$r.x > 0', request) is True

# ** test: feature_context_evaluate_condition_false_expression
def test_feature_context_evaluate_condition_false_expression(feature_context):
    """Test that evaluate_condition returns False when expression resolves to False."""

    # Create a request with data for the condition.
    request = RequestContext(data={'x': -1})

    # Assert that the condition evaluates to False.
    assert feature_context.evaluate_condition('$r.x > 0', request) is False

# ** test: feature_context_evaluate_condition_string_equality
def test_feature_context_evaluate_condition_string_equality(feature_context):
    """Test that evaluate_condition supports string equality checks."""

    # Create a request with a string value.
    request = RequestContext(data={'mode': 'advanced'})

    # Assert string equality condition evaluates correctly.
    assert feature_context.evaluate_condition("$r.mode == 'advanced'", request) is True
    assert feature_context.evaluate_condition("$r.mode == 'basic'", request) is False

# ** test: feature_context_evaluate_condition_missing_key_returns_false
def test_feature_context_evaluate_condition_missing_key_returns_false(feature_context):
    """Test that evaluate_condition returns False when a referenced key is missing."""

    # Create a request without the referenced key.
    request = RequestContext(data={})

    # Assert that a condition referencing a missing key evaluates to False.
    assert feature_context.evaluate_condition('$r.x > 0', request) is False

# ** test: feature_context_evaluate_condition_invalid_expression_returns_false
def test_feature_context_evaluate_condition_invalid_expression_returns_false(feature_context):
    """Test that evaluate_condition returns False on unparseable expressions."""

    # Create a mock request.
    request = RequestContext(data={'x': 5})

    # Assert that an invalid expression evaluates to False (defensive).
    assert feature_context.evaluate_condition('$r.x >>>!!! invalid', request) is False

# ** test: feature_context_resolve_feature_steps_yields_steps
def test_feature_context_resolve_feature_steps_yields_steps(feature_context, get_feature_evt, feature, test_command):
    """Test that resolve_feature_steps yields (cmd, feature_event, params) for each step."""

    # Add two steps to the feature.
    step_a = FeatureEvent(name='Step A', service_id='test_command')
    step_b = FeatureEvent(name='Step B', service_id='test_command')
    feature.steps.extend([step_a, step_b])

    # Set the feature as the GetFeature event's return value.
    get_feature_evt.execute.return_value = feature

    # Create a request.
    request = RequestContext(data={'key': 'value'})

    # Resolve steps and collect results.
    resolved = list(feature_context.resolve_feature_steps(feature.id, request))

    # Assert both steps were yielded with the correct command and empty params.
    assert len(resolved) == 2
    assert resolved[0] == (test_command, step_a, {})
    assert resolved[1] == (test_command, step_b, {})

# ** test: feature_context_resolve_feature_steps_skips_false_condition
def test_feature_context_resolve_feature_steps_skips_false_condition(feature_context, get_feature_evt, feature, test_command):
    """Test that resolve_feature_steps skips steps with false conditions."""

    # Add a skipped step (false condition) and an unconditional step.
    skipped = FeatureEvent(name='Skipped', service_id='test_command', condition='$r.x > 100')
    executed = FeatureEvent(name='Executed', service_id='test_command')
    feature.steps.extend([skipped, executed])

    # Set the feature.
    get_feature_evt.execute.return_value = feature

    # Create a request where x=5 (fails the condition).
    request = RequestContext(data={'key': 'value', 'x': 5})

    # Resolve and assert only the unconditional step is yielded.
    resolved = list(feature_context.resolve_feature_steps(feature.id, request))
    assert len(resolved) == 1
    assert resolved[0][1] is executed

# ** test: feature_context_resolve_feature_steps_yields_true_condition
def test_feature_context_resolve_feature_steps_yields_true_condition(feature_context, get_feature_evt, feature, test_command):
    """Test that resolve_feature_steps yields steps with true conditions."""

    # Add a step with a true condition.
    step = FeatureEvent(name='Conditional', service_id='test_command', condition='$r.x > 0')
    feature.steps.append(step)

    # Set the feature.
    get_feature_evt.execute.return_value = feature

    # Create a request where x=5 (passes the condition).
    request = RequestContext(data={'key': 'value', 'x': 5})

    # Resolve and assert the step is yielded.
    resolved = list(feature_context.resolve_feature_steps(feature.id, request))
    assert len(resolved) == 1
    assert resolved[0][1] is step

# ** test: feature_context_resolve_feature_steps_parses_parameters
def test_feature_context_resolve_feature_steps_parses_parameters(feature_context, get_feature_evt, feature, test_command):
    """Test that resolve_feature_steps parses request-backed parameters."""

    # Add a step with a request-backed parameter.
    step = FeatureEvent(
        name='Parameterized',
        service_id='test_command',
        parameters={'param': '$r.key'},
    )
    feature.steps.append(step)

    # Set the feature.
    get_feature_evt.execute.return_value = feature

    # Create a request.
    request = RequestContext(data={'key': 'resolved_value'})

    # Resolve and assert the parameter was parsed.
    resolved = list(feature_context.resolve_feature_steps(feature.id, request))
    assert len(resolved) == 1
    assert resolved[0][2] == {'param': 'resolved_value'}

# ** test: feature_context_resolve_feature_steps_empty_feature
def test_feature_context_resolve_feature_steps_empty_feature(feature_context, get_feature_evt, feature):
    """Test that resolve_feature_steps yields nothing for a feature with no steps."""

    # Set the feature (no steps appended).
    get_feature_evt.execute.return_value = feature

    # Create a request.
    request = RequestContext(data={'key': 'value'})

    # Resolve and assert nothing is yielded.
    resolved = list(feature_context.resolve_feature_steps(feature.id, request))
    assert len(resolved) == 0

# ** test: feature_context_execute_feature_with_pass_on_error
def test_feature_context_execute_feature_with_pass_on_error(feature_context, get_feature_evt, feature):
    """Test executing a feature with pass_on_error in the FeatureContext."""

    # Add a feature step with pass_on_error enabled.
    feature.steps.append(FeatureEvent(
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

# ** fixture: async_test_command
@pytest.fixture
def async_test_command():

    class AsyncTestEvent(AsyncDomainEvent):
        """An async domain event for testing purposes."""

        async def execute(self, key: str, param: str = None, **kwargs) -> Any:
            """Async execute method that returns a test response."""

            # Verify that the key exists.
            self.verify(key, 'KEY_NOT_FOUND', 'No key provided for command execution.')

            # Mock response data.
            if not param:
                return {"status": "async_success", "data": {"key": key}}
            return {"status": "async_success", "data": {"key": key, "param": param}}

    # Return an instance of the async event.
    return AsyncTestEvent()

# ** fixture: async_services_context
@pytest.fixture
def async_services_context(async_test_command):
    """Fixture to provide a mock DI context that returns the async test command."""

    # Create a mock DI context.
    ctx = mock.Mock(spec=DIContext)
    ctx.get_dependency.return_value = async_test_command
    return ctx

# ** fixture: async_feature_context
@pytest.fixture
def async_feature_context(get_feature_evt, async_services_context):
    """Fixture to provide a FeatureContext wired with the async command."""

    return FeatureContext(
        get_feature_evt=get_feature_evt,
        services=async_services_context
    )

# ** test: feature_context_handle_command_async
@pytest.mark.asyncio
async def test_feature_context_handle_command_async(async_feature_context, async_test_command):
    """Test handling an async command in the FeatureContext."""

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Handle the async command.
    await async_feature_context.handle_command_async(async_test_command, request)
    response = request.handle_response()

    # Assert that the response matches the expected output.
    assert response == {"status": "async_success", "data": {"key": "value"}}

# ** test: feature_context_handle_command_async_with_sync_command
@pytest.mark.asyncio
async def test_feature_context_handle_command_async_with_sync_command(feature_context, test_command):
    """Test that handle_command_async correctly dispatches a sync command."""

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Handle a sync command via the async handler.
    await feature_context.handle_command_async(test_command, request)
    response = request.handle_response()

    # Assert that the sync command executed correctly.
    assert response == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_handle_command_async_with_error
@pytest.mark.asyncio
async def test_feature_context_handle_command_async_with_error(async_feature_context, async_test_command):
    """Test handling an async command that raises an error."""

    # Create a request that will cause verify to fail.
    request = RequestContext(data={'key': None})

    # Attempt to handle the command and catch the raised error.
    with pytest.raises(TiferetError) as exc_info:
        await async_feature_context.handle_command_async(async_test_command, request)

    assert exc_info.value.error_code == 'KEY_NOT_FOUND'

# ** test: feature_context_handle_command_async_pass_on_error
@pytest.mark.asyncio
async def test_feature_context_handle_command_async_pass_on_error(async_feature_context, async_test_command):
    """Test handling an async command with pass_on_error."""

    # Create a request that will cause verify to fail.
    request = RequestContext(data={'key': None})

    # Handle with pass_on_error=True.
    await async_feature_context.handle_command_async(async_test_command, request, pass_on_error=True)

    # Assert that the request handled the error without raising.
    assert not request.handle_response()

# ** test: feature_context_execute_feature_async_basic
@pytest.mark.asyncio
async def test_feature_context_execute_feature_async_basic(async_feature_context, get_feature_evt, feature):
    """Test execute_feature_async with a single async step."""

    # Add an async feature step.
    feature.steps.append(FeatureEvent(
        name='Async Command',
        service_id='async_test_command',
    ))

    # Set the feature as the GetFeature event's return value.
    get_feature_evt.execute.return_value = feature

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the feature asynchronously.
    await async_feature_context.execute_feature_async(feature.id, request)

    # Assert the result.
    assert request.handle_response() == {"status": "async_success", "data": {"key": "value"}}

# ** test: feature_context_execute_feature_async_mixed_chain
@pytest.mark.asyncio
async def test_feature_context_execute_feature_async_mixed_chain(get_feature_evt, feature):
    """Test execute_feature_async with mixed sync and async steps."""

    # Create both sync and async commands.
    class SyncStep(DomainEvent):
        def execute(self, key=None, **kwargs):
            return {"sync": True, "key": key}

    class AsyncStep(AsyncDomainEvent):
        async def execute(self, key=None, **kwargs):
            return {"async": True, "key": key}

    sync_cmd = SyncStep()
    async_cmd = AsyncStep()

    # Mock DI context to return the right command per service_id.
    services = mock.Mock(spec=DIContext)
    def resolve(service_id, *flags):
        if service_id == 'sync_step':
            return sync_cmd
        return async_cmd
    services.get_dependency.side_effect = resolve

    # Build the feature context.
    ctx = FeatureContext(get_feature_evt=get_feature_evt, services=services)

    # Add a sync step followed by an async step.
    feature.steps.append(FeatureEvent(
        name='Sync Step',
        service_id='sync_step',
        data_key='sync_result',
    ))
    feature.steps.append(FeatureEvent(
        name='Async Step',
        service_id='async_step',
        data_key='async_result',
    ))

    # Set the feature as the GetFeature event's return value.
    get_feature_evt.execute.return_value = feature

    # Create a request.
    request = RequestContext(data={"key": "mixed"})

    # Clear the cache to avoid stale feature data from prior tests.
    ctx.cache.clear()

    # Execute the feature asynchronously (supports mixed chains).
    await ctx.execute_feature_async(feature.id, request)

    # Assert both steps executed correctly.
    assert request.data.get('sync_result') == {"sync": True, "key": "mixed"}
    assert request.data.get('async_result') == {"async": True, "key": "mixed"}

