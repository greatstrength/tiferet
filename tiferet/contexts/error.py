# *** imports

# ** core
from typing import Any, Tuple, List

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
        errors = {error.id: error for error in error_repo.list()}

        # Add custom errors.
        errors.update({error.id: error for error in self.load_custom_errors()})

        # Set the errors lookup and validate.
        super().__init__(dict(errors=errors))
        self.validate()

    # * method: load_custom_errors
    def load_custom_errors(self) -> List[Error]:
        '''
        Load custom errors.

        :return: The list of custom errors.
        :rtype: list
        '''

        # Get custom errors.
        return [
            Error.new(
                name='FEATURE_NOT_FOUND',
                error_code='FEATURE_NOT_FOUND',
                message=[
                    ErrorMessage.new(
                        lang='en_US',
                        text='The feature with ID was not found: {}'
                    )
                ]
            )
        ]

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

        # Split error message into error name and data.
        message_tokens = error_message.split(': ', 1)

        # Get error name and data.
        if len(message_tokens) > 1:
            error_name, error_data = message_tokens
        else:
            error_name = error_message
            error_data = None

        # Format error data if present.
        error_data = error_data.split(', ') if error_data else None

        # Get error.
        error = self.errors.get(error_name)

        # Set error response.
        error_response = dict(
            message=error.format(lang, *error_data if error_data else []),
            error_code=error.error_code,
            **kwargs
        )

        # Return error response.
        return error_response


