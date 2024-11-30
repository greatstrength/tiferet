# *** imports 

# ** core
from ..domain import *


# *** models

# ** model: error_message0
class ErrorMessage(ValueObject):
    '''
    An error message object.
    '''

    # * attribute: lang
    lang = t.StringType(
        required=True,
        metadata=dict(
            description='The language of the error message text.'
        )
    )

    # * attribute: text
    text = t.StringType(
        required=True,
        metadata=dict(
            description='The error message text.'
        )
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'ErrorMessage':
        '''Initializes a new ErrorMessage object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ErrorMessage object.
        :rtype: ErrorMessage
        '''

        # Create and return a new ErrorMessage object.
        return super(ErrorMessage, ErrorMessage).new(
            ErrorMessage,
            **kwargs
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
    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the error.'
        )
    )

    # * attribute: error_code
    error_code = t.StringType(
        metadata=dict(
            description='The unique code of the error.'
        )
    )

    # * attribute: message
    message = t.ListType(
        t.ModelType(ErrorMessage),
        required=True,
        metadata=dict(
            description='The error message translations for the error.'
        )
    )

    # * method: new
    @staticmethod
    def new(name: str, id: str = None, error_code: str = None, **kwargs) -> 'Error':
        '''Initializes a new Error object.

        :param name: The name of the error.
        :type name: str
        :param id: The unique identifier for the error.
        :type id: str
        :param error_code: The error code for the error.
        :type error_code: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Error object.
        '''

        # Format name as upper case snake case.
        name = name.upper().replace(' ', '_')
        
        # Set Id as the name if not provided.
        if not id:
            id = name

        # Set the error code as the name if not provided.
        if not error_code:
            error_code = name

        # Create and return a new Error object.
        return super(Error, Error).new(
            Error,
            id=id,
            name=name,
            error_code=error_code,
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
