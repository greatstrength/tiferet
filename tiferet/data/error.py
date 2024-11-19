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
            'to_data.yaml': DataObject.allow('id'),
            'to_object.yaml': DataObject.allow()
        }


# ** data: error_data
class ErrorData(Error, DataObject):
    '''
    A data representation of an error object.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_data.yaml': DataObject.deny('id'),
            'to_object.yaml': DataObject.allow()
        }

    # * attribute: message
    message = ListType(
        ModelType(ErrorMessageData),
        required=True,
        metadata=dict(
            description='The error messages.'
        )
    )

    # * method: map
    def map(self, role: str = 'to_object.yaml', **kwargs):
        '''
        Maps the error data to an error object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new error object.
        :rtype: Error
        '''

        # Map the error messages.
        return super().map(Error, role, **kwargs)

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'ErrorData':
        '''
        Creates a new ErrorData object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ErrorData object.
        :rtype: ErrorData
        '''

        # Create a new ErrorData object.
        return ErrorData(
            super(ErrorData, ErrorData).new(**kwargs)
        )
