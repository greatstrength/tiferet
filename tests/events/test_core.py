"""Tiferet Event Core Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.core import DomainEvent, AsyncDomainEvent, TiferetError

# *** fixtures

# ** fixture: event
@pytest.fixture
def event() -> DomainEvent:
    '''
    Fixture to provide a fresh DomainEvent instance.

    :return: A DomainEvent instance.
    :rtype: DomainEvent
    '''

    # Return the DomainEvent instance.
    return DomainEvent()

# ** fixture: mocker
@pytest.fixture
def mocker() -> mock.Mock:
    '''
    Fixture to provide a mocker type for testing.

    :return: A mocker type.
    :rtype: mock.Mock
    '''

    # Return the mocker type.
    return mock.Mock

# *** tests

# ** test: test_execute_not_implemented
def test_execute_not_implemented(event: DomainEvent):
    '''
    Test that execute raises NotImplementedError.

    :param event: The DomainEvent instance to test.
    :type event: DomainEvent
    '''

    # Attempt to call execute, expecting an error.
    with pytest.raises(NotImplementedError):
        event.execute()

# ** test: test_raise_error_basic
def test_raise_error_basic():
    '''
    Test raising a TiferetError with basic parameters.
    '''

    # Raise error with code and message, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.raise_error('TEST_ERROR', 'An error has occurred.')

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info.value), 'Should include the provided message'

# ** test: test_raise_error_with_args
def test_raise_error_with_args():
    '''
    Test raising a TiferetError with additional arguments.
    '''

    # Raise error with code, message, and args, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.raise_error('TEST_ERROR', 'An error has occurred.', arg1='arg1', arg2='arg2')

    # Verify error code, message, and additional arguments.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info.value), 'Should include the provided message'
    assert exc_info.value.kwargs.get('arg1') == 'arg1', 'Should include additional argument arg1'
    assert exc_info.value.kwargs.get('arg2') == 'arg2', 'Should include additional argument arg2'

# ** test: test_verify_success
def test_verify_success(event: DomainEvent):
    '''
    Test verify with a true expression.

    :param event: The DomainEvent instance to test.
    :type event: DomainEvent
    '''

    # Verify true expression, expect no error.
    try:
        event.verify(True, 'TEST_ERROR', 'Test message')
    except TiferetError:
        pytest.fail('Verify should not raise an error for true expression')

# ** test: test_verify_failure
def test_verify_failure(event: DomainEvent):
    '''
    Test verify with a false expression.

    :param event: The DomainEvent instance to test.
    :type event: DomainEvent
    '''

    # Verify false expression, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        event.verify(False, 'TEST_ERROR', 'Test message')

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'Test message' in str(exc_info.value), 'Should include the provided message'

# ** test: test_handle_command
def test_handle_command(mocker: mock.Mock):
    '''
    Test handle method with a mock command.

    :param mocker: The mocker fixture.
    :type mocker: mock.Mock
    '''

    # Create mock command instance and set execute return value.
    mock_command_instance = mocker()
    mock_command_instance.execute.return_value = 'result'

    # Create mock command returning the instance.
    mock_command = mocker(return_value=mock_command_instance)

    # Call handle with dependencies and arguments.
    result = DomainEvent.handle(mock_command, dependencies={'dep': 'value'}, arg='test')

    # Verify result.
    assert result == 'result', 'Should return the event execution result'

    # Verify command instantiation and execution.
    mock_command.assert_called_once_with(dep='value')
    mock_command_instance.execute.assert_called_once_with(arg='test')

# ** test: test_parameters_required_raises_on_missing_param
def test_parameters_required_raises_on_missing_param():
    '''
    Test that parameters_required raises on a missing parameter.
    '''

    # Define a test event with parameters_required decorator.
    class TestEvent(DomainEvent):

        @DomainEvent.parameters_required(['id'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute without the required parameter, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent, id=None)

    # Verify the error contains the missing parameter.
    assert 'id' in exc_info.value.kwargs.get('parameters', []), 'Should list missing parameter'
    assert exc_info.value.kwargs.get('command') == 'TestEvent', 'Should include the command name'

# ** test: test_parameters_required_raises_on_none_value
def test_parameters_required_raises_on_none_value():
    '''
    Test that parameters_required raises when a parameter value is None.
    '''

    # Define a test event with parameters_required decorator.
    class TestEvent(DomainEvent):

        @DomainEvent.parameters_required(['name'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute with None value, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent, name=None)

    # Verify the error contains the None parameter.
    assert 'name' in exc_info.value.kwargs.get('parameters', []), 'Should list None parameter'

# ** test: test_parameters_required_raises_on_empty_string
def test_parameters_required_raises_on_empty_string():
    '''
    Test that parameters_required raises when a parameter is an empty/whitespace string.
    '''

    # Define a test event with parameters_required decorator.
    class TestEvent(DomainEvent):

        @DomainEvent.parameters_required(['name'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute with whitespace-only string, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent, name='   ')

    # Verify the error contains the empty string parameter.
    assert 'name' in exc_info.value.kwargs.get('parameters', []), 'Should list empty string parameter'

# ** test: test_parameters_required_passes_valid_value
def test_parameters_required_passes_valid_value():
    '''
    Test that parameters_required passes when a valid string value is provided.
    '''

    # Define a test event with parameters_required decorator.
    class TestEvent(DomainEvent):

        @DomainEvent.parameters_required(['id'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute with a valid value, expect success.
    result = DomainEvent.handle(TestEvent, id='valid_id')
    assert result == 'ok', 'Should return the execution result'

# ** test: test_parameters_required_multiple_missing
def test_parameters_required_multiple_missing():
    '''
    Test that parameters_required collects all violations in a single error.
    '''

    # Define a test event with multiple required parameters.
    class TestEvent(DomainEvent):

        @DomainEvent.parameters_required(['id', 'name', 'value'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute with all parameters missing or invalid, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent, name=None, value='  ')

    # Verify all three parameters are collected in a single error.
    missing = exc_info.value.kwargs.get('parameters', [])
    assert 'id' in missing, 'Should list missing parameter id'
    assert 'name' in missing, 'Should list None parameter name'
    assert 'value' in missing, 'Should list empty string parameter value'
    assert len(missing) == 3, 'Should collect exactly three violations'

# ** test: test_parameters_required_non_string_falsy_passes
def test_parameters_required_non_string_falsy_passes():
    '''
    Test that non-string falsy values (0, [], {}, False) pass validation.
    '''

    # Define a test event with parameters_required decorator.
    class TestEvent(DomainEvent):

        @DomainEvent.parameters_required(['a', 'b', 'c', 'd'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute with falsy-but-valid non-string values, expect success.
    result = DomainEvent.handle(TestEvent, a=0, b=[], c={}, d=False)
    assert result == 'ok', 'Should accept non-string falsy values'

# ** test: test_parameters_required_error_message_content
def test_parameters_required_error_message_content():
    '''
    Test that the error kwargs contain the correct command name and parameters list.
    '''

    # Define a test event with parameters_required decorator.
    class MyCustomEvent(DomainEvent):

        @DomainEvent.parameters_required(['id', 'name'])
        def execute(self, **kwargs):
            return 'ok'

    # Execute without required parameters, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(MyCustomEvent)

    # Verify error kwargs contain the correct command and parameters.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED', 'Should use correct error code'
    assert exc_info.value.kwargs.get('command') == 'MyCustomEvent', 'Should include the event class name'
    assert exc_info.value.kwargs.get('parameters') == ['id', 'name'], 'Should list all missing parameters'

# ** test: test_async_domain_event_is_subclass
def test_async_domain_event_is_subclass():
    '''
    Test that AsyncDomainEvent is a subclass of DomainEvent.
    '''

    # AsyncDomainEvent should extend DomainEvent.
    assert issubclass(AsyncDomainEvent, DomainEvent), 'AsyncDomainEvent should subclass DomainEvent'

# ** test: test_async_execute_not_implemented
@pytest.mark.asyncio
async def test_async_execute_not_implemented():
    '''
    Test that the base AsyncDomainEvent.execute raises NotImplementedError.
    '''

    # Instantiate the base async event.
    event = AsyncDomainEvent()

    # Awaiting the base execute should raise NotImplementedError.
    with pytest.raises(NotImplementedError):
        await event.execute()

# ** test: test_async_execute_returns_result
@pytest.mark.asyncio
async def test_async_execute_returns_result():
    '''
    Test that a concrete async execute returns its result.
    '''

    # Define a concrete async event.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            return 'async_result'

    # Awaiting execute should return the result.
    result = await AsyncEvent().execute()
    assert result == 'async_result', 'Concrete async execute should return its result'

# ** test: test_async_verify_success
@pytest.mark.asyncio
async def test_async_verify_success():
    '''
    Test that verify passes for a true expression in an async context.
    '''

    # Define an async event that verifies a true expression.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            self.verify(True, 'TEST_ERROR', 'Should not raise')
            return 'ok'

    # Awaiting execute should return the result without raising.
    result = await AsyncEvent().execute()
    assert result == 'ok', 'verify should not raise for a true expression in async context'

# ** test: test_async_verify_failure
@pytest.mark.asyncio
async def test_async_verify_failure():
    '''
    Test that verify raises a TiferetError for a false expression in an async context.
    '''

    # Define an async event that verifies a false expression.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            self.verify(False, 'TEST_ERROR', 'Async failure')
            return 'ok'

    # Awaiting execute should raise a structured error.
    with pytest.raises(TiferetError) as exc_info:
        await AsyncEvent().execute()

    # Verify the error code is propagated.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise with the correct error code'

# ** test: test_handle_async_without_dependencies
@pytest.mark.asyncio
async def test_handle_async_without_dependencies():
    '''
    Test handle_async instantiates and awaits an event with no dependencies.
    '''

    # Define a concrete async event.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, value, **kwargs):
            return value * 2

    # handle_async should await execute and return the result.
    result = await DomainEvent.handle_async(AsyncEvent, value=21)
    assert result == 42, 'handle_async should await and return the event result'

# ** test: test_handle_async_with_dependencies
@pytest.mark.asyncio
async def test_handle_async_with_dependencies():
    '''
    Test handle_async injects dependencies before awaiting execute.
    '''

    # Define an async event that depends on an injected service.
    class AsyncEvent(AsyncDomainEvent):
        def __init__(self, service):
            self.service = service

        async def execute(self, **kwargs):
            return self.service

    # handle_async should inject the dependency and return it.
    result = await DomainEvent.handle_async(AsyncEvent, dependencies={'service': 'injected'})
    assert result == 'injected', 'handle_async should inject dependencies'

# ** test: test_async_parameters_required_missing
@pytest.mark.asyncio
async def test_async_parameters_required_missing():
    '''
    Test parameters_required raises on a missing param for an async execute.
    '''

    # Define an async event with a required parameter.
    class AsyncEvent(AsyncDomainEvent):

        @DomainEvent.parameters_required(['id'])
        async def execute(self, **kwargs):
            return 'ok'

    # Awaiting handle_async without the param should raise.
    with pytest.raises(TiferetError) as exc_info:
        await DomainEvent.handle_async(AsyncEvent, id=None)

    # Verify the missing parameter is reported.
    assert 'id' in exc_info.value.kwargs.get('parameters', []), 'Should list the missing parameter'

# ** test: test_async_parameters_required_valid
@pytest.mark.asyncio
async def test_async_parameters_required_valid():
    '''
    Test parameters_required passes a valid value for an async execute.
    '''

    # Define an async event with a required parameter.
    class AsyncEvent(AsyncDomainEvent):

        @DomainEvent.parameters_required(['id'])
        async def execute(self, **kwargs):
            return 'ok'

    # Awaiting handle_async with a valid value should succeed.
    result = await DomainEvent.handle_async(AsyncEvent, id='valid')
    assert result == 'ok', 'Should return the execution result for a valid value'

# ** test: test_async_parameters_required_multiple_missing
@pytest.mark.asyncio
async def test_async_parameters_required_multiple_missing():
    '''
    Test parameters_required collects all violations for an async execute.
    '''

    # Define an async event with multiple required parameters.
    class AsyncEvent(AsyncDomainEvent):

        @DomainEvent.parameters_required(['id', 'name', 'value'])
        async def execute(self, **kwargs):
            return 'ok'

    # Awaiting handle_async with all invalid should aggregate violations.
    with pytest.raises(TiferetError) as exc_info:
        await DomainEvent.handle_async(AsyncEvent, name=None, value='  ')

    # Verify all three violations are collected in order.
    missing = exc_info.value.kwargs.get('parameters', [])
    assert missing == ['id', 'name', 'value'], 'Should collect all three violations in order'

# ** test: test_handle_no_middleware_unchanged
def test_handle_no_middleware_unchanged():
    '''
    Test that handle with no middleware behaves like a plain execute.
    '''

    # Define a simple event.
    class Event(DomainEvent):
        def execute(self, **kwargs):
            return 'base'

    # Both None and empty middleware should preserve base behavior.
    assert DomainEvent.handle(Event) == 'base', 'No middleware should preserve base behavior'
    assert DomainEvent.handle(Event, middleware=[]) == 'base', 'Empty middleware should preserve base behavior'

# ** test: test_handle_single_middleware_order
def test_handle_single_middleware_order():
    '''
    Test a single middleware wraps execution with pre/execute/post ordering.
    '''

    # Track the execution order.
    calls = []

    # Define an event that records its execution.
    class Event(DomainEvent):
        def execute(self, **kwargs):
            calls.append('execute')
            return 'result'

    # Define a middleware recording pre/post around next_fn.
    def middleware(event, kwargs, next_fn):
        calls.append('pre')
        result = next_fn()
        calls.append('post')
        return result

    # Handle with the single middleware.
    result = DomainEvent.handle(Event, middleware=[middleware])

    # The result should pass through with pre/execute/post ordering.
    assert result == 'result', 'Middleware should return the event result'
    assert calls == ['pre', 'execute', 'post'], 'Order should be pre, execute, post'

# ** test: test_handle_multiple_middleware_outermost_first
def test_handle_multiple_middleware_outermost_first():
    '''
    Test multiple middleware compose outermost-first.
    '''

    # Track the execution order.
    calls = []

    # Define an event that records its execution.
    class Event(DomainEvent):
        def execute(self, **kwargs):
            calls.append('execute')
            return 'result'

    # Build labeled middleware recording entry/exit.
    def make_mw(label):
        def mw(event, kwargs, next_fn):
            calls.append(f'{label}:pre')
            result = next_fn()
            calls.append(f'{label}:post')
            return result
        return mw

    # Handle with two middleware; the first entry is the outermost wrapper.
    result = DomainEvent.handle(Event, middleware=[make_mw('outer'), make_mw('inner')])

    # Outermost-first: outer wraps inner wraps execute.
    assert result == 'result'
    assert calls == ['outer:pre', 'inner:pre', 'execute', 'inner:post', 'outer:post'], \
        'First list entry should be the outermost wrapper'

# ** test: test_handle_middleware_argument_capture
def test_handle_middleware_argument_capture():
    '''
    Test middleware receives the event instance and execution kwargs.
    '''

    # Capture the arguments passed to the middleware.
    captured = {}

    # Define an event.
    class Event(DomainEvent):
        def execute(self, **kwargs):
            return 'result'

    # Define a middleware capturing the event and kwargs.
    def middleware(event, kwargs, next_fn):
        captured['event'] = event
        captured['kwargs'] = kwargs
        return next_fn()

    # Handle with execution kwargs.
    DomainEvent.handle(Event, middleware=[middleware], a=1, b='two')

    # The middleware should see the event instance and the merged kwargs.
    assert isinstance(captured['event'], Event), 'Middleware should receive the event instance'
    assert captured['kwargs'] == {'a': 1, 'b': 'two'}, 'Middleware should receive the execution kwargs'

# ** test: test_handle_middleware_exception_interception
def test_handle_middleware_exception_interception():
    '''
    Test middleware can intercept exceptions raised by the event.
    '''

    # Define an event that raises.
    class Event(DomainEvent):
        def execute(self, **kwargs):
            raise ValueError('boom')

    # Define a middleware that intercepts the exception.
    def middleware(event, kwargs, next_fn):
        try:
            return next_fn()
        except ValueError:
            return 'intercepted'

    # The middleware should swallow the error and return its fallback.
    result = DomainEvent.handle(Event, middleware=[middleware])
    assert result == 'intercepted', 'Middleware should be able to intercept exceptions'

# ** test: test_handle_async_no_middleware_unchanged
@pytest.mark.asyncio
async def test_handle_async_no_middleware_unchanged():
    '''
    Test that handle_async with no middleware awaits the base execute.
    '''

    # Define a concrete async event.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            return 'base'

    # Both None and empty middleware should preserve base behavior.
    assert await DomainEvent.handle_async(AsyncEvent) == 'base'
    assert await DomainEvent.handle_async(AsyncEvent, middleware=[]) == 'base'

# ** test: test_handle_async_single_middleware_order
@pytest.mark.asyncio
async def test_handle_async_single_middleware_order():
    '''
    Test a single async middleware wraps async execution in order.
    '''

    # Track the execution order.
    calls = []

    # Define an async event.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            calls.append('execute')
            return 'result'

    # Define an async middleware awaiting next_fn.
    class Middleware:
        async def __call__(self, event, kwargs, next_fn):
            calls.append('pre')
            result = await next_fn()
            calls.append('post')
            return result

    # Handle with the single async middleware.
    result = await DomainEvent.handle_async(AsyncEvent, middleware=[Middleware()])

    # The result should pass through with pre/execute/post ordering.
    assert result == 'result'
    assert calls == ['pre', 'execute', 'post']

# ** test: test_handle_async_multiple_middleware_outermost_first
@pytest.mark.asyncio
async def test_handle_async_multiple_middleware_outermost_first():
    '''
    Test multiple async middleware compose outermost-first.
    '''

    # Track the execution order.
    calls = []

    # Define an async event.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            calls.append('execute')
            return 'result'

    # Build labeled async middleware.
    def make_mw(label):
        class Middleware:
            async def __call__(self, event, kwargs, next_fn):
                calls.append(f'{label}:pre')
                result = await next_fn()
                calls.append(f'{label}:post')
                return result
        return Middleware()

    # Handle with two async middleware; the first entry is the outermost wrapper.
    result = await DomainEvent.handle_async(AsyncEvent, middleware=[make_mw('outer'), make_mw('inner')])

    # Outermost-first ordering.
    assert result == 'result'
    assert calls == ['outer:pre', 'inner:pre', 'execute', 'inner:post', 'outer:post']

# ** test: test_handle_async_passthrough_sync_middleware
@pytest.mark.asyncio
async def test_handle_async_passthrough_sync_middleware():
    '''
    Test that pass-through synchronous middleware composes under handle_async.

    A sync middleware that returns ``next_fn()`` without awaiting it composes
    correctly because the async runner awaits the returned coroutine; only
    sync middleware that inspects or transforms the result cannot do so.
    '''

    # Track the execution order.
    calls = []

    # Define an async event.
    class AsyncEvent(AsyncDomainEvent):
        async def execute(self, **kwargs):
            calls.append('execute')
            return 'result'

    # Define a synchronous pass-through middleware returning next_fn() directly.
    def middleware(event, kwargs, next_fn):
        calls.append('pre')
        return next_fn()

    # Handle with the synchronous pass-through middleware.
    result = await DomainEvent.handle_async(AsyncEvent, middleware=[middleware])

    # The async runner awaits the returned coroutine, so the value passes through.
    assert result == 'result', 'Pass-through sync middleware should compose under handle_async'
    assert calls == ['pre', 'execute'], 'Sync pass-through middleware should run before execute'
