# *** imports

# ** core
from typing import Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..settings import DomainEvent, TiferetError

# *** fixtures

# ** fixture: domain_event
@pytest.fixture
def domain_event() -> DomainEvent:
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
def test_execute_not_implemented(domain_event: DomainEvent):
    '''
    Test that execute raises NotImplementedError.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Attempt to call execute, expecting an error
    with pytest.raises(NotImplementedError):
        domain_event.execute()

# ** test: test_raise_error_basic
def test_raise_error_basic(domain_event: DomainEvent):
    '''
    Test raising a TiferetError with basic parameters.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Raise error with code and message, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        domain_event.raise_error('TEST_ERROR', 'An error has occurred.')

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info.value), 'Should include the provided message'

# ** test: test_raise_error_with_args
def test_raise_error_with_args(domain_event: DomainEvent):
    '''
    Test raising a TiferetError with additional arguments.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Raise error with code, message, and args, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        domain_event.raise_error('TEST_ERROR', 'An error has occurred.', arg1='arg1', arg2='arg2')
   
    # Verify error code, message, and additional arguments.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info.value), 'Should include the provided message'
    assert 'arg1' in str(exc_info.value), 'Should include additional argument arg1'
    assert 'arg2' in str(exc_info.value), 'Should include additional argument arg2'

# ** test: test_verify_success
def test_verify_success(domain_event: DomainEvent):
    '''
    Test verify with a true expression.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Verify true expression, expect no error.
    try:
        domain_event.verify(True, 'TEST_ERROR', 'Test message')
    except TiferetError:
        pytest.fail('Verify should not raise an error for true expression')

# ** test: test_verify_failure
def test_verify_failure(domain_event: DomainEvent):
    '''
    Test verify with a false expression.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Verify false expression, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        domain_event.verify(False, 'TEST_ERROR', 'Test message')

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'Test message' in str(exc_info.value), 'Should include the provided message'

# ** test: verify_parameter_success
def test_verify_parameter_success(domain_event: DomainEvent):
    '''
    Test verify_parameter with a valid parameter.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Verify non-empty parameter, expect no error.
    try:
        domain_event.verify_parameter('valid', 'param', 'TestCommand')
    except TiferetError:
        pytest.fail('verify_parameter should not raise an error for valid parameter')

# ** test: verify_parameter_failure
def test_verify_parameter_failure(domain_event: DomainEvent):
    '''
    Test verify_parameter with an invalid parameter.
    
    :param domain_event: The DomainEvent instance to test.
    :type domain_event: DomainEvent
    '''

    # Verify empty parameter, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        domain_event.verify_parameter('', 'param', 'TestCommand')

    # Verify error code and message.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED', 'Should raise error for missing parameter'
    assert exc_info.value.kwargs.get('parameter') == 'param', 'Should include parameter_name in kwargs'
    assert exc_info.value.kwargs.get('command') == 'TestCommand', 'Should include command_name in kwargs'

# ** test: test_handle_command
def test_handle_command(mocker: mock.Mock):
    '''
    Test handle method with a mock domain event.
    
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
   
    # Verify result
    assert result == 'result', 'Should return the command execution result'

    # Verify command instantiation and execution.
    mock_command.assert_called_once_with(dep='value')
    mock_command_instance.execute.assert_called_once_with(arg='test')

# ** test: test_parameters_required_raises_on_missing_param
def test_parameters_required_raises_on_missing_param():
    '''
    Test that the parameter_required decorator raises on a missing parameter.
    '''

    # Define a test event with a decorated execute method.
    class TestEvent(DomainEvent):
        @DomainEvent.parameters_required(['id'])
        def execute(self, id: str = None, **kwargs) -> Any:
            return id

    # Invoke without providing 'id', expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent)

    # Verify error details.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED'
    assert 'id' in exc_info.value.kwargs.get('parameters', [])
    assert exc_info.value.kwargs.get('command') == 'TestEvent'

# ** test: test_parameters_required_raises_on_none_value
def test_parameters_required_raises_on_none_value():
    '''
    Test that the parameter_required decorator raises when a parameter is None.
    '''

    # Define a test event with a decorated execute method.
    class TestEvent(DomainEvent):
        @DomainEvent.parameters_required(['id'])
        def execute(self, id: str = None, **kwargs) -> Any:
            return id

    # Invoke with id=None, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent, id=None)

    # Verify error details.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED'
    assert 'id' in exc_info.value.kwargs.get('parameters', [])

# ** test: test_parameters_required_raises_on_empty_string
def test_parameters_required_raises_on_empty_string():
    '''
    Test that the parameter_required decorator raises on an empty string (after strip).
    '''

    # Define a test event with a decorated execute method.
    class TestEvent(DomainEvent):
        @DomainEvent.parameters_required(['name'])
        def execute(self, name: str = None, **kwargs) -> Any:
            return name

    # Invoke with name='   ', expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent, name='   ')

    # Verify error details.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED'
    assert 'name' in exc_info.value.kwargs.get('parameters', [])

# ** test: test_parameters_required_passes_valid_value
def test_parameters_required_passes_valid_value():
    '''
    Test that the parameter_required decorator passes a valid value through.
    '''

    # Define a test event with a decorated execute method.
    class TestEvent(DomainEvent):
        @DomainEvent.parameters_required(['id'])
        def execute(self, id: str = None, **kwargs) -> Any:
            return id

    # Invoke with a valid id, expect no error.
    result = DomainEvent.handle(TestEvent, id='valid_id')
    assert result == 'valid_id'

# ** test: test_parameters_required_multiple_missing
def test_parameters_required_multiple_missing():
    '''
    Test that the parameter_required decorator collects all missing parameters.
    '''

    # Define a test event with multiple required parameters.
    class TestEvent(DomainEvent):
        @DomainEvent.parameters_required(['id', 'name', 'message'])
        def execute(self, id: str = None, name: str = None, message: str = None, **kwargs) -> Any:
            return id

    # Invoke with all missing, expect TiferetError listing all three.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(TestEvent)

    # Verify all missing parameters are listed.
    missing = exc_info.value.kwargs.get('parameters', [])
    assert 'id' in missing
    assert 'name' in missing
    assert 'message' in missing

# ** test: test_parameters_required_non_string_falsy_passes
def test_parameters_required_non_string_falsy_passes():
    '''
    Test that non-string falsy values (0, [], {}, False) pass validation.
    '''

    # Define a test event with a decorated execute method.
    class TestEvent(DomainEvent):
        @DomainEvent.parameters_required(['count', 'items', 'meta', 'flag'])
        def execute(self, count=None, items=None, meta=None, flag=None, **kwargs) -> Any:
            return {'count': count, 'items': items, 'meta': meta, 'flag': flag}

    # Invoke with falsy non-string values, expect success.
    result = DomainEvent.handle(TestEvent, count=0, items=[], meta={}, flag=False)
    assert result == {'count': 0, 'items': [], 'meta': {}, 'flag': False}

# ** test: test_parameters_required_error_message_content
def test_parameters_required_error_message_content():
    '''
    Test that the error message includes the correct parameter and command names.
    '''

    # Define a test event with a decorated execute method.
    class MySpecialEvent(DomainEvent):
        @DomainEvent.parameters_required(['id'])
        def execute(self, id: str = None, **kwargs) -> Any:
            return id

    # Invoke without providing 'id', expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(MySpecialEvent)

    # Verify error message content.
    assert 'MySpecialEvent' in str(exc_info.value)
    assert exc_info.value.kwargs.get('command') == 'MySpecialEvent'
    assert exc_info.value.kwargs.get('parameters') == ['id']
