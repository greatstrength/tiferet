"""Tiferet CLI Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict, List

# ** infra
import pytest, yaml

# ** app
from ...mappers import (
    TransferObject,
    CliArgumentAggregate,
    CliCommandYamlObject,
)
from ..cli import CliYamlRepository


# *** constants

# ** constant: test_cmd_add_id
TEST_CMD_ADD_ID = 'calc.add'

# ** constant: test_cmd_subtract_id
TEST_CMD_SUBTRACT_ID = 'calc.subtract'

# ** constant: cli_data
CLI_DATA: Dict = {
    'cli': {
        'cmds': {
            'calc': {
                'add': {
                    'name': 'Add Number Command',
                    'description': 'Adds two numbers.',
                    'key': 'add',
                    'group_key': 'calc',
                    'args': [
                        {
                            'name_or_flags': ['--value1', '-v1'],
                            'description': 'The first number to add.',
                            'type': 'str',
                        },
                        {
                            'name_or_flags': ['--value2', '-v2'],
                            'description': 'The second number to add.',
                            'type': 'str',
                        },
                    ],
                },
                'subtract': {
                    'name': 'Subtract Number Command',
                    'description': 'Subtracts one number from another.',
                    'key': 'subtract',
                    'group_key': 'calc',
                    'args': [
                        {
                            'name_or_flags': ['--value1', '-v1'],
                            'description': 'The number to subtract from.',
                            'type': 'str',
                        },
                        {
                            'name_or_flags': ['--value2', '-v2'],
                            'description': 'The number to subtract.',
                            'type': 'str',
                        },
                    ],
                },
            },
        },
        'parent_args': [
            {
                'name_or_flags': ['--verbose', '-v'],
                'description': 'Enable verbose output.',
                'action': 'store_true',
            },
            {
                'name_or_flags': ['--config', '-c'],
                'description': 'Path to configuration file.',
                'type': 'str',
            },
        ],
    },
}

# *** fixtures

# ** fixture: cli_yaml_file
@pytest.fixture
def cli_yaml_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the CLI YAML configuration file.

    :return: The CLI YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample CLI configuration content.
    file_path = tmp_path / 'test_cli.yaml'

    # Write the sample CLI configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(CLI_DATA, yaml_file)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: cli_config_repo
@pytest.fixture
def cli_config_repo(cli_yaml_file: str) -> CliYamlRepository:
    '''
    Fixture to create an instance of the CLI Configuration Repository.

    :param cli_yaml_file: The CLI YAML configuration file path.
    :type cli_yaml_file: str
    :return: An instance of CliYamlRepository.
    :rtype: CliYamlRepository
    '''

    # Create and return the CliYamlRepository instance.
    return CliYamlRepository(cli_yaml_file)

# *** tests

# ** test_int: cli_config_repo_list
def test_int_cli_config_repo_list(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the list method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # List all CLI commands.
    commands = cli_config_repo.list()

    # Check the commands.
    assert commands
    assert len(commands) == 2
    command_ids = [cmd.id for cmd in commands]
    assert TEST_CMD_ADD_ID in command_ids
    assert TEST_CMD_SUBTRACT_ID in command_ids

# ** test_int: cli_config_repo_get
def test_int_cli_config_repo_get(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the get method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Get a CLI command by id.
    cmd = cli_config_repo.get(TEST_CMD_ADD_ID)

    # Check the command fields.
    assert cmd
    assert cmd.id == TEST_CMD_ADD_ID
    assert cmd.name == 'Add Number Command'
    assert cmd.description == 'Adds two numbers.'
    assert cmd.key == 'add'
    assert cmd.group_key == 'calc'

    # Check the nested arguments.
    assert len(cmd.arguments) == 2
    assert cmd.arguments[0].name_or_flags == ['--value1', '-v1']
    assert cmd.arguments[0].description == 'The first number to add.'
    assert cmd.arguments[1].name_or_flags == ['--value2', '-v2']
    assert cmd.arguments[1].description == 'The second number to add.'

# ** test_int: cli_config_repo_get_not_found
def test_int_cli_config_repo_get_not_found(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the get method of the CliYamlRepository for a non-existent command.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Attempt to get a non-existent CLI command.
    cmd = cli_config_repo.get('calc.missing')

    # Check that the command is None.
    assert not cmd

# ** test_int: cli_config_repo_get_parent_arguments
def test_int_cli_config_repo_get_parent_arguments(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the get_parent_arguments method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Get all parent-level CLI arguments.
    parent_args = cli_config_repo.get_parent_arguments()

    # Check the parent arguments.
    assert parent_args
    assert len(parent_args) == 2
    assert parent_args[0].name_or_flags == ['--verbose', '-v']
    assert parent_args[0].description == 'Enable verbose output.'
    assert parent_args[0].action == 'store_true'
    assert parent_args[1].name_or_flags == ['--config', '-c']
    assert parent_args[1].description == 'Path to configuration file.'

# ** test_int: cli_config_repo_save
def test_int_cli_config_repo_save(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the save method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Create constant for new test CLI command.
    new_cmd_id = 'calc.multiply'

    # Create new CLI command config data and map to an aggregate.
    cmd = TransferObject.from_data(
        CliCommandYamlObject,
        id=new_cmd_id,
        name='Multiply Number Command',
        description='Multiplies two numbers.',
        key='multiply',
        group_key='calc',
        args=[
            {
                'name_or_flags': ['--value1', '-v1'],
                'description': 'The first number to multiply.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--value2', '-v2'],
                'description': 'The second number to multiply.',
                'type': 'str',
            },
        ],
    ).map()

    # Save the new CLI command.
    cli_config_repo.save(cmd)

    # Reload the CLI command to verify it was saved.
    new_cmd = cli_config_repo.get(new_cmd_id)

    # Check the new CLI command.
    assert new_cmd
    assert new_cmd.id == new_cmd_id
    assert new_cmd.name == 'Multiply Number Command'
    assert new_cmd.description == 'Multiplies two numbers.'
    assert len(new_cmd.arguments) == 2

# ** test_int: cli_config_repo_delete
def test_int_cli_config_repo_delete(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the delete method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Delete an existing CLI command.
    cli_config_repo.delete(TEST_CMD_SUBTRACT_ID)

    # Attempt to get the deleted CLI command.
    deleted_cmd = cli_config_repo.get(TEST_CMD_SUBTRACT_ID)

    # Check that the CLI command is None.
    assert not deleted_cmd

    # Verify the remaining command still exists.
    remaining_cmd = cli_config_repo.get(TEST_CMD_ADD_ID)
    assert remaining_cmd
    assert remaining_cmd.id == TEST_CMD_ADD_ID

# ** test_int: cli_config_repo_delete_idempotent
def test_int_cli_config_repo_delete_idempotent(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the delete method of the CliYamlRepository for idempotent behavior.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Delete a non-existent CLI command (should not raise).
    cli_config_repo.delete('calc.missing')

    # Verify existing commands are unaffected.
    commands = cli_config_repo.list()
    assert len(commands) == 2

# ** test_int: cli_config_repo_save_parent_arguments
def test_int_cli_config_repo_save_parent_arguments(
        cli_config_repo: CliYamlRepository,
    ) -> None:
    '''
    Test the save_parent_arguments method of the CliYamlRepository.

    :param cli_config_repo: The CLI configuration repository.
    :type cli_config_repo: CliYamlRepository
    '''

    # Create new parent arguments.
    new_parent_args = [
        CliArgumentAggregate.new(
            name_or_flags=['--debug', '-d'],
            description='Enable debug mode.',
            action='store_true',
        ),
        CliArgumentAggregate.new(
            name_or_flags=['--output', '-o'],
            description='Output file path.',
            type='str',
        ),
    ]

    # Save the new parent arguments.
    cli_config_repo.save_parent_arguments(new_parent_args)

    # Reload parent arguments to verify they were saved.
    reloaded_args = cli_config_repo.get_parent_arguments()

    # Check the reloaded parent arguments.
    assert reloaded_args
    assert len(reloaded_args) == 2
    assert reloaded_args[0].name_or_flags == ['--debug', '-d']
    assert reloaded_args[0].description == 'Enable debug mode.'
    assert reloaded_args[0].action == 'store_true'
    assert reloaded_args[1].name_or_flags == ['--output', '-o']
    assert reloaded_args[1].description == 'Output file path.'
