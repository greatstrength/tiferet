from schematics import types as t
from schematics import Model

class FeatureHandler(Model):
    name = t.StringType(required=True)
    function_path = t.StringType(required=True)
    data_mapping = t.StringType()
    use_services = t.StringType()
    params = t.DictType(t.StringType(), default={})
    log_activity = t.BooleanType(default=True)