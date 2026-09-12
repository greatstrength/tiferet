"""Tiferet CLI Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet import use_tester
from tiferet.mappers import (
    CliArgumentAggregate,
    CliCommandAggregate,
)
from tiferet.repos.cli import CliConfigRepository

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
                'type': 'bool',
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

# *** testers

# ** tester: test_cli_config_repository
@use_tester(
    type='repo',
    target_cls=CliConfigRepository,
    config_parameter='cli_config',
    sample_data={
    },
    equality_fields=[
        'id',
        'name',
    ],
    aggregate_cls=CliCommandAggregate,
    aggregate_sample_data={
        'id': 'calc.multiply',
        'name': 'Multiply Number Command',
        'description': 'Multiplies two numbers.',
        'key': 'multiply',
        'group_key': 'calc',
        'arguments': [
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
    },
    get_cases=[
        (TEST_CMD_ADD_ID, {
            'id': TEST_CMD_ADD_ID,
            'name': 'Add Number Command',
        }),
        (TEST_CMD_SUBTRACT_ID, {
            'id': TEST_CMD_SUBTRACT_ID,
            'name': 'Subtract Number Command',
        }),
        ('calc.missing', None),
    ],
    list_ids=[
        TEST_CMD_ADD_ID,
        TEST_CMD_SUBTRACT_ID,
    ],
    delete_ids=[
        TEST_CMD_SUBTRACT_ID,
    ],
)
class TestCliConfigRepository:
    '''
    Tests for CliConfigRepository using the repo tester.
    '''

    # * test: get
    def test_get(self, test_ctx, cli_yaml_file: str) -> None:
        '''
        Test the get method of the CliConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param cli_yaml_file: The CLI YAML configuration file path.
        :type cli_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=cli_yaml_file)

        # Assert get cases against the seeded ids.
        test_ctx.assert_get(repo)

        # Check nested fields on the add command.
        cmd = repo.get(TEST_CMD_ADD_ID)
        assert cmd.description == 'Adds two numbers.'
        assert cmd.key == 'add'
        assert cmd.group_key == 'calc'
        assert len(cmd.arguments) == 2
        assert cmd.arguments[0].name_or_flags == ['--value1', '-v1']
        assert cmd.arguments[0].description == 'The first number to add.'
        assert cmd.arguments[1].name_or_flags == ['--value2', '-v2']
        assert cmd.arguments[1].description == 'The second number to add.'

    # * test: list
    def test_list(self, test_ctx, cli_yaml_file: str) -> None:
        '''
        Test the list method of the CliConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param cli_yaml_file: The CLI YAML configuration file path.
        :type cli_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=cli_yaml_file)

        # Assert unfiltered list ids.
        test_ctx.assert_list(repo)

    # * test: get_parent_arguments
    def test_get_parent_arguments(self, test_ctx, cli_yaml_file: str) -> None:
        '''
        Test the get_parent_arguments method of the CliConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param cli_yaml_file: The CLI YAML configuration file path.
        :type cli_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=cli_yaml_file)

        # Get all parent-level CLI arguments.
        parent_args = repo.get_parent_arguments()

        # Check the parent arguments.
        assert parent_args
        assert len(parent_args) == 2
        assert parent_args[0].name_or_flags == ['--verbose', '-v']
        assert parent_args[0].description == 'Enable verbose output.'
        assert parent_args[0].type == 'bool'
        assert parent_args[1].name_or_flags == ['--config', '-c']
        assert parent_args[1].description == 'Path to configuration file.'

    # * test: save
    def test_save(self, test_ctx, cli_yaml_file: str) -> None:
        '''
        Test the save method of the CliConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param cli_yaml_file: The CLI YAML configuration file path.
        :type cli_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=cli_yaml_file)

        # Assert save persists the aggregate sample.
        test_ctx.assert_save(repo)

        # Check nested fields on the saved command.
        new_cmd = repo.get('calc.multiply')
        assert new_cmd.description == 'Multiplies two numbers.'
        assert len(new_cmd.arguments) == 2

    # * test: delete
    def test_delete(self, test_ctx, cli_yaml_file: str) -> None:
        '''
        Test the delete method of the CliConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param cli_yaml_file: The CLI YAML configuration file path.
        :type cli_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=cli_yaml_file)

        # Assert delete removes the id and is idempotent.
        test_ctx.assert_delete(repo)

        # Verify the remaining command still exists.
        remaining_cmd = repo.get(TEST_CMD_ADD_ID)
        assert remaining_cmd
        assert remaining_cmd.id == TEST_CMD_ADD_ID

    # * test: save_parent_arguments
    def test_save_parent_arguments(self, test_ctx, cli_yaml_file: str) -> None:
        '''
        Test the save_parent_arguments method of the CliConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param cli_yaml_file: The CLI YAML configuration file path.
        :type cli_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=cli_yaml_file)

        # Create new parent arguments.
        new_parent_args = [
            CliArgumentAggregate(
                name_or_flags=['--debug', '-d'],
                description='Enable debug mode.',
                type='bool',
            ),
            CliArgumentAggregate(
                name_or_flags=['--output', '-o'],
                description='Output file path.',
                type='str',
            ),
        ]

        # Save the new parent arguments.
        repo.save_parent_arguments(new_parent_args)

        # Reload parent arguments to verify they were saved.
        reloaded_args = repo.get_parent_arguments()

        # Check the reloaded parent arguments.
        assert reloaded_args
        assert len(reloaded_args) == 2
        assert reloaded_args[0].name_or_flags == ['--debug', '-d']
        assert reloaded_args[0].description == 'Enable debug mode.'
        assert reloaded_args[0].type == 'bool'
        assert reloaded_args[1].name_or_flags == ['--output', '-o']
        assert reloaded_args[1].description == 'Output file path.'
