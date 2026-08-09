"""Tiferet Error Events"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any
)

# ** app
from .core import DomainEvent, a
from ..domain import Error
from ..interfaces import ErrorService
from ..mappers import ErrorAggregate

# *** events

# ** event: error_event
# >> see: @guides/events/error.md#errorevent
class ErrorEvent(DomainEvent):
    '''
    Base event providing the shared ErrorService dependency for error domain events.
    '''

    # * attribute: error_service
    error_service: ErrorService

    # * init
    def __init__(self, error_service: ErrorService):
        '''
        Initialize the error event with its shared service dependency.

        :param error_service: The error service shared across error events.
        :type error_service: ErrorService
        '''

        # Set the error service dependency.
        self.error_service = error_service

# ** event: add_error
# >> see: @guides/events/error.md#adderror
class AddError(ErrorEvent):
    '''
    Event to add a new Error domain object to the repository.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'message'])
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

        # Check if an error with the same ID already exists.
        exists = self.error_service.exists(id)
        self.verify(
            expression=exists is False,
            error_code=a.error.ERROR_ALREADY_EXISTS_ID,
            message=f'An error with ID {id} already exists.',
            id=id
        )

        # Create the Error aggregate.
        error_messages = [{'lang': lang, 'text': message}] + additional_messages
        new_error = ErrorAggregate(
            id=id,
            name=name,
            message=error_messages,
        )

        # Save the new error.
        self.error_service.save(new_error)

        # Return the new error.
        return new_error

# ** event: get_error
# >> see: @guides/events/error.md#geterror
class GetError(ErrorEvent):
    '''
    Event to retrieve an Error domain object by its ID.
    '''

    # * method: execute
    def execute(self, id: str, **kwargs) -> Error:
        '''
        Retrieve an Error by its ID.

        :param id: The unique identifier of the error.
        :type id: str
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

        # If not found, raise structured error.
        self.raise_error(
            error_code=a.error.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id,
        )

# ** event: list_errors
# >> see: @guides/events/error.md#listerrors
class ListErrors(ErrorEvent):
    '''
    Event to list all Error domain objects.
    '''

    # * method: execute
    def execute(self, **kwargs) -> List[Error]:
        '''
        List all Errors.

        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        :return: The list of Error domain model instances.
        :rtype: List[Error]
        '''

        # Retrieve all errors from the repository.
        return self.error_service.list()

# ** event: rename_error
# >> see: @guides/events/error.md#renameerror
class RenameError(ErrorEvent):
    '''
    Event to rename an existing Error domain object.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['new_name'])
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

        # Retrieve the existing error.
        error = self.error_service.get(id)

        # Verify that the error exists.
        self.verify(
            expression=error,
            error_code=a.error.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id
        )

        # Update the name.
        error.rename(new_name)

        # Save the updated error.
        self.error_service.save(error)

        # Return the updated error.
        return error

# ** event: set_error_message
# >> see: @guides/events/error.md#seterrormessage
class SetErrorMessage(ErrorEvent):
    '''
    Event to set the message of an existing Error domain object.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['message'])
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

        # Retrieve the existing error.
        error = self.error_service.get(id)

        # Verify that the error exists.
        self.verify(
            expression=error,
            error_code=a.error.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id
        )

        # Update the message.
        error.set_message(lang, message)

        # Save the updated error.
        self.error_service.save(error)

        # Return the updated error id.
        return id

# ** event: remove_error_message
# >> see: @guides/events/error.md#removeerrormessage
class RemoveErrorMessage(ErrorEvent):
    '''
    Event to remove a message from an existing Error domain object.
    '''

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
            error_code=a.error.ERROR_NOT_FOUND_ID,
            message=f'Error not found: {id}.',
            id=id
        )

        # Remove the message.
        error.remove_message(lang)

        # Verify that at least one message remains.
        self.verify(
            expression=len(error.message) > 0,
            error_code=a.error.NO_ERROR_MESSAGES_ID,
            message=f'No error messages are defined for error ID {id}.',
            id=id
        )

        # Save the updated error.
        self.error_service.save(error)

        # Return the updated error id.
        return id

# ** event: remove_error
# >> see: @guides/events/error.md#removeerror
class RemoveError(ErrorEvent):
    '''
    Event to remove an existing Error domain object by its ID.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> None:
        '''
        Remove an existing Error by its ID.

        :param id: The unique identifier of the error to remove.
        :type id: str
        :param kwargs: Additional context (passed to error if raised).
        :type kwargs: dict
        '''

        # Remove the error.
        self.error_service.delete(id)

        # Return the removed error id.
        return id
