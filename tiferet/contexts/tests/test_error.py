# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...configs import TiferetError as LegacyTiferetError
from ...configs.error import ERRORS
from ..error import ErrorService, ErrorContext
from ...models.error import *


# *** fixtures

# ** fixture: error_service
@pytest.fixture
def error_service():
    """Fixture to provide a mock error service."""
    
    # Create a mock error service.
    service = mock.Mock(spec=ErrorService)
    service.load_errors.return_value = [
        ModelObject.new(Error, **error_data) for error_data in ERRORS 
    ]

    # Return the mock error service.
    return service


# ** fixture: error_context
@pytest.fixture
def error_context(error_service):
    """Fixture to provide an instance of ErrorContext."""
    
    # Create an instance of ErrorContext with the mock error service.
    return ErrorContext(error_service=error_service)


# *** tests

# ** test: error_context_load_errors
def test_error_context_load_errors(error_context):
    """Test loading errors from the ErrorContext."""
    
    # Load errors using the error context.
    loaded_errors = error_context.load_errors()
    
    # Assert that the loaded errors match the configured errors.
    assert len(loaded_errors) == len(ERRORS)
    
    # Assert that each loaded error matches the expected data.
    for i, error in enumerate(loaded_errors):
        assert error.error_code == ERRORS[i]['error_code']
        for j, message in enumerate(error.message):
            assert message.lang == ERRORS[i]['message'][j]['lang']
            assert message.text == ERRORS[i]['message'][j]['text']


# ** test: error_context_get_error_by_code
def test_error_context_get_error_by_code(error_context):
    """Test retrieving an error by its code from the ErrorContext."""
    

    error = error_context.get_error_by_code('ERROR_NOT_FOUND')
    
    # Assert that the retrieved error matches the expected data.
    assert error
    assert error.error_code == 'ERROR_NOT_FOUND'
    assert error.name == 'Error Not Found'
    assert len(error.message) == 1
    assert error.message[0].lang == 'en_US'
    assert error.message[0].text == 'Error not found: {}.'


# ** test: error_context_get_error_by_code_not_found
def test_error_context_get_error_by_code_not_found(error_context):
    """Test handling the case where an error code is not found in the ErrorContext."""
    
    # Attempt to retrieve a non-existent error code.
    with pytest.raises(LegacyTiferetError) as exc_info:
        error_context.get_error_by_code('NON_EXISTENT_ERROR')
    
    # Assert that the raised error is of type TiferetError.
    assert isinstance(exc_info.value, LegacyTiferetError)
    
    # Assert that the error message matches the expected format.
    assert exc_info.value.error_code == 'ERROR_NOT_FOUND'
    assert 'Error not found: NON_EXISTENT_ERROR.' in str(exc_info.value)


# ** test: error_context_handle_error
def test_error_context_handle_error(error_context):
    """Test handling an error using the ErrorContext."""
    
    # Create a TiferetError instance.
    tiferet_error = LegacyTiferetError('ERROR_NOT_FOUND', 'Error not found: NON_EXISTENT_ERROR.', 'NON_EXISTENT_ERROR')
    
    # Handle the error using the error context.
    response = error_context.handle_error(tiferet_error, lang='en_US')
    
    # Assert that the response contains the expected error message.
    assert response['error_code'] == 'ERROR_NOT_FOUND'
    assert response['message'] == 'Error not found: NON_EXISTENT_ERROR.'