from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import ModelData
from ..objects.container import ContainerAttribute
from ..objects.container import AttributeValue
from ..objects.container import DependencyValue
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY


class ContainerAttributeData(ContainerAttribute, ModelData):

    class Options():
        roles = {
            'to_object.yaml': blacklist('data'),
            'to_data.yaml': wholelist()
        }
        serialize_when_none = False

    data = t.DictType(t.DictType(t.StringType), default={}, required=True)

    def map(self, role: str, flag: str, **kwargs):
        data = self.data[flag]
        if self.type == CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE:
            data = AttributeValue(data)
        elif self.type == CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY:
            data = DependencyValue(data)
        return super().map(ContainerAttribute, role, data=data, **kwargs)

    @staticmethod
    def new(id: str, type: str, data: dict):
        return ContainerAttributeData(dict(
            id=id,
            type=type,
            data=data
        ))
