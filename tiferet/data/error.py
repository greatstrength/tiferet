"""Tiferet Error Data Objects"""

# *** imports

# ** app
from ..models import (
    Error,
    ErrorMessage,
    ListType,
    ModelType,
)
from ..contracts import (
    ErrorContract,
)
from .settings import (
    DataObject,
)

# *** data

# ** data: error_config_data
class ErrorConfigData(Error, DataObject):
    '''
    A data representation of an error object.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('message'),
            'to_data.yaml': DataObject.deny('id', 'message'),
            'to_data.json': DataObject.deny('id', 'message')
        }

    # * class: error_message_config_data
    class ErrorMessageConfigData(ErrorMessage, DataObject):
        '''
        A data representation of an error message.
        '''

        pass

    # * attribute: message
    message = ListType(
        ModelType(ErrorMessageConfigData),
        required=True,
        metadata=dict(
            description='The error messages.'
        )
    )

    # * to_primitive
    def to_primitive(self, role: str, **kwargs) -> dict:
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
    def from_data(**kwargs) -> 'ErrorConfigData':
        '''
        Creates a new ErrorData object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ErrorData object.
        :rtype: ErrorData
        '''

        # Create a new ErrorData object.
        return super(ErrorConfigData, ErrorConfigData).from_data(
            ErrorConfigData, 
            **kwargs
        )