from schematics import types as t, Model

class ExecuteFeature(Model):

    feature_id = t.StringType(required=True)
    data = t.StringType(required=True)
    debug = t.BooleanType(default=False)