from typing import List, Dict, Any

from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import ModelData
from ..objects.data import DefaultOptions
from ..objects.error import Error
from ..objects.error import ErrorMessage


class ErrorMessageData(ErrorMessage, ModelData):

    class Options():
        serialize_when_none = False
        roles = {
            'to_data.yaml': wholelist('id'),
            'to_object.yaml': wholelist()
        }


class ErrorData(Error, ModelData):

    class Options():
        serialize_when_none = False
        roles = {
            'to_data.yaml': blacklist('id'),
            'to_object.yaml': wholelist()
        }

    message = t.ListType(t.ModelType(ErrorMessageData), required=True)

    def map(self, role: str = 'to_object.yaml', lang: str = 'en_US', **kwargs):
        
        return super().map(Error, role, **kwargs)

    @staticmethod
    def new(**kwargs):

        # Create a new ErrorData object.
        _data: ErrorData = ErrorData(dict(
            **kwargs
        ))

        # Validate the new ErrorData object.
        _data.validate()

        # Return the new ErrorData object.
        return _data

    
    @staticmethod
    def from_yaml_data(id: str, **kwargs):

        # Create a new ErrorData object.
        return ErrorData.new(
            id=id,
            **kwargs
        )
