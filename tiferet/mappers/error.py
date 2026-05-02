"""Tiferet Error Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import Field

# ** app
from ..domain import Error, ErrorMessage
from .settings import Aggregate, TransferObject

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

        # Update the name; validate_assignment=True triggers validation.
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

        # Update existing message in place if a matching language is found.
        for msg in self.message:
            if msg.lang == lang:
                msg.text = text
                return

        # Otherwise append a new ErrorMessage; reassignment triggers validation.
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

        # Reassign so validate_assignment=True triggers validation.
        self.message = [msg for msg in self.message if msg.lang != lang]

# ** mapper: error_message_yaml_object
class ErrorMessageYamlObject(ErrorMessage, TransferObject):
    '''
    A YAML data representation of an error message object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {'by_alias': True},
    }

    # * method: map
    def map(self, **overrides) -> ErrorMessage:
        '''
        Maps the error message data to an error message object.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new ErrorMessage instance.
        :rtype: ErrorMessage
        '''

        # Delegate to the base mapper, targeting ErrorMessage.
        return super().map(ErrorMessage, **overrides)

# ** mapper: error_yaml_object
class ErrorYamlObject(Error, TransferObject):
    '''
    A YAML data representation of an error object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'message'}},
        'to_data.yaml': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: message
    message: List[ErrorMessageYamlObject] = Field(
        default_factory=list,
        description='The error messages.',
    )

    # * method: map
    def map(self, **overrides) -> ErrorAggregate:
        '''
        Maps the error data to an error aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new ErrorAggregate instance.
        :rtype: ErrorAggregate
        '''

        # Convert nested YAML messages into runtime ErrorMessage instances.
        return super().map(
            ErrorAggregate,
            message=[msg.map() for msg in self.message],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, error: Error, **overrides) -> 'ErrorYamlObject':
        '''
        Creates an ErrorYamlObject from an Error model.

        :param error: The error model to copy from.
        :type error: Error
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new ErrorYamlObject instance.
        :rtype: ErrorYamlObject
        '''

        # Convert each runtime message into an ErrorMessageYamlObject.
        return super().from_model(
            error,
            message=[ErrorMessageYamlObject.from_model(msg) for msg in error.message],
            **overrides,
        )
