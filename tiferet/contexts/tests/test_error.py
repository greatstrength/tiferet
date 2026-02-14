# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...assets import (
    TiferetError, 
    TiferetAPIError,
    DEFAULT_ERRORS,
    ERROR_NOT_FOUND_ID
)
from ..error import ErrorContext
from ...models import Error
from ...commands.error import GetError

# *** fixtures

# ** fixture: get_error_cmd_mock
@pytest.fixture
def get_error_cmd_mock() -> GetError:
    '''
    Fixture to create a mock GetError command.

    :return: A mock GetError command.
    :rtype: mock.Mock
    '''

    # Return the mocked GetError command.
    return mock.Mock(spec=GetError)

# ** fixture: error_context
@pytest.fixture
def error_context(get_error_cmd_mock: GetError):
    '''
    Fixture to create a new ErrorContext object.
    '''
    
    # Create an instance of ErrorContext with the mock error service.
    return ErrorContext(get_error_cmd=get_error_cmd_mock)

# *** tests

# ** test: error_context_get_error_by_code
def test_error_context_get_error_by_code(get_error_cmd_mock: GetError, error_context: ErrorContext):
    '''
    Test retrieving an error by its code from the ErrorContext.

    :param get_error_cmd_mock: The mocked GetError command.
    :type get_error_cmd_mock: GetError
    :param error_context: The error context to test.
    :type error_context: ErrorContext
    '''

    # Mock the get_error_handler to return a sample Error.
    get_error_cmd_mock.execute.return_value = Error.new(**DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID))
    
    error = error_context.get_error_by_code(ERROR_NOT_FOUND_ID)
    
    # Assert that the retrieved error matches the expected data.
    assert error
    assert error.error_code == ERROR_NOT_FOUND_ID
    assert error.name == 'Error Not Found'
    assert len(error.message) == 1
    assert error.message[0].lang == 'en_US'
    assert error.message[0].text == 'Error not found: {id}.'


# ** test: error_context_get_error_by_code_not_found
def test_error_context_get_error_by_code_not_found(error_context: ErrorContext):
    '''
    Test retrieving a non-existent error code from the ErrorContext.

    :param error_context: The error context to test.
    :type error_context: ErrorContext
    '''

    # Mock the get_error_handler to raise a TiferetError when the error is not found.
    error_context.get_error_handler = mock.Mock(side_effect=TiferetError('ERROR_NOT_FOUND', id='NON_EXISTENT_ERROR'))
    
    # Attempt to retrieve a non-existent error code.
    with pytest.raises(TiferetAPIError) as exc_info:
        error_context.get_error_by_code('NON_EXISTENT_ERROR')
    
    # Assert that the raised error is of type TiferetError.
    assert isinstance(exc_info.value, TiferetAPIError)
    
    # Assert that the error message matches the expected format.
    assert exc_info.value.error_code == ERROR_NOT_FOUND_ID
    assert exc_info.value.name == 'Error Not Found'
    assert 'Error not found: {id}.' in str(exc_info.value.message)
    assert exc_info.value.kwargs.get('id') == 'NON_EXISTENT_ERROR'

# ** test: error_context_handle_error
def test_error_context_handle_error(error_context):
    """Test handling an error using the ErrorContext."""

    # Do this again, but with the new TiferetError.
    tiferet_error = TiferetError('ERROR_NOT_FOUND', id='NON_EXISTENT_ERROR')

    # Mock the get_error_handler to return the appropriate Error object.
    error_context.get_error_handler = mock.Mock(return_value=Error.new(**DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID)))

    # Handle the error using the error context.
    response = error_context.handle_error(tiferet_error, lang='en_US')
    
    # Assert that the response is a dictionary containing the expected error data.
    assert isinstance(response, dict)
    assert response.get('error_code') == 'ERROR_NOT_FOUND'
    assert response.get('name') == 'Error Not Found'
    assert 'Error not found: NON_EXISTENT_ERROR.' in response.get('message', '')
    assert response.get('id') == 'NON_EXISTENT_ERROR'
    
