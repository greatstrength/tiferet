from ..repositories.error import ErrorRepository
from ..objects.error import Error

class ErrorContext(object):
    '''
    The error context object.
    '''
    
    error: str = None # The error message.
    
    def __init__(self, error_repo: ErrorRepository):
        '''
        Initialize the error context object.
        
        :param error_repo: The error repository.
        :type error_repo: ErrorRepository
        '''
        
        # Set the error repository.
        self.error_repo = error_repo

    def handle_error(self, error: str, lang: str = 'en_US', error_type: type = Error, **kwargs):

        # Parse error.
        try:
            error_name, error_data = error.split(': ')
            error_data = error_data.split(', ')
        # Handle error without data if ValueError is raised.
        except ValueError:
            error_name = error
            error_data = None

        # Get error.
        error: Error = self.error_repo.get(
            error_name, lang=lang, error_type=error_type)
        
        # Add format arguments to error.
        if error_data:
            error.set_format_args(*error_data)

        return error