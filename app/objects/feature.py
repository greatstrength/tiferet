from schematics import types as t

from .object import Entity
from .object import ValueObject


class FeatureHandler(ValueObject):
    name = t.StringType(required=True)
    attribute_id = t.StringType(required=True)
    params = t.DictType(t.StringType(), default={})
    return_to_data = t.BooleanType(default=False)
    data_key = t.StringType()
    exit_on_error = t.BooleanType(default=True)
    log_activity = t.BooleanType(default=True)


class FeatureGroup(ValueObject):
    name = t.StringType(required=True)


class Feature(Entity):
    name = t.StringType(required=True)
    use_role = t.StringType()
    group = t.ModelType(FeatureGroup)
    request_type_path = t.StringType()
    handlers = t.ListType(t.ModelType(FeatureHandler), default=[])
    log_params = t.DictType(t.StringType(), default={})
