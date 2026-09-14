"""Tiferet Error Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet import use_tester
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

# ** tester: test_error_config_repository
@use_tester(
    type='repo',
    target_cls=ErrorConfigRepository,
    config_parameter='error_config',
    sample_data={
    },
    equality_fields=[
        'id',
        'name',
    ],
    aggregate_cls=ErrorAggregate,
    aggregate_sample_data={
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
    },
    exists_cases=[
        (TEST_ERROR_CODE, True),
        (TEST_FORMATTED_ERROR_CODE, True),
        ('MISSING_ERROR_CODE', False),
    ],
    get_cases=[
        (TEST_ERROR_CODE, {
            'id': TEST_ERROR_CODE,
            'name': 'Test Error',
        }),
        (TEST_FORMATTED_ERROR_CODE, {
            'id': TEST_FORMATTED_ERROR_CODE,
            'name': 'Test Formatted Error',
        }),
        ('MISSING_ERROR_CODE', None),
    ],
    list_ids=[
        TEST_ERROR_CODE,
        TEST_FORMATTED_ERROR_CODE,
    ],
    delete_ids=[
        TEST_FORMATTED_ERROR_CODE,
    ],
)
class TestErrorConfigRepository:
    '''
    Tests for ErrorConfigRepository using the repo tester.
    '''

    # * test: exists
    def test_exists(self, test_ctx, error_yaml_file: str) -> None:
        '''
        Test the exists method of the ErrorConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param error_yaml_file: The error YAML configuration file path.
        :type error_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=error_yaml_file)

        # Assert exists cases against the seeded ids.
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, error_yaml_file: str) -> None:
        '''
        Test the get method of the ErrorConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param error_yaml_file: The error YAML configuration file path.
        :type error_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=error_yaml_file)

        # Assert get cases against the seeded ids.
        test_ctx.assert_get(repo)

        # Check nested messages on the seeded errors.
        error = repo.get(TEST_ERROR_CODE)
        assert len(error.message) == 2
        assert error.message[0].lang == 'en'
        assert error.message[0].text == 'A test error occurred'
        assert error.message[1].lang == 'es'
        assert error.message[1].text == 'Ocurrió un error de prueba'

        formatted_error = repo.get(TEST_FORMATTED_ERROR_CODE)
        assert len(formatted_error.message) == 2
        assert formatted_error.message[0].lang == 'en'
        assert formatted_error.message[0].text == 'Error for {item_name}'
        assert formatted_error.message[1].lang == 'es'
        assert formatted_error.message[1].text == 'Error para {item_name}'

    # * test: list
    def test_list(self, test_ctx, error_yaml_file: str) -> None:
        '''
        Test the list method of the ErrorConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param error_yaml_file: The error YAML configuration file path.
        :type error_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=error_yaml_file)

        # Assert unfiltered list ids.
        test_ctx.assert_list(repo)

    # * test: save
    def test_save(self, test_ctx, error_yaml_file: str) -> None:
        '''
        Test the save method of the ErrorConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param error_yaml_file: The error YAML configuration file path.
        :type error_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=error_yaml_file)

        # Assert save persists the aggregate sample.
        test_ctx.assert_save(repo)

        # Check nested messages on the saved error.
        new_error = repo.get('NEW_ERROR_CODE')
        assert len(new_error.message) == 2
        assert new_error.message[0].lang == 'en'
        assert new_error.message[0].text == 'A new error occurred'
        assert new_error.message[1].lang == 'es'
        assert new_error.message[1].text == 'Ocurrió un nuevo error'

    # * test: delete
    def test_delete(self, test_ctx, error_yaml_file: str) -> None:
        '''
        Test the delete method of the ErrorConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param error_yaml_file: The error YAML configuration file path.
        :type error_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=error_yaml_file)

        # Assert delete removes the id and is idempotent.
        test_ctx.assert_delete(repo)
