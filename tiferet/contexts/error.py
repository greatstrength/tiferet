# *** imports

# ** core
from typing import Any, Tuple

# ** app
from ..domain import *
from ..repos.error import ErrorRepository


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
        errors = {error.name: error for error in error_repo.list()}

        # Set the errors lookup and validate.
        super().__init__(dict(errors=errors))
        self.validate()

    # * method: handle_error
    def handle_error(self, exception: Exception, lang: str = 'en_US', **kwargs) -> Tuple[bool, Any]:
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
