# *** imports

# ** infra
import pytest

# ** app
from ..core import *
from ...models import ValueObject
from ...contexts.container import DependencyImportFailureError


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
                self.verify(throw_error == False, 'MY_FORMATTED_ERROR', 'An error occurred: {}', *error_args)
            else:
                self.verify(throw_error == False, 'MY_ERROR', 'An error occurred.')

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
    with pytest.raises(TiferetError) as e:
        test_service_command.execute('param1', 'param2', throw_error=True)
    
    # Verify the error.
    assert e.value.error_code == 'MY_ERROR'

    # Execute the command with error arguments.
    with pytest.raises(TiferetError) as e:
        test_service_command.execute('param1', 'param2', throw_error=True, error_args=['arg1', 'arg2'])

    # Verify the error.
    assert e.value.error_code == 'MY_FORMATTED_ERROR'


# ** test: test_create_model_object
def test_create_model_object():
    '''
    Test the create model object command.
    '''

    # Create a command object.
    command = CreateModelObject()

    # Execute the command.
    result: TestModel = command.execute('tiferet.commands.tests.test_core', 'TestModel', test_attribute='test')

    # Verify the result.
    assert result.test_attribute == 'test'


# ** test: test_create_model_object_invalid_import_path
def test_create_model_object_invalid_import_path():
    '''
    Test the create model object command with an invalid module import path.
    '''

    # Create a command object.
    command = CreateModelObject()

    # Execute the command.
    with pytest.raises(InvalidModelObject) as e:
        command.execute('invalid.module.path', 'TestModel', test_attribute='test')

        # Verify the error.
        assert e.value.error_code == 'INVALID_MODEL_OBJECT'