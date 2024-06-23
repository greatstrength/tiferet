from schematics import Model, types as t
from schematics.types.serializable import serializable
from schematics.transforms import wholelist, whitelist, blacklist


class DefaultOptions():
    serialize_when_none = False
    roles = {
        'to_object': wholelist(),
        'to_data': wholelist()
    }


class DataObject(Model):

    def map(self, type: type, role: str = 'to_object', **kwargs):
        return type(dict(
            **kwargs,
            **self.to_primitive(role=role)
        ), strict=False)
