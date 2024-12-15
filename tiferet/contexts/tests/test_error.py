# *** imports

# ** app
from . import *


# *** tests

# ** test: test_error_context_init
def test_error_context_init(error_context, error_repo):

    # Test initialization with error repo
    assert len(error_context.errors.values()) == 4
    assert error_context.errors["MY_ERROR"] == error_repo.errors[0]
    assert error_context.errors["FORMATTED_ERROR"] == error_repo.errors[1]
    assert error_context.errors["MULTI_FORMATTED_ERROR"] == error_repo.errors[2]
    assert error_context.errors["FEATURE_NOT_FOUND"] == error_repo.errors[3]


# ** test: test_error_context_load_custom_errors
def test_error_context_load_custom_errors(error_context):

    # Test loading custom errors
    custom_errors = error_context.load_custom_errors()

    # Check if the custom errors are loaded correctly
    assert len(custom_errors) == 1
    assert custom_errors[0].name == "FEATURE_NOT_FOUND"


# ** test: test_error_context_handle_error_with_error
def test_error_context_handle_error_with_assertion_error(error_context):
    
    
    # Test handling an error with an assertion error
    message = error_context.handle_error(AssertionError("MY_ERROR"), lang="en_US")

    # Check if the error message is correctly formatted
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
