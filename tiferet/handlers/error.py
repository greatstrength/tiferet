# *** imports

# ** app
from ..contracts.error import *


# *** handlers

# ** handler: error_handler
class ErrorHandler(ErrorService):
    '''
    A handler for error objects.
    '''

    # * attribute: error_repo
    error_repo: ErrorRepository

    # * method: init
    def __init__(self, error_repo: ErrorRepository):
        '''
        Initialize the error handler.

        :param error_repo: The error repository to use for handling errors.
        :type error_repo: ErrorRepository
        '''
        
        # Assign the attributes.
        self.error_repo = error_repo

    # * method: load_errors
    def load_errors(self, configured_errors: List[Error] = []) -> List[Error]:
        '''
        Load errors by their codes.

        :param configured_errors: The list of hard-coded errors to load.
        :type configured_errors: List[Error]
        :return: The list of loaded errors.
        :rtype: List[Error]
        '''
        
        # Load the errors from the repository.
        errors = self.error_repo.list()

        # If there are configured errors, extend the list with them.
        if configured_errors:
            errors.extend(configured_errors)

        # Return the list of errors.
        return errors