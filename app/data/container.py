from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import DataObject
from ..objects.container import ContainerAttribute


class ContainerAttributeData(ContainerAttribute, DataObject):

    class Options():
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }

    type = t.StringType(required=True)
    data = t.DictType(t.DictType(t.StringType()), required=True)

    @staticmethod
    def new(id: str, type: str, data: dict):
        return ContainerAttributeData(dict(
            id=id,
            type=type,
            data=data
        ))
