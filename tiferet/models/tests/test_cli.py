# *** imports

# ** infra
import pytest

# ** app
from ..cli import *

# *** fixtures

# ** fixture: cli_argument
@pytest.fixture
def cli_argument() -> CliArgument:
    '''
    Fixture to provide a sample CLI argument for testing.
    This argument is used to test the CLI argument model.
    '''
    return ModelObject.new(
        CliArgument,
        name_or_flags=['--test-arg', '-t'],
        description='A test argument for CLI commands.',
        required=True,
        type='str'
    )

# ** fixture: cli_command
@pytest.fixture
def cli_command() -> CliCommand:
    '''
    Fixture to provide a sample CLI command for testing.
    This command is used to test the CLI command model.
    '''
    return CliCommand.new(
        group_key='test-group',
        key='test-feature',
        name='Test Feature Command',
        description='A command for testing CLI features.',
        arguments=[
            ModelObject.new(
                CliArgument,
                name_or_flags=['--arg1', '-a'],
                description='An argument for the test command.',
                required=True,
                type='str'
            )
        ]
    )

# *** tests

# ** test: cli_argument_get_type_str
def test_cli_argument_get_type_str(cli_argument: CliArgument):
    '''
    Test the get_type method of a CLI argument with a string type.
    '''
    # Get the type of the CLI argument.
    arg_type = cli_argument.get_type()
    
    # Assert that the type is 'str'.
    assert arg_type == str

# ** test: cli_argument_get_type_int
def test_cli_argument_get_type_int(cli_argument: CliArgument):
    '''
    Test the get_type method of a CLI argument with an integer type.
    '''
    # Change the type of the CLI argument to 'int'.
    cli_argument.type = 'int'
    
    # Get the type of the CLI argument.
    arg_type = cli_argument.get_type()
    
    # Assert that the type is 'int'.
    assert arg_type == int

# ** test: cli_argument_get_type_float
def test_cli_argument_get_type_float(cli_argument: CliArgument):
    '''
    Test the get_type method of a CLI argument with a float type.
    '''
    # Change the type of the CLI argument to 'float'.
    cli_argument.type = 'float'
    
    # Get the type of the CLI argument.
    arg_type = cli_argument.get_type()
    
    # Assert that the type is 'float'.
    assert arg_type == float

# ** test: cli_argument_get_type_none
def test_cli_argument_get_type_none(cli_argument: CliArgument):
    '''
    Test the get_type method of a CLI argument with no type specified.
    '''
    # Change the type of the CLI argument to None.
    cli_argument.type = None
    
    # Get the type of the CLI argument.
    arg_type = cli_argument.get_type()
    
    # Assert that the type is 'str' by default.
    assert arg_type == str

# ** test: cli_command_new
def test_cli_command_new(cli_command: CliCommand):
    '''
    Test the creation of a CLI command with the new method.
    '''
    assert cli_command.id == 'test_group.test_feature'

# ** test: cli_command_has_argument
def test_cli_command_has_argument(cli_command: CliCommand):
    '''
    Test that a CLI command can check for an argument.
    '''
    assert cli_command.has_argument(['-a', '--arg1'])
    assert not cli_command.has_argument(['-b', '--arg2'])

# ** test: cli_command_add_argument
def test_cli_command_add_argument(cli_command: CliCommand):
    '''
    Test that a CLI command can add an argument.
    '''
    # Create a new argument.
    new_argument = ModelObject.new(
        CliArgument,
        name_or_flags=['--new-arg', '-n'],
        description='A new argument for the command.',
        required=False,
        type='str'
    )
    
    # Add the new argument to the command.
    cli_command.add_argument(new_argument)
    
    # Assert that the new argument is now part of the command's arguments.
    assert cli_command.has_argument(['-n', '--new-arg'])