from schematics import Model, types as t

from ..objects import Entity
from ..objects import ValueObject


class ErrorMessage(ValueObject):

    lang = t.StringType(required=True)
    text = t.StringType(required=True)

    def format(self, *args):
        if not args:
            return
        self.text = self.text.format(*args)


class Error(Entity):
    '''
    An error object.
    '''

    name = t.StringType(required=True, deserialize_from=['name', 'error_name'])
    error_code = t.StringType()
    message = t.ListType(t.ModelType(ErrorMessage), required=True)

    def set_format_args(self, *args):
        for msg in self.message:
            msg.format(*args)

    def get_message(self, lang: str = 'en_US', *args) -> str:
        for msg in self.message:
            if msg.lang != lang:
                continue
            text = msg.text
            if args:
                text = text.format(*args)
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

        # Validate the new Error object.
        obj.validate()

        # Return the new Error object.
        return obj
