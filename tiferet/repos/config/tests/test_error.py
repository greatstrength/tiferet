"""Tiferet Error Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ....assets import TiferetError
from ....data import DataObject, ErrorConfigData
from ..error import ErrorConfigurationRepository

# *** constants

# ** constant: test_error_code_id
TEST_ERROR_CODE_ID = 'TEST_ERROR_CODE'

# ** constant: test_formatted_error_code_id
TEST_FORMATTED_ERROR_CODE_ID = 'TEST_FORMATTED_ERROR_CODE'

# ** constant: error_data
ERROR_DATA = {
    'errors': {
        TEST_ERROR_CODE_ID: {
            'name': 'Test Error',
            'message': [
                {
                    'lang': 'en',
                    'text': 'This is a test error message.'
                }
            ]
        },
        TEST_FORMATTED_ERROR_CODE_ID: {
            'name': 'Test Formatted Error',
            'message': [
                {
                    'lang': 'en',
                    'text': 'This is a test formatted error message with a placeholder: {placeholder}.'
                }
            ]
        }
    }
}
# *** fixtures

# ** fixture: error_config_file
@pytest.fixture
def error_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the error YAML configuration file.

    :return: The error YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample error configuration content.
    file_path = tmp_path / 'test_error.yaml'

    # Write the sample error configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(ERROR_DATA, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: error_config_repo
@pytest.fixture
def error_config_repo(error_config_file: str) -> ErrorConfigurationRepository:
    '''
    Fixture to create an instance of the Error Configuration Repository.

    :param error_read_config_file: The error YAML configuration file path.
    :type error_ModelObject_file: str
    :return: An instance of ErrorConfigurationRepository.
    :rtype: ErrorConfigurationRepository
    '''

    # Create and return the ErrorConfigurationRepository instance.
    return ErrorConfigurationRepository(error_config_file)

# *** tests

# ** test_int: error_config_repo_exists
def test_int_error_config_repo_exists(
        error_config_repo: ErrorConfigurationRepository,
    ):
    '''
    Test the exists method of the ErrorConfigurationRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorConfigurationRepository
    '''

    # Check if the error exists.
    assert error_config_repo.exists(TEST_ERROR_CODE_ID)
    assert error_config_repo.exists(TEST_FORMATTED_ERROR_CODE_ID)
    assert not error_config_repo.exists('NON_EXISTENT_ERROR_CODE')

# ** test_int: error_config_repo_get
def test_int_error_config_repo_get(
        error_config_repo: ErrorConfigurationRepository,
    ):
    '''
    Test the get method of the ErrorConfigurationRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorConfigurationRepository
    :param errors: The dictionary of expected errors.
    :type errors: Dict[str, Error]
    '''

    # Get the error.
    test_error = error_config_repo.get(TEST_ERROR_CODE_ID)
    test_formatted_error = error_config_repo.get(TEST_FORMATTED_ERROR_CODE_ID)

    # Check the error.
    assert test_error
    assert test_error.id == TEST_ERROR_CODE_ID
    assert test_error.name == 'Test Error'
    assert len(test_error.message) == 1
    assert test_error.message[0].lang == 'en'
    assert test_error.message[0].text == 'This is a test error message.'

    # Check the formatted error.
    assert test_formatted_error
    assert test_formatted_error.id == TEST_FORMATTED_ERROR_CODE_ID
    assert test_formatted_error.name == 'Test Formatted Error'
    assert len(test_formatted_error.message) == 1
    assert test_formatted_error.message[0].lang == 'en'
    assert test_formatted_error.message[0].text == 'This is a test formatted error message with a placeholder: {placeholder}.'

# ** test_int: error_config_repo_get_not_found
def test_int_error_config_repo_get_not_found(
        error_config_repo: ErrorConfigurationRepository,
    ):
    '''
    Test the get method of the ErrorConfigurationRepository for a non-existent error.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorConfigurationRepository
    '''

    # Get the error.
    test_error = error_config_repo.get('NOT_FOUUND_ERROR_CODE')

    # Check the error.
    assert not test_error

# ** test_int: error_config_repo_list
def test_int_error_config_repo_list(
        error_config_repo: ErrorConfigurationRepository,
    ):
    '''
    Test the list_all method of the ErrorConfigurationRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorConfigurationRepository
    '''

    # List all errors.
    test_errors = error_config_repo.list()

    # Check the errors.
    assert test_errors
    assert len(test_errors) == 2
    error_ids = [error.id for error in test_errors]
    assert TEST_ERROR_CODE_ID in error_ids
    assert TEST_FORMATTED_ERROR_CODE_ID in error_ids


# ** test_int: error_config_repo_save
def test_int_error_config_repo_save(
        error_config_repo: ErrorConfigurationRepository,
    ):
    '''
    Test the save method of the ErrorConfigurationRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorConfigurationRepository
    '''

    # Create constant for new test error.
    NEW_TEST_ERROR_CODE_ID = 'NEW_TEST_ERROR_CODE'

    # Create new error.
    error = DataObject.from_data(
        ErrorConfigData,
        id=NEW_TEST_ERROR_CODE_ID,
        name='New Test Error',
        message=[{
            'lang': 'en',
            'text': 'This is a new test error message.'
        }]
    ).map()

    # Save the modified error.
    error_config_repo.save(error)

    # Reload the error to verify the changes.
    new_error = error_config_repo.get(NEW_TEST_ERROR_CODE_ID)

    # Check the new error.
    assert new_error
    assert new_error.id == NEW_TEST_ERROR_CODE_ID
    assert new_error.name == 'New Test Error'
    assert len(new_error.message) == 1
    assert new_error.message[0].lang == 'en'
    assert new_error.message[0].text == 'This is a new test error message.'

# ** test_int: error_config_repo_delete
def test_int_error_config_repo_delete(
        error_config_repo: ErrorConfigurationRepository,
    ):
    '''
    Test the delete method of the ErrorConfigurationRepository.

    :param error_config_repo: The error configuration repository.
    :type error_config_repo: ErrorConfigurationRepository
    '''

    # Delete an existing error.
    error_config_repo.delete(TEST_FORMATTED_ERROR_CODE_ID)

    # Attempt to get the deleted error.
    deleted_error = error_config_repo.get(TEST_FORMATTED_ERROR_CODE_ID)

    # Check that the error is None.
    assert not deleted_error
