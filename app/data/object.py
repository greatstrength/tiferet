from typing import List, Dict, Any

from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import ModelData
from ..objects.data import DefaultOptions
from ..objects.object import ModelObject


class ModelObjectData(ModelObject, ModelData):
    '''A data representation of a model object.'''

    class Options(DefaultOptions):
        '''The default options for the model object data.'''

        roles = {
            'to_data.yaml': blacklist('id'),
            'to_object.yaml': wholelist()
        }

    id = t.StringType()

    @staticmethod
    def new(**kwargs):
        '''Initializes a new ModelObjectData object.
        
        :return: A new ModelObjectData object.
        '''

        # Create a new ModelObjectData object.
        return ModelObjectData(kwargs)

    def map(self, role: str = 'to_object.yaml', **kwargs) -> ModelObject:
        '''Maps the model object data to a model object.
        
        :param id: The unique identifier for the model object.
        :type id: str
        :param role: The role for the mapping.
        :type role: str
        :return: A new model object
        '''

        # Map the model object data to a model object.
        return super().map(ModelObject, role, **kwargs)