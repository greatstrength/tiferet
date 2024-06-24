from schematics import Model, types as t


class ModelObject(Model):
    pass


class Entity(ModelObject):
    id = t.StringType(required=True)


class ValueObject(ModelObject):
    pass
