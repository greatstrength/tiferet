# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..settings import Command, TiferetError


# *** fixtures

# ** fixture: command
@pytest.fixture
def command():
    '''Fixture to provide a fresh Command instance.'''
    return Command()


# ** fixture: mocker
@pytest.fixture
def mocker():
    '''Fixture to provide a mocker type for testing.'''
    return mock.Mock


# *** tests

# ** test: test_execute_not_implemented
def test_execute_not_implemented(command):
    '''Test that execute raises NotImplementedError.'''

    # Attempt to call execute, expecting an error
    with pytest.raises(NotImplementedError):
        command.execute()

# ** test: test_raise_error_basic
def test_raise_error_basic():
    '''Test raising a TiferetError with basic parameters.'''

    # Raise error with code and message, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.raise_error('TEST_ERROR', 'An error has occurred.')

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info.value), 'Should include the provided message'

# ** test: test_raise_error_with_args
def test_raise_error_with_args():
    '''Test raising a TiferetError with additional arguments.'''

    # Raise error with code, message, and args, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        Command.raise_error('TEST_ERROR', 'An error has occurred.', 'arg1', 'arg2')
   
    # Verify error code, message, and additional arguments.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info.value), 'Should include the provided message'
    assert 'arg1' in str(exc_info.value), 'Should include additional argument arg1'
    assert 'arg2' in str(exc_info.value), 'Should include additional argument arg2'

# ** test: test_verify_success
def test_verify_success(command):
    '''Test verify with a true expression.'''

    # Verify true expression, expect no error.
    try:
        command.verify(True, 'TEST_ERROR', 'Test message')
    except TiferetError:
        pytest.fail('Verify should not raise an error for true expression')

# ** test: test_verify_failure
def test_verify_failure(command):
    '''Test verify with a false expression.'''

    # Verify false expression, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        command.verify(False, 'TEST_ERROR', 'Test message')

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'Test message' in str(exc_info.value), 'Should include the provided message'

# ** test: test_handle_command
def test_handle_command(mocker):
    '''Test handle method with a mock command.'''

    # Create mock command instance and set execute return value.
    mock_command_instance = mocker()
    mock_command_instance.execute.return_value = 'result'

    # Create mock command returning the instance.
    mock_command = mocker(return_value=mock_command_instance)

    # Call handle with dependencies and arguments.
    result = Command.handle(mock_command, dependencies={'dep': 'value'}, arg='test')
   
    # Verify result
    assert result == 'result', 'Should return the command execution result'

    # Verify command instantiation and execution.
    mock_command.assert_called_once_with(dep='value')
    mock_command_instance.execute.assert_called_once_with(arg='test')
