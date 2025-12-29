"""Tiferet Error Commands"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any
)

# ** app
from .settings import Command, const
from ..models import Error
from ..contracts import ErrorService

# *** commands

# ** command: add_error
class AddError(Command):
    '''
    Command to add a new Error domain object to the repository.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the AddError command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self,
            id: str,
            name: str,
            message: str, 
            lang: str = 'en_US', 
            additional_messages: List[Dict[str, Any]] = []
        ) -> None:
        '''
        Add a new Error to the app.

        :param id: The unique identifier of the error.
        :type id: str
        :param name: The name of the error.
        :type name: str
        :param message: The primary error message text.
        :type message: str
        :param lang: The language of the primary error message (default is 'en_US').
        :type lang: str
        :param additional_messages: Additional error messages in different languages.
        :type additional_messages: List[Dict[str, Any]]
        '''

        # Verfy that the id is not null/empty.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name='AddError'
        )

        # Verify that the name is not null/empty.
        self.verify_parameter(
            parameter=name,
            parameter_name='name',
            command_name='AddError'
        )

        # Verify that the message is not null/empty.
        self.verify_parameter(
            parameter=message,
            parameter_name='message',
            command_name='AddError'
        )

        # Check if an error with the same ID already exists.
        exists = self.error_service.exists(id)
        self.verify(
            expression=exists is False,
            error_code=const.ERROR_ALREADY_EXISTS_ID,
            message=f'An error with ID {id} already exists.',
            id=id
        )

        # Create the Error instance.
        error_messages = [{'lang': lang, 'text': message}] + additional_messages
        new_error = Error.new(
            id=id,
            name=name,
            message=error_messages
        )

        # Save the new error.
        self.error_service.save(new_error)

        # Return the new error.
        return new_error

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
            error_data = const.DEFAULT_ERRORS.get(id)
            if error_data:
                return Error.new(**error_data)

        # If still not found and defaults not included, raise structured error.
        self.raise_error(
            error_code=const.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id,
        )

# ** command: list_errors
class ListErrors(Command):
    '''
    Command to list all Error domain objects.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the ListErrors command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self, include_defaults: bool = False, **kwargs) -> List[Error]:
        '''
        List all Errors.

        :return: The list of Error domain model instances.
        :rtype: List[Error]
        :param include_defaults: If True, include DEFAULT_ERRORS in the list.
        :type include_defaults: bool
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        '''

        # If defaults are not included, retrieve from repository only.
        if not include_defaults:
            return self.error_service.list()
        
        # If defaults are included, merge repository and default errors.
        errors = {id: Error.new(**data) for id, data in const.DEFAULT_ERRORS.items()}
        repo_errors = self.error_service.list()
        errors.update({error.id: error for error in repo_errors})

        # Return the merged list of errors.
        return list(errors.values())

# ** command: rename_error
class RenameError(Command):
    '''
    Command to rename an existing Error domain object.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the RenameError command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self, id: str, new_name: str, **kwargs) -> Error:
        '''
        Rename an existing Error by its ID.

        :param id: The unique identifier of the error to rename.
        :type id: str
        :param new_name: The new name for the error.
        :type new_name: str
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        :return: The updated Error domain model instance.
        :rtype: Error
        '''

        # Verify that the new name is not null/empty.
        self.verify_parameter(
            parameter=new_name,
            parameter_name='new_name',
            command_name='RenameError'
        )

        # Retrieve the existing error.
        error = self.error_service.get(id)
        self.verify(
            expression=error,
            error_code=const.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id
        )

        # Update the name.
        error.rename(new_name)

        # Save the updated error.
        self.error_service.save(error)

        # Return the updated error.
        return error

# ** command: set_error_message
class SetErrorMessage(Command):
    '''
    Command to set the message of an existing Error domain object.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the SetErrorMessage command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self, id: str, message: str, lang: str = 'en_US', **kwargs) -> str:
        '''
        Set the message of an existing Error by its ID.

        :param id: The unique identifier of the error.
        :type id: str
        :param message: The new message text.
        :type message: str
        :param lang: The language of the message (default is 'en_US').
        :type lang: str
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        :return: The unique identifier of the updated error.
        :rtype: str
        '''

        # Verify that the message is not null/empty.
        self.verify_parameter(
            parameter=message,
            parameter_name='message',
            command_name='SetErrorMessage'
        )

        # Retrieve the existing error.
        error = self.error_service.get(id)
        self.verify(
            expression=error,
            error_code=const.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id
        )

        # Update the message.
        error.set_message(lang, message)

        # Save the updated error.
        self.error_service.save(error)

        # Return the updated error id.
        return id

# ** command: remove_error_message
class RemoveErrorMessage(Command):
    '''
    Command to remove a message from an existing Error domain object.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the RemoveErrorMessage command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self, id: str, lang: str = 'en_US', **kwargs) -> str:
        '''
        Remove a message from an existing Error by its ID.

        :param id: The unique identifier of the error.
        :type id: str
        :param lang: The language of the message to remove (default is 'en_US').
        :type lang: str
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        :return: The unique identifier of the updated error.
        :rtype: str
        '''

        # Retrieve the existing error.
        error = self.error_service.get(id)
        self.verify(
            expression=error,
            error_code=const.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id
        )

        # Remove the message.
        error.remove_message(lang)

        # Verify that at least one message remains.
        self.verify(
            expression=len(error.message) > 0,
            error_code=const.NO_ERROR_MESSAGES_ID,
            message=f'No error messages are defined for error ID {id}.',
            id=id
        )

        # Save the updated error.
        self.error_service.save(error)

        # Return the updated error id.
        return id

# ** command: remove_error
class RemoveError(Command):
    '''
    Command to remove an existing Error domain object by its ID.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the RemoveError command.

        :param error_repo: The error service to use.
        :type error_repo: ErrorService
        '''
        self.error_service = error_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> None:
        '''
        Remove an existing Error by its ID.

        :param id: The unique identifier of the error to remove.
        :type id: str
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        '''

        # Verify that the id parameter is not null or empty.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name='RemoveError'
        )

        # Remove the error.
        self.error_service.delete(id)

        # Return the removed error id.
        return id