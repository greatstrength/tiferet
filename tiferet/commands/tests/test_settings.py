# *** imports

# ** infra
import pytest

# ** app
from ..settings import *
from ...models.settings import *


# *** classes

# ** class: test_model
class TestModel(ValueObject):

    # * attribute: test_attribute
    test_attribute = StringType(
        required=True,
        metadata=dict(
            description='The test attribute.'
        )
    )

# ** class: test_service_command
class TestCommand(Command):
    '''
    A test service command class.
    '''

    def execute(self, param1: str, param2: str, throw_error: bool = False, error_args: List[str] = [], **kwargs) -> Tuple[str, str]:

        # Throw an error if requested.
        if error_args:
            self.verify(throw_error == False, 'TEST_FORMATTED_ERROR',
                        'An error occurred: {}', *error_args)
        else:
            self.verify(throw_error == False,
                        'TEST_ERROR', 'An error occurred.')

        # Return the result.
        return (param1, param2)


# *** fixtures

# ** fixture: test_service_command
@pytest.fixture
def test_service_command() -> Command:
    '''
    A test service command fixture.
    '''

    return TestCommand()


# *** tests

# ** test: test_service_command_execute
def test_service_command_execute(test_service_command):
    '''
    Test the service command execute method.
    '''

    # Execute the command.
    result: Command = test_service_command.execute('param1', 'param2')

    # Verify the result.
    assert result == ('param1', 'param2')


# ** test: test_service_command_execute_with_error
def test_service_command_execute_with_error(test_service_command):
    '''
    Test the service command execute method with an error.
    '''

    # Execute the command.
    with pytest.raises(TiferetError) as e:
        test_service_command.execute('param1', 'param2', throw_error=True)

    # Verify the error.
    assert e.value.error_code == 'TEST_ERROR'

    # Execute the command with error arguments.
    with pytest.raises(TiferetError) as e:
        test_service_command.execute(
            'param1', 'param2', throw_error=True, error_args=['arg1', 'arg2'])

    # Verify the error.
    assert e.value.error_code == 'TEST_FORMATTED_ERROR'


# ** test: handle_command
def test_handle_command():
    '''
    Test the handle command method.
    '''

    # Handle the command.
    result = Command.handle(
        TestCommand,
        param1='param1',
        param2='param2'
    )

    # Verify the result.
    assert result == ('param1', 'param2')
