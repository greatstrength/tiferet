# *** imports

# ** infra
import pytest

# ** app
from ..settings import Command, TiferetError

# *** fixtures

# ** fixture: command
@pytest.fixture
def command() -> Command:
    '''
    Fixture to provide a fresh Command instance.
    
    :return: A Command instance.
    :rtype: Command
    '''

    # Return the Command instance.
    return Command()

# *** tests

# ** test: verify_parameter_success
def test_verify_parameter_success(command: Command):
    '''
    Test verify_parameter with a valid parameter.
    
    :param command: The Command instance to test.
    :type command: Command
    '''

    # Verify non-empty parameter, expect no error.
    try:
        command.verify_parameter('valid', 'param', 'TestCommand')
    except TiferetError:
        pytest.fail('verify_parameter should not raise an error for valid parameter')

# ** test: verify_parameter_failure
def test_verify_parameter_failure(command: Command):
    '''
    Test verify_parameter with an invalid parameter.
    
    :param command: The Command instance to test.
    :type command: Command
    '''

    # Verify empty parameter, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        command.verify_parameter('', 'param', 'TestCommand')

    # Verify error code and message.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED', 'Should raise error for missing parameter'
    assert exc_info.value.kwargs.get('parameter') == 'param', 'Should include parameter_name in kwargs'
    assert exc_info.value.kwargs.get('command') == 'TestCommand', 'Should include command_name in kwargs'
