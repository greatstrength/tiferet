from schematics import types as t
from schematics import Model

CLI_ARGUMENT_TYPES = ['command', 'parent_argument']
CLI_ARGUMENT_TYPE_DEFAULT = 'command'
CLI_ARGUMENT_DATA_TYPES = ['str', 'int', 'float']
CLI_ARGUMENT_DATA_TYPE_DEFAULT = 'str'

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
    type = t.StringType(default=CLI_ARGUMENT_TYPE_DEFAULT, choices=CLI_ARGUMENT_TYPES)
    feature_id = t.StringType()
    flags = t.ListType(t.StringType(), default=[])
    data_type = t.StringType(default=CLI_ARGUMENT_DATA_TYPE_DEFAULT, choices=CLI_ARGUMENT_DATA_TYPES)
    required = t.BooleanType()
    default = t.StringType()
    positional = t.BooleanType()
    choices = t.ListType(t.StringType(), default=[])
    nargs = t.IntType()
    action = t.StringType()