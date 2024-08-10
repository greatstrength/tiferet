from typing import List, Dict, Any

from schematics import types as t

from . import object as obj


CONTAINER_ATTRIBUTE_TYPE_DATA = 'data'
CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY = 'dependency'
CONTAINER_ATTRIBUTE_TYPES = [
    CONTAINER_ATTRIBUTE_TYPE_DATA,
    CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY
]


class ContainerAttribute(obj.Entity):
    '''
    A container attribute object.
    '''

    type = t.StringType(
        required=True,
        choices=CONTAINER_ATTRIBUTE_TYPES,
        metadata=dict(
            description='The type of container attribute.'
        )
    )


class DataValue(obj.ValueObject):
    '''
    A container attribute data value object.
    '''

    value = t.StringType(
        required=True,
        metadata=dict(
            description='The value for a data attribute.'
        )
    )


class DependencyValue(obj.ValueObject):
    '''
    A container attribute dependency value object.
    '''

    module_path = t.StringType(
        required=True,
        metadata=dict(
            description='The module path for a dependency attribute.'
        )
    )

    class_name = t.StringType(
        required=True,
        metadata=dict(
            description='The class name for a dependency attribute.'
        )
    )


class DataAttribute(ContainerAttribute):
    '''
    A container attribute object for a data-type value.
    '''

    type = t.StringType(
        default=CONTAINER_ATTRIBUTE_TYPE_DATA,
        metadata=dict(
            description='The type of container attribute (defaults to data).'
        )
    )

    data = t.ModelType(
        DataValue,
        required=True,
        metadata=dict(
            description='The data for a data attribute.'
        )
    )

    @staticmethod
    def new(**kwargs) -> 'DataAttribute':
        '''Initializes a new DataAttribute object.
        
        :return: A new DataAttribute object.
        '''

        # Create a new DataAttribute object.
        obj = DataAttribute(
            dict(**kwargs),
            strict=False
        )

        # Validate the new DataAttribute object.
        obj.validate()

        # Return the new DataAttribute object.
        return obj


class DependencyAttribute(ContainerAttribute):
    '''
    A container attribute object for a dependency-type value.
    '''

    type = t.StringType(
        default=CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY,
        metadata=dict(
            description='The type of container attribute (defaults to dependency).'
        )
    )

    data = t.ModelType(
        DependencyValue,
        required=True,
        metadata=dict(
            description='The data for a dependency attribute.'
        )
    )

    @staticmethod
    def new(**kwargs) -> 'DependencyAttribute':
        '''Initializes a new DependencyAttribute object.
        
        :return: A new DependencyAttribute object.
        '''

        # Create a new DependencyAttribute object.
        obj = DependencyAttribute(
            dict(**kwargs),
            strict=False
        )

        # Validate the new DependencyAttribute object.
        obj.validate()

        # Return the new DependencyAttribute object.
        return obj
