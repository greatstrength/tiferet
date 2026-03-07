"""Tiferet Error Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ...mappers import (
    TransferObject,
    ErrorYamlObject,
)
from ..error import ErrorYamlRepository


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

# ** fixture: error_config_repo
@pytest.fixture
def error_config_repo(error_yaml_file: str) -> ErrorYamlRepository:
    '''
    Fixture to create an instance of the Error Configuration Repository.

    :param error_yaml_file: The error YAML configuration file path.
    :type error_yaml_file: str
    :return: An instance of ErrorYamlRepository.
    :rtype: ErrorYamlRepository
    '''

    # Create and return the ErrorYamlRepository instance.
    return ErrorYamlRepository(error_yaml_file)

# *** tests

# ** test_int: error_config_repo_exists
def test_int_error_config_repo_exists(
        error_config_repo: ErrorYamlRepository,
    ) -> None:
    '''
    Test the exists method of the ErrorYamlRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorYamlRepository
    '''

    # Check if the errors exist.
    assert error_config_repo.exists(TEST_ERROR_CODE)
    assert error_config_repo.exists(TEST_FORMATTED_ERROR_CODE)
    assert not error_config_repo.exists('MISSING_ERROR_CODE')

# ** test_int: error_config_repo_get
def test_int_error_config_repo_get(
        error_config_repo: ErrorYamlRepository,
    ) -> None:
    '''
    Test the get method of the ErrorYamlRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorYamlRepository
    '''

    # Get errors by id.
    error = error_config_repo.get(TEST_ERROR_CODE)
    formatted_error = error_config_repo.get(TEST_FORMATTED_ERROR_CODE)

    # Check the first error.
    assert error
    assert error.id == TEST_ERROR_CODE
    assert error.name == 'Test Error'
    assert len(error.message) == 2
    assert error.message[0].lang == 'en'
    assert error.message[0].text == 'A test error occurred'
    assert error.message[1].lang == 'es'
    assert error.message[1].text == 'Ocurrió un error de prueba'

    # Check the second error.
    assert formatted_error
    assert formatted_error.id == TEST_FORMATTED_ERROR_CODE
    assert formatted_error.name == 'Test Formatted Error'
    assert len(formatted_error.message) == 2
    assert formatted_error.message[0].lang == 'en'
    assert formatted_error.message[0].text == 'Error for {item_name}'
    assert formatted_error.message[1].lang == 'es'
    assert formatted_error.message[1].text == 'Error para {item_name}'

# ** test_int: error_config_repo_get_not_found
def test_int_error_config_repo_get_not_found(
        error_config_repo: ErrorYamlRepository,
    ) -> None:
    '''
    Test the get method of the ErrorYamlRepository for a non-existent error.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorYamlRepository
    '''

    # Attempt to get a non-existent error.
    error = error_config_repo.get('MISSING_ERROR_CODE')

    # Check that the error is None.
    assert not error

# ** test_int: error_config_repo_list
def test_int_error_config_repo_list(
        error_config_repo: ErrorYamlRepository,
    ) -> None:
    '''
    Test the list method of the ErrorYamlRepository for all errors.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorYamlRepository
    '''

    # List all errors.
    errors = error_config_repo.list()

    # Check the errors.
    assert errors
    assert len(errors) == 2
    error_ids = [error.id for error in errors]
    assert TEST_ERROR_CODE in error_ids
    assert TEST_FORMATTED_ERROR_CODE in error_ids

# ** test_int: error_config_repo_save
def test_int_error_config_repo_save(
        error_config_repo: ErrorYamlRepository,
    ) -> None:
    '''
    Test the save method of the ErrorYamlRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorYamlRepository
    '''

    # Create constant for new test error.
    new_error_id = 'NEW_ERROR_CODE'

    # Create new error config data and map to an aggregate.
    error = TransferObject.from_data(
        ErrorYamlObject,
        id=new_error_id,
        name='New Error',
        message=[
            {
                'lang': 'en',
                'text': 'A new error occurred',
            },
            {
                'lang': 'es',
                'text': 'Ocurrió un nuevo error',
            },
        ],
    ).map()

    # Save the new error.
    error_config_repo.save(error)

    # Reload the error to verify it was saved.
    new_error = error_config_repo.get(new_error_id)

    # Check the new error.
    assert new_error
    assert new_error.id == new_error_id
    assert new_error.name == 'New Error'
    assert len(new_error.message) == 2
    assert new_error.message[0].lang == 'en'
    assert new_error.message[0].text == 'A new error occurred'
    assert new_error.message[1].lang == 'es'
    assert new_error.message[1].text == 'Ocurrió un nuevo error'

# ** test_int: error_config_repo_delete
def test_int_error_config_repo_delete(
        error_config_repo: ErrorYamlRepository,
    ) -> None:
    '''
    Test the delete method of the ErrorYamlRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorYamlRepository
    '''

    # Delete an existing error.
    error_config_repo.delete(TEST_FORMATTED_ERROR_CODE)

    # Attempt to get the deleted error.
    deleted_error = error_config_repo.get(TEST_FORMATTED_ERROR_CODE)

    # Check that the error is None.
    assert not deleted_error

    # Ensure that deleting a non-existent error is idempotent.
    error_config_repo.delete('MISSING_ERROR_CODE')
