from schematics import Model, types as t

class ModelObject(Model):
    name = t.StringType()
    description = t.StringType()
