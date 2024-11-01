# *** imports

# ** app
from ..repositories.error import ErrorRepository
from ..objects.error import Error


# *** contexts

# ** context: error_context
class ErrorContext(object):
    '''
    The error context object.
    '''

    # ** field: error_repo
    error_repo: ErrorRepository = None  # The error repository.

    # ** method: init
    def __init__(self, error_repo: ErrorRepository):
        '''
        Initialize the error context object.
        
        :param error_repo: The error repository.
        :type error_repo: ErrorRepository
        '''

        # Set the error repository.
        self.error_repo = error_repo

    # ** method: handle_error
    def handle_error(self, error: str, lang: str = 'en_US', error_type: type = Error, **kwargs):
        '''
        Handle an error.

        :param error: The error message.
        :type error: str
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
            error_name, error_data = error.split(': ')
            error_data = error_data.split(', ')
        except ValueError:
            error_name = error
            error_data = None

        # Get error.
        error: Error = self.error_repo.get(
            error_name, lang=lang, error_type=error_type)

        # Add format arguments to error.
        if error_data:
            error.set_format_args(*error_data)

        # Return error.
        return error
