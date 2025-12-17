"""Tiferet Tests for Error Commands"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..error import (
    Error,
    ErrorRepository, 
    GetError
)
from ...assets import TiferetError, DEFAULT_ERRORS
from ...assets.constants import ERROR_NOT_FOUND_ID

# *** fixtures
@pytest.fixture
def error() -> Error:
    '''
    Fixture to create a sample Error instance.

    :return: A sample Error instance.
    :rtype: Error
    '''

    # Return a sample Error.
    return Error.new(
        id='TEST_ERROR',
        name='Test Error',
        description='A detailed description of the test error.',
        message=[{
            'lang': 'en_US',
            'text': 'This is a test error message.'
        }]
    )


# ** fixture: error_repo_mock
@pytest.fixture
def error_repo_mock() -> ErrorRepository:
    '''
    Fixture to create a mock ErrorRepository.

    :return: A mock ErrorRepository.
    :rtype: ErrorRepository
    '''

    # Return the mocked repository.
    return mock.Mock(spec=ErrorRepository)

# ** fixture: get_error_command
@pytest.fixture
def get_error_command(error_repo_mock: ErrorRepository) -> GetError:
    '''
    Fixture to create a GetError command instance.

    :param error_repo_mock: The mocked ErrorRepository.
    :type error_repo_mock: ErrorRepository
    :return: The GetError command instance.
    :rtype: GetError
    '''

    # Return the GetError command with the mocked repository.
    return GetError(error_repo=error_repo_mock)

# *** tests

# ** test: get_error_found_in_repo
def test_get_error_found_in_repo(error: Error, error_repo_mock: ErrorRepository, get_error_command: GetError):
    '''
    Test retrieving an error that exists in the repository.

    :param error: The sample Error instance.
    :type error: Error
    :param error_repo_mock: The mocked ErrorRepository.
    :type error_repo_mock: ErrorRepository
    :param get_error_command: The GetError command instance.
    :type get_error_command: GetError
    '''

    # Arrange the mock to return the error.
    error_id = 'TEST_ERROR'
    error_repo_mock.get.return_value = error

    # Act to retrieve the error.
    result = get_error_command.execute(id=error_id)

    # Assert the result matches the expected error.
    assert result == error
    error_repo_mock.get.assert_called_once_with(error_id)

# ** test: get_error_found_in_defaults
def test_get_error_found_in_defaults(error_repo_mock: ErrorRepository, get_error_command: GetError):
    '''
    Test retrieving an error that exists in the default errors.

    :param error_repo_mock: The mocked ErrorRepository.
    :type error_repo_mock: ErrorRepository
    :param get_error_command: The GetError command instance.
    :type get_error_command: GetError
    '''

    # Arrange the mock to return None.
    error_id = ERROR_NOT_FOUND_ID
    error_repo_mock.get.return_value = None

    # Act to retrieve the error.
    result = get_error_command.execute(id=error_id, include_defaults=True)

    # Assert the result matches the expected default error.
    expected_error = Error.new(**DEFAULT_ERRORS.get(error_id))
    assert result == expected_error
    error_repo_mock.get.assert_called_once_with(error_id)

# ** test: get_error_not_found
def test_get_error_not_found(error_repo_mock: ErrorRepository, get_error_command: GetError):
    '''
    Test retrieving an error that does not exist in the repository or defaults.

    :param error_repo_mock: The mocked ErrorRepository.
    :type error_repo_mock: ErrorRepository
    :param get_error_command: The GetError command instance.
    :type get_error_command: GetError
    '''

    # Arrange the mock to return None.
    error_id = 'NON_EXISTENT_ERROR'
    error_repo_mock.get.return_value = None

    # Act & Assert that retrieving the error raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        get_error_command.execute(id=error_id, include_defaults=False)

    # Verify the exception message.
    assert exc_info.value.error_code == ERROR_NOT_FOUND_ID
    assert exc_info.value.kwargs.get('id') == error_id
    assert f'Error not found: {error_id}.' in str(exc_info.value)
    error_repo_mock.get.assert_called_once_with(error_id)