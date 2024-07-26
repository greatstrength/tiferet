from schematics import types as t

from . import object as obj


CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE = 'attribute'
CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY = 'dependency'
CONTAINER_ATTRIBUTE_TYPES = [
    CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE,
    CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY
]


class AttributeValue(obj.ValueObject):
    
    value = t.StringType(required=True)


class DependencyValue(obj.ValueObject):

    module_path = t.StringType(required=True)
    class_name = t.StringType(required=True)


class ContainerAttribute(obj.Entity):

    type = t.StringType(required=True)
    data = t.PolyModelType([AttributeValue, DependencyValue], required=True)

    @staticmethod
    def new(id: str, type: str, data: dict):
        return ContainerAttribute(dict(
            id=id,
            type=type,
            data=data
        ))
