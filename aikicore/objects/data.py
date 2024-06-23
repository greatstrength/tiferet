from schematics import Model, types as t
from schematics.types.serializable import serializable
from schematics.transforms import wholelist, whitelist, blacklist

class DefaultOptions():
    serialize_when_none = False
    roles = {
        'to_object': wholelist(),
        'to_data': wholelist()
    }
