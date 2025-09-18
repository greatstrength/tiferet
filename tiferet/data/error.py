# *** imports

# ** app
from ..configs import *
from ..data import DataObject
from ..models.error import *
from ..contracts.error import Error as ErrorContract


# *** data

# ** data: error_data
class ErrorData(Error, DataObject):
    '''
    A data representation of an error object.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_data': DataObject.deny('id', 'message'),
            'to_model': DataObject.deny('message')
        }

    # * attribute: message
    message = ListType(
        ModelType(ErrorMessage),
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
        return dict(
            **super().to_primitive(
                role,
                **kwargs
            ),
            message=[msg.to_primitive() for msg in self.message]
        ) 
        

    # * method: map
    def map(self, **kwargs) -> ErrorContract:
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
