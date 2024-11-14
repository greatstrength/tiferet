# *** imports

# ** core
from typing import List

# ** app
from ...domain import *
from ...repos.error import ErrorRepository


# *** mocks

# ** mock: mock_error_repository
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