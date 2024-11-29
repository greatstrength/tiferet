# *** imports

# ** app
from ..configs import *
from ..domain import DataObject
from ..domain.error import Error, ErrorMessage


# *** data

# ** data: error_message_data
class ErrorMessageData(ErrorMessage, DataObject):
    '''
    A data representation of an error message object.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_data': DataObject.allow(),
            'to_model': DataObject.allow()
        }


# ** data: error_data
class ErrorData(Error, DataObject):
    '''
    A data representation of an error object.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_data': DataObject.deny('id'),
            'to_model': DataObject.allow()
        }

    # * attribute: message
    message = ListType(
        ModelType(ErrorMessageData),
        required=True,
        metadata=dict(
            description='The error messages.'
        )
    )

    # * to_primitive
    def to_primitive(self, role: str = 'to_data', **kwargs) -> dict:
        '''
        Converts the data object to a primitive dictionary.

        :param role: The role.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The primitive dictionary.
        :rtype: dict
        '''

        # Convert the data object to a primitive dictionary.
        return super().to_primitive(
            role,
            **kwargs
        )

    # * method: map
    def map(self, **kwargs) -> Error:
        '''
        Maps the error data to an error object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new error object.
        :rtype: Error
        '''

        # Map the error messages.
        return super().map(Error,
            **self.to_primitive('to_model'),
            **kwargs)

    # * method: from_data
    @staticmethod
    def from_data(**kwargs) -> 'ErrorData':
        '''
        Creates a new ErrorData object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ErrorData object.
        :rtype: ErrorData
        '''

        # Create a new ErrorData object.
        return super(ErrorData, ErrorData).from_data(
            ErrorData, 
            **kwargs
        )
