# *** imports

# ** infra
import pytest

# ** app
from ..settings import *
from ...configs import TiferetError

# *** fixtures

# ** fixture: service_handler
@pytest.fixture
def service_handler():
    '''
    Fixture for creating a ServiceHandler instance.
    '''

    return ServiceHandler()

# *** tests

# ** test: test_raise_error_basic
def test_raise_error_basic(service_handler):
    '''Test raising a TiferetError with basic parameters.'''

    # Raise error with code and message, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        service_handler.raise_error('TEST_ERROR', 'An error has occurred.') 

    # Verify error code and message.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info), 'Should raise error with correct message' 

# ** test: test_raise_error_with_args
def test_raise_error_with_args(service_handler):
    '''Test raising a TiferetError with additional arguments.'''

    # Raise error with code, message, and args, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        service_handler.raise_error('TEST_ERROR', 'An error has occurred.', 'tiferet.handlers.settings', 'ServiceHandler') 

    # Verify error code, message, and additional arguments.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'An error has occurred.' in str(exc_info), 'Should raise error with correct message' 
    assert 'tiferet.handlers.settings' in str(exc_info), 'Should raise error with correct module path' 
    assert 'ServiceHandler' in str(exc_info), 'Should raise error with correct class name'