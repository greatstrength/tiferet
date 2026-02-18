"""Tiferet CLI Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ...mappers import TransferObject, CliCommandYamlObject
from ...entities import CliCommand, CliArgument, Aggregate
from ..cli import CliYamlRepository

# *** constants

# ** constant: test_command_id_add
TEST_COMMAND_ID_ADD = 'calc.add'

# ** constant: test_command_id_subtract
TEST_COMMAND_ID_SUBTRACT = 'calc.subtract'

# ** constant: cli_data
CLI_DATA = {
    'cli': {
        'cmds': {
            'calc': {
                'add': {
                    'name': 'Add Command',
                    'description': 'Add two numbers',
                    'key': 'add',
                    'group_key': 'calc',
                    'args': [
                        {
                            'name_or_flags': ['--value1'],
                            'description': 'First value',
                            'type': 'float',
                            'required': True
                        },
                        {
                            'name_or_flags': ['--value2'],
                            'description': 'Second value',
                            'type': 'float',
                            'required': True
                        }
                    ]
                },
                'subtract': {
                    'name': 'Subtract Command',
                    'description': 'Subtract two numbers',
                    'key': 'subtract',
                    'group_key': 'calc',
                    'args': [
                        {
                            'name_or_flags': ['--value1'],
                            'description': 'First value',
                            'type': 'float',
                            'required': True
                        },
                        {
                            'name_or_flags': ['--value2'],
                            'description': 'Second value',
                            'type': 'float',
                            'required': True
                        }
                    ]
                }
            }
        },
        'parent_args': [
            {
                'name_or_flags': ['--verbose', '-v'],
                'description': 'Enable verbose output',
                'action': 'store_true'
            },
            {
                'name_or_flags': ['--config', '-c'],
                'description': 'Configuration file path',
                'type': 'str'
            }
        ]
    }
}

# *** fixtures

# ** fixture: cli_config_file
@pytest.fixture
def cli_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the CLI YAML configuration file.

    :return: The CLI YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample CLI configuration content.
    file_path = tmp_path / 'test_cli.yaml'

    # Write the sample CLI configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(CLI_DATA, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: cli_config_repo
@pytest.fixture
def cli_config_repo(cli_config_file: str) -> CliYamlRepository:
    '''
    Fixture to create an instance of the CLI Configuration Repository.

    :param cli_config_file: The CLI YAML configuration file path.
    :type cli_config_file: str
    :return: An instance of CliYamlRepository.
    :rtype: CliYamlRepository
    '''

    # Create and return the CliYamlRepository instance.
    return CliYamlRepository(cli_config_file)

# *** tests

# ** test_int: cli_config_repo_get_commands
def test_int_cli_config_repo_get_commands(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the get_commands method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # List all commands.
    commands = cli_config_repo.get_commands()

    # Check the commands.
    assert commands
    assert len(commands) == 2
    command_ids = [cmd.id for cmd in commands]
    assert TEST_COMMAND_ID_ADD in command_ids
    assert TEST_COMMAND_ID_SUBTRACT in command_ids

# ** test_int: cli_config_repo_get_command
def test_int_cli_config_repo_get_command(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the get_command method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Get the add command.
    add_command = cli_config_repo.get_command(TEST_COMMAND_ID_ADD)

    # Check the add command.
    assert add_command
    assert add_command.id == TEST_COMMAND_ID_ADD
    assert add_command.name == 'Add Command'
    assert add_command.description == 'Add two numbers'
    assert add_command.key == 'add'
    assert add_command.group_key == 'calc'
    assert len(add_command.arguments) == 2
    assert add_command.arguments[0].name_or_flags == ['--value1']
    assert add_command.arguments[0].description == 'First value'
    assert add_command.arguments[0].type == 'float'
    assert add_command.arguments[0].required == True

    # Get the subtract command.
    subtract_command = cli_config_repo.get_command(TEST_COMMAND_ID_SUBTRACT)

    # Check the subtract command.
    assert subtract_command
    assert subtract_command.id == TEST_COMMAND_ID_SUBTRACT
    assert subtract_command.name == 'Subtract Command'

# ** test_int: cli_config_repo_get_command_not_found
def test_int_cli_config_repo_get_command_not_found(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the get_command method of the CliYamlRepository for a non-existent command.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Get a non-existent command.
    command = cli_config_repo.get_command('calc.nonexistent')

    # Check the command.
    assert not command

# ** test_int: cli_config_repo_get_parent_arguments
def test_int_cli_config_repo_get_parent_arguments(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the get_parent_arguments method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Get the parent arguments.
    parent_args = cli_config_repo.get_parent_arguments()

    # Check the parent arguments.
    assert parent_args
    assert len(parent_args) == 2
    assert parent_args[0].name_or_flags == ['--verbose', '-v']
    assert parent_args[0].description == 'Enable verbose output'
    assert parent_args[0].action == 'store_true'
    assert parent_args[1].name_or_flags == ['--config', '-c']
    assert parent_args[1].description == 'Configuration file path'
    assert parent_args[1].type == 'str'

# ** test_int: cli_config_repo_save_command
def test_int_cli_config_repo_save_command(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the save_command method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Create constant for new test command.
    NEW_TEST_COMMAND_ID = 'calc.multiply'

    # Create new command.
    new_command = CliCommand.new(
        group_key='calc',
        key='multiply',
        name='Multiply Command',
        description='Multiply two numbers',
        arguments=[
            ModelObject.new(
                CliArgument,
                name_or_flags=['--value1'],
                description='First value',
                type='float',
                required=True
            ),
            ModelObject.new(
                CliArgument,
                name_or_flags=['--value2'],
                description='Second value',
                type='float',
                required=True
            )
        ]
    )

    # Save the new command.
    cli_config_repo.save_command(new_command)

    # Reload the command to verify the changes.
    saved_command = cli_config_repo.get_command(NEW_TEST_COMMAND_ID)

    # Check the new command.
    assert saved_command
    assert saved_command.id == NEW_TEST_COMMAND_ID
    assert saved_command.name == 'Multiply Command'
    assert saved_command.description == 'Multiply two numbers'
    assert len(saved_command.arguments) == 2
    assert saved_command.arguments[0].name_or_flags == ['--value1']

# ** test_int: cli_config_repo_delete_command
def test_int_cli_config_repo_delete_command(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the delete_command method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Delete an existing command.
    cli_config_repo.delete_command(TEST_COMMAND_ID_SUBTRACT)

    # Attempt to get the deleted command.
    deleted_command = cli_config_repo.get_command(TEST_COMMAND_ID_SUBTRACT)

    # Check that the command is None.
    assert not deleted_command

    # Verify the remaining command still exists.
    remaining_command = cli_config_repo.get_command(TEST_COMMAND_ID_ADD)
    assert remaining_command

# ** test_int: cli_config_repo_delete_command_idempotent
def test_int_cli_config_repo_delete_command_idempotent(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test that delete_command is idempotent (can delete non-existent command).

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Delete a non-existent command (should not raise an error).
    cli_config_repo.delete_command('calc.nonexistent')

    # Verify existing commands are still intact.
    commands = cli_config_repo.get_commands()
    assert len(commands) == 2

# ** test_int: cli_config_repo_save_parent_arguments
def test_int_cli_config_repo_save_parent_arguments(
        cli_config_repo: CliYamlRepository,
    ):
    '''
    Test the save_parent_arguments method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Create new parent arguments.
    new_parent_args = [
        ModelObject.new(
            CliArgument,
            name_or_flags=['--debug', '-d'],
            description='Enable debug mode',
            action='store_true'
        ),
        ModelObject.new(
            CliArgument,
            name_or_flags=['--output', '-o'],
            description='Output file path',
            type='str',
            required=True
        )
    ]

    # Save the new parent arguments.
    cli_config_repo.save_parent_arguments(new_parent_args)

    # Reload the parent arguments to verify the changes.
    saved_parent_args = cli_config_repo.get_parent_arguments()

    # Check the new parent arguments.
    assert saved_parent_args
    assert len(saved_parent_args) == 2
    assert saved_parent_args[0].name_or_flags == ['--debug', '-d']
    assert saved_parent_args[0].description == 'Enable debug mode'
    assert saved_parent_args[1].name_or_flags == ['--output', '-o']
    assert saved_parent_args[1].description == 'Output file path'
    assert saved_parent_args[1].required == True
