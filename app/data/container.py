from ..objects.data import DataObject
from schematics import types as t


class ContainerAttributeData(DataObject):
        
    type = t.StringType(required=True)
    data = t.DictType(t.DictType(t.StringType()), required=True)

class ContainerData(DataObject):

    attributes = t.DictType(t.ModelType(ContainerAttributeData), required=True, serialized_name='attrs', deserialize_from=['attrs'])

    @staticmethod
    def new(data: dict, **kwargs):
        return ContainerData(data, **kwargs)