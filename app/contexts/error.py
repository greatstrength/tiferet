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
    @staticmethod
    def handle_error(self, func):
        '''
        Handle an error.

        :param func: The function to handle.
        :type func: function
        :return: The wrapped function.
        :rtype: Any
        '''

        # Import wraps.
        from functools import wraps

        # Define the wrapper.
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AssertionError as e:
                return self.format_error_response(str(e), **kwargs)

        # Return the wrapper.
        return wrapper

    # * method: format_error_response
    def format_error_response(self, error_message: str, lang: str = 'en_US', **kwargs) -> str:
        '''
        Format the error response.

        :param error_message: The error message.
        :type error_message: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The formatted error message.
        :rtype: str
        '''

        # Split error message.
        try:
            error_name, error_data = error_message.split(': ')
        except ValueError:
            error_name = error_message
            error_data = None

        # Format error data if present.
        error_data = error_data.split(', ') if error_data else None

        # Get error.
        error = self.errors.get(error_name)

        # Set error response.
        error_response = dict(
            message=error.format(lang, *error_data if error_data else []),
            **kwargs
        )

        # Return error response.
        return error_response
