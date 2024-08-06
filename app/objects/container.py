from typing import List, Dict, Any

from schematics import types as t

from . import object as obj


CONTAINER_ATTRIBUTE_TYPE_DATA = 'data'
CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY = 'dependency'
CONTAINER_ATTRIBUTE_TYPES = [
    CONTAINER_ATTRIBUTE_TYPE_DATA,
    CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY
]


class AttributeValue(obj.ValueObject):

    value = t.StringType(required=True)


class DependencyValue(obj.ValueObject):

    module_path = t.StringType(required=True)
    class_name = t.StringType(required=True)


class ContainerAttribute(obj.Entity):

    type = t.StringType(required=True, choices=CONTAINER_ATTRIBUTE_TYPES)


class DataAttribute(ContainerAttribute):

    type = t.StringType(default=CONTAINER_ATTRIBUTE_TYPE_DATA)
    data = t.ModelType(AttributeValue, required=True)

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

    type = t.StringType(default=CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY)
    data = t.ModelType(DependencyValue, required=True)

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