from typing import List, Dict, Any

from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import ModelData
from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute
from ..objects.object import ObjectMethod
from ..objects.object import ObjectMethodParameter
from ..objects.object import ObjectMethodCodeBlock


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


class ObjectMethodParameterData(ObjectMethodParameter, ModelData):
    '''
    A data representation of an object method parameter.
    '''

    class Options():
        '''
        The options for the object method parameter data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the object method parameter data.
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }


class ObjectMethodCodeBlockData(ObjectMethodCodeBlock, ModelData):
    '''
    A data representation of an object method code block.
    '''

    class Options():
        '''
        The options for the object method code block data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the object method code block data.
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }


class ObjectMethodData(ObjectMethod, ModelData):
    '''
    A data representation of an object method.
    '''

    class Options():
        '''
        The options for the object method data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the object method data.
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }

    parameters = t.ListType(
        t.ModelType(ObjectMethodParameterData),
        default=[],
        metadata=dict(
            description='The model object method parameters.'
        )
    )

    code_block = t.ListType(
        t.ModelType(ObjectMethodCodeBlockData),
        default=[],
        metadata=dict(
            description='The model object method code block.'
        )
    )


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

    id = t.StringType(
        metadata=dict(
            description='The model object unique identifier.'
        )
    )

    attributes = t.ListType(
        t.ModelType(ObjectAttributeData),
        default=[],
        metadata=dict(
            description='The model object attributes.'
        )
    )

    methods = t.ListType(
        t.ModelType(ObjectMethodData),
        default=[],
        metadata=dict(
            description='The model object methods.'
        )
    )

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
