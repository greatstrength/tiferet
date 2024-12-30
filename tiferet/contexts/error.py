# *** imports

# ** app
from ..configs import *
from ..models.error import *
from ..repos.error import *


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
            errors = {error.id: error for error in error_repo.list()}
        except Exception as e:
            raise ErrorLoadingError(e)

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

        # Execute the feature function and handle the errors.
        if isinstance(exception, AssertionError):
            return self.format_error_response(str(exception), lang, **kwargs)

    # * method: format_error_response
    def format_error_response(self, error_message: str, lang: str, **kwargs) -> Any:
        '''
        Format the error response.

        :param error_message: The error message.
        :type error_message: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The formatted error message.
        :rtype: Any
        '''

        # Split error message into error name and data.
        try:
            message_tokens = error_message.split(': ', 1)
            if len(message_tokens) > 1:
                error_name, error_data = message_tokens
            else:
                error_name = error_message
                error_data = None
        except Exception as e:
            raise InvalidErrorMessageError(error_message, e)

        # Format error data if present.
        error_data = error_data.split(', ') if error_data else None

        # Get error.
        try:
            error = self.errors.get(error_name)
        except Exception as e:
            raise ErrorNotFoundError(error_name)
        
        # Format the error response message.
        error_response_message = error.format(lang, *error_data if error_data else [])
        if not error_response_message:
            raise ErrorLanguageNotSupportedError(error.id, lang)
        
        # Verify the error code.
        if not error.error_code:
            raise InvalidErrorCodeError(error.id)

        # Set error response.
        error_response = dict(
            message=error_response_message,
            error_code=error.error_code,
            **kwargs
        )

        # Return error response.
        return error_response
    

# *** exceptions

# ** exception: error_loading_error
class ErrorLoadingError(Exception):
    '''
    The error loading errors.
    '''
    
    # * method: init
    def __init__(self, exception: Exception):
        '''
        Initialize the error loading errors exception.
        
        :param exception: The exception.
        :type exception: Exception
        '''
        
        # Set the exception.
        self.exception = exception
        super().__init__(f'Error when loading errors: {exception}')


# ** exception: invalid_error_message_error
class InvalidErrorMessageError(Exception):
    '''
    The invalid error message error.
    '''
    
    # * method: init
    def __init__(self, error_message: str, exception: Exception):
        '''
        Initialize the invalid error message error.
        
        :param error_message: The error message.
        :type error_message: str
        :param exception: The exception.
        :type exception: Exception
        '''
        
        # Set the error message.
        self.error_message = error_message
        super().__init__(f'Invalid error message: {error_message} - {exception}')


# ** exception: error_not_found_error
class ErrorNotFoundError(Exception):
    '''
    The error not found error.
    '''
    
    # * method: init
    def __init__(self, error_id: str):
        '''
        Initialize the error not found error.
        
        :param error_id: The error ID.
        :type error_id: str
        '''
        
        # Set the error ID.
        self.error_id = error_id
        super().__init__(f'Error not found: {error_id}')


# ** exception: error_language_not_supported_error
class ErrorLanguageNotSupportedError(Exception):
    '''
    The error language not supported error.
    '''
    
    # * method: init
    def __init__(self, error_id: str, lang: str):
        '''
        Initialize the error language not supported error.
        
        :param error_id: The error ID.
        :type error_id: str
        :param lang: The language.
        :type lang: str
        '''
        
        # Set the error ID and language.
        self.error_id = error_id
        self.lang = lang
        super().__init__(f'Error language not supported: {error_id} ({lang})')


# ** exception: invalid_error_code_error
class InvalidErrorCodeError(Exception):
    '''
    The invalid error code error.
    '''
    
    # * method: init
    def __init__(self, error_id: str):
        '''
        Initialize the invalid error code error.
        
        :param error_code: The error code.
        :type error_code: str
        '''
        
        # Set the error ID with the invalid error code.
        self.error_id = error_id
        super().__init__(f'Invalid error code for error: {error_id}')
