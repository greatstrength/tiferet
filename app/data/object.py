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

    @staticmethod
    def new(required: bool = False, **kwargs) -> 'ObjectAttributeData':
        '''Initializes a new ObjectAttributeData object.
        
        :param required: Whether the attribute is required.
        :type required: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ObjectAttributeData object.
        :rtype: ObjectAttributeData
        '''

        # Set the required flag to None if it is false.
        required = None if not required else required

        # Create a new ObjectAttributeData object.
        return ObjectAttributeData( 
            super(ObjectAttributeData, ObjectAttributeData).new(
                required=required,
                **kwargs
            )
        )


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

    @staticmethod
    def new(required: bool = None, **kwargs) -> 'ObjectMethodParameterData':
        '''Initializes a new ObjectMethodParameterData object.
        
        :param required: Whether the parameter is required.
        :type required: bool
        :return: A new ObjectMethodParameterData object.
        :rtype: ObjectMethodParameterData
        '''

        # Set the required flag to None if it is false.
        required = None if not required else required

        # Create a new ObjectMethodParameterData object.
        return ObjectMethodParameterData(
            super(ObjectMethodParameterData, ObjectMethodParameterData).new(
                required=required,
                **kwargs
            )
        )


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

    @staticmethod
    def new(**kwargs) -> 'ObjectMethodCodeBlockData':
        '''Initializes a new ObjectMethodCodeBlockData object.
        
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new ObjectMethodCodeBlockData object.
        :rtype: ObjectMethodCodeBlockData
        '''

        # Create a new ObjectMethodCodeBlockData object.
        return ObjectMethodCodeBlockData(
            super(ObjectMethodCodeBlockData, ObjectMethodCodeBlockData).new(**kwargs)
        )


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

    @staticmethod
    def new(parameters: List[Any], code_block: List[Any], **kwargs) -> 'ObjectMethodData':
        '''Initializes a new ObjectMethodData object.
        
        :param parameters: The model object method parameters.
        :type parameters: List[Any]
        :param code_block: The model object method code block.
        :type code_block: List[Any]
        :param kwargs: Additional keyword arguments.
        :return: A new ObjectMethodData object.
        :rtype: ObjectMethodData
        '''

        # Map the parameters to ObjectMethodParameterData objects.
        parameters = [
            ObjectMethodParameterData.new(**parameter)
            for parameter in parameters
        ]

        # Map the code block to ObjectMethodCodeBlockData objects.
        code_block = [
            ObjectMethodCodeBlockData.new(**block)
            for block in code_block
        ]

        # Create a new ObjectMethodData object.
        return ObjectMethodData(
            super(
                ObjectMethodData, ObjectMethodData).new(
                parameters=parameters,
                code_block=code_block,
                **kwargs
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
    def new(attributes: List[Any], methods: List[Any], **kwargs):
        '''Initializes a new ModelObjectData object.
        
        :param attributes: The model object attributes.
        :type attributes: List[Any]
        :param methods: The model object methods.
        :type methods: List[Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ModelObjectData object.
        :rtype: ModelObjectData
        '''

        # Map the attributes to ObjectAttributeData objects.
        attributes = [
            ObjectAttributeData.new(**attribute)
            for attribute in attributes
        ]

        # Map the methods to ObjectMethodData objects.
        methods = [
            ObjectMethodData.new(**method)
            for method in methods
        ]

        # Create a new ModelObjectData object.
        return ModelObjectData(
            super(ModelObjectData, ModelObjectData).new(
                attributes=attributes,
                methods=methods,
                **kwargs
            )
        )

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
