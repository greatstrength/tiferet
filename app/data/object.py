from typing import List, Dict, Any

from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import ModelData
from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute


class ObjectAttributeData(ObjectAttribute, ModelData):
    '''
    A data representation of an object attribute.
    '''

    class Options():
        '''
        The options for the object attribute data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the object attribute data.
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }


class ModelObjectData(ModelObject, ModelData):
    '''A data representation of a model object.'''

    class Options():
        '''The default options for the model object data.'''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the model object data.
        roles = {
            'to_data.yaml': blacklist('id'),
            'to_object.yaml': wholelist()
        }

    id = t.StringType()
    attributes = t.ListType(t.ModelType(ObjectAttributeData), default=[])

    @staticmethod
    def new(**kwargs):
        '''Initializes a new ModelObjectData object.
        
        :return: A new ModelObjectData object.
        '''

        # Create a new ModelObjectData object.
        return ModelObjectData(kwargs, strict=False)

    @staticmethod
    def from_yaml_data(id: str, **kwargs) -> 'ModelObjectData':
        '''Initializes a new ModelObjectData object from YAML data.
        
        :param id: The unique identifier for the model object.
        :type id: str
        :return: A new ModelObjectData object.
        '''

        # Create a new ModelObjectData object.
        _data = ModelObjectData(dict(
            id=id,
            **kwargs
        ), strict=False)

        # Validate the new ModelObjectData object.
        _data.validate()

        # Return the new ModelObjectData object.
        return _data

    def map(self, role: str = 'to_object.yaml', **kwargs) -> ModelObject:
        '''Maps the model object data to a model object.
        
        :param role: The role for the mapping.
        :type role: str
        :return: A new model object
        '''

        # Map the model object data to a model object.
        return super().map(ModelObject, role, **kwargs)
