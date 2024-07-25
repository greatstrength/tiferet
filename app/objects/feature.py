from schematics import types as t
from schematics import Model


class FeatureHandler(Model):
    name = t.StringType(required=True)
    import_path = t.StringType(required=True)
    function_name = t.StringType(required=True)
    params = t.DictType(t.StringType(), default={})
    return_to_data = t.BooleanType(default=False)
    data_key = t.StringType()
    return_to_result = t.BooleanType(default=False)
    exit_on_error = t.BooleanType(default=True)
    log_activity = t.BooleanType(default=True)


class FeatureGroup(Model):
    name = t.StringType(required=True)


class Feature(Model):
    name = t.StringType(required=True)
    use_role = t.StringType()
    data_mapping = t.StringType()
    header_mapping = t.StringType()
    group = t.ModelType(FeatureGroup)
    request_type_path = t.StringType() 
    handlers = t.ListType(t.ModelType(FeatureHandler), default=[])
    log_params = t.DictType(t.StringType(), default={})
