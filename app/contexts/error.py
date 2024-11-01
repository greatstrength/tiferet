# *** imports

# ** core
from typing import Dict

# ** app
from ..repositories.error import ErrorRepository
from ..objects.error import Error


# *** contexts

# ** context: error_context
class ErrorContext(object):
    '''
    The error context object.
    '''

    # * field: errors
    errors: Dict[str, Error] = None  # The error repository.

    # * method: init
    def __init__(self, error_repo: ErrorRepository):
        '''
        Initialize the error context object.
        
        :param error_repo: The error repository.
        :type error_repo: ErrorRepository
        '''

        # Set the errors lookup from the error repository.
        self.errors = {error.name: error for error in error_repo.list()}

    # * method: handle_error
    def format_error(self, error_message: str, lang: str = 'en_US', **kwargs):
        '''
        Handle an error.

        :param error_message: The error message.
        :type error_message: str
        :param lang: The language of the error message.
        :type lang: str
        :param error_type: The error type.
        :type error_type: type
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error.
        :rtype: Error
        '''

        # Parse error.
        # Handle error without data if ValueError is raised.
        try:
            error_name, error_data = error_message.split(': ')
            error_data = error_data.split(', ')
        except ValueError:
            error_name = error
            error_data = None

        # Get error.
        error = self.errors.get(error_name)

        # Set error response.
        error_response = dict(
            message=error.format(lang, *error_data if error_data else []),
            **kwargs
        )

        # Return error response.
        return error_response
