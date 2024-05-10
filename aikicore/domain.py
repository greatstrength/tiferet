from typing import List, Any
from schematics import types as t, Model
from schematics.transforms import blacklist, whitelist
from schematics.types.serializable import serializable


class AppDomainModel(Model):

    name = t.StringType()
    description = t.StringType()


class AppValueObject(AppDomainModel):
    pass


class AppEntity(AppDomainModel):

    id = t.StringType(required=True)
