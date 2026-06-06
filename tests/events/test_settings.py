# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.settings import DomainEvent, AsyncDomainEvent, TiferetError

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

# ** test: test_async_execute_not_implemented
@pytest.mark.asyncio
async def test_async_execute_not_implemented():
    '''
    Test that AsyncDomainEvent.execute raises NotImplementedError.
    '''

    # Create an AsyncDomainEvent instance and attempt to call execute.
    event = AsyncDomainEvent()
    with pytest.raises(NotImplementedError):
        await event.execute()

# ** test: test_async_execute_returns_result
@pytest.mark.asyncio
async def test_async_execute_returns_result():
    '''
    Test that a concrete AsyncDomainEvent returns a result.
    '''

    # Define a concrete async event.
    class AddAsync(AsyncDomainEvent):
        async def execute(self, a=0, b=0, **kwargs):
            return a + b

    # Execute and verify the result.
    event = AddAsync()
    result = await event.execute(a=3, b=4)
    assert result == 7, 'Should return the sum'

# ** test: test_async_verify_success
@pytest.mark.asyncio
async def test_async_verify_success():
    '''
    Test that verify works correctly in an async event context.
    '''

    # Define a concrete async event that uses verify.
    class VerifyAsync(AsyncDomainEvent):
        async def execute(self, value=None, **kwargs):
            self.verify(value is not None, 'VALUE_REQUIRED', 'Value is required.')
            return value

    # Execute with a valid value, expect no error.
    event = VerifyAsync()
    result = await event.execute(value='hello')
    assert result == 'hello', 'Should return the value'

# ** test: test_async_verify_failure
@pytest.mark.asyncio
async def test_async_verify_failure():
    '''
    Test that verify raises TiferetError in an async event context.
    '''

    # Define a concrete async event that uses verify.
    class VerifyAsync(AsyncDomainEvent):
        async def execute(self, value=None, **kwargs):
            self.verify(value is not None, 'VALUE_REQUIRED', 'Value is required.')
            return value

    # Execute with None, expect TiferetError.
    event = VerifyAsync()
    with pytest.raises(TiferetError) as exc_info:
        await event.execute(value=None)
    assert exc_info.value.error_code == 'VALUE_REQUIRED', 'Should raise with correct error code'

# ** test: test_handle_async_basic
@pytest.mark.asyncio
async def test_handle_async_basic():
    '''
    Test handle_async with a concrete async event.
    '''

    # Define a concrete async event.
    class MultiplyAsync(AsyncDomainEvent):
        async def execute(self, a=0, b=0, **kwargs):
            return a * b

    # Handle via the static async method.
    result = await DomainEvent.handle_async(MultiplyAsync, a=5, b=6)
    assert result == 30, 'Should return the product'

# ** test: test_handle_async_with_dependencies
@pytest.mark.asyncio
async def test_handle_async_with_dependencies(mocker: mock.Mock):
    '''
    Test handle_async with injected dependencies.

    :param mocker: The mocker fixture.
    :type mocker: mock.Mock
    '''

    # Create a mock service dependency.
    mock_service = mocker()
    mock_service.fetch.return_value = 'fetched'

    # Define an async event with a dependency.
    class FetchAsync(AsyncDomainEvent):
        def __init__(self, service):
            self.service = service

        async def execute(self, key=None, **kwargs):
            return self.service.fetch(key)

    # Handle via handle_async.
    result = await DomainEvent.handle_async(
        FetchAsync,
        dependencies={'service': mock_service},
        key='test_key'
    )
    assert result == 'fetched', 'Should return the fetched value'
    mock_service.fetch.assert_called_once_with('test_key')

# ** test: test_parameters_required_async_raises_on_missing
@pytest.mark.asyncio
async def test_parameters_required_async_raises_on_missing():
    '''
    Test that parameters_required raises on a missing parameter for an async event.
    '''

    # Define an async event with parameters_required.
    class AsyncRequiredEvent(AsyncDomainEvent):

        @DomainEvent.parameters_required(['id'])
        async def execute(self, **kwargs):
            return 'ok'

    # Handle without required parameter, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        await DomainEvent.handle_async(AsyncRequiredEvent, id=None)
    assert 'id' in exc_info.value.kwargs.get('parameters', []), 'Should list missing parameter'
    assert exc_info.value.kwargs.get('command') == 'AsyncRequiredEvent', 'Should include the command name'

# ** test: test_parameters_required_async_passes_valid
@pytest.mark.asyncio
async def test_parameters_required_async_passes_valid():
    '''
    Test that parameters_required passes for a valid async event invocation.
    '''

    # Define an async event with parameters_required.
    class AsyncRequiredEvent(AsyncDomainEvent):

        @DomainEvent.parameters_required(['id'])
        async def execute(self, **kwargs):
            return 'ok'

    # Handle with a valid value, expect success.
    result = await DomainEvent.handle_async(AsyncRequiredEvent, id='valid')
    assert result == 'ok', 'Should return the execution result'

# ** test: test_parameters_required_async_multiple_missing
@pytest.mark.asyncio
async def test_parameters_required_async_multiple_missing():
    '''
    Test that parameters_required collects all violations for an async event.
    '''

    # Define an async event with multiple required parameters.
    class AsyncMultiEvent(AsyncDomainEvent):

        @DomainEvent.parameters_required(['id', 'name', 'value'])
        async def execute(self, **kwargs):
            return 'ok'

    # Handle with all parameters missing or invalid, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        await DomainEvent.handle_async(AsyncMultiEvent, name=None, value='  ')

    # Verify all three parameters are collected.
    missing = exc_info.value.kwargs.get('parameters', [])
    assert 'id' in missing, 'Should list missing parameter id'
    assert 'name' in missing, 'Should list None parameter name'
    assert 'value' in missing, 'Should list empty string parameter value'
    assert len(missing) == 3, 'Should collect exactly three violations'

# ** test: test_async_domain_event_inherits_domain_event
def test_async_domain_event_inherits_domain_event():
    '''
    Test that AsyncDomainEvent is a subclass of DomainEvent.
    '''

    # Verify inheritance.
    assert issubclass(AsyncDomainEvent, DomainEvent), 'AsyncDomainEvent should extend DomainEvent'

    # Verify instance check.
    event = AsyncDomainEvent()
    assert isinstance(event, DomainEvent), 'AsyncDomainEvent instance should be a DomainEvent'
