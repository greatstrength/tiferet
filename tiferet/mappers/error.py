"""Tiferet Error Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..entities import (
    Error,
    ErrorMessage,
    ListType,
    ModelType,
)
from .settings import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: error_aggregate
class ErrorAggregate(Error, Aggregate):
    '''
    An aggregate representation of an error.
    '''

    # * method: new
    @staticmethod
    def new(
        error_data: Dict[str, Any],
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'ErrorAggregate':
        '''
        Initializes a new error aggregate.

        :param error_data: The data to create the error aggregate from.
        :type error_data: dict
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new error aggregate.
        :rtype: ErrorAggregate
        '''

        # Create a new error aggregate from the provided data.
        return Aggregate.new(
            ErrorAggregate,
            validate=validate,
            strict=strict,
            **error_data,
            **kwargs
        )

    # * method: rename
    def rename(self, new_name: str) -> None:
        '''
        Renames the error.

        :param new_name: The new name for the error.
        :type new_name: str
        :return: None
        :rtype: None
        '''

        # Update the name.
        self.name = new_name

        # Perform final aggregate validation.
        self.validate()

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

        # If not, create a new ErrorMessage object and add it to the message list.
        from ..entities import ModelObject
        self.message.append(
            ModelObject.new(
                ErrorMessage,
                lang=lang,
                text=text
            )
        )

    # * method: remove_message
    def remove_message(self, lang: str) -> None:
        '''
        Removes the error message for the specified language.

        :param lang: The language of the error message to remove.
        :type lang: str
        :return: None
        :rtype: None
        '''

        # Filter out the message with the specified language.
        self.message = [msg for msg in self.message if msg.lang != lang]

# ** mapper: error_message_yaml_object
class ErrorMessageYamlObject(ErrorMessage, TransferObject):
    '''
    A YAML data representation of an error message object.
    '''

    class Options():
        '''
        The options for the error message data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny(),
            'to_data.yaml': TransferObject.deny(),
            'to_data.json': TransferObject.deny(),
        }

    # * method: map
    def map(self, **kwargs) -> ErrorMessage:
        '''
        Maps the error message data to an error message object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new error message object.
        :rtype: ErrorMessage
        '''

        # Map to the error message object.
        return super().map(
            ErrorMessage,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(error_message: ErrorMessage, **kwargs) -> 'ErrorMessageYamlObject':
        '''
        Creates an ErrorMessageYamlObject from an ErrorMessage model.

        :param error_message: The error message model.
        :type error_message: ErrorMessage
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ErrorMessageYamlObject.
        :rtype: ErrorMessageYamlObject
        '''

        # Create a new ErrorMessageYamlObject from the model.
        return TransferObject.from_model(
            ErrorMessageYamlObject,
            error_message,
            **kwargs,
        )


# ** mapper: error_yaml_object
class ErrorYamlObject(Error, TransferObject):
    '''
    A YAML data representation of an error object.
    '''

    class Options():
        '''
        The options for the error data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('message'),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id'),
        }

    # * attribute: message
    message = ListType(
        ModelType(ErrorMessageYamlObject),
        required=True,
        metadata=dict(
            description='The error messages.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> ErrorAggregate:
        '''
        Maps the error data to an error aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new error aggregate.
        :rtype: ErrorAggregate
        '''

        # Map the error data.
        return super().map(
            ErrorAggregate,
            message=[msg.map() for msg in self.message],
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(error: Error, **kwargs) -> 'ErrorYamlObject':
        '''
        Creates an ErrorYamlObject from an Error model.

        :param error: The error model.
        :type error: Error
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ErrorYamlObject.
        :rtype: ErrorYamlObject
        '''

        # Create a new ErrorYamlObject from the model, converting
        # the message list into ErrorMessageYamlObject instances.
        return TransferObject.from_model(
            ErrorYamlObject,
            error,
            message=[
                TransferObject.from_model(ErrorMessageYamlObject, msg)
                for msg in error.message
            ],
            **kwargs,
        )
