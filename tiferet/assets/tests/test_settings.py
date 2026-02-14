# *** imports

# ** app
from ...assets.settings import *


# *** tests

# ** test: tiferet_error
def test_tiferet_error():
    """
    Test the TiferetError exception.
    """

    # Create an instance of TiferetError with a specific error code and message.
    error_code = 'TEST_ERROR'
    message = 'This is a test error.'
    error = TiferetError(error_code, message)

    # Assert that the error code and message are set correctly.
    assert error.error_code == error_code, f"Expected {error_code}, got {error.error_code}"
    assert str(error) == '{"error_code": "TEST_ERROR", "message": "This is a test error."}', \
        f"Expected error message to match, got {str(error)}"
    

# ** test: tiferet_error_with_args
def test_tiferet_error_with_args():
    """
    Test the TiferetError exception with additional arguments.
    """

    # Create an instance of TiferetError with a specific error code, message, and additional arguments.
    error_code = 'TEST_ERROR_WITH_ARGS'
    message = 'This is a test error with args: {} and {}.'
    args = ('arg1', 'arg2')
    error = TiferetError(error_code, message.format(*args), *args)

    # Assert that the error code and message are set correctly.
    assert error.error_code == error_code
    assert 'This is a test error with args: arg1 and arg2.' in str(error)