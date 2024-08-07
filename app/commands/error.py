from ..objects.error import Error
from ..repositories.error import ErrorRepository
from ..services import error as error_service

class AddNewError(object):

    def __init__(self, error_repo: ErrorRepository):
        self.error_repo = error_repo

    def execute(self, **kwargs) -> Error:

        # Create a new error.
        error = error_service.create_error(**kwargs)

        # Assert that the error does not already exist.
        assert not self.error_repo.exists(error.id), f'ERROR_ALREADY_EXISTS: {error.id}'

        # Save the error.
        self.error_repo.save(error)

        # Return the new error.
        return error