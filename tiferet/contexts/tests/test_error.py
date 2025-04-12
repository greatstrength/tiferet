# *** imports

# ** infra
import pytest

# ** app
from ..error import *


# *** classes

# class: mock_error_repo
class MockErrorRepository(ErrorRepository):
        
    def __init__(self, errors: List[Error] = []):
        self.errors = errors

    def exists(self, id, **kwargs):
        return any(error.id == id for error in self.errors)

    def get(self, id):
        return next((error for error in self.errors if error.id == id), None)

    def list(self):
        return self.errors

    def save(self, error):
        pass


# *** fixtures

# ** fixture: mock_error_repo_raise_error
@pytest.fixture
def mock_error_repo_raise_error():
    
    class MockErrorRepository(ErrorRepository):

        def exists(self, id, **kwargs):
            raise Exception("Error")

        def get(self, id):
            raise Exception("Error")

        def list(self):
            raise Exception("Error")

        def save(self, error):
            raise Exception("Error")

    return MockErrorRepository()


# ** fixture: error_message
@pytest.fixture
def error_message() -> ErrorMessage:
    return ValueObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred.'
    )


# ** fixture: formatted_error_message
@pytest.fixture
def formatted_error_message() -> ErrorMessage:
    return ValueObject.new(
        ErrorMessage,
        lang='en_US',
        text='An error occurred: {}'
    )


# ** fixture: error
@pytest.fixture
def error(error_message) -> Error:
    return Error.new(
        name='My Error',
        message=[error_message]
    )


# ** fixture: error_with_formatted_message
@pytest.fixture
def error_with_formatted_message(formatted_error_message) -> Error:
    return ValueObject.new(
        Error,
        name='My formatted error',
        id='MY_FORMATTED_ERROR',
        error_code='MY_FORMATTED_ERROR',
        message=[formatted_error_message]
    )


# ** fixture: error_repo 
@pytest.fixture
def error_repo(error, error_with_formatted_message):
    return MockErrorRepository(
        errors=[
            error,
            error_with_formatted_message
        ]
    )


# ** fixture: error_context 
@pytest.fixture
def error_context(error_repo):
    return ErrorContext(
        error_repo=error_repo
    )


# *** tests

# ** test: test_raise_error
def test_raise_error():

    # Check that the error is raised correctly.
    with pytest.raises(TiferetError):
        raise_error("MY_ERROR")

    # Check that the error with format arguments is raised correctly.
    with pytest.raises(TiferetError):
        raise_error("MY_FORMATTED_ERROR", "This is the error.")


# ** test: test_error_context_init
def test_error_context_init(error_context, error_repo):

    # Check that there are errors present.
    assert len(error_context.errors.values()) > 0

    # Check that the errors are loaded correctly.
    assert error_context.errors["MY_ERROR"] == error_repo.errors[0]
    assert error_context.errors["MY_FORMATTED_ERROR"] == error_repo.errors[1]


# ** test: test_error_context_init_with_error
def test_error_context_init_with_error(mock_error_repo_raise_error):

    # Check that an error is raised when loading errors.
    with pytest.raises(ErrorLoadingError):
        ErrorContext(
            error_repo=mock_error_repo_raise_error
        )


# ** test: test_format_error_response_error_not_found
def test_format_error_response_error_not_found(error_context):

    # Check that an error is raised when the error is not found.
    with pytest.raises(ErrorNotFoundError):
        error_context.format_error_response("ERROR_NOT_FOUND", lang="en_US")


# ** test: test_format_error_response_use_default_language
def test_format_error_response_use_default_language(error_context):

    # Test formatting an error response with the default language.
    formatted_message = error_context.format_error_response("MY_ERROR", lang="es_ES")

    # Check if the error message is correctly formatted
    assert formatted_message['message'] == "An error occurred."


# ** test: test_format_error_response_with_args
def test_format_error_response(error_context):

    # Test formatting an error response with no arguments.
    message = error_context.format_error_response("MY_ERROR", lang="en_US")

    # Check if the error message is correctly formatted
    assert message['error_code'] == "MY_ERROR"
    assert message['message'] == "An error occurred."

    # Test formatting an error response with arguments
    formatted_message = error_context.format_error_response("MY_FORMATTED_ERROR", lang="en_US", error_data=["This is the error."])

    # Check if the error message is correctly formatted
    assert formatted_message['error_code'] == "MY_FORMATTED_ERROR"
    assert formatted_message['message'] == "An error occurred: This is the error."


# ** test: test_handle_error_raise_exception
def test_handle_error_raise_exception(error_context):

    # Create an exception using an unknown error code.
    exception = Exception("An error occurred.")

    # Test handling an error and raising an exception
    with pytest.raises(Exception):
        error_context.handle_error(
            exception, 
            lang="en_US"
        )


# ** test: test_handle_error_return_formatted_error_response
def test_handle_error_return_formatted_error_response(error_context):

    # Create Tiferet Error using a known error code.
    exception = TiferetError(
        error_code="MY_ERROR",
    )

    # Test handling an error and returning a formatted error response
    formatted_message = error_context.handle_error(
        exception, 
        lang="en_US"
    )

    # Check if the error message is correctly formatted
    assert formatted_message['error_code'] == "MY_ERROR"
    assert formatted_message['message'] == "An error occurred."


# ** test: test_handle_error_raise_exception
def test_handle_error_raise_tiferet_error_exception(error_context):

    # Create an exception using an unknown error code.
    exception = TiferetError(
        error_code="ERROR_NOT_FOUND"
    )

    # Test handling an error and raising an exception
    with pytest.raises(TiferetError):
        error_context.handle_error(
            exception, 
            lang="en_US"
        )