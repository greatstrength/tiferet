# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..settings import DomainEvent, TiferetError

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
