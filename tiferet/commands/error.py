from ..domain.error import Error
from ..repos.error import ErrorRepository

class AddNewError(object):

    def __init__(self, error_repo: ErrorRepository):
        self.error_repo = error_repo

    def execute(self, **kwargs) -> Error:

        # Create a new error.
        error: Error = Error.new(**kwargs)

        # Assert that the error does not already exist.
        assert not self.error_repo.exists(error.id), f'ERROR_ALREADY_EXISTS: {error.id}'

        # Save the error.
        self.error_repo.save(error)

        # Return the new error.
        return error