# *** imports

# ** app
from ..configs import *
from ..commands import *
from ..models.error import *


# *** contexts

# ** context: error_context
class ErrorContext(Model):
    '''
    The error context object.
    '''

    # * attribute: errors
    errors: Dict[str, Error]

    # * method: init
    def __init__(self, errors: List[Error]):
        '''
        Initialize the error context object.
        
        :param errors: The list of errors to initialize the context with.
        :type errors: List[Error]
        '''

        # Add the errors to the context.
        self.errors = {
            error.error_code: error for error in errors
        }

    # * method: handle_error
    def handle_error(self, exception: Exception, lang: str = 'en_US', **kwargs) -> Any:
        '''
        Handle an error.

        :param exception: The exception to handle.
        :type exception: Exception
        :param lang: The language to use for the error message.
        :type lang: str
        :return: Whether the error was handled.
        :rtype: bool
        '''

        # Raise the exception if it is not a Tiferet error.
        if not isinstance(exception, TiferetError):
            raise exception

        # Get error.
        # If the error does not exist, raise an error not found error.
        error = self.errors.get(exception.error_code, None)
        if not error:
            raise_error.execute(
                'ERROR_NOT_FOUND', 
                f'Error not found: {exception.error_code}.',
                exception.error_code
            )
        
        # Format the error response.
        return self.format_error_response(
            error, 
            lang,
            error_data=list(exception.args), 
            **kwargs)

    # * method: format_error_response
    def format_error_response(self, error: Error, lang: str, error_data: List[str] = [], **kwargs) -> Any:
        '''
        Format the error response.

        :param error_message: The error message.
        :type error_message: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The formatted error message.
        :rtype: Any
        '''
        
        # Format the error response message.
        return error.format_response(
            lang,
            *error_data,
            **kwargs
        )
