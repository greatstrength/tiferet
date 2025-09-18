# *** imports 

# ** core
from typing import List, Any

# ** app
from .settings import *


# *** models

# ** model: error_message
class ErrorMessage(ValueObject):
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
    def format(self, *args) -> str:
        '''
        Formats the error message text.

        :param args: The arguments to format the error message text with.
        :type args: tuple
        :return: The formatted error message text.
        :rtype: str
        '''

        # If there are no arguments, return the error message text.
        if not args:
            return self.text

        # Format the error message text and return it.
        return self.text.format(*args)


# ** model: error
class Error(Entity):
    '''
    An error object.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the error.'
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
    def new(name: str, id: str = None, error_code: str = None, message: List[ErrorMessage | Any] = [], **kwargs) -> 'Error':
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
        
        # Set Id as the name lower cased if not provided.
        if not id:
            id = name.lower().replace(' ', '_')

        # Set the error code as the id upper cased if not provided.
        if not error_code:
            error_code = id.upper().replace(' ', '_')

        # Convert any error message dicts to ErrorMessage objects.
        message_objs = []
        for msg in message:
            if isinstance(msg, ErrorMessage):
                message_objs.append(msg)
            elif not isinstance(msg, ErrorMessage) and isinstance(msg, dict):
                message_objs.append(ValueObject.new(ErrorMessage, **msg))


        # Create and return a new Error object.
        return Entity.new(
            Error,
            id=id,
            name=name,
            error_code=error_code,
            message=message_objs,
            **kwargs
        )

    # * method: format_message
    def format_message(self, lang: str = 'en_US', *args) -> str:
        '''
        Formats the error message text for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param args: The format arguments for the error message text.
        :type args: tuple
        :return: The formatted error message text.
        :rtype: str
        '''

        # Iterate through the error messages.
        for msg in self.message:

            # Skip if the language does not match.
            if msg.lang != lang:
                continue

            # Format the error message text.
            return msg.format(*args)
        
    # * method: format_response
    def format_response(self, lang: str = 'en_US', *args, **kwargs) -> Any:
        '''
        Formats the error response for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param args: The format arguments for the error message text.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The formatted error response.
        :rtype: dict
        '''

        # Format the error message text.
        error_message = self.format_message(lang, *args)

        # If the error message is not found, return no response.
        if not error_message:
            return None

        # Return the formatted error response.
        return dict(
            error_code=self.error_code,
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
            ValueObject.new(
                ErrorMessage,
                lang=lang,
                text=text
            )
        )