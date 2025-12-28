"""Tiferet Error Commands"""

# *** imports

# ** app
from .settings import Command
from ..assets.constants import DEFAULT_ERRORS, ERROR_NOT_FOUND_ID
from ..models import Error
from ..contracts import ErrorService

# *** commands

# ** command: get_error
class GetError(Command):
    '''
    Command to retrieve an Error domain object by its ID.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the GetError command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self, id: str, include_defaults: bool = False, **kwargs) -> Error:
        '''
        Retrieve an Error by its ID.

        :param id: The unique identifier of the error.
        :type id: str
        :param include_defaults: If True, search DEFAULT_ERRORS if not found in repository.
        :type include_defaults: bool
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        :return: The Error domain model instance.
        :rtype: Error
        '''

        # Attempt to retrieve from configured repository.
        error = self.error_service.get(id)

        # If found, return immediately.
        if error:
            return error

        # If requested, check built-in defaults and return as error if found.
        if include_defaults:
            error_data = DEFAULT_ERRORS.get(id)
            if error_data:
                return Error.new(**error_data)

        # If still not found and defaults not included, raise structured error.
        self.raise_error(
            error_code=ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id,
        )