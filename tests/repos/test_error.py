"""Tiferet Error Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.mappers import ErrorAggregate
from tiferet.repos.error import ErrorConfigRepository

# *** constants

# ** constant: test_error_code
TEST_ERROR_CODE = 'TEST_ERROR_CODE'

# ** constant: test_formatted_error_code
TEST_FORMATTED_ERROR_CODE = 'TEST_FORMATTED_ERROR_CODE'

# ** constant: error_data
ERROR_DATA: Dict = {
    'errors': {
        TEST_ERROR_CODE: {
            'name': 'Test Error',
            'message': [
                {
                    'lang': 'en',
                    'text': 'A test error occurred',
                },
                {
                    'lang': 'es',
                    'text': 'Ocurrió un error de prueba',
                },
            ],
        },
        TEST_FORMATTED_ERROR_CODE: {
            'name': 'Test Formatted Error',
            'message': [
                {
                    'lang': 'en',
                    'text': 'Error for {item_name}',
                },
                {
                    'lang': 'es',
                    'text': 'Error para {item_name}',
                },
            ],
        },
    },
}

# ** constant: new_error_sample
NEW_ERROR_SAMPLE = {
    'id': 'NEW_ERROR_CODE',
    'name': 'New Error',
    'message': [
        {
            'lang': 'en',
            'text': 'A new error occurred',
        },
        {
            'lang': 'es',
            'text': 'Ocurrió un nuevo error',
        },
    ],
}

# *** fixtures

# ** fixture: error_yaml_file
@pytest.fixture
def error_yaml_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the error YAML configuration file.

    :return: The error YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample error configuration content.
    file_path = tmp_path / 'test_error.yaml'

    # Write the sample error configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(ERROR_DATA, yaml_file)

    # Return the file path as a string.
    return str(file_path)

# *** testers

# ** tester: ErrorConfigRepositoryTester
@use_tester(
    type='repo',
    target_cls=ErrorConfigRepository,
    config_parameter='error_config',
    equality_fields=['id', 'name'],
    aggregate_cls=ErrorAggregate,
    aggregate_sample_data=NEW_ERROR_SAMPLE,
    exists_cases=[
        (TEST_ERROR_CODE, True),
        (TEST_FORMATTED_ERROR_CODE, True),
        ('MISSING_ERROR_CODE', False),
    ],
    get_cases=[
        (TEST_ERROR_CODE, {'id': TEST_ERROR_CODE, 'name': 'Test Error'}),
        (
            TEST_FORMATTED_ERROR_CODE,
            {'id': TEST_FORMATTED_ERROR_CODE, 'name': 'Test Formatted Error'},
        ),
        ('MISSING_ERROR_CODE', None),
    ],
    list_ids=[TEST_ERROR_CODE, TEST_FORMATTED_ERROR_CODE],
    delete_ids=[TEST_FORMATTED_ERROR_CODE],
)
class ErrorConfigRepositoryTester:
    '''ErrorConfigRepository five-method coverage via RepoTesterContext.'''

    # * test: exists
    def test_exists(self, test_ctx, error_yaml_file: str) -> None:
        '''Verify exists cases against a seeded error config.'''

        repo = test_ctx.make_target(config_file=error_yaml_file)
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, error_yaml_file: str) -> None:
        '''Verify get cases against a seeded error config.'''

        repo = test_ctx.make_target(config_file=error_yaml_file)
        test_ctx.assert_get(repo)

    # * test: list
    def test_list(self, test_ctx, error_yaml_file: str) -> None:
        '''Verify listed identifiers against a seeded error config.'''

        repo = test_ctx.make_target(config_file=error_yaml_file)
        test_ctx.assert_list(repo)

    # * test: save
    def test_save(self, test_ctx, error_yaml_file: str) -> None:
        '''Verify save round-trips the declared aggregate sample.'''

        repo = test_ctx.make_target(config_file=error_yaml_file)
        test_ctx.assert_save(repo)

    # * test: delete
    def test_delete(self, test_ctx, error_yaml_file: str) -> None:
        '''Verify idempotent delete of declared identifiers.'''

        repo = test_ctx.make_target(config_file=error_yaml_file)
        test_ctx.assert_delete(repo)

    # * test: new
    def test_new(self, test_ctx, error_yaml_file: str) -> None:
        '''Verify repository construction and default_role.'''

        test_ctx.assert_new(config_file=error_yaml_file)

    # * test: format_dispatch
    def test_format_dispatch(self, test_ctx, tmp_path) -> None:
        '''Verify YAML and JSON payload round-trip.'''

        yaml_file = tmp_path / 'dispatch.yaml'
        json_file = tmp_path / 'dispatch.json'
        yaml_file.write_text('root: {}\n', encoding='utf-8')
        json_file.write_text('{"root": {}}\n', encoding='utf-8')
        test_ctx.assert_format_dispatch(str(yaml_file), str(json_file))
