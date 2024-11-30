# *** imports

# ** app
from . import *


# *** tests

# ** test: test_error_context_init
def test_error_context_init(error_context, error_repo):

    # Test initialization with error repo
    assert len(error_context.errors.values()) == 3
    assert error_context.errors["MY_ERROR"] == error_repo.errors[0]
    assert error_context.errors["FORMATTED_ERROR"] == error_repo.errors[1]
    assert error_context.errors["MULTI_FORMATTED_ERROR"] == error_repo.errors[2]


# ** test: test_error_context_handle_error_no_error
def test_error_context_handle_error_no_error(error_context):
    
    # Test when no error is raised
    result = error_context.handle_error(lambda: None)
    assert result == (False, None)


# ** test: test_error_context_handle_error_with_error
def test_error_context_handle_error_with_assertion_error(error_context):
    
    # Test handling an AssertionError
    def raise_assertion_error():
        raise AssertionError("MY_ERROR")

    result = error_context.handle_error(raise_assertion_error)
    has_error, message = result
    assert has_error is True
    assert message['message'] == "An error occurred."


# ** test: test_format_error_response_with_args
def test_format_error_response_with_args(error_context):

    # Test formatting an error response with arguments
    formatted_message = error_context.format_error_response("FORMATTED_ERROR: This is the error.", lang="en_US")

    # Check if the error message is correctly formatted
    assert formatted_message['message'] == "An error occurred: This is the error."


# ** test: test_format_error_response_with_multiple_args
def test_format_error_response_with_multiple_args(error_context):

    # Test formatting an error response with multiple arguments
    formatted_message = error_context.format_error_response("MULTI_FORMATTED_ERROR: This is the error, 12345", lang="en_US")

    # Check if the error message is correctly formatted
    assert formatted_message['message'] == "An error occurred: This is the error - 12345."
