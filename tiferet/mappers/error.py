"""Tiferet Error Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import Field

# ** app
from ..domain import (
    Error,
    ErrorMessage,
)
from .core import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: error_aggregate
class ErrorAggregate(Error, Aggregate):
    '''
    An aggregate representation of an error.
    '''

    # * method: rename
    def rename(self, new_name: str) -> None:
        '''
        Renames the error.

        :param new_name: The new name for the error.
        :type new_name: str
        :return: None
        :rtype: None
        '''

        # Update the name; validate_assignment=True handles re-validation.
        self.name = new_name

    # * method: set_message
    def set_message(self, lang: str, text: str) -> None:
        '''
        Sets the error message text for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param text: The error message text.
        :type text: str
        :return: None
        :rtype: None
        '''

        # Check if the message already exists for the language.
        for msg in self.message:
            if msg.lang == lang:
                msg.text = text
                return

        # If not, create a new ErrorMessage and add it via list reassignment.
        self.message = self.message + [ErrorMessage(lang=lang, text=text)]

    # * method: remove_message
    def remove_message(self, lang: str) -> None:
        '''
        Removes the error message for the specified language.

        :param lang: The language of the error message to remove.
        :type lang: str
        :return: None
        :rtype: None
        '''

        # Filter out the message with the specified language via list reassignment.
        self.message = [msg for msg in self.message if msg.lang != lang]


# ** mapper: error_message_config_object
class ErrorMessageConfigObject(ErrorMessage, TransferObject):
    '''
    A configuration data representation of an error message object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * method: map
    def map(self, **overrides) -> ErrorMessage:
        '''
        Maps the error message data to an error message object.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new error message object.
        :rtype: ErrorMessage
        '''

        # Map to the error message object.
        return super().map(ErrorMessage, **overrides)


# ** mapper: error_config_object
class ErrorConfigObject(Error, TransferObject):
    '''
    A configuration data representation of an error object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'message'}},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: message
    message: List[ErrorMessageConfigObject] = Field(
        default_factory=list,
        description='The error messages.',
    )

    # * method: map
    def map(self, **overrides) -> ErrorAggregate:
        '''
        Maps the error data to an error aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new error aggregate.
        :rtype: ErrorAggregate
        '''

        # Map the error data with nested message conversion.
        return super().map(
            ErrorAggregate,
            message=[msg.map() for msg in self.message],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, error: Error, **overrides) -> 'ErrorConfigObject':
        '''
        Creates an ErrorConfigObject from an Error model.

        :param error: The error model.
        :type error: Error
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new ErrorConfigObject.
        :rtype: ErrorConfigObject
        '''

        # Create a new ErrorConfigObject from the model, converting
        # the message list into ErrorMessageConfigObject instances.
        return super().from_model(
            error,
            message=[
                ErrorMessageConfigObject.from_model(msg)
                for msg in error.message
            ],
            **overrides,
        )
