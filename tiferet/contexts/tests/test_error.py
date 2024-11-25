# *** imports

# ** core
from typing import List

# ** infra
import pytest

# ** app
from . import *


# *** fixtures

# ** fixtures: mock_error_repo
@pytest.fixture
def mock_error_repo(error, error_with_formatted_message, error_with_multiple_args):

    class MockErrorRepository(ErrorRepository):
        '''
        A mock error repository.
        '''

        # * method: init
        def __init__(self, errors: List[Error] = None):
            '''
            Initialize the mock error repository.

            :param errors: The errors.
            :type errors: list
            '''

            # Set the errors.
            self.errors = errors or []

        # * method: exists
        def exists(self, id: str, **kwargs) -> bool:
            '''
            Check if the error exists.

            :param id: The error id.
            :type id: str
            :param kwargs: Additional keyword arguments.
            :type kwargs: dict
            :return: Whether the error exists.
            :rtype: bool
            '''

            # Return whether the error exists.
            return any(error.id == id for error in self.errors)
        
        # * method: get
        def get(self, id: str) -> Error:
            '''
            Get the error.

            :param id: The error id.
            :type id: str
            :return: The error.
            :rtype: Error
            '''

            # Find the error by ID.
            return next((error for error in self.errors if error.id == id), None)

        # * method: list
        def list(self):
            '''
            List all errors.

            :return: The list of errors.
            :rtype: List[Error]
            '''
            return self.errors
        
        # * method: save
        def save(self, error: Error):
            '''
            Save the error.

            :param error: The error.
            :type error: Error
            '''

            # Add the error to the errors.
            self.errors.append(error)

    # Return the mock error repository.
    return MockErrorRepository(errors=[
        error,
        error_with_formatted_message,
        error_with_multiple_args
    ])


# ** mock: mock_error_context
@pytest.fixture
def error_context(mock_error_repo):
    return ErrorContext(error_repo=mock_error_repo)


# ** fixture: error_with_multiple_args
@pytest.fixture
def error_with_multiple_args():
    return Error.new(
        name="MULTI_FORMATTED_ERROR",
        error_code="MULTI_FORMATTED_ERROR",
        message=[
            ErrorMessage.new(
                lang="en_US",
                text="An error occurred: {0} - {1}."
            )
        ]
    )

# *** tests


# ** test: test_error_context_init
def test_error_context_init(error_context, mock_error_repo):

    # Test initialization with error repo
    assert len(error_context.errors.values()) == 3
    assert error_context.errors["MY_ERROR"] == mock_error_repo.errors[0]
    assert error_context.errors["FORMATTED_ERROR"] == mock_error_repo.errors[1]
    assert error_context.errors["MULTI_FORMATTED_ERROR"] == mock_error_repo.errors[2]


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
def test_format_error_response_with_multiple_args(error_context, error_with_multiple_args):

    # Test formatting an error response with multiple arguments
    formatted_message = error_context.format_error_response("MULTI_FORMATTED_ERROR: This is the error, 12345", lang="en_US")

    # Check if the error message is correctly formatted
    assert formatted_message['message'] == "An error occurred: This is the error - 12345."
