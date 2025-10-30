# *** imports

# ** app
from ..models.error import (
    Error
)
from ..contracts.error import (
    ErrorRepository
)

class AddNewError(object):
    '''
    Add a new error.
    '''

    # * init
    def __init__(self, error_repo: ErrorRepository):
        self.error_repo = error_repo

    # * method: execute
    def execute(self, **kwargs) -> Error:
        '''
        Execute the command to add a new error.

        :param kwargs: The keyword arguments for the new error.
        :type kwargs: dict
        :return: The new error.
        :rtype: Error
        '''

        # Create a new error.
        error: Error = Error.new(**kwargs)

        # Assert that the error does not already exist.
        self.verify(self.error_repo.exists(error.id), 
            'ERROR_ALREADY_EXISTS',
            args=(error.id,)
        )

        # Save the error.
        self.error_repo.save(error)

        # Return the new error.
        return error