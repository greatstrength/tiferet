"""Tiferet Feature Context Tests"""

# *** imports

# ** core
from typing import Any

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.contexts.feature import (
    FeatureContext,
    AsyncFeatureContext,
    RequestContext,
    parse_request_parameter,
    evaluate_condition,
    validate_request,
)
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent, AsyncDomainEvent
from tiferet.domain import (
    Feature,
    EventFeatureStep,
)

# *** fixtures

# ** fixture: services_context
@pytest.fixture
def services_context(test_command):
    """Fixture to provide a mock DI context."""

    # Create a mock holder exposing a get_dependency resolution handler.
    services_context = mock.Mock()

    # Set the handler to return the test command when requested.
    services_context.get_dependency.return_value = test_command

    # Return the mock holder.
    return services_context

# ** fixture: feature_context
@pytest.fixture
def feature_context(services_context):
    """Fixture to provide an instance of FeatureContext."""

    # Create an instance of FeatureContext with the mock resolution handler.
    return FeatureContext(get_dependency=services_context.get_dependency)

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

# ** test: feature_context_parse_request_parameter_success (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_parse_request_parameter_request_ref_success
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_parse_request_parameter_success(feature_context):
    """Test parsing a request-backed parameter successfully."""

    # Create a mock request with data.
    request = RequestContext(data={"key": "value"})

    # Parse the parameter from the request.
    result = feature_context.parse_request_parameter('$r.key', request)

    # Assert that the parsed value is correct.
    assert result == 'value'

# ** test: feature_context_parse_request_parameter_request_not_found (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_parse_request_parameter_request_not_found
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_parse_request_parameter_request_not_found(feature_context):
    """Test that an error is raised when request is None for a request-backed parameter."""

    from tiferet.assets import TiferetError

    # Assert that an error is raised when request is None.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.parse_request_parameter('$r.key', None)

    assert exc_info.value.error_code == 'REQUEST_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.key'

# ** test: feature_context_parse_request_parameter_not_found (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_parse_request_parameter_key_missing
# ++ todo: remove when instance methods are removed at FE2 cleanup
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

# ** test: feature_context_parse_request_parameter_delegates_to_parse_parameter (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_parse_request_parameter_delegates_to_parse_parameter
# ++ todo: remove when instance methods are removed at FE2 cleanup
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

    feature_event: EventFeatureStep = EventFeatureStep(
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

    feature_event: EventFeatureStep = EventFeatureStep(
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

    feature_event: EventFeatureStep = EventFeatureStep(
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

    feature_event: EventFeatureStep = EventFeatureStep(
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

    feature_event: EventFeatureStep = EventFeatureStep(
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

    feature_event: EventFeatureStep = EventFeatureStep(
        name='Missing Command',
        service_id='non_existent_command',
        flags=['flagX'],
    )

    with pytest.raises(TiferetError) as exc_info:
        feature_context.load_feature_step(feature_event)

    assert exc_info.value.error_code == 'FEATURE_COMMAND_LOADING_FAILED'
    assert exc_info.value.kwargs.get('service_id') == 'non_existent_command'
    assert 'Failed to load feature step attribute: non_existent_command' in str(exc_info.value)

# ** test: feature_context_load_feature_middleware
def test_feature_context_load_feature_middleware(feature_context, services_context, test_command):
    """Test resolving middleware service IDs to instances in order."""

    # Resolve a list of middleware ids via the injected handler.
    middleware = feature_context.load_feature_middleware(['mw_one', 'mw_two'])

    # Assert each id resolved to the handler's return value, preserving order.
    assert middleware == [test_command, test_command]
    assert services_context.get_dependency.call_count == 2

# ** test: feature_context_load_feature_middleware_empty
def test_feature_context_load_feature_middleware_empty(feature_context, services_context):
    """Test that an empty middleware list resolves to an empty list without resolution."""

    # Resolve an empty middleware list.
    middleware = feature_context.load_feature_middleware([])

    # Assert no resolution occurred and the result is empty.
    assert middleware == []
    services_context.get_dependency.assert_not_called()

# ** test: feature_context_load_feature_middleware_failed
def test_feature_context_load_feature_middleware_failed(feature_context, services_context):
    """Test that load_feature_middleware raises MIDDLEWARE_LOADING_FAILED on resolution failure."""

    # Configure the resolution handler to fail for the middleware id.
    services_context.get_dependency.side_effect = TiferetError(
        'TEST_ERROR',
        'Middleware not found in services: missing_mw',
    )

    # Assert the structured middleware-loading error is raised.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.load_feature_middleware(['missing_mw'])

    assert exc_info.value.error_code == 'MIDDLEWARE_LOADING_FAILED'
    assert exc_info.value.kwargs.get('service_id') == 'missing_mw'
    assert 'Failed to load middleware: missing_mw' in str(exc_info.value)

# ** test: feature_context_handle_feature_step
def test_feature_context_handle_feature_step(feature_context, test_command):
    """Test handling a command in the FeatureContext."""

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Handle the command using the feature context.
    feature_context.handle_feature_step(test_command, request)
    response = request.handle_response()

    # Assert that the response matches the expected output.
    assert response == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_handle_feature_step_with_error
def test_feature_context_handle_feature_step_with_error(feature_context, test_command):
    """Test handling a command that raises an error in the FeatureContext."""

    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})

    # Attempt to handle the command and catch the raised error.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.handle_feature_step(test_command, request)

    # Assert that the exception message is as expected.
    assert exc_info.value.error_code == 'KEY_NOT_FOUND'
    assert 'No key provided for command execution.' in str(exc_info.value)

# ** test: feature_context_handle_feature_step_with_data_key
def test_feature_context_handle_feature_step_with_data_key(feature_context, test_command):
    """Test handling a command with a data key in the FeatureContext."""

    # Create a mock request with a data key.
    request = RequestContext(data={"key": "value"})

    # Handle the command using the feature context.
    feature_context.handle_feature_step(test_command, request, data_key="response_data")

    # Assert that the response matches the expected output.
    assert request.data.get('response_data') == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_handle_feature_step_with_pass_on_error
def test_feature_context_handle_feature_step_with_pass_on_error(feature_context, test_command):
    """Test handling a command with pass_on_error in the FeatureContext."""

    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})

    # Handle the command with pass_on_error set to True.
    feature_context.handle_feature_step(test_command, request, pass_on_error=True)

    # Assert that the request handled the error without raising an exception.
    assert not request.handle_response()

# ** test: feature_context_execute_feature
def test_feature_context_execute_feature(feature_context, feature):

    # Add a standard feature step with no data key or pass on error.
    feature.steps.append(EventFeatureStep(
        name='Test Command',
        service_id='test_command',
    ))

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the pre-loaded feature using the feature context.
    feature_context.execute_feature(feature, request)

    # Assert that the request handled the response correctly.
    assert request.handle_response() == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_execute_feature_with_request_parameter
def test_feature_context_execute_feature_with_request_parameter(feature_context, feature):
    """Test executing a feature with a request parameter in the FeatureContext."""

    # Add a feature step with a data key and request parameter.
    feature.steps.append(EventFeatureStep(
        name='Test Command',
        service_id='test_command',
        parameters=dict(
            param='$r.key',
        ),
        data_key='response_data',
    ))

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the pre-loaded feature using the feature context with a data key.
    feature_context.execute_feature(feature, request)

    # Assert that the response is stored in the request data under the specified key.
    assert request.data.get('response_data') == {"status": "success", "data": {"key": "value", "param": "value"}}

# ** test: feature_context_evaluate_condition_none_returns_true (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_none_returns_true
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_none_returns_true(feature_context):
    """Test that evaluate_condition returns True when condition is None."""

    # Create a mock request.
    request = RequestContext(data={})

    # Assert that None condition evaluates to True.
    assert feature_context.evaluate_condition(None, request) is True

# ** test: feature_context_evaluate_condition_empty_returns_true (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_empty_returns_true
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_empty_returns_true(feature_context):
    """Test that evaluate_condition returns True when condition is empty."""

    # Create a mock request.
    request = RequestContext(data={})

    # Assert that empty string condition evaluates to True.
    assert feature_context.evaluate_condition('', request) is True
    assert feature_context.evaluate_condition('   ', request) is True

# ** test: feature_context_evaluate_condition_true_expression (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_true_expression
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_true_expression(feature_context):
    """Test that evaluate_condition returns True when expression resolves to True."""

    # Create a request with data for the condition.
    request = RequestContext(data={'x': 5})

    # Assert that the condition evaluates to True.
    assert feature_context.evaluate_condition('$r.x > 0', request) is True

# ** test: feature_context_evaluate_condition_false_expression (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_false_expression
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_false_expression(feature_context):
    """Test that evaluate_condition returns False when expression resolves to False."""

    # Create a request with data for the condition.
    request = RequestContext(data={'x': -1})

    # Assert that the condition evaluates to False.
    assert feature_context.evaluate_condition('$r.x > 0', request) is False

# ** test: feature_context_evaluate_condition_string_equality (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_string_equality
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_string_equality(feature_context):
    """Test that evaluate_condition supports string equality checks."""

    # Create a request with a string value.
    request = RequestContext(data={'mode': 'advanced'})

    # Assert string equality condition evaluates correctly.
    assert feature_context.evaluate_condition("$r.mode == 'advanced'", request) is True
    assert feature_context.evaluate_condition("$r.mode == 'basic'", request) is False

# ** test: feature_context_evaluate_condition_missing_key_returns_false (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_missing_key_returns_false
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_missing_key_returns_false(feature_context):
    """Test that evaluate_condition returns False when a referenced key is missing."""

    # Create a request without the referenced key.
    request = RequestContext(data={})

    # Assert that a condition referencing a missing key evaluates to False.
    assert feature_context.evaluate_condition('$r.x > 0', request) is False

# ** test: feature_context_evaluate_condition_invalid_expression_returns_false (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_evaluate_condition_invalid_expression_returns_false
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_evaluate_condition_invalid_expression_returns_false(feature_context):
    """Test that evaluate_condition returns False on unparseable expressions."""

    # Create a mock request.
    request = RequestContext(data={'x': 5})

    # Assert that an invalid expression evaluates to False (defensive).
    assert feature_context.evaluate_condition('$r.x >>>!!! invalid', request) is False

# ** test: feature_context_resolve_feature_steps_yields_steps
def test_feature_context_resolve_feature_steps_yields_steps(feature_context, feature, test_command):
    """Test that resolve_feature_steps yields (cmd, feature_event, params) for each step."""

    # Add two steps to the feature.
    step_a = EventFeatureStep(name='Step A', service_id='test_command')
    step_b = EventFeatureStep(name='Step B', service_id='test_command')
    feature.steps.extend([step_a, step_b])

    # Create a request.
    request = RequestContext(data={'key': 'value'})

    # Resolve steps from the pre-loaded feature and collect results.
    resolved = list(feature_context.resolve_feature_steps(feature, request))

    # Assert both steps were yielded with the correct command and empty params.
    assert len(resolved) == 2
    assert resolved[0] == (test_command, step_a, {})
    assert resolved[1] == (test_command, step_b, {})

# ** test: feature_context_resolve_feature_steps_skips_false_condition
def test_feature_context_resolve_feature_steps_skips_false_condition(feature_context, feature, test_command):
    """Test that resolve_feature_steps skips steps with false conditions."""

    # Add a skipped step (false condition) and an unconditional step.
    skipped = EventFeatureStep(name='Skipped', service_id='test_command', condition='$r.x > 100')
    executed = EventFeatureStep(name='Executed', service_id='test_command')
    feature.steps.extend([skipped, executed])

    # Create a request where x=5 (fails the condition).
    request = RequestContext(data={'key': 'value', 'x': 5})

    # Resolve and assert only the unconditional step is yielded.
    resolved = list(feature_context.resolve_feature_steps(feature, request))
    assert len(resolved) == 1
    assert resolved[0][1] is executed

# ** test: feature_context_resolve_feature_steps_yields_true_condition
def test_feature_context_resolve_feature_steps_yields_true_condition(feature_context, feature, test_command):
    """Test that resolve_feature_steps yields steps with true conditions."""

    # Add a step with a true condition.
    step = EventFeatureStep(name='Conditional', service_id='test_command', condition='$r.x > 0')
    feature.steps.append(step)

    # Create a request where x=5 (passes the condition).
    request = RequestContext(data={'key': 'value', 'x': 5})

    # Resolve and assert the step is yielded.
    resolved = list(feature_context.resolve_feature_steps(feature, request))
    assert len(resolved) == 1
    assert resolved[0][1] is step

# ** test: feature_context_resolve_feature_steps_parses_parameters
def test_feature_context_resolve_feature_steps_parses_parameters(feature_context, feature, test_command):
    """Test that resolve_feature_steps parses request-backed parameters."""

    # Add a step with a request-backed parameter.
    step = EventFeatureStep(
        name='Parameterized',
        service_id='test_command',
        parameters={'param': '$r.key'},
    )
    feature.steps.append(step)

    # Create a request.
    request = RequestContext(data={'key': 'resolved_value'})

    # Resolve and assert the parameter was parsed.
    resolved = list(feature_context.resolve_feature_steps(feature, request))
    assert len(resolved) == 1
    assert resolved[0][2] == {'param': 'resolved_value'}

# ** test: feature_context_resolve_feature_steps_empty_feature
def test_feature_context_resolve_feature_steps_empty_feature(feature_context, feature):
    """Test that resolve_feature_steps yields nothing for a feature with no steps."""

    # Create a request.
    request = RequestContext(data={'key': 'value'})

    # Resolve and assert nothing is yielded.
    resolved = list(feature_context.resolve_feature_steps(feature, request))
    assert len(resolved) == 0

# ** test: feature_context_execute_feature_with_pass_on_error
def test_feature_context_execute_feature_with_pass_on_error(feature_context, feature):
    """Test executing a feature with pass_on_error in the FeatureContext."""

    # Add a feature step with pass_on_error enabled.
    feature.steps.append(EventFeatureStep(
        name='Test Command',
        service_id='test_command',
        pass_on_error=True,
    ))

    # Create a mock request that will raise an error.
    request = RequestContext(data={'key': None})

    # Execute the pre-loaded feature using the feature context.
    feature_context.execute_feature(feature, request)

    # Assert that the request handled the error without raising an exception.
    assert not request.handle_response()

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

    # Create a mock holder exposing an async get_dependency handler.
    ctx = mock.Mock()
    ctx.get_dependency.return_value = async_test_command
    return ctx

# ** fixture: async_feature_context
@pytest.fixture
def async_feature_context(async_services_context):
    """Fixture to provide an AsyncFeatureContext wired with the async command."""

    return AsyncFeatureContext(get_dependency=async_services_context.get_dependency)

# ** test: feature_context_handle_feature_step_async
@pytest.mark.asyncio
async def test_feature_context_handle_feature_step_async(async_feature_context, async_test_command):
    """Test handling an async command in the FeatureContext."""

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Handle the async command.
    await async_feature_context.handle_feature_step_async(async_test_command, request)
    response = request.handle_response()

    # Assert that the response matches the expected output.
    assert response == {"status": "async_success", "data": {"key": "value"}}

# ** test: feature_context_handle_feature_step_async_with_sync_command
@pytest.mark.asyncio
async def test_feature_context_handle_feature_step_async_with_sync_command(async_feature_context, test_command):
    """Test that handle_feature_step_async correctly dispatches a sync command."""

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Handle a sync command via the async handler.
    await async_feature_context.handle_feature_step_async(test_command, request)
    response = request.handle_response()

    # Assert that the sync command executed correctly.
    assert response == {"status": "success", "data": {"key": "value"}}

# ** test: feature_context_handle_feature_step_async_with_error
@pytest.mark.asyncio
async def test_feature_context_handle_feature_step_async_with_error(async_feature_context, async_test_command):
    """Test handling an async command that raises an error."""

    # Create a request that will cause verify to fail.
    request = RequestContext(data={'key': None})

    # Attempt to handle the command and catch the raised error.
    with pytest.raises(TiferetError) as exc_info:
        await async_feature_context.handle_feature_step_async(async_test_command, request)

    assert exc_info.value.error_code == 'KEY_NOT_FOUND'

# ** test: feature_context_handle_feature_step_async_pass_on_error
@pytest.mark.asyncio
async def test_feature_context_handle_feature_step_async_pass_on_error(async_feature_context, async_test_command):
    """Test handling an async command with pass_on_error."""

    # Create a request that will cause verify to fail.
    request = RequestContext(data={'key': None})

    # Handle with pass_on_error=True.
    await async_feature_context.handle_feature_step_async(async_test_command, request, pass_on_error=True)

    # Assert that the request handled the error without raising.
    assert not request.handle_response()

# ** test: feature_context_execute_feature_async_basic
@pytest.mark.asyncio
async def test_feature_context_execute_feature_async_basic(async_feature_context, feature):
    """Test execute_feature_async with a single async step."""

    # Add an async feature step.
    feature.steps.append(EventFeatureStep(
        name='Async Command',
        service_id='async_test_command',
    ))

    # Create a mock request.
    request = RequestContext(data={"key": "value"})

    # Execute the pre-loaded feature asynchronously.
    await async_feature_context.execute_feature_async(feature, request)

    # Assert the result.
    assert request.handle_response() == {"status": "async_success", "data": {"key": "value"}}

# ** test: feature_context_handle_feature_step_with_middleware
def test_feature_context_handle_feature_step_with_middleware(feature_context, test_command):
    """Test that middleware is applied when provided to handle_feature_step."""

    # Track execution order.
    order = []

    # Define a simple middleware.
    class TrackMiddleware:
        def __call__(self, event, kwargs, next_fn):
            order.append('pre')
            result = next_fn()
            order.append('post')
            return result

    # Create a mock request.
    request = RequestContext(data={'key': 'value'})

    # Handle the command with middleware.
    feature_context.handle_feature_step(
        test_command,
        request,
        middleware=[TrackMiddleware()],
    )

    # Assert middleware ran in correct order and result is correct.
    assert order == ['pre', 'post']
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_feature_with_feature_middleware
def test_feature_context_execute_feature_with_feature_middleware(feature_context, feature):
    """Test execute_feature resolves and applies feature-level middleware."""

    # Track call count.
    call_counts = {'pre': 0, 'post': 0}

    # Define tracking middleware.
    class CountMiddleware:
        def __call__(self, event, kwargs, next_fn):
            call_counts['pre'] += 1
            result = next_fn()
            call_counts['post'] += 1
            return result

    # Wire up the DI context to return the middleware for the middleware service_id.
    mw_instance = CountMiddleware()

    # Add feature-level middleware and a step.
    feature.middleware = ['count_middleware']
    feature.steps.append(EventFeatureStep(
        name='Test Command',
        service_id='test_command',
    ))

    # Resolve the middleware and the test command per service_id.
    def resolve_full(service_id, *flags):
        if service_id == 'count_middleware':
            return mw_instance
        from tiferet.contexts.feature import DomainEvent
        from typing import Any
        class TestEvent(DomainEvent):
            def execute(self, key=None, **kwargs) -> Any:
                return {'status': 'success', 'data': {'key': key}}
        return TestEvent()

    feature_context.get_dependency.side_effect = resolve_full

    request = RequestContext(data={'key': 'value'})

    # Execute the pre-loaded feature.
    feature_context.execute_feature(feature, request)

    # Assert middleware was called once per step.
    assert call_counts['pre'] == 1
    assert call_counts['post'] == 1

# ** test: feature_context_load_feature_middleware_empty
def test_feature_context_load_feature_middleware_empty(feature_context):
    """Test that load_feature_middleware returns empty list for empty input."""

    # Assert empty list returned for no middleware.
    assert feature_context.load_feature_middleware([]) == []
    assert feature_context.load_feature_middleware(None) == []

# ** test: feature_context_load_feature_middleware_resolves_services
def test_feature_context_load_feature_middleware_resolves_services(feature_context, services_context):
    """Test that load_feature_middleware resolves service IDs from the DI context."""

    # Configure the DI context to return a sentinel value.
    sentinel = object()
    services_context.get_dependency.return_value = sentinel

    # Resolve middleware.
    result = feature_context.load_feature_middleware(['mw_a', 'mw_b'])

    # Verify both service IDs were resolved.
    assert len(result) == 2
    assert result[0] is sentinel
    assert result[1] is sentinel

# ** test: feature_context_execute_feature_async_mixed_chain
@pytest.mark.asyncio
async def test_feature_context_execute_feature_async_mixed_chain(feature):
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

    # Mock the resolution handler to return the right command per service_id.
    services = mock.Mock()
    def resolve(service_id, *flags):
        if service_id == 'sync_step':
            return sync_cmd
        return async_cmd
    services.get_dependency.side_effect = resolve

    # Build the async feature context.
    ctx = AsyncFeatureContext(get_dependency=services.get_dependency)

    # Add a sync step followed by an async step.
    feature.steps.append(EventFeatureStep(
        name='Sync Step',
        service_id='sync_step',
        data_key='sync_result',
    ))
    feature.steps.append(EventFeatureStep(
        name='Async Step',
        service_id='async_step',
        data_key='async_result',
    ))

    # Create a request.
    request = RequestContext(data={"key": "mixed"})

    # Execute the pre-loaded feature asynchronously (supports mixed chains).
    await ctx.execute_feature_async(feature, request)

    # Assert both steps executed correctly.
    assert request.data.get('sync_result') == {"sync": True, "key": "mixed"}
    assert request.data.get('async_result') == {"async": True, "key": "mixed"}

# ** test: async_feature_context_subclasses_feature_context
def test_async_feature_context_subclasses_feature_context():
    """Test that AsyncFeatureContext inherits the synchronous FeatureContext helpers."""

    # Assert the inheritance relationship.
    assert issubclass(AsyncFeatureContext, FeatureContext)

    # Assert the shared helpers and sync execution are inherited (not redefined).
    shared = (
        'load_feature_step',
        'load_feature_middleware',
        'handle_feature_step',
        'parse_request_parameter',
        'evaluate_condition',
        'resolve_feature_steps',
        'execute_feature',
    )
    for helper in shared:
        assert getattr(AsyncFeatureContext, helper) is getattr(FeatureContext, helper)

    # Assert the async methods live on AsyncFeatureContext, not on FeatureContext.
    assert hasattr(AsyncFeatureContext, 'handle_feature_step_async')
    assert hasattr(AsyncFeatureContext, 'execute_feature_async')
    assert not hasattr(FeatureContext, 'handle_feature_step_async')
    assert not hasattr(FeatureContext, 'execute_feature_async')

# ** test: feature_context_validate_request_no_schema_is_noop (obsolete)
# -- obsolete: tests the obsolete instance method wrapper; superseded by test_validate_request_no_schema_is_noop
# ++ todo: remove when instance methods are removed at FE2 cleanup
def test_feature_context_validate_request_no_schema_is_noop(feature_context, feature):
    """Test that validate_request leaves data unchanged when no schema is set."""

    # Create a request with raw string data.
    request = RequestContext(data={'a': '5'})

    # Validate against a schema-less feature.
    feature_context.validate_request(feature, request)

    # Assert the data is unchanged.
    assert request.data == {'a': '5'}

# ** test: feature_context_execute_feature_validates_and_coerces
def test_feature_context_execute_feature_validates_and_coerces(feature_context, services_context):
    """Test that execute_feature coerces request data before steps run."""

    # Capture the kwargs the command receives.
    captured = {}

    class CaptureEvent(DomainEvent):
        def execute(self, a=None, b=None, **kwargs):
            captured['a'] = a
            captured['b'] = b
            return {'a': a, 'b': b}

    # Resolve the capturing command for the step.
    services_context.get_dependency.return_value = CaptureEvent()

    # Build a feature with a params schema and a single step.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int', 'b': 'float'},
        steps=[EventFeatureStep(name='cap', service_id='cap')],
    )
    request = RequestContext(data={'a': '5', 'b': '2'})

    # Execute the feature.
    feature_context.execute_feature(feature, request)

    # Assert request data was coerced and the command received coerced values.
    assert request.data['a'] == 5
    assert request.data['b'] == 2.0
    assert captured['a'] == 5
    assert captured['b'] == 2.0

# ** test: feature_context_execute_feature_invalid_request_fails_fast
def test_feature_context_execute_feature_invalid_request_fails_fast(feature_context, services_context):
    """Test that invalid request data fails before any step executes."""

    # Track command executions.
    calls = {'count': 0}

    class CountEvent(DomainEvent):
        def execute(self, **kwargs):
            calls['count'] += 1
            return None

    # Resolve the counting command for the step.
    services_context.get_dependency.return_value = CountEvent()

    # Build a feature whose schema rejects the request.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int'},
        steps=[EventFeatureStep(name='cap', service_id='cap')],
    )
    request = RequestContext(data={'a': 'notint'})

    # Assert the validation error is raised and no command ran.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.execute_feature(feature, request)

    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'

# ** test: feature_context_execute_feature_accepts_flags
def test_feature_context_execute_feature_accepts_flags(feature_context, feature):
    """Test that execute_feature accepts *flags positional arguments without error."""

    # Add a standard step.
    feature.steps.append(EventFeatureStep(name='Test Command', service_id='test_command'))
    request = RequestContext(data={'key': 'value'})

    # Passing flags should not raise and execution should complete normally.
    feature_context.execute_feature(feature, request, 'flag_a', 'flag_b')

    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: async_feature_context_execute_feature_async_accepts_flags
@pytest.mark.asyncio
async def test_async_feature_context_execute_feature_async_accepts_flags(async_feature_context, feature):
    """Test that execute_feature_async accepts *flags positional arguments without error."""

    # Add an async step.
    feature.steps.append(EventFeatureStep(name='Async Command', service_id='async_test_command'))
    request = RequestContext(data={'key': 'value'})

    # Passing flags should not raise and async execution should complete normally.
    await async_feature_context.execute_feature_async(feature, request, 'flag_a', 'flag_b')

    assert request.handle_response() == {'status': 'async_success', 'data': {'key': 'value'}}

# ** test: async_feature_context_execute_feature_async_validates
@pytest.mark.asyncio
async def test_async_feature_context_execute_feature_async_validates(async_services_context):
    """Test that execute_feature_async coerces request data before steps run."""

    # Capture the kwargs the command receives.
    captured = {}

    class CaptureEvent(DomainEvent):
        def execute(self, a=None, **kwargs):
            captured['a'] = a
            return a

    # Resolve the capturing command and build an async context.
    async_services_context.get_dependency.return_value = CaptureEvent()
    ctx = AsyncFeatureContext(get_dependency=async_services_context.get_dependency)

    # Build a feature with a params schema and a single step.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int'},
        steps=[EventFeatureStep(name='cap', service_id='cap')],
    )
    request = RequestContext(data={'a': '7'})

    # Execute the feature asynchronously.
    await ctx.execute_feature_async(feature, request)

    # Assert coercion happened before the step ran.
    assert request.data['a'] == 7
    assert captured['a'] == 7

# ** test: async_feature_context_execute_feature_async_invalid_fails_fast
@pytest.mark.asyncio
async def test_async_feature_context_execute_feature_async_invalid_fails_fast(async_services_context):
    """Test that invalid request data fails before any async step executes."""

    # Track command executions.
    calls = {'count': 0}

    class CountEvent(DomainEvent):
        def execute(self, **kwargs):
            calls['count'] += 1

    # Resolve the counting command and build an async context.
    async_services_context.get_dependency.return_value = CountEvent()
    ctx = AsyncFeatureContext(get_dependency=async_services_context.get_dependency)

    # Build a feature whose schema rejects the request.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int'},
        steps=[EventFeatureStep(name='cap', service_id='cap')],
    )
    request = RequestContext(data={'a': 'bad'})

    # Assert the validation error is raised and no command ran.
    with pytest.raises(TiferetError) as exc_info:
        await ctx.execute_feature_async(feature, request)

    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'
    assert calls['count'] == 0

# ** test: parse_request_parameter_request_ref_success
def test_parse_request_parameter_request_ref_success():
    """Test that parse_request_parameter extracts a $r.-prefixed value from request data."""

    # Create a request containing the referenced key.
    request = RequestContext(data={'key': 'value'})

    # Parse the request-backed parameter.
    result = parse_request_parameter('$r.key', request)

    # Assert the extracted value is returned.
    assert result == 'value'

# ** test: parse_request_parameter_request_not_found
def test_parse_request_parameter_request_not_found():
    """Test that parse_request_parameter raises REQUEST_NOT_FOUND when no request is given."""

    # Assert the structured error is raised when no request is provided.
    with pytest.raises(TiferetError) as exc_info:
        parse_request_parameter('$r.key', None)

    assert exc_info.value.error_code == 'REQUEST_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.key'

# ** test: parse_request_parameter_key_missing
def test_parse_request_parameter_key_missing():
    """Test that parse_request_parameter raises PARAMETER_NOT_FOUND when the key is absent."""

    # Create a request that does not contain the referenced key.
    request = RequestContext(data={})

    # Assert the structured error is raised when the key is missing.
    with pytest.raises(TiferetError) as exc_info:
        parse_request_parameter('$r.missing', request)

    assert exc_info.value.error_code == 'PARAMETER_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.missing'

# ** test: parse_request_parameter_delegates_to_parse_parameter
def test_parse_request_parameter_delegates_to_parse_parameter(monkeypatch):
    """Test that non-$r. parameters are forwarded to ParseParameter.execute."""

    from tiferet.events import static as static_events

    called = {}

    def fake_execute(parameter: str):
        called['parameter'] = parameter
        return 'parsed-value'

    monkeypatch.setattr(static_events.ParseParameter, 'execute', staticmethod(fake_execute))

    # A non-$r. parameter should delegate to ParseParameter.execute.
    result = parse_request_parameter('$env.MY_VAR', RequestContext(data={}))

    assert result == 'parsed-value'
    assert called['parameter'] == '$env.MY_VAR'

# ** test: evaluate_condition_none_returns_true
def test_evaluate_condition_none_returns_true():
    """Test that evaluate_condition returns True when condition is None."""

    request = RequestContext(data={})

    assert evaluate_condition(None, request) is True

# ** test: evaluate_condition_empty_returns_true
def test_evaluate_condition_empty_returns_true():
    """Test that evaluate_condition returns True when condition is empty or blank."""

    request = RequestContext(data={})

    assert evaluate_condition('', request) is True
    assert evaluate_condition('   ', request) is True

# ** test: evaluate_condition_true_expression
def test_evaluate_condition_true_expression():
    """Test that evaluate_condition returns True when the expression resolves to True."""

    request = RequestContext(data={'x': 5})

    assert evaluate_condition('$r.x > 0', request) is True

# ** test: evaluate_condition_false_expression
def test_evaluate_condition_false_expression():
    """Test that evaluate_condition returns False when the expression resolves to False."""

    request = RequestContext(data={'x': -1})

    assert evaluate_condition('$r.x > 0', request) is False

# ** test: evaluate_condition_string_equality
def test_evaluate_condition_string_equality():
    """Test that evaluate_condition handles string equality checks correctly."""

    request = RequestContext(data={'mode': 'advanced'})

    assert evaluate_condition("$r.mode == 'advanced'", request) is True
    assert evaluate_condition("$r.mode == 'basic'", request) is False

# ** test: evaluate_condition_missing_key_returns_false
def test_evaluate_condition_missing_key_returns_false():
    """Test that evaluate_condition returns False when a referenced key is absent."""

    request = RequestContext(data={})

    assert evaluate_condition('$r.x > 0', request) is False

# ** test: evaluate_condition_invalid_expression_returns_false
def test_evaluate_condition_invalid_expression_returns_false():
    """Test that evaluate_condition returns False on an unparseable expression."""

    request = RequestContext(data={'x': 5})

    assert evaluate_condition('$r.x >>>!!! invalid', request) is False

# ** test: validate_request_no_schema_is_noop
def test_validate_request_no_schema_is_noop(feature):
    """Test that validate_request leaves request data unchanged when the feature has no schema."""

    # Create a request with raw string data.
    request = RequestContext(data={'a': '5'})

    # Validate against a schema-less feature.
    validate_request(feature, request)

    # Assert the data is unchanged.
    assert request.data == {'a': '5'}

# ** test: validate_request_coerces_data
def test_validate_request_coerces_data():
    """Test that validate_request coerces request data to the feature's declared types."""

    # Build a feature with an int/float schema.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int', 'b': 'float'},
        steps=[],
    )
    request = RequestContext(data={'a': '5', 'b': '2'})

    # Validate and coerce the request.
    validate_request(feature, request)

    # Assert the data was coerced to the declared types.
    assert request.data['a'] == 5
    assert request.data['b'] == 2.0

# ** test: validate_request_invalid_data_raises
def test_validate_request_invalid_data_raises():
    """Test that validate_request raises REQUEST_VALIDATION_FAILED for type-incompatible data."""

    # Build a feature with an int schema.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int'},
        steps=[],
    )
    request = RequestContext(data={'a': 'notint'})

    # Assert the structured validation error is raised.
    with pytest.raises(TiferetError) as exc_info:
        validate_request(feature, request)

    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'
