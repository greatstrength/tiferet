# *** imports

# ** app
from ..configs import *
from ..models.error import *
from ..repos.error import *


# *** functions

# ** function: raise_error
def raise_error(error_code: str, message: str, *args):
    '''
    Raise an error.

    :param error_code: The error code.
    :type error_code: str
    :param args: Additional error arguments.
    :type args: tuple
    '''

    # Raise the error.
    raise TiferetError(error_code, message, *args)


# *** contexts

# ** context: error_context
class ErrorContext(Model):
    '''
    The error context object.
    '''

    # * attribute: errors
    errors = DictType(
        ModelType(Error),
        required=True,
        metadata=dict(
            description='The errors lookup.'
        )
    )

    # * method: init
    def __init__(self, error_repo: ErrorRepository):
        '''
        Initialize the error context object.
        
        :param error_repo: The error repository.
        :type error_repo: ErrorRepository
        '''

        # Create the errors lookup from the error repository.
        try:

            # Create the errors lookup from the hard-configured errors.
            errors = {id: ModelObject.new(Error, **data) for id, data in ERRORS.items()}

            # Iterate over the errors in the error repository.
            for error in error_repo.list():
                
                # Add the error to the errors lookup.
                errors[error.id] = error

        # If the error repository fails to load, raise an error.   
        except Exception as e:
            raise_error(
                'ERROR_LOADING_FAILED',
                f'Failed to load errors: {str(e)}.',
                str(e),
            )

        # Set the errors lookup and validate.
        super().__init__(dict(errors=errors))
        self.validate()

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
            raise_error(
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
        # If the error message does not exist in the specified language, use the default language.
        error_response_message = error.format(lang, *error_data if error_data else [])
        if not error_response_message:
            error_response_message = error.format('en_US', *error_data if error_data else [])

        # Set error response.
        error_response = dict(
            message=error_response_message,
            error_code=error.error_code,
            **kwargs
        )

        # Return error response.
        return error_response
    

