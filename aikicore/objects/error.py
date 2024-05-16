from schematics import Model, types as t

class Error(Model):
    error_code = t.StringType(required=True)
    error_name = t.StringType(required=True)
    message = t.StringType(required=True)