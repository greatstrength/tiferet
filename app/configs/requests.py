from schematics import types as t
from schematics import Model

from ..objects.cli import CLI_ARGUMENT_DATA_TYPES as DATA_TYPES
from ..objects.cli import CLI_ARGUMENT_DATA_TYPE_DEFAULT as DATA_TYPE_DEFAULT
from ..objects.cli import CLI_ARGUMENT_TYPES as ARG_TYPES
from ..objects.cli import CLI_ARGUMENT_TYPE_DEFAULT as ARG_TYPE_DEFAULT
from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute
from ..objects.container import ContainerAttribute


class AddCliCommand(Model):
    
    interface_id = t.StringType(required=True)
    group_id = t.StringType(required=True)
    command_key = t.StringType(required=True)
    name = t.StringType(required=True)
    help = t.StringType(required=True, deserialize_from=['help', 'description'])


class AddCliArgument(Model):

    name = t.StringType(required=True)
    interface_id = t.StringType(required=True)
    help = t.StringType(required=True, deserialize_from=['help', 'description'])
    arg_type = t.StringType(default=ARG_TYPE_DEFAULT, choices=ARG_TYPES)
    feature_id = t.StringType()
    flags = t.ListType(t.StringType(), default=[])
    type = t.StringType(default=DATA_TYPE_DEFAULT, choices=DATA_TYPES)
    required = t.BooleanType()
    default = t.StringType()
    positional = t.BooleanType()
    choices = t.ListType(t.StringType(), default=[])
    nargs = t.StringType()
    action = t.StringType()


class AddContainerAttribute(ContainerAttribute):

    data = t.ListType(t.StringType(), default=[])


class AddNewObject(ModelObject):

    id = t.StringType()
    class_name = t.StringType()


class AddObjectAttribute(ObjectAttribute):
    
    object_id = t.StringType(required=True)
    type_properties = t.DictType(t.StringType(), default={})
