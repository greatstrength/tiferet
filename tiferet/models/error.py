"""Tiferet Error Models"""

# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import (
    ModelObject,
    StringType,
    ListType,
    ModelType,
)

# *** models

# ** model: error_message
class ErrorMessage(ModelObject):
    '''
    An error message object.
    '''

    # * attribute: lang
    lang = StringType(
        required=True,
        metadata=dict(
            description='The language of the error message text.'
        )
    )

    # * attribute: text
    text = StringType(
        required=True,
        metadata=dict(
            description='The error message text.'
        )
    )

    # * method: format
    def format(self, **kwargs) -> str:
        '''
        Formats the error message text.

        :param kwargs: The format keyword arguments for the error message text.
        :type kwargs: dict
        :return: The formatted error message text.
        :rtype: str
        '''

        # If there are no arguments, return the error message text.
        if not kwargs:
            return self.text

        # Format the error message text and return it.
        return self.text.format(**kwargs)

# ** model: error
class Error(ModelObject):
    '''
    An error object.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the error.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the error.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the error.'
        )
    )

    # * attribute: error_code
    error_code = StringType(
        metadata=dict(
            description='The unique code of the error.'
        )
    )

    # * attribute: message
    message = ListType(
        ModelType(ErrorMessage),
        required=True,
        metadata=dict(
            description='The error message translations for the error.'
        )
    )

    # * method: new
    @staticmethod
    def new(name: str, id: str, message: List[Dict[str, str]] = [], **kwargs) -> 'Error':
        '''Initializes a new Error object.

        :param name: The name of the error.
        :type name: str
        :param id: The unique identifier for the error.
        :type id: str
        :param error_code: The error code for the error.
        :type error_code: str
        :param message: The error message translations for the error.
        :type message: list 
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Error object.
        '''

        # Set the error code as the id upper cased.
        error_code = id.upper().replace(' ', '_')

        # Create and return a new Error object.
        return ModelObject.new(
            Error,
            id=id,
            name=name,
            error_code=error_code,
            message=message,
            **kwargs
        )
    
    # * method: rename
    def rename(self, new_name: str):
        '''
        Renames the error.

        :param new_name: The new name for the error.
        :type new_name: str
        '''

        # Update the name.
        self.name = new_name

    # * method: format_message
    def format_message(self, lang: str = 'en_US', **kwargs) -> str:
        '''
        Formats the error message text for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param kwargs: Additional format arguments for the error message text.
        :type kwargs: dict
        :return: The formatted error message text.
        :rtype: str
        '''

        # Iterate through the error messages.
        for msg in self.message:

            # Skip if the language does not match.
            if msg.lang != lang:
                continue

            # Format the error message text.
            return msg.format(**kwargs)

    # * method: format_response
    def format_response(self, lang: str = 'en_US', **kwargs) -> Any:
        '''
        Formats the error response for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param kwargs: Additional format arguments for the error message text.
        :type kwargs: dict
        :return: The formatted error response.
        :rtype: dict
        '''

        # Format the error message text.
        error_message = self.format_message(lang, **kwargs)

        # If the error message is not found, return no response.
        if not error_message:
            return None

        # Return the formatted error response.
        return dict(
            error_code=self.id,
            name=self.name,
            message=error_message,
            **kwargs
        )

    # * method: set_message
    def set_message(self, lang: str, text: str):
        '''
        Sets the error message text for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param text: The error message text.
        :type text: str
        '''

        # Check if the message already exists for the language.
        for msg in self.message:
            if msg.lang == lang:
                msg.text = text
                return

        # If not, create a new ErrorMessage object and add it to the message list.
        self.message.append(
            ModelObject.new(
                ErrorMessage,
                lang=lang,
                text=text
            )
        )

    # * method: remove_message
    def remove_message(self, lang: str):
        '''
        Removes the error message for the specified language.

        :param lang: The language of the error message to remove.
        :type lang: str
        '''

        # Filter out the message with the specified language.
        self.message = [msg for msg in self.message if msg.lang != lang]