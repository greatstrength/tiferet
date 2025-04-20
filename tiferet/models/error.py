# *** imports 

# ** app
from .settings import *


# *** models

# ** model: error_message0
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

    # * method: format
    def format(self, lang: str = 'en_US', *args) -> str:
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