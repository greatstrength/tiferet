# *** imports

# ** core
import sys

# ** infra
import pytest
from unittest import mock

# ** app
from ..cli import CliHandler, CliRepository
from ...models.cli import *

# *** fixtures

# ** fixture: cli_commands
@pytest.fixture
def cli_commands():
    '''
    Fixture to provide a mock CLI commands list.
    This data is used to test the CLI handler's ability to process commands.
    '''
    # Create a mock command map with some sample commands.
    return [
        CliCommand.new(
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
    ]

# ** fixture: parent_arguments
@pytest.fixture
def parent_arguments():
    '''
    Fixture to provide a mock parent arguments map.
    This is used to test the CLI handler's ability to retrieve parent arguments.
    '''
    # Create a mock parent arguments map with some sample arguments.
    return [
        ModelObject.new(
            CliArgument,
            name_or_flags=['--parent-arg1', '-p1'],
            description='A parent argument for the test group.',
            type='str'
        )
    ]

# ** fixture: cli_repo
@pytest.fixture
def cli_repo(cli_commands, parent_arguments):
    '''
    Fixture to provide a mock CLI repository.
    This is used to test the CLI handler without needing a real repository.
    '''
    cli_repo = mock.Mock(spec=CliRepository)
    cli_repo.get_commands.return_value = cli_commands
    cli_repo.get_parent_arguments.return_value = parent_arguments
    return cli_repo

# ** fixture: cli_handler
@pytest.fixture
def cli_handler(cli_repo):
    '''
    Fixture to create an instance of the CLI handler.
    This handler is used to process CLI requests and commands.
    '''
    return CliHandler(cli_repo=cli_repo)

# *** tests

# ** test: get_commands
def test_get_commands(cli_handler, cli_commands):
    '''
    Test the CLI handler's ability to retrieve commands.
    This checks if the handler correctly returns the commands from the repository.
    '''
    # Call the get_commands method.
    commands = cli_handler.get_commands()
    
    # Assert that the returned commands match the mock commands.
    assert commands
    assert 'test-group' in commands
    assert len(commands['test-group']) == len(cli_commands)
    # Check that the first command in the group matches the mock command.
    assert commands['test-group'][0].id == cli_commands[0].id
    assert commands['test-group'][0].name == cli_commands[0].name
    assert commands['test-group'][0].group_key == cli_commands[0].group_key
    assert commands['test-group'][0].key == cli_commands[0].key

# ** test: parse_arguments
def test_parse_arguments(cli_handler: CliHandler, cli_commands, parent_arguments):
    '''
    Test the CLI handler's ability to parse command line arguments.
    This checks if the handler correctly creates an argument parser and parses the commands.
    '''
    # Get the commands mapped by group from the CLI handler.
    commands = cli_handler.get_commands()
    
    # Add system arguments to simulate command line input.
    sys.argv = ['test_script.py', 'test-group', 'test-feature', '--arg1', 'value1', '-p1', 'parent_value']
    
    # Call the parse_arguments method with the mock commands.
    parsed_args = cli_handler.parse_arguments(commands)
    
    # Assert that the parsed arguments are not empty.
    assert parsed_args
    assert 'group' in parsed_args
    assert parsed_args['group'] == 'test-group'
    assert 'command' in parsed_args
    assert parsed_args['command'] == 'test-feature'
    assert 'arg1' in parsed_args
    assert parsed_args['arg1'] == 'value1'
    assert 'parent_arg1' in parsed_args
    assert parsed_args['parent_arg1'] == 'parent_value'