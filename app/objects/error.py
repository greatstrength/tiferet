from schematics import Model, types as t

from ..objects import Entity
from ..objects import ValueObject


class ErrorMessage(ValueObject):
    '''
    An error message object.
    '''

    lang = t.StringType(
        required=True,
        metadata=dict(
            description='The language of the error message text.'
        )
    )

    text = t.StringType(
        required=True,
        metadata=dict(
            description='The error message text.'
        )
    )

    def format(self, *args):
        '''
        Formats the error message text.

        :param args: The arguments to format the error message text with.
        :type args: tuple
        '''

        # If there are no arguments, return.
        if not args:
            return

        # Format the error message text.
        self.text = self.text.format(*args)


class Error(Entity):
    '''
    An error object.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the error.'
        )
    )

    error_code = t.StringType(
        metadata=dict(
            description='The unique code of the error.'
        )
    )

    message = t.ListType(
        t.ModelType(ErrorMessage),
        required=True,
        metadata=dict(
            description='The error message translations for the error.'
        )
    )

    def set_format_args(self, *args):
        '''
        Sets the format arguments for the error messages.
        
        :param args: The format arguments for the error messages.
        :type args: tuple
        '''

        # Set the format arguments for the error messages.
        for msg in self.message:
            msg.format(*args)

    def get_message(self, lang: str = 'en_US', *args) -> str:
        '''
        Returns the error message text for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param args: The format arguments for the error message text.
        :type args: tuple
        :return: The error message text.
        :rtype: str
        '''

        # Iterate through the error messages.
        for msg in self.message:

            # Skip if the language does not match.
            if msg.lang != lang:
                continue

            # Set the error message text.
            text = msg.text

            # Format the error message text if there are arguments.
            if args:
                text = text.format(*args)

            # Return the error message text.
            return text

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

        # Upper snake case the name.
        name = name.upper()

        # Set the error code as the name if not provided.
        if not error_code:
            error_code = name

        # Set Id as the name if not provided.
        if not id:
            id = name

        # Create a new Error object.
        obj = Error(dict(
            id=id,
            name=name,
            error_code=error_code,
            **kwargs),
            strict=False
        )

        # Validate and return the new Error object.
        obj.validate()
        return obj
