# *** imports

# ** app
from ..configs import *
from ..models.error import *
from .core import *


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
