"""Tiferet CLI Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet.blueprints.tester import use_tester
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

# ** constant: new_cmd_sample
NEW_CMD_SAMPLE = {
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

# ** tester: CliConfigRepositoryTester
@use_tester(
    type='repo',
    target_cls=CliConfigRepository,
    config_parameter='cli_config',
    equality_fields=['id', 'name'],
    aggregate_cls=CliCommandAggregate,
    aggregate_sample_data=NEW_CMD_SAMPLE,
    exists_cases=[
        (TEST_CMD_ADD_ID, True),
        (TEST_CMD_SUBTRACT_ID, True),
        ('calc.missing', False),
    ],
    get_cases=[
        (TEST_CMD_ADD_ID, {'id': TEST_CMD_ADD_ID, 'name': 'Add Number Command'}),
        ('calc.missing', None),
    ],
    list_ids=[TEST_CMD_ADD_ID, TEST_CMD_SUBTRACT_ID],
    delete_ids=[TEST_CMD_SUBTRACT_ID],
)
class CliConfigRepositoryTester:
    '''CliConfigRepository five-method coverage via RepoTesterContext.'''

    # * test: exists
    def test_exists(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify exists cases against a seeded CLI config.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify get cases against a seeded CLI config.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
        test_ctx.assert_get(repo)

    # * test: list
    def test_list(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify listed identifiers against a seeded CLI config.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
        test_ctx.assert_list(repo)

    # * test: save
    def test_save(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify save round-trips the declared aggregate sample.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
        test_ctx.assert_save(repo)

    # * test: delete
    def test_delete(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify idempotent delete of declared identifiers.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
        test_ctx.assert_delete(repo)

    # * test: get_parent_arguments
    def test_get_parent_arguments(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify parent arguments remain a bespoke CLI method.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
        parent_args = repo.get_parent_arguments()
        assert len(parent_args) == 2
        assert parent_args[0].name_or_flags == ['--verbose', '-v']
        assert parent_args[0].type == 'bool'
        assert parent_args[1].name_or_flags == ['--config', '-c']

    # * test: save_parent_arguments
    def test_save_parent_arguments(self, test_ctx, cli_yaml_file: str) -> None:
        '''Verify parent argument save remains a bespoke CLI method.'''

        repo = test_ctx.make_target(config_file=cli_yaml_file)
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
        repo.save_parent_arguments(new_parent_args)
        reloaded_args = repo.get_parent_arguments()
        assert len(reloaded_args) == 2
        assert reloaded_args[0].name_or_flags == ['--debug', '-d']
        assert reloaded_args[1].name_or_flags == ['--output', '-o']
