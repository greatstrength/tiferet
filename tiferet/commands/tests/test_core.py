# *** imports

# ** infra
import pytest

# ** app
from ..core import *


# *** fixtures

# ** fixture: test_service_command
@pytest.fixture
def test_service_command() -> ServiceCommand:
    '''
    A test service command fixture.
    '''
    class TestServiceCommand(ServiceCommand):
        '''
        A test service command class.
        '''
        
        def execute(self, param1: str, param2: str, throw_error: bool = False, error_args: List[str] = [], **kwargs) -> Tuple[str, str]:

            # Throw an error if requested.
            if error_args:
                self.verify(throw_error == False, 'MY_FORMATTED_ERROR', *error_args)
            else:
                self.verify(throw_error == False, 'MY_ERROR')

            # Return the result.
            return (param1, param2)
        
    return TestServiceCommand()


# *** tests

# ** test: test_service_command_execute
def test_service_command_execute(test_service_command):
    '''
    Test the service command execute method.
    '''

    # Execute the command.
    result: ServiceCommand = test_service_command.execute('param1', 'param2')

    # Verify the result.
    assert result == ('param1', 'param2')


# ** test: test_service_command_execute_with_error
def test_service_command_execute_with_error(test_service_command):
    '''
    Test the service command execute method with an error.
    '''

    # Execute the command.
    with pytest.raises(AssertionError):
        test_service_command.execute('param1', 'param2', throw_error=True)

    # Verify the error message.
    try:
        test_service_command.execute('param1', 'param2', throw_error=True)
    except AssertionError as e:
        assert str(e) == 'MY_ERROR'

    # Execute the command with formatted error.
    try:
        test_service_command.execute('param1', 'param2', throw_error=True, error_args=['err_arg1', 'err_arg2'])
    except AssertionError as e:
        assert str(e) == 'MY_FORMATTED_ERROR: err_arg1, err_arg2'