from schematics import Model, types as t


class ModelObject(Model):
    name = t.StringType()
    description = t.StringType()


class Entity(ModelObject):
    id = t.StringType(required=True)


class ValueObject(ModelObject):
    pass
