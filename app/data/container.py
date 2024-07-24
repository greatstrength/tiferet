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

    def map(self, role: str, **kwargs):
        return super().map(ContainerAttribute, role, **kwargs)

    @staticmethod
    def new(id: str, type: str, data: dict):
        return ContainerAttributeData(dict(
            id=id,
            type=type,
            data=data
        ))
